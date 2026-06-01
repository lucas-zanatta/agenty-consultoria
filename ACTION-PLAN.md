# Plano de Ação SEO — agenty.com.br
**Data:** 2026-06-01 | **Score atual:** 62/100 | **Score estimado pós-fixes:** 78/100

---

## CRÍTICO — Fix imediato (hoje)

### 1. Adicionar H1 em gestor-reputacao.html
**Impacto:** Alto | **Esforço:** 5 min

A seção hero usa `<span>` para o texto principal. Envolver o texto principal em um H1.

```html
<!-- Antes (linha ~68): -->
<div class="sh__text" id="sh-text">
  <span id="sh-word-l">Seu Google</span>
  <span id="sh-word-r">respondendo sozinho.</span>
</div>

<!-- Depois: -->
<h1 class="sh__text" id="sh-text">
  <span id="sh-word-l">Seu Google</span>
  <span id="sh-word-r">respondendo sozinho.</span>
</h1>
```

---

### 2. Adicionar gestor-reputacao.html ao sitemap.xml
**Impacto:** Alto | **Esforço:** 2 min

```xml
<url>
  <loc>https://agenty.com.br/gestor-reputacao.html</loc>
  <lastmod>2026-06-01</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.9</priority>
</url>
```
Inserir antes de `servicos.html` (segunda posição por importância).

---

### 3. Adicionar links de navegação na homepage
**Impacto:** Alto | **Esforço:** 15 min

O nav da homepage aponta apenas para âncoras internas. Adicionar links para subpáginas no nav ou no footer para garantir que o crawl do Google alcance todas as páginas.

**Opção A (recomendada):** Adicionar links no footer da homepage:
```html
<!-- Adicionar ao footer-new__right: -->
<a href="servicos.html" class="footer-new__legal-link">Serviços</a>
<a href="sobre.html" class="footer-new__legal-link">Sobre</a>
<a href="casos.html" class="footer-new__legal-link">Casos</a>
<a href="faq.html" class="footer-new__legal-link">FAQ</a>
```

**Opção B:** Substituir o nav da homepage pelo nav completo das subpáginas (maior impacto visual mas quebra o design de single-page atual).

---

## ALTO — Esta semana

### 4. Corrigir URL exibida no CTA da homepage
**Arquivo:** `index.html:390`

```html
<!-- Antes: -->
<p class="cta-big__url">cal.com/lucaszanatta/diagnostico</p>

<!-- Depois: -->
<p class="cta-big__url">cal.com/lucas-zanatta/diagnostico</p>
```
Ou remover o parágrafo se a URL de exibição não for necessária.

---

### 5. Adicionar Twitter Card tags em todas as páginas
**Impacto:** Médio-Alto | **Esforço:** 20 min (busca e substituição)

Adicionar após as tags og: em cada página:
```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="[mesmo og:title]">
<meta name="twitter:description" content="[mesmo og:description]">
<meta name="twitter:image" content="https://agenty.com.br/assets/og-image.png">
```

---

### 6. Adicionar og:description em faq.html
**Arquivo:** `faq.html` — inserir após og:url

```html
<meta property="og:description" content="Tire suas dúvidas sobre IA para pequenos negócios. Prazo, custos, LGPD e como funciona a Agenty. Curitiba-PR.">
```

---

### 7. Adicionar Schema à gestor-reputacao.html
**Impacto:** Médio | **Esforço:** 10 min

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "Gestor de Reputação Automático",
  "description": "Monitora e responde avaliações do Google Maps automaticamente. Resposta em até 2 horas, 24h por dia.",
  "url": "https://agenty.com.br/gestor-reputacao.html",
  "provider": {
    "@type": "LocalBusiness",
    "name": "Agenty",
    "url": "https://agenty.com.br"
  },
  "areaServed": { "@type": "City", "name": "Curitiba" },
  "serviceType": "Gestão de Reputação Online com IA"
}
</script>
```

---

### 8. Completar LocalBusiness schema na homepage
**Arquivo:** `index.html:17-28`

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Agenty",
  "description": "Consultoria de inteligência artificial para pequenos negócios em Curitiba.",
  "url": "https://agenty.com.br",
  "email": "contato@agenty.com.br",
  "image": "https://agenty.com.br/assets/og-image.png",
  "priceRange": "$$",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Curitiba",
    "addressRegion": "PR",
    "addressCountry": "BR"
  },
  "areaServed": { "@type": "City", "name": "Curitiba" },
  "sameAs": ["https://www.linkedin.com/in/lucas-zanatta-1b46b2113/"]
}
```

