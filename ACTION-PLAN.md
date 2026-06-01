# Plano de Ação SEO — agenty.com.br
**Data:** 2026-06-01 | **Auditoria #2** | **Score atual:** 69/100 | **Score estimado pós-fixes:** 82/100

---

## CRÍTICO — Fix imediato (impacto em CTR e rankings)

### C1. Encurtar títulos das páginas de nicho e do artigo gestao
**Esforço:** 15 min | **Impacto:** Alto (CTR direto nos SERPs)

Títulos acima de 60 chars são truncados no Google — a palavra-chave principal pode ser cortada.

| Arquivo | Título atual | Título proposto |
|---------|-------------|----------------|
| `saloes.html` | IA para Salão de Beleza em Curitiba \| Atendimento e Agendamento Automático \| Agenty (83) | IA para Salão de Beleza em Curitiba \| Agenty (46) |
| `restaurantes.html` | IA para Restaurantes em Curitiba \| Atendimento e Reputação Automáticos \| Agenty (79) | IA para Restaurantes em Curitiba \| Agenty (43) |
| `varejo.html` | IA para Varejo Local em Curitiba \| Atendimento WhatsApp e Google Maps \| Agenty (78) | IA para Varejo Local em Curitiba \| Agenty (43) |
| `clinicas.html` | IA para Clínicas em Curitiba \| Atendimento e Reputação Automáticos \| Agenty (75) | IA para Clínicas em Curitiba \| Agenty (38) |
| `gestao-google-meu-negocio-curitiba.html` | Quanto Custa a Gestão do Google Meu Negócio em Curitiba? \| Agenty (65) | Gestão Google Meu Negócio Curitiba \| Quanto Custa \| Agenty (60) |

### C2. Alt text em hero-man.png
**Esforço:** 2 min | **Impacto:** Médio (acessibilidade + Google Images)

Em `index.html`, alterar:
```html
<!-- ANTES -->
<img src="assets/hero-man.png" alt="">

<!-- DEPOIS -->
<img src="assets/hero-man.png" alt="Consultor de IA para pequenos negócios em Curitiba" width="520" height="680" loading="lazy">
```

### C3. Linkar artigo `gestao-google-meu-negocio-curitiba.html` internamente
**Esforço:** 20 min | **Impacto:** Alto (PageRank interno + crawl budget)

A página tem conteúdo de profundidade (Article + FAQPage schema) mas recebe apenas 2 links internos.

**Adicionar link em `gestor-reputacao.html`** — dentro de uma seção de contexto ou antes do CTA:
```html
<p>Quer entender quanto custa a gestão manual antes de automatizar? 
   <a href="gestao-google-meu-negocio-curitiba.html">Veja o guia completo →</a></p>
```

**Adicionar link no footer de `index.html`** — na coluna de links do footer:
```html
<a href="gestao-google-meu-negocio-curitiba.html" class="footer-new__link">Gestão Google</a>
```

**Adicionar link em `servicos.html`** — dentro do card/seção de Gestor de Reputação:
```html
<a href="gestao-google-meu-negocio-curitiba.html">Guia: Quanto custa a gestão Google →</a>
```

---

## ALTO — Fix esta semana

### A1. Completar LocalBusiness schema no index.html
**Esforço:** 10 min | **Impacto:** Alto (Local Pack, Knowledge Panel)

Adicionar os campos ausentes no bloco JSON-LD do `index.html`:
```json
"telephone": "+55-41-XXXX-XXXX",
"openingHours": "Mo-Fr 09:00-18:00",
"geo": {
  "@type": "GeoCoordinates",
  "latitude": -25.4290,
  "longitude": -49.2710
}
```
Substitua o telefone e coordenadas pelos dados reais.

### A2. Atualizar CSS version em todas as páginas para v=13
**Esforço:** 5 min | **Impacto:** Médio (consistência de estilo)

Páginas desatualizadas:
- `index.html`, `sobre.html`, `servicos.html`, `casos.html`, `faq.html` → v=10 → mudar para v=13
- `gestor-reputacao.html` → v=11 → mudar para v=13
- `gestao-google-meu-negocio-curitiba.html` → v=10 → mudar para v=13

### A3. Atualizar nav/footer de `gestao-google-meu-negocio-curitiba.html`
**Esforço:** 10 min | **Impacto:** Médio (UX + internal linking)

A página usa o nav antigo. Atualizar para incluir os links Clínicas, Salões, Restaurantes, Varejo no footer (igual às outras páginas).

