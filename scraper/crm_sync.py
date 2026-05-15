"""
Notion CRM Sync — Agenty
Sincroniza leads analisados com o banco de dados no Notion.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import httpx

sys.path.insert(0, str(Path(__file__).parent))
import config

log = logging.getLogger("agenty.crm_sync")

NOTION_API_VERSION = "2022-06-28"
NOTION_API_BASE    = "https://api.notion.com/v1"


class NotionCRMSync:

    def __init__(
        self,
        api_key: str = config.NOTION_API_KEY,
        database_id: str = config.NOTION_DATABASE_ID,
    ):
        if not api_key or not database_id:
            raise ValueError(
                "Configure NOTION_API_KEY e NOTION_DATABASE_ID como variáveis de ambiente."
            )
        self.api_key = api_key
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        }

    async def sync_leads(self, leads: list[dict]) -> int:
        """Adiciona leads ao Notion. Retorna o número de leads sincronizados."""
        synced = 0
        async with httpx.AsyncClient(timeout=30) as client:
            for lead in leads:
                try:
                    # Verifica se o negócio já existe pelo nome + telefone
                    existing = await self._find_existing(client, lead["nome"], lead["telefone"])
                    if existing:
                        log.debug(f"Lead já existe: {lead['nome']} — pulando")
                        continue

                    payload = self._build_notion_payload(lead)
                    resp = await client.post(
                        f"{NOTION_API_BASE}/pages",
                        headers=self.headers,
                        json=payload,
                    )
                    resp.raise_for_status()
                    synced += 1
                    log.info(f"  ✅ CRM: {lead['nome']} ({lead['prioridade']}) adicionado")
                except httpx.HTTPStatusError as e:
                    log.warning(f"  ❌ Erro ao adicionar {lead['nome']}: {e.response.text}")
                except Exception as e:
                    log.warning(f"  ❌ Erro ao adicionar {lead['nome']}: {e}")

                # Rate limit: Notion API permite ~3 req/s
                await asyncio.sleep(0.4)

        return synced

    async def _find_existing(self, client: httpx.AsyncClient, name: str, phone: str) -> bool:
        """Busca se um lead com o mesmo nome já existe no banco."""
        try:
            payload = {
                "filter": {
                    "property": "Nome do Negócio",
                    "title": {"equals": name},
                }
            }
            resp = await client.post(
                f"{NOTION_API_BASE}/databases/{self.database_id}/query",
                headers=self.headers,
                json=payload,
            )
            data = resp.json()
            return len(data.get("results", [])) > 0
        except Exception:
            return False

    def _build_notion_payload(self, lead: dict) -> dict:
        """Constrói o payload para criar uma página no Notion."""

        def rich_text(text: str) -> list:
            return [{"type": "text", "text": {"content": str(text)[:2000]}}]

        def select(value: str) -> dict:
            return {"name": str(value)[:100]}

        def multi_select(values: str) -> list:
            items = [v.strip() for v in values.split("|") if v.strip()]
            return [{"name": item[:100]} for item in items[:10]]

        rating = lead.get("avaliacao")
        reviews = lead.get("num_avaliacoes", 0)
        score = lead.get("score", 0)

        properties: dict = {
            "Nome do Negócio": {
                "title": rich_text(lead.get("nome", "")),
            },
            "Status": {
                "select": select(lead.get("status", "Novo")),
            },
            "Prioridade": {
                "select": select(lead.get("prioridade", "Baixa")),
            },
            "Categoria": {
                "rich_text": rich_text(lead.get("categoria", "")),
            },
            "Telefone": {
                "phone_number": str(lead.get("telefone", ""))[:50] or None,
            },
            "Site": {
                "url": lead.get("site") or None,
            },
            "Google Maps": {
                "url": lead.get("maps_url") or None,
            },
            "Endereço": {
                "rich_text": rich_text(lead.get("endereco", "")),
            },
            "Score": {
                "number": int(score),
            },
            "Dores Identificadas": {
                "rich_text": rich_text(lead.get("dores", "")),
            },
            "Oportunidades": {
                "rich_text": rich_text(lead.get("oportunidades", "")),
            },
            "Script de Abordagem": {
                "rich_text": rich_text(lead.get("script_abordagem", "")[:2000]),
            },
            "Fonte": {
                "select": select("Google Maps"),
            },
            "Responde Avaliações": {
                "checkbox": bool(lead.get("responde_avaliacoes", False)),
            },
            "Tem Site": {
                "checkbox": bool(lead.get("site", "")),
            },
        }

        # Adiciona rating e reviews apenas se disponíveis (Notion não aceita None em number)
        if rating is not None:
            properties["Avaliação Google"] = {"number": float(rating)}
        if reviews:
            properties["Nº Avaliações"] = {"number": int(reviews)}

        # Remove phone_number None
        if properties["Telefone"]["phone_number"] is None:
            del properties["Telefone"]

        return {
            "parent": {"database_id": self.database_id},
            "properties": properties,
        }


# ── Setup inicial do banco Notion ─────────────────────────────────────────────

async def setup_notion_database(api_key: str, parent_page_id: str) -> str:
    """
    Cria o banco de dados de Leads no Notion.
    Retorna o ID do banco criado.

    Uso: python crm_sync.py --setup --page-id SEU_PAGE_ID
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }

    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "🎯 Leads — Agenty CRM"}}],
        "properties": {
            "Nome do Negócio": {"title": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Novo",             "color": "blue"},
                        {"name": "A contatar",       "color": "yellow"},
                        {"name": "Contato feito",    "color": "orange"},
                        {"name": "Em negociação",    "color": "purple"},
                        {"name": "Proposta enviada", "color": "pink"},
                        {"name": "Cliente",          "color": "green"},
                        {"name": "Descartado",       "color": "gray"},
                        {"name": "Sem interesse",    "color": "red"},
                    ]
                }
            },
            "Prioridade": {
                "select": {
                    "options": [
                        {"name": "Alta",  "color": "red"},
                        {"name": "Média", "color": "yellow"},
                        {"name": "Baixa", "color": "blue"},
                    ]
                }
            },
            "Score":           {"number": {"format": "number"}},
            "Avaliação Google": {"number": {"format": "number"}},
            "Nº Avaliações":   {"number": {"format": "number"}},
            "Telefone":        {"phone_number": {}},
            "Site":            {"url": {}},
            "Google Maps":     {"url": {}},
            "Endereço":        {"rich_text": {}},
            "Categoria":       {"rich_text": {}},
            "Dores Identificadas": {"rich_text": {}},
            "Oportunidades":   {"rich_text": {}},
            "Script de Abordagem": {"rich_text": {}},
            "Notas":           {"rich_text": {}},
            "Fonte": {
                "select": {
                    "options": [
                        {"name": "Google Maps",  "color": "green"},
                        {"name": "Indicação",    "color": "blue"},
                        {"name": "LinkedIn",     "color": "purple"},
                        {"name": "Instagram",    "color": "pink"},
                        {"name": "Site",         "color": "orange"},
                        {"name": "Outro",        "color": "gray"},
                    ]
                }
            },
            "Responde Avaliações": {"checkbox": {}},
            "Tem Site":            {"checkbox": {}},
            "Data de Cadastro":    {"created_time": {}},
            "Próximo Contato":     {"date": {}},
        },
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{NOTION_API_BASE}/databases",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        db_id = resp.json()["id"]
        print(f"\n✅ Banco de dados criado com sucesso!")
        print(f"   ID: {db_id}")
        print(f"   Adicione ao seu .env: NOTION_DATABASE_ID={db_id}")
        return db_id


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agenty — Notion CRM Setup")
    parser.add_argument("--setup", action="store_true",
                        help="Cria o banco de dados de leads no Notion")
    parser.add_argument("--page-id", type=str,
                        help="ID da página pai no Notion onde criar o banco")
    parser.add_argument("--api-key", type=str, default=config.NOTION_API_KEY,
                        help="Notion API Key (ou use a variável NOTION_API_KEY)")
    args = parser.parse_args()

    if args.setup:
        if not args.page_id:
            print("❌ Informe o --page-id da página pai no Notion.")
            sys.exit(1)
        if not args.api_key:
            print("❌ Informe --api-key ou configure NOTION_API_KEY.")
            sys.exit(1)
        asyncio.run(setup_notion_database(args.api_key, args.page_id))
    else:
        parser.print_help()
