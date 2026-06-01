# Auditoria SEO Completa — agenty.com.br
**Data:** 2026-06-01 | **Ferramenta:** claude-seo v2.0.0  
**Tipo de negócio detectado:** Local Service — Consultoria de IA para PMEs (Curitiba, PR)  
**Páginas rastreadas:** 8

---

## SEO Health Score: 62 / 100

| Categoria | Peso | Pontuação | Ponderado |
|-----------|------|-----------|-----------|
| Technical SEO | 22% | 62/100 | 13,6 |
| Content Quality | 23% | 58/100 | 13,3 |
| On-Page SEO | 20% | 72/100 | 14,4 |
| Schema / Dados Estruturados | 10% | 52/100 | 5,2 |
| Performance (CWV) | 10% | N/D* | 7,0 |
| AI Search Readiness | 10% | 48/100 | 4,8 |
| Imagens | 5% | 65/100 | 3,3 |

*PSI rate-limited sem API key. Estimativa conservadora aplicada.

---

## Resumo Executivo

### Top 5 Problemas Críticos
1. `gestor-reputacao.html` sem H1 — página de produto sem heading principal indexável
2. `gestor-reputacao.html` ausente do sitemap.xml — Google não descobre via mapa
3. Homepage sem links de navegação para subpáginas — crawl fragmentado
4. Nenhuma página tem Twitter Card meta tags
5. CNPJ "em breve" no rodapé — sinal negativo de E-E-A-T / autoridade

### Top 5 Quick Wins
1. Adicionar H1 em `gestor-reputacao.html` (5 min)
2. Adicionar URL ao sitemap.xml (2 min)
3. Adicionar links de nav na homepage para subpáginas (15 min)
4. Adicionar Twitter Card tags em todas as páginas (20 min)
5. Corrigir URL exibida no CTA (`cal.com/lucaszanatta/diagnostico` → URL correta)

---

## 1. Technical SEO

### Rastreabilidade e Indexação
| Item | Status | Detalhe |
|------|--------|---------|
| robots.txt | ✅ OK | Permite tudo, aponta para sitemap |
| sitemap.xml | ⚠️ Incompleto | 7 URLs — falta `gestor-reputacao.html` |
| Canonicals | ✅ OK | Todas as páginas têm canonical correto |
| lang="pt-BR" | ✅ OK | Todas as páginas |
| HTTPS | ✅ OK | Redirecionamento ativo |
| meta robots | ✅ OK | `index, follow` em todas as páginas |

### Problemas Técnicos
- **CRÍTICO:** `gestor-reputacao.html` não está no sitemap. É a única página de produto com conteúdo publicado e link da homepage — o Google pode demorar semanas para descobri-la organicamente.
- **ALTO:** Homepage não tem links de navegação para `sobre.html`, `servicos.html`, `casos.html`, `faq.html`. Os links do nav são âncoras internas (`#dores`, `#produtos`, etc.). Um crawler chegando pela homepage só pode seguir para `gestor-reputacao.html`, `privacidade.html` e `termos.html`. PageRank não flui para as subpáginas.
- **MÉDIO:** `sobre.html` carrega `css/style.css` sem query string de versão (`?v=N`), diferente das demais páginas. Risco de CSS em cache.
- **MÉDIO:** `gestor-reputacao.html` tem elemento `<video autoplay muted loop>` sem atributos `width` e `height` — pode causar CLS (Cumulative Layout Shift).

---

## 2. On-Page SEO

### Resumo por Página

