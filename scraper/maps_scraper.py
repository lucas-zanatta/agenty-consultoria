"""
Google Maps Scraper — Agenty
Raspa resultados do Google Maps por query e extrai dados dos negócios.
Usa Playwright para lidar com o JS dinâmico do Maps.

Uso:
    python maps_scraper.py --query "restaurante Curitiba" --max 30
    python maps_scraper.py --all   # Roda todas as queries do config.py
"""

import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import argparse
import asyncio
import json
import logging
import os
import re
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Page, BrowserContext

# Adiciona o diretório pai ao path para imports relativos
sys.path.insert(0, str(Path(__file__).parent))
import config

# ── Logging ───────────────────────────────────────────────────────────────────
Path(config.OUTPUT_DIR).mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(config.OUTPUT_DIR) / config.LOG_FILE, encoding="utf-8"),
    ],
)
log = logging.getLogger("agenty.scraper")


# ── Modelo de dados ────────────────────────────────────────────────────────────
@dataclass
class Business:
    name: str = ""
    category: str = ""
    address: str = ""
    phone: str = ""
    website: str = ""
    rating: Optional[float] = None
    reviews_count: int = 0
    responds_to_reviews: bool = False
    maps_url: str = ""
    hours: str = ""
    query_source: str = ""
    scraped_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S"))

    def to_dict(self) -> dict:
        return asdict(self)


