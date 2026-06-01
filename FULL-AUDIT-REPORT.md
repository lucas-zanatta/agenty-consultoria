# Auditoria SEO Completa — agenty.com.br
**Data:** 2026-06-01 | **Auditoria #2 (atualizada)**
**Tipo de negócio:** Local Service — Consultoria de IA para PMEs (Curitiba, PR)
**Páginas auditadas:** 13 (vs. 8 na auditoria anterior)

---

## SEO Health Score: **69 / 100** _(era 62 na auditoria #1 — +7 pts)_

| Categoria | Peso | Nota | Score |
|-----------|------|------|-------|
| Technical SEO | 22% | 78/100 | 17,2 |
| Content Quality | 23% | 70/100 | 16,1 |
| On-Page SEO | 20% | 60/100 | 12,0 |
| Schema / Dados Estruturados | 10% | 75/100 | 7,5 |
| Performance (CWV) | 10% | 65/100 | 6,5 |
| AI Search Readiness | 10% | 68/100 | 6,8 |
| Imagens | 5% | 80/100 | 4,0 |
| **TOTAL** | 100% | — | **70,1** |

---

## O que melhorou desde a auditoria #1

| Problema anterior | Status |
|-------------------|--------|
| `gestor-reputacao.html` sem H1 | ✅ CORRIGIDO |
| `gestor-reputacao.html` ausente do sitemap | ✅ CORRIGIDO (13 URLs no sitemap) |
| Homepage sem links para subpáginas | ✅ CORRIGIDO (footer linkado) |
| Twitter Card tags ausentes | ✅ CORRIGIDO (todas as páginas têm twitter:card) |
| CNPJ "em breve" no rodapé | ✅ CORRIGIDO (CNPJ no schema LocalBusiness) |
| Schema LocalBusiness incompleto | ⚠️ PARCIAL (falta telefone/openingHours/geo) |
| `faq.html` sem og:description | ✅ CORRIGIDO |
| Páginas de nicho (4x) criadas e otimizadas | ✅ NOVO |
| Artigo SEO `gestao-google-meu-negocio-curitiba.html` | ✅ NOVO |

---

## Executive Summary

### Top 5 Problemas Críticos
1. **5 títulos acima de 60 chars** — truncados nos SERPs, afetam CTR direto
2. **`gestao-google-meu-negocio-curitiba.html` quase órfã** — artigo valioso com apenas 2 inbound links internos
3. **`hero-man.png` com alt vazio** — imagem indexável sem contexto semântico
4. **LocalBusiness schema sem telefone, horários e geo** — impacto no Local Pack
5. **`gestao` page com CSS v=10** — pode estar sem estilos recentes (página usa v10, resto v13)

### Top 5 Quick Wins
1. Encurtar títulos das 4 páginas de nicho + gestao (15 min, impacto imediato no CTR)
2. Linkar `gestao-google-meu-negocio-curitiba.html` a partir de gestor-reputacao.html e footer
3. Adicionar alt text descritivo à `hero-man.png`
4. Adicionar `telephone` e `openingHours` ao schema LocalBusiness no index.html
5. Adicionar OG tags a `privacidade.html` e `termos.html`

---

## 1. Technical SEO (78/100)

### Crawlabilidade e Indexação

| Item | Status | Detalhe |
|------|--------|---------|
| robots.txt | ✅ | `Allow: /` — todos os crawlers permitidos |
| Sitemap | ✅ | 13 URLs com lastmod e changefreq corretos |
| Canonical tags | ✅ | Todas as 13 páginas com canonical correto |
| lang="pt-BR" | ✅ | Todas as páginas |
| HTTPS | ✅ | Ativo via GitHub Pages |
| meta robots | ✅ | `index, follow` em todas as páginas |
| Footer navigation | ✅ | Subpáginas linkadas no footer de todas as páginas |

### Problemas Técnicos Restantes

**ALTO — CSS versão inconsistente:**
```
gestao-google-meu-negocio-curitiba.html  →  style.css?v=10  (desatualizado)
gestor-reputacao.html                    →  style.css?v=11  (desatualizado)
index, sobre, servicos, casos, faq       →  style.css?v=10  (desatualizado)
clinicas, saloes, restaurantes, varejo   →  style.css?v=13  (atual)
```
A versão atual do CSS é v13. Páginas com v=10 e v=11 podem exibir estilos em cache do navegador. Isso não afeta o Google diretamente, mas pode quebrar o visual do usuário.

**MÉDIO — `gestao` page com nav antigo:**
A página `gestao-google-meu-negocio-curitiba.html` usa o nav e footer antigos (sem links Clínicas/Salões/Restaurantes/Varejo). As páginas de nicho foram criadas depois e o nav da gestao page não foi atualizado.

---

## 2. On-Page SEO (60/100)

### Títulos — Auditoria completa

