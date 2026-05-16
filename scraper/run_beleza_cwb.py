"""
Prospecção: beleza & bem-estar nos bairros norte de Curitiba.
Roda até 100 leads únicos e sincroniza no Notion CRM.

Uso:
    python run_beleza_cwb.py
    python run_beleza_cwb.py --visible   (modo debug com browser visível)
    python run_beleza_cwb.py --no-crm    (sem sync Notion)
"""

import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import argparse
import asyncio
import csv
import json
import logging
import re
import time
from pathlib import Path

from playwright.async_api import async_playwright, Page

sys.path.insert(0, str(Path(__file__).parent))
import config
from lead_analyzer import LeadAnalyzer

# ── Config desta rodada ────────────────────────────────────────────────────────

TARGET_LEADS = 100
MAX_PER_QUERY = 8   # coleta até 8 por query; para ao bater 100 únicos

BAIRROS = [
    "Bairro Alto", "Bacacheri", "Boa Vista", "Santa Candida",
    "Capao da Imbuia", "Taruma", "Juveve", "Ahu", "Hugo Langue", "Alto da XV",
]

TIPOS = [
    "salao de beleza",
    "barbearia",
    "clinica estetica",
    "pilates",
]

QUERIES = [f"{tipo} {bairro} Curitiba" for tipo in TIPOS for bairro in BAIRROS]

# ── Logging ────────────────────────────────────────────────────────────────────

Path(config.OUTPUT_DIR).mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            Path(config.OUTPUT_DIR) / "beleza_cwb.log", encoding="utf-8"
        ),
    ],
)
log = logging.getLogger("agenty.beleza")


# ── Modelo de dados (inline p/ evitar import circular) ────────────────────────

from dataclasses import dataclass, asdict, field
from typing import Optional

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

    def to_dict(self):
        return asdict(self)


# ── Scraping com browser compartilhado ────────────────────────────────────────

async def scrape_all(queries: list[str], max_per_query: int, headless: bool, target: int) -> list[Business]:
    all_businesses: list[Business] = []
    seen_urls: set[str] = set()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="pt-BR",
        )
        page: Page = await context.new_page()

        # Aceita cookies na primeira navegação
        await page.goto("https://www.google.com/maps", wait_until="domcontentloaded", timeout=60_000)
        await page.wait_for_timeout(2_000)
        try:
            await page.click('button:has-text("Aceitar tudo")', timeout=4_000)
            await page.wait_for_timeout(1_000)
        except Exception:
            pass

        for qi, query in enumerate(queries, 1):
            if len(all_businesses) >= target:
                log.info(f"Meta de {target} leads atingida — encerrando buscas.")
                break

            log.info(f"[{qi}/{len(queries)}] Buscando: '{query}' | Total ate agora: {len(all_businesses)}")

            links = await _collect_links(page, query, max_per_query)
            log.info(f"  -> {len(links)} links coletados")

            for link in links:
                if len(all_businesses) >= target:
                    break
                if link in seen_urls:
                    continue
                seen_urls.add(link)

                try:
                    biz = await _scrape_business(page, link, query)
                    if biz and biz.name:
                        all_businesses.append(biz)
                        log.info(
                            f"  [{len(all_businesses)}] {biz.name} | "
                            f"{biz.rating} ({biz.reviews_count} aval.) | "
                            f"Site: {'sim' if biz.website else 'nao'}"
                        )
                except Exception as e:
                    log.warning(f"  Erro em {link}: {e}")

                await page.wait_for_timeout(1_200)

        await browser.close()

    return all_businesses


async def _collect_links(page: Page, query: str, max_results: int) -> list[str]:
    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=60_000)
        await page.wait_for_timeout(int(config.PAGE_LOAD_WAIT * 1000))
    except Exception as e:
        log.warning(f"Erro ao carregar '{query}': {e}")
        return []

    results_panel = page.locator('[role="feed"]')
    if not await results_panel.is_visible(timeout=8_000):
        return []

    collected: list[str] = []
    seen: set[str] = set()
    scroll_attempts = 0
    max_scrolls = max_results // 4 + 4

    while len(collected) < max_results and scroll_attempts < max_scrolls:
        links = await page.locator('a[href*="/maps/place/"]').all()
        for link in links:
            href = await link.get_attribute("href")
            if href and "/maps/place/" in href:
                base = href.split("?")[0]
                if base not in seen:
                    seen.add(base)
                    collected.append(base)
            if len(collected) >= max_results:
                break

        if len(collected) >= max_results:
            break

        await results_panel.evaluate("el => el.scrollBy(0, 700)")
        await page.wait_for_timeout(int(config.SCROLL_DELAY * 1000))

        end_msg = page.locator("text=Voce chegou ao fim da lista")
        if await end_msg.is_visible(timeout=400):
            break

        scroll_attempts += 1

    return collected[:max_results]