---

### 9. Corrigir/remover CNPJ "em breve" no rodapé
**Arquivo:** `index.html:401`

Se o CNPJ já existe, adicioná-lo. Se não, remover a menção — melhor não mencionar do que destacar a ausência.

```html
<!-- Opção A — se tem CNPJ: -->
<p class="footer-new__tagline">CONSULTORIA DE IA · CURITIBA, PR · CNPJ 00.000.000/0001-00</p>

<!-- Opção B — sem CNPJ ainda: -->
<p class="footer-new__tagline">CONSULTORIA DE IA · CURITIBA, PR · BR</p>
```

---

### 10. Corrigir dados falsos em sobre.html
**Arquivo:** `sobre.html:177`

O footer de `sobre.html` tem `wa.me/5541999999999` (número fictício) e `linkedin.com/company/agenty` (verificar se existe). Substituir pelo número real ou remover.

---

## MÉDIO — Próximas 2 semanas

### 11. Ampliar sobre.html (253 → 450+ palavras)
Adicionar seções: trajetória do Lucas, por que escolheu PMEs, tecnologias que usa, diferenciais vs agências grandes. Ajuda com E-E-A-T e busca por "consultoria IA Curitiba".

### 12. Adicionar schema BreadcrumbList nas subpáginas
`sobre.html` já tem breadcrumb HTML — falta o schema. Adicionar em: servicos, casos, faq, gestor-reputacao.

```json
{
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Início", "item": "https://agenty.com.br/"},
    {"@type": "ListItem", "position": 2, "name": "[Nome da página]", "item": "https://agenty.com.br/[pagina].html"}
  ]
}
```

### 13. Adicionar width/height ao `<video>` em gestor-reputacao.html
Previne CLS:
```html
<video autoplay muted loop playsinline preload="auto" width="1280" height="720">
```

### 14. Sincronizar CSS version em sobre.html
Trocar `href="css/style.css"` por `href="css/style.css?v=10"` (ou versão atual).

### 15. Criar llms.txt para AI search
Arquivo `/llms.txt` na raiz com orientação para crawlers de IA:
```
# Agenty — Consultoria de IA para PMEs em Curitiba
# https://agenty.com.br

## Permissões
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

## Sobre este site
Agenty é uma consultoria de IA para pequenos e médios negócios em Curitiba, PR.
Serviços: Gestor de Reputação, Atendente WhatsApp, Recepcionista por Voz, Gerador de Orçamentos, Redutor de No-Show.
Contato: contato@agenty.com.br
```

### 16. Instalar Google Analytics
Adicionar GA4 tracking em todas as páginas. Necessário para dados orgânicos reais e para configurar GSC com precisão.

---

## BAIXO — Backlog

### 17. Popularizar casos.html com casos reais
Assim que o primeiro cliente (ex: Cássia Marconi) tiver resultado, documentar com: segmento, problema, solução aplicada, resultado mensurável. Adicionar Review schema.

### 18. Atualizar lastmod do sitemap.xml dinamicamente
Ou manualmente a cada deploy. Datas estáticas (`2026-05-15`) prejudicam re-crawl de páginas atualizadas.

### 19. Configurar Google Business Profile
Criar/reclamar o perfil no GBP para agenty.com.br. Essencial para aparecer no Map Pack local de Curitiba e validar o próprio produto principal.

### 20. Obter API key gratuita do PageSpeed Insights
`console.cloud.google.com` → PageSpeed Insights API (key gratuita). Permite monitorar CWV reais via CrUX.

### 21. Configurar Moz API gratuita
2.500 rows/mês grátis. Habilita rastreamento de backlinks e DA ao longo do tempo.

---

## Estimativa de Impacto

| # | Fix | Esforço | Impacto no Score |
|---|-----|---------|-----------------|
| 1 | H1 em gestor-reputacao | 5 min | +3 pts |
| 2 | gestor-reputacao no sitemap | 2 min | +3 pts |
| 3 | Links de nav na homepage | 15 min | +4 pts |
| 4-6 | Twitter Cards + og:description | 20 min | +2 pts |
| 7-8 | Schema gestor-rep + LocalBusiness | 15 min | +3 pts |
| 9-10 | CNPJ + dados falsos | 5 min | +1 pt |
| 11-16 | Melhorias médias | 2-3h total | +5 pts |

**Score projetado após itens críticos e altos:** ~78/100