| Página | Chars | Status |
|--------|-------|--------|
| `saloes.html` | **83** | CRÍTICO — truncado nos SERPs |
| `restaurantes.html` | **79** | CRÍTICO |
| `varejo.html` | **78** | CRÍTICO |
| `clinicas.html` | **75** | CRÍTICO |
| `gestao-google-meu-negocio-curitiba.html` | **65** | ALTO |
| `faq.html` | **61** | MÉDIO (1 char acima) |
| `index.html` | **61** | MÉDIO (1 char acima) |
| `casos.html` | 57 | ✅ OK |
| `gestor-reputacao.html` | 58 | ✅ OK |
| `sobre.html` | 50 | ✅ OK |
| `servicos.html` | 44 | ✅ OK |
| `privacidade.html` | 32 | ✅ OK |
| `termos.html` | **22** | BAIXO — muito curto |

**Títulos sugeridos:**

| Página | Atual (chars) | Sugerido (chars) |
|--------|--------------|-----------------|
| `saloes.html` | 83 | "IA para Salão de Beleza em Curitiba \| Agenty" (46) |
| `restaurantes.html` | 79 | "IA para Restaurantes em Curitiba \| Agenty" (43) |
| `varejo.html` | 78 | "IA para Varejo Local em Curitiba \| Agenty" (43) |
| `clinicas.html` | 75 | "IA para Clínicas em Curitiba \| Agenty" (38) |
| `gestao` | 65 | "Gestão Google Meu Negócio em Curitiba \| Quanto Custa \| Agenty" (62) |
| `termos.html` | 22 | "Termos de Uso \| Agenty — Curitiba, PR" (38) |

### Meta Descriptions
Todas as 13 páginas têm meta description com comprimentos adequados. ✅

### OG / Social Tags

| Página | og:title | og:desc | og:image | twitter |
|--------|----------|---------|---------|---------|
| index | ✅ | ✅ | ✅ | ✅ |
| servicos | ✅ | ✅ | ✅ | ✅ |
| sobre | ✅ | ✅ | ✅ | ✅ |
| casos | ✅ | ✅ | ✅ | ✅ |
| faq | ✅ | ✅ | ✅ | ✅ |
| gestor-reputacao | ✅ | ✅ | ✅ | ✅ |
| clinicas | ✅ | ✅ | ✅ | ✅ |
| saloes | ✅ | ✅ | ✅ | ✅ |
| restaurantes | ✅ | ✅ | ✅ | ✅ |
| varejo | ✅ | ✅ | ✅ | ✅ |
| gestao-google | ✅ | ✅ | ✅ | ✅ |
| privacidade | ❌ | ❌ | ❌ | ❌ |
| termos | ❌ | ❌ | ❌ | ❌ |

### Internal Linking

| Página | Inbound links internos |
|--------|----------------------|
| faq.html | 34 ✅ |
| casos.html | 29 ✅ |
| sobre.html | 29 ✅ |
| servicos.html | 24 ✅ |
| privacidade.html | 16 ✅ |
| termos.html | 15 ✅ |
| clinicas.html | 7 ✅ |
| saloes.html | 7 ✅ |
| gestor-reputacao.html | 7 ✅ |
| restaurantes.html | 6 ⚠️ Baixo |
| varejo.html | 6 ⚠️ Baixo |
| **gestao-google-meu-negocio-curitiba.html** | **2 ❌ Quase órfã** |

**`gestao` está linkada apenas em:**
- Ela própria (via nav/footer auto-referência)
- `varejo.html` (1 link de conteúdo)

**Oportunidades para linkar `gestao-google-meu-negocio-curitiba.html`:**
- `gestor-reputacao.html` → "Entenda quanto custa a gestão manual do Google Meu Negócio →"
- `index.html` footer → adicionar link "Guia: Gestão Google"
- `servicos.html` → dentro do card do Gestor de Reputação
- `clinicas.html`, `saloes.html`, `restaurantes.html` → seção de recursos relacionados

---

## 3. Schema / Dados Estruturados (75/100)

### Inventário completo

| Página | Tipos implementados |
|--------|-------------------|
| index.html | LocalBusiness |
| sobre.html | AboutPage |
| servicos.html | ItemList + BreadcrumbList |
| casos.html | CollectionPage + BreadcrumbList |
| faq.html | FAQPage + BreadcrumbList |
| gestor-reputacao.html | Service + BreadcrumbList |
| clinicas.html | Service + BreadcrumbList |
| saloes.html | Service + BreadcrumbList |
| restaurantes.html | Service + BreadcrumbList |
| varejo.html | Service + BreadcrumbList |
| gestao-google | Article + FAQPage + BreadcrumbList |
| privacidade.html | ❌ Nenhum |
| termos.html | ❌ Nenhum |

### LocalBusiness schema — o que falta