async def _scrape_business(page: Page, url: str, query: str) -> Optional[Business]:
    await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    await page.wait_for_timeout(1_500)

    biz = Business(maps_url=url, query_source=query)

    try:
        name_el = page.locator('h1.DUwDvf, h1[class*="fontHeadlineLarge"]').first
        biz.name = (await name_el.text_content(timeout=5_000) or "").strip()
    except Exception:
        pass

    try:
        cat_el = page.locator('button[jsaction*="category"]').first
        biz.category = (await cat_el.text_content(timeout=3_000) or "").strip()
    except Exception:
        pass

    try:
        rating_el = page.locator('[aria-label*="estrelas"], [aria-label*="stars"]').first
        rating_text = await rating_el.get_attribute("aria-label", timeout=3_000) or ""
        match = re.search(r"(\d[,\.]\d)", rating_text)
        if match:
            biz.rating = float(match.group(1).replace(",", "."))
    except Exception:
        pass

    try:
        reviews_el = page.locator('button[aria-label*="avalia"], button[aria-label*="review"]').first
        reviews_text = await reviews_el.get_attribute("aria-label", timeout=3_000) or ""
        match = re.search(r"([\d\.,]+)\s+avalia", reviews_text)
        if match:
            biz.reviews_count = int(match.group(1).replace(".", "").replace(",", ""))
    except Exception:
        pass

    try:
        addr_el = page.locator('[data-item-id="address"] .Io6YTe, [aria-label*="endereco"]').first
        biz.address = (await addr_el.text_content(timeout=3_000) or "").strip()
    except Exception:
        pass

    try:
        phone_el = page.locator('[data-item-id*="phone"] .Io6YTe, [aria-label*="telefone"]').first
        biz.phone = (await phone_el.text_content(timeout=3_000) or "").strip()
    except Exception:
        pass

    try:
        web_el = page.locator('[data-item-id="authority"] a, a[aria-label*="site"], a[aria-label*="website"]').first
        href = await web_el.get_attribute("href", timeout=3_000) or ""
        biz.website = href.split("?")[0] if href else ""
    except Exception:
        pass

    try:
        await page.locator('button[aria-label*="Avaliacoes"], [data-tab-index="1"]').click(timeout=3_000)
        await page.wait_for_timeout(1_500)
        biz.responds_to_reviews = await page.locator('text=Resposta do proprietario').count() > 0
    except Exception:
        pass

    return biz


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Prospecção beleza CWB")
    parser.add_argument("--visible", action="store_true", help="Browser visivel (debug)")
    parser.add_argument("--no-crm",  action="store_true", help="Nao sincroniza com Notion")
    parser.add_argument("--max",     type=int, default=MAX_PER_QUERY, help="Resultados por query")
    parser.add_argument("--target",  type=int, default=TARGET_LEADS,  help="Meta de leads unicos")
    args = parser.parse_args()

    log.info(f"Iniciando prospecção: {len(QUERIES)} queries | meta: {args.target} leads")
    log.info(f"Tipos: {TIPOS}")
    log.info(f"Bairros: {BAIRROS}\n")

    businesses = await scrape_all(QUERIES, args.max, not args.visible, args.target)

    if not businesses:
        log.warning("Nenhum negocio encontrado.")
        return

    log.info(f"\nTotal coletado: {len(businesses)} estabelecimentos")

    # Salva JSON raw
    out = Path(config.OUTPUT_DIR)
    json_file = out / "beleza_cwb.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump([b.to_dict() for b in businesses], f, ensure_ascii=False, indent=2)
    log.info(f"JSON salvo: {json_file}")

    # Analisa e classifica
    analyzer = LeadAnalyzer()
    leads = [analyzer.analyze(b) for b in businesses]

    csv_file = out / "beleza_cwb.csv"
    with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=leads[0].keys())
        writer.writeheader()
        writer.writerows(leads)
    log.info(f"CSV salvo: {csv_file}")

    # Estatísticas
    high = sum(1 for l in leads if l["prioridade"] == "Alta")
    med  = sum(1 for l in leads if l["prioridade"] == "Media")
    low  = sum(1 for l in leads if l["prioridade"] == "Baixa")
    log.info(f"\nClassificacao:")
    log.info(f"  Alta:  {high}")
    log.info(f"  Media: {med}")
    log.info(f"  Baixa: {low}")

    # Sincroniza com Notion
    if not args.no_crm and config.NOTION_API_KEY and config.NOTION_DATABASE_ID:
        from crm_sync import NotionCRMSync
        crm = NotionCRMSync()
        log.info("\nSincronizando com Notion CRM...")
        synced = await crm.sync_leads(leads)
        log.info(f"{synced} leads adicionados ao Notion CRM")
    elif not args.no_crm:
        log.warning("Credenciais Notion nao configuradas. Use --no-crm ou configure .env")


if __name__ == "__main__":
    asyncio.run(main())
