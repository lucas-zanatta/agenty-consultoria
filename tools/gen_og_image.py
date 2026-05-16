"""
Gera assets/og-image.png (1200x630) usando Playwright + Chromium.
Rodar: python tools/gen_og_image.py
"""
import asyncio
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@900&family=Instrument+Serif:ital@1&family=Inter:wght@500&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  width: 1200px; height: 630px; overflow: hidden;
  background: #18130e;
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
  position: relative;
}

/* Geometric right accent */
.bg-right {
  position: absolute;
  top: 0; right: 0;
  width: 400px; height: 630px;
  background: linear-gradient(160deg, #d44d22 0%, #a83210 35%, #5c1a08 65%, #18130e 100%);
  opacity: 0.9;
}
.bg-slash {
  position: absolute;
  top: -80px; right: -40px;
  width: 260px; height: 480px;
  background: rgba(18,13,10,0.55);
  transform: rotate(-18deg);
  transform-origin: top right;
}

/* Content */
.wrap {
  position: relative; z-index: 2;
  padding: 60px 80px;
  height: 630px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* Top row */
.top { display: flex; justify-content: space-between; align-items: flex-start; }
.logo {
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 900; font-size: 26px;
  letter-spacing: 0.08em; color: #faf7f2;
}
.logo-sub {
  font-size: 11px; font-weight: 500;
  letter-spacing: 0.12em; color: rgba(250,247,242,0.3);
  margin-top: 5px; text-transform: uppercase;
}
.badge {
  border: 1px solid rgba(242,183,5,0.35);
  color: #f2b705;
  font-size: 10px; font-weight: 500;
  letter-spacing: 0.14em; text-transform: uppercase;
  padding: 7px 18px; border-radius: 2px;
  background: rgba(242,183,5,0.07);
}

/* Headline */
.mid { flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 32px 0; }
.h1 {
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 900; font-size: 118px;
  line-height: 0.87; letter-spacing: -0.025em;
  text-transform: uppercase; color: #faf7f2;
}
.h1-serif {
  font-family: 'Instrument Serif', serif;
  font-style: italic; font-weight: 400;
  text-transform: none; color: #c94a1f;
  font-size: 102px; letter-spacing: -0.01em;
}
.tagline {
  margin-top: 28px;
  font-size: 20px; line-height: 1.6;
  color: rgba(250,247,242,0.42);
  max-width: 560px;
}

/* Bottom row */
.bot { display: flex; align-items: center; justify-content: space-between; }
.accent-line { width: 56px; height: 2px; background: #f2b705; }
.url {
  font-size: 14px; letter-spacing: 0.14em;
  text-transform: uppercase; color: rgba(250,247,242,0.2);
}
</style>
</head>
<body>
  <div class="bg-right">
    <div class="bg-slash"></div>
  </div>

  <div class="wrap">
    <div class="top">
      <div>
        <div class="logo">AGENTY</div>
        <div class="logo-sub">CWB / BR</div>
      </div>
      <div class="badge">Consultoria de IA para PMEs</div>
    </div>

    <div class="mid">
      <div class="h1">
        Sua empresa<br>
        <span class="h1-serif">fatura mais</span><br>
        com IA.
      </div>
      <p class="tagline">
        Automações personalizadas para negócios em Curitiba.<br>
        WhatsApp · Google Meu Negócio · Atendimento por Voz
      </p>
    </div>

    <div class="bot">
      <div class="accent-line"></div>
      <div class="url">agenty.com.br</div>
    </div>
  </div>
</body>
</html>"""


async def main():
    from playwright.async_api import async_playwright

    out = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'assets', 'og-image.png')
    )

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1200, 'height': 630})
        await page.set_content(HTML, wait_until='domcontentloaded')
        # Wait for Google Fonts to load
        await page.wait_for_timeout(2000)
        await page.screenshot(
            path=out,
            clip={'x': 0, 'y': 0, 'width': 1200, 'height': 630}
        )
        await browser.close()

    print(f"Salvo: {out}")


asyncio.run(main())