```json
// ATUAL em index.html (campos presentes):
{
  "@type": "LocalBusiness",
  "name": "Agenty",
  "description": "...",
  "url": "https://agenty.com.br",
  "email": "contato@agenty.com.br",
  "image": "https://agenty.com.br/assets/og-image.png",
  "priceRange": "$$",
  "address": { "addressLocality": "Curitiba", "addressRegion": "PR", "addressCountry": "BR" },
  "areaServed": { "@type": "City", "name": "Curitiba" },
  "sameAs": ["https://www.linkedin.com/in/lucas-zanatta-1b46b2113/"],
  "legalName": "Xpert Brasil Consultoria, Planejamento e Projetos",
  "taxID": "00.261.584/0001-59"
}

// CAMPOS A ADICIONAR (alta prioridade para Local Pack):
"telephone": "+55-41-XXXX-XXXX",
"openingHours": "Mo-Fr 09:00-18:00",
"geo": {
  "@type": "GeoCoordinates",
  "latitude": -25.4290,
  "longitude": -49.2710
}
```

---

## 4. Imagens (80/100)

| Imagem | Página | Alt atual | Status |
|--------|--------|-----------|--------|
| hero-man.png | index | `""` vazio | ❌ Adicionar alt descritivo |
| lucas1.png | index | "Lucas Zanatta" | ✅ |
| lucas2.png | index | "Lucas Zanatta" | ✅ |
| lucas3.jpg | index | "Lucas Zanatta" | ✅ |

**Recomendação:**
```html
<img src="assets/hero-man.png" alt="Consultor de IA para pequenos negócios em Curitiba" 
     width="520" height="680" loading="lazy">
```
O `width`/`height` previne CLS (Cumulative Layout Shift). O `loading="lazy"` melhora o LCP da página.

**Nota:** Subpáginas têm 0 imagens. Não é problema de SEO técnico, mas imagens em páginas de produto aumentam engajamento e chances de aparecer no Google Images.

---

## 5. Qualidade de Conteúdo / E-E-A-T (70/100)

### Sinais positivos
- Autor real identificado (Lucas Zanatta) com fotos e LinkedIn ✅
- Localização explícita (Curitiba, PR) em títulos, descriptions e conteúdo ✅
- CNPJ e razão social no schema ✅
- Email de contato público ✅
- Artigo de profundidade (`gestao-google`) bem estruturado ✅
- FAQPage com perguntas e respostas diretas ✅

### Lacunas de E-E-A-T
- **Sem telefone público** em nenhuma página — sinal de confiança ausente
- **Casos.html**: conteúdo ainda genérico, sem depoimentos reais (task pendente)
- **Sem certificações ou logos de parceiros** (Meta, Google, Anthropic) — validadores de autoridade
- **Sem Google Business Profile** confirmado — o próprio produto principal depende disso

---

## 6. Performance — estimativa estática (65/100)

| Fator | Avaliação |
|-------|-----------|
| Google Fonts (3 famílias) | ⚠️ `display=swap` presente, mas 3 famílias pesam |
| JS próprio (main.js) | ✅ Leve, sem frameworks |
| Cal.com embed | ⚠️ Script de terceiro em todas as páginas |
| `hero-man.png` sem width/height | ⚠️ Risco de CLS na homepage |
| GitHub Pages CDN | ✅ TTFB baixo globalmente |
| Sem lazy loading em imagens | ⚠️ Menor prioridade para site com poucas imagens |

**Para dados reais:** Conectar Google Search Console + CrUX (gratuito via API do Google).

---

## 7. AI Search Readiness / GEO (68/100)

| Sinal | Status |
|-------|--------|
| FAQPage schema | ✅ faq.html + gestao-google |
| Conteúdo citável por passagem | ✅ Seções "Dores", "Processo", FAQ |
| Autor identificado com credencial | ✅ |
| Dados factuais específicos | ✅ Preços, prazos, CNPJ |
| llms.txt | ❌ Ausente |
| Fontes externas citadas | ❌ Sem links para fontes |
| NAP completo (Nome/Endereço/Telefone) | ⚠️ Sem telefone |

**Ação de maior impacto:** Criar `/llms.txt` com instruções para crawlers de IA (GPTBot, ClaudeBot, PerplexityBot).

---

## 8. Local SEO

| Sinal | Status |
|-------|--------|
| Cidade no title de todas as páginas | ✅ |
| "Curitiba" em meta descriptions | ✅ |
| Schema `LocalBusiness` | ✅ (incompleto — sem tel/horário/geo) |
| Google Business Profile | ❓ Não verificado |
| Páginas de nicho por segmento | ✅ (clinicas, saloes, restaurantes, varejo) |
| NAP consistente | ⚠️ Telefone ausente |

---

## 9. Comparativo Auditoria #1 vs #2

| Métrica | Auditoria #1 | Auditoria #2 | Delta |
|---------|-------------|-------------|-------|
| Páginas no sitemap | 7 | 13 | +6 |
| Páginas auditadas | 8 | 13 | +5 |
| Twitter Card | 0/8 | 11/13 | ✅ |
| Schema blocks totais | ~6 | 23 | ✅ |
| Pages com OG completo | 5/8 | 11/13 | ✅ |
| Score geral | 62 | 69 | +7 |

---

## Distribuição de Prioridades

```
CRÍTICO (fix imediato):   3 issues
ALTO    (fix esta semana): 5 issues
MÉDIO   (fix este mês):   4 issues
BAIXO   (backlog):        3 issues
```

Ver ACTION-PLAN.md para lista detalhada com esforço estimado.