# ── Scraper ────────────────────────────────────────────────────────────────────
class GoogleMapsScraper:

    def __init__(self, headless: bool = True):
        self.headless = headless

    async def scrape_query(self, query: str, max_results: int) -> list[Business]:
        """Raspa resultados do Google Maps para uma query."""
        log.info(f"Buscando: '{query}' (máx. {max_results} resultados)")
        businesses: list[Business] = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            context: BrowserContext = await browser.new_context(
                viewport={"width": 1280, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="pt-BR",
            )
            page: Page = await context.new_page()

            try:
                # Navega para o Google Maps com a query
                search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
                await page.goto(search_url, wait_until="domcontentloaded", timeout=60_000)
                await page.wait_for_timeout(int(config.PAGE_LOAD_WAIT * 1000))

                # Fecha modal de cookies se aparecer
                try:
                    await page.click('button:has-text("Aceitar tudo")', timeout=3_000)
                    await page.wait_for_timeout(1_000)
                except Exception:
                    pass

                # Localiza o painel de resultados
                results_panel = page.locator('[role="feed"]')
                if not await results_panel.is_visible(timeout=10_000):
                    log.warning(f"Painel de resultados não encontrado para '{query}'")
                    return businesses

                # Coleta links de estabelecimentos via scroll progressivo
                collected_links: set[str] = set()
                scroll_attempts = 0
                max_scrolls = max_results // 5 + 5

                while len(collected_links) < max_results and scroll_attempts < max_scrolls:
                    # Pega todos os links de estabelecimentos visíveis
                    links = await page.locator('a[href*="/maps/place/"]').all()
                    for link in links:
                        href = await link.get_attribute("href")
                        if href and "/maps/place/" in href:
                            # Normaliza o URL
                            base = href.split("?")[0]
                            collected_links.add(base)
                        if len(collected_links) >= max_results:
                            break

                    if len(collected_links) >= max_results:
                        break

                    # Scrolla o painel para carregar mais resultados
                    await results_panel.evaluate("el => el.scrollBy(0, 600)")
                    await page.wait_for_timeout(int(config.SCROLL_DELAY * 1000))

                    # Verifica se chegou ao fim
                    end_msg = page.locator("text=Você chegou ao fim da lista")
                    if await end_msg.is_visible(timeout=500):
                        log.info("Fim da lista de resultados atingido")
                        break

                    scroll_attempts += 1

                log.info(f"  → {len(collected_links)} estabelecimentos encontrados para '{query}'")

                # Visita cada página de estabelecimento
                for i, link in enumerate(list(collected_links)[:max_results], 1):
                    try:
                        biz = await self._scrape_business_page(page, link, query)
                        if biz and biz.name:
                            businesses.append(biz)
                            log.info(f"  [{i}/{min(len(collected_links), max_results)}] {biz.name} -- {biz.rating} ({biz.reviews_count} avaliacoes)")
                    except Exception as e:
                        log.warning(f"  Erro ao raspar {link}: {e}")

                    await page.wait_for_timeout(int(config.ACTION_DELAY * 1000))

            except Exception as e:
                log.error(f"Erro na query '{query}': {e}")
            finally:
                await browser.close()

        return businesses

    async def _scrape_business_page(self, page: Page, url: str, query: str) -> Optional[Business]:
        """Extrai dados de um estabelecimento específico."""
        await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        await page.wait_for_timeout(1_500)

        biz = Business(maps_url=url, query_source=query)

        try:
            # Nome
            name_el = page.locator('h1.DUwDvf, h1[class*="fontHeadlineLarge"]').first
            biz.name = await name_el.text_content(timeout=5_000) or ""
            biz.name = biz.name.strip()
        except Exception:
            pass

        try:
            # Categoria
            cat_el = page.locator('button[jsaction*="category"]').first
            biz.category = (await cat_el.text_content(timeout=3_000) or "").strip()
        except Exception:
            pass

        try:
            # Rating — busca padrão "4,5" ou "4.5"
            rating_el = page.locator('[aria-label*="estrelas"], [aria-label*="stars"]').first
            rating_text = await rating_el.get_attribute("aria-label", timeout=3_000) or ""
            match = re.search(r"(\d[,\.]\d)", rating_text)
            if match:
                biz.rating = float(match.group(1).replace(",", "."))
            else:
                # fallback: texto direto
                r_el = page.locator('span.ceNzKf, span[aria-hidden="true"]').first
                r_text = await r_el.text_content(timeout=2_000) or ""
                match2 = re.search(r"(\d[,\.]\d)", r_text)
                if match2:
                    biz.rating = float(match2.group(1).replace(",", "."))
        except Exception:
            pass

        try:
            # Número de avaliações
            reviews_el = page.locator('button[aria-label*="avaliações"], button[aria-label*="reviews"]').first
            reviews_text = await reviews_el.get_attribute("aria-label", timeout=3_000) or ""
            match = re.search(r"([\d\.,]+)\s+avalia", reviews_text)
            if match:
                biz.reviews_count = int(match.group(1).replace(".", "").replace(",", ""))
        except Exception:
            pass

        try:
            # Endereço
            addr_el = page.locator('[data-item-id="address"] .Io6YTe, [aria-label*="endereço"]').first
            biz.address = (await addr_el.text_content(timeout=3_000) or "").strip()
        except Exception:
            pass

        try:
            # Telefone
            phone_el = page.locator('[data-item-id*="phone"] .Io6YTe, [aria-label*="telefone"]').first
            biz.phone = (await phone_el.text_content(timeout=3_000) or "").strip()
        except Exception:
            pass

        try:
            # Site
            web_el = page.locator('[data-item-id="authority"] a, a[aria-label*="site"], a[aria-label*="website"]').first
            biz.website = (await web_el.get_attribute("href", timeout=3_000) or "").strip()
            # Remove UTMs do Google
            biz.website = biz.website.split("?")[0] if biz.website else ""
        except Exception:
            pass

        try:
            # Horário
            hours_el = page.locator('[aria-label*="horário"], [data-item-id*="oh"]').first
            biz.hours = (await hours_el.text_content(timeout=3_000) or "").strip()
        except Exception:
            pass

        try:
            # Verifica se responde a avaliações (indicador de engajamento)
            # Busca texto "Resposta do proprietário" nas avaliações
            await page.locator('button[aria-label*="Avaliações"], [data-tab-index="1"]').click(timeout=3_000)
            await page.wait_for_timeout(2_000)
            response_text = await page.locator('text=Resposta do proprietário').count()
            biz.responds_to_reviews = response_text > 0
        except Exception:
            pass

        return biz


# ── CLI ────────────────────────────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser(description="Agenty — Google Maps Scraper")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", "-q", type=str, help="Query de busca específica")
    group.add_argument("--all", "-a", action="store_true", help="Roda todas as queries do config.py")
    parser.add_argument("--max", "-m", type=int, default=config.MAX_RESULTS_PER_QUERY,
                        help=f"Máximo de resultados por query (padrão: {config.MAX_RESULTS_PER_QUERY})")
    parser.add_argument("--visible", action="store_true", help="Modo visível (sem headless)")
    parser.add_argument("--no-crm", action="store_true", help="Não sincroniza com o Notion CRM")
    args = parser.parse_args()

    scraper = GoogleMapsScraper(headless=not args.visible)
    queries = config.SEARCH_QUERIES if args.all else [args.query]

    all_businesses: list[Business] = []

    for query in queries:
        businesses = await scraper.scrape_query(query, args.max)
        all_businesses.extend(businesses)
        log.info(f"Subtotal: {len(all_businesses)} estabelecimentos coletados\n")

    if not all_businesses:
        log.warning("Nenhum estabelecimento encontrado.")
        return

    log.info(f"\n✅ Total coletado: {len(all_businesses)} estabelecimentos")

    # Salva JSON raw
    out_path = Path(config.OUTPUT_DIR)
    json_file = out_path / config.OUTPUT_JSON
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump([b.to_dict() for b in all_businesses], f, ensure_ascii=False, indent=2)
    log.info(f"💾 Dados brutos salvos em: {json_file}")

    # Analisa e classifica leads
    from lead_analyzer import LeadAnalyzer
    analyzer = LeadAnalyzer()
    leads = [analyzer.analyze(b) for b in all_businesses]

    # Salva CSV de leads classificados
    import csv
    csv_file = out_path / config.OUTPUT_CSV
    if leads:
        with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=leads[0].keys())
            writer.writeheader()
            writer.writerows(leads)
        log.info(f"📊 Leads classificados salvos em: {csv_file}")

    # Estatísticas
    high = sum(1 for l in leads if l["prioridade"] == "Alta")
    med  = sum(1 for l in leads if l["prioridade"] == "Média")
    low  = sum(1 for l in leads if l["prioridade"] == "Baixa")
    log.info(f"\nClassificacao de leads:")
    log.info(f"   Alta prioridade:  {high}")
    log.info(f"   Media prioridade: {med}")
    log.info(f"   Baixa prioridade: {low}")

    # Sincroniza com Notion CRM
    if not args.no_crm and config.NOTION_API_KEY and config.NOTION_DATABASE_ID:
        from crm_sync import NotionCRMSync
        crm = NotionCRMSync()
        log.info("\n🔄 Sincronizando com Notion CRM...")
        synced = await crm.sync_leads(leads)
        log.info(f"✅ {synced} leads adicionados ao Notion CRM")
    elif not args.no_crm:
        log.warning("⚠️  NOTION_API_KEY ou NOTION_DATABASE_ID não configurados. Pule com --no-crm ou configure as variáveis de ambiente.")


if __name__ == "__main__":
    asyncio.run(main())