### A4. Adicionar OG tags em `privacidade.html` e `termos.html`
**Esforço:** 10 min | **Impacto:** Baixo (previews em redes sociais)

```html
<meta property="og:title" content="Política de Privacidade | Agenty">
<meta property="og:description" content="Política de Privacidade da Agenty em conformidade com a LGPD.">
<meta property="og:image" content="https://agenty.com.br/assets/og-image.png">
<meta property="og:url" content="https://agenty.com.br/privacidade.html">
<meta name="twitter:card" content="summary_large_image">
```

### A5. Corrigir título de `termos.html` (muito curto)
**Esforço:** 2 min

```html
<!-- ANTES -->
<title>Termos de Uso | Agenty</title>

<!-- DEPOIS -->
<title>Termos de Uso | Agenty — Curitiba, PR</title>
```

---

## MÉDIO — Fix este mês

### M1. Criar `llms.txt` na raiz do site
**Esforço:** 30 min | **Impacto:** Médio (IA Search — GPTBot, ClaudeBot, Perplexity)

```
# llms.txt — Agenty (agenty.com.br)
# Consultoria de IA para pequenos negócios em Curitiba, PR

## Sobre
A Agenty desenvolve automações de inteligência artificial personalizadas para PMEs em Curitiba.
Fundador: Lucas Zanatta | contato@agenty.com.br

## Páginas para citação
- Homepage: https://agenty.com.br/
- Serviços: https://agenty.com.br/servicos.html
- FAQ: https://agenty.com.br/faq.html
- Gestor de Reputação: https://agenty.com.br/gestor-reputacao.html
- Guia Google Meu Negócio: https://agenty.com.br/gestao-google-meu-negocio-curitiba.html

## Não citar
- privacidade.html
- termos.html
```

### M2. Publicar caso de uso real na `casos.html`
**Esforço:** 2h (conteúdo) | **Impacto:** Alto (E-E-A-T, conversão)

Quando o setup da Cássia Marconi (Gestor de Reputação) estiver completo, publicar:
- Nome e segmento do negócio
- Problema antes da Agenty
- Solução implementada
- Resultado mensurado (ex.: "de 2 para 4,7 estrelas em 60 dias")
- Adicionar `Review` schema

### M3. Adicionar telefone público ao site
**Esforço:** 5 min | **Impacto:** Alto (E-E-A-T, Local SEO, conversão)

Exibir número de telefone/WhatsApp:
1. No footer de todas as páginas
2. No schema LocalBusiness
3. Na seção de contato/CTA

Benefício: NAP completo = melhor sinal para Local Pack do Google Maps.

### M4. width/height em hero-man.png para evitar CLS
**Incluído no C2** — adicionar `width="520" height="680"` previne Cumulative Layout Shift durante o carregamento.

---

## BAIXO — Backlog

### B1. Configurar Google Analytics 4
Tag GA4 não encontrada em nenhuma página. Sem dados de tráfego orgânico para medir impacto das ações de SEO.

### B2. Conectar Google Search Console
Verificar indexação por URL, ver queries de busca reais, detectar erros de crawl.

### B3. Criar Google Business Profile
O produto principal (Gestor de Reputação) depende de GBP ativo. Criar e verificar o perfil é obrigatório tanto para a própria credibilidade quanto para demonstrar o produto.

### B4. Expandir o artigo `gestao-google`
O artigo atual tem bom potencial para rankear em "gestão google meu negócio curitiba". Expandir com:
- Tabela comparativa com concorrentes locais
- Perguntas frequentes específicas de Curitiba
- CTA interno mais forte para gestor-reputacao.html

---

## Estimativa de impacto total

| Ação | Esforço | Score delta |
|------|---------|------------|
| C1 — Encurtar títulos | 15 min | +2,0 |
| C2 — Alt text hero | 2 min | +0,5 |
| C3 — Links para gestao page | 20 min | +1,5 |
| A1 — Schema LocalBusiness | 10 min | +2,0 |
| A2 — CSS v=13 em todas | 5 min | +0,5 |
| A3 — Nav gestao page | 10 min | +0,5 |
| A4 — OG tags privacidade/termos | 10 min | +0,5 |
| A5 — Título termos | 2 min | +0,2 |
| M1 — llms.txt | 30 min | +1,0 |
| M2 — Caso real | 2h | +3,0 |
| M3 — Telefone público | 5 min | +1,5 |
| **TOTAL estimado** | ~4h | **+13 pts → Score 82/100** |