| Página | Title | Desc | H1 | Schema | Palavras |
|--------|-------|------|----|--------|---------|
| index.html | ✅ 65 chars | ✅ 179 chars | ✅ 1 | ✅ LocalBusiness | 598 |
| gestor-reputacao.html | ✅ 43 chars | ✅ 139 chars | ❌ 0 | ❌ Nenhum | 504 |
| servicos.html | ✅ 41 chars | ✅ 168 chars | ✅ 1 | ✅ | 726 |
| sobre.html | ✅ 51 chars | ✅ 135 chars | ✅ 1 | ✅ AboutPage | 253 |
| casos.html | ✅ 60 chars | ✅ 159 chars | ✅ 1 | ❌ Nenhum | 397 |
| faq.html | ✅ 55 chars | ✅ 143 chars | ✅ 1 | ✅ FAQPage | 717 |
| privacidade.html | — | — | — | — | — |
| termos.html | — | — | — | — | — |

### Problemas de On-Page

**CRÍTICO — gestor-reputacao.html sem H1:**  
O hero da página usa `<span id="sh-word-l">Seu Google</span>` e `<span id="sh-word-r">respondendo sozinho.</span>` dentro de uma `<div class="sh__text">` — sem H1 em nenhum lugar da página. O Google não tem heading principal para entender o tópico da página.

**ALTO — Discrepância de preço:**  
Homepage exibe `R$99/mês` no card de manutenção. O CLAUDE.md registra `R$150/mês`. Uma das versões está errada — inconsistência que pode gerar desconfiança se capturada por comparadores ou citada por IA.

**ALTO — URL exibida no CTA incorreta:**  
Linha 390 do `index.html`:
```html
<p class="cta-big__url">cal.com/lucaszanatta/diagnostico</p>
```
URL real: `cal.com/lucas-zanatta-bettbr/diagnostico`. Quem digitar a URL exibida manualmente chegará em lugar errado.

**ALTO — "CNPJ EM BREVE" no rodapé:**  
```html
<p class="footer-new__tagline">CONSULTORIA DE IA · CURITIBA, PR · CNPJ EM BREVE</p>
```
Ausência de CNPJ é sinal negativo de E-E-A-T. Negócios sem CNPJ visível têm menor autoridade percebida pelo Google.

**MÉDIO — sobre.html conteúdo ralo (253 palavras):**  
Para uma página "Sobre", 253 palavras é thin content. Páginas de "About" em nichos de serviços profissionais geralmente precisam de 400–600 palavras para sinalizar autoridade.

---

## 3. Social / Open Graph

| Tag | index | gestor-rep. | servicos | sobre | casos | faq |
|-----|-------|-------------|----------|-------|-------|-----|
| og:title | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| og:description | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| og:image | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| og:url | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| twitter:card | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| twitter:title | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Problemas:**
- Nenhuma página tem Twitter/X Card tags. Posts no X e alguns parsers de links usam estas tags; sem elas o preview pode não aparecer.
- `faq.html` não tem `og:description`.
- `og:type` é `website` em todas as páginas — páginas de produto poderiam usar tipo mais específico.

---

## 4. Schema / Dados Estruturados

| Página | Schema presente | Problemas |
|--------|----------------|-----------|
| index.html | LocalBusiness | Falta: telephone, openingHours, image, sameAs (LinkedIn), priceRange |
| gestor-reputacao.html | ❌ Nenhum | Deveria ter Product ou Service schema |
| servicos.html | ✅ (tipo não verificado) | — |
| sobre.html | AboutPage + Organization | Organization sem URL, foundingDate, founder |
| casos.html | ❌ Nenhum | Poderia ter ItemList ou Review schema |
| faq.html | ✅ FAQPage | Bem implementado |

**LocalBusiness incompleto (index.html):**
```json
{
  "@type": "LocalBusiness",
  "name": "Agenty",
  // Faltando:
  "telephone": "",
  "image": "https://agenty.com.br/assets/og-image.png",
  "priceRange": "$$",
  "openingHours": "Mo-Fr 09:00-18:00",
  "sameAs": ["https://linkedin.com/in/lucas-zanatta-1b46b2113/"]
}
```

---

## 5. Imagens

| Imagem | Alt text | Problema |
|--------|----------|---------|
| assets/hero-man.png | `alt=""` | Decorativa — OK se intencional |
| assets/lucas1.png | `alt="Lucas Zanatta"` | ✅ |
| assets/lucas2.png | `alt="Lucas Zanatta"` | ✅ |
| assets/lucas3.jpg | `alt="Lucas Zanatta"` | ✅ |

- Subpáginas (sobre, servicos, casos, faq, gestor-reputacao) têm **0 imagens** — conteúdo 100% texto. Falta de imagens reduz possibilidade de aparecer em Image Search e diminui engajamento.
- OG image (`og-image.png`) presente em todas as páginas — ✅ bom.

---

## 6. Conteúdo / E-E-A-T

**Pontos fortes:**
- Autor identificado com nome real (Lucas Zanatta), fotos, LinkedIn
- Localização explícita (Curitiba, PR) em múltiplos pontos
- Proposta de valor clara e específica
- Copy direto, sem jargão desnecessário

**Pontos fracos:**
- `casos.html` sem casos reais — a página existe mas o conteúdo é placeholder ou muito vago (397 palavras)
- Sem depoimentos de clientes em nenhuma página
- Sem CNPJ visível (rodapé homepage)
- Placeholder `wa.me/5541999999999` no footer de `sobre.html` — se publicado assim, é dado falso rastreável
- Links no footer de `sobre.html` para `linkedin.com/company/agenty` — verificar se empresa existe no LinkedIn

---

## 7. AI Search Readiness (GEO)

| Sinal | Status |
|-------|--------|
| llms.txt | ❌ Ausente |
| Conteúdo cível por passagem | Parcial — FAQPage bem estruturado, resto é marketing |
| Brand mentions externas | Desconhecido (sem dados de backlinks) |
| Perguntas respondidas diretamente | ✅ FAQ tem respostas diretas |
| Schema para AI | FAQPage ✅ — suficiente para AI Overviews |

- Sem `llms.txt`, crawlers de IA (GPTBot, Claude, Perplexity) não têm orientação explícita sobre o que podem citar.
- O FAQ (`faq.html`) é a página com melhor citabilidade para IA — perguntas diretas com respostas específicas.
- Homepage tem bom conteúdo de passagem nas seções "Dores" e "Processo" — potencial para AI Overviews locais de Curitiba.

---

## 8. Local SEO

| Sinal | Status |
|-------|--------|
| NAP na homepage | Parcial — nome e cidade, sem telefone/endereço completo |
| Google Business Profile | Não verificado |
| Avaliações | Não verificado |
| LocalBusiness schema | ✅ Presente mas incompleto |
| Palavras-chave locais | ✅ "Curitiba" em títulos, descrições e conteúdo |

**Recomendação:** Criar/otimizar Google Business Profile é a ação de maior impacto para visibilidade local. O próprio produto principal (Gestor de Reputação) depende do GBP estar ativo.

---

## 9. Sitemap

**Estado atual:**
```
7 URLs registradas — gestor-reputacao.html ausente
Todas com lastmod: 2026-05-15 (estático)
Prioridades: bem configuradas
changefreq: adequado por tipo de página
```

**Problema crítico:** A página de produto mais importante do site não está no sitemap.

---

## 10. Performance (estimativa sem API key)

| Métrica | Estimativa | Risco |
|---------|------------|-------|
| LCP | Moderado | Google Fonts (3 famílias) bloqueia render |
| INP | Baixo | JS mínimo, sem frameworks pesados |
| CLS | Risco em gestor-reputacao.html | `<video>` sem width/height |
| TTFB | Baixo | GitHub Pages CDN global |

**Recomendação:** Obter API key do Google PageSpeed Insights (gratuita) para dados reais de CrUX e Lighthouse.

---

## Dados de Backlinks

Tier 0 (Common Crawl apenas — sem Moz/Bing API keys):
- Sem dados históricos de backlinks disponíveis
- Site novo — normal ter perfil de backlinks vazio
- **Recomendação:** Configurar Moz API (grátis, 2.500 rows/mês) para monitorar crescimento

