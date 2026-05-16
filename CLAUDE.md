# CLAUDE.md — Agenty Consultoria

Projeto de consultoria de IA para PMEs em Curitiba. Este arquivo documenta decisões técnicas, estrutura do projeto e convenções para desenvolvimento assistido.

---

## Visão geral

**Empresa:** Agenty  
**Posicionamento:** "Sua empresa fatura mais com IA."  
**Mercado:** Pequenas e médias empresas em Curitiba — PR  
**Modelo:** Soluções de IA personalizadas por cliente, desenvolvidas a partir de bases reutilizáveis  
**Domínio:** agenty.com.br  
**Repositório GitHub:** github.com/lucas-zanatta/agenty-consultoria  
**Hospedagem:** GitHub Pages  

---

## Modelo de preço

| Item | Valor |
|------|-------|
| Implementação | R$ 3.000 (50% na assinatura + 50% na entrega) |
| Manutenção mensal | R$ 150/mês |
| Apresentação no site | Soluções personalizadas — sem preço público por produto |

---

## Estrutura do repositório

```
CONSULTORIA/
├── index.html               # Landing page principal
├── sobre.html
├── servicos.html
├── casos.html
├── faq.html
├── privacidade.html
├── termos.html
├── sitemap.xml
├── robots.txt
├── CNAME                    # agenty.com.br
├── css/
│   └── style.css            # Design system completo (paleta quente, editorial)
├── js/
│   └── main.js              # Nav, FAQ accordion, scroll animations, rotating text, parallax
├── assets/
│   ├── favicon.svg
│   ├── hero-man.png         # Pessoa com fundo transparente — overlay desktop no hero
│   └── og-image.png         # OG image 1200×630px (gerada via tools/gen_og_image.py)
├── tools/
│   └── gen_og_image.py      # Gera og-image.png com Playwright — rodar ao mudar branding
└── scraper/
    ├── maps_scraper.py      # Google Maps scraper (Playwright)
    ├── lead_analyzer.py     # Scoring e classificação de leads
    ├── crm_sync.py          # Sync com Notion CRM
    ├── config.py            # Configurações e carregamento do .env
    ├── requirements.txt     # playwright, httpx
    ├── README.md
    └── .env                 # NUNCA commitar — gitignored
```

Produtos do portfólio ficam em `/produtos/{slug}/` quando desenvolvidos.

---

## Design system (website)

**Paleta quente — tema editorial:**
```css
--paper:   #faf7f2   /* fundo principal */
--smoke:   #f0ebe0   /* cards e superfícies alternadas */
--ink:     #18130e   /* texto principal e fundos escuros */
--ink-2:   #2e2520   /* bordas em fundos escuros */
--ember:   #c94a1f   /* cor principal — laranja escuro */
--ochre:   #f2b705   /* destaque — amarelo ouro */
--moss:    #2d7a4f   /* verde — status online / indicadores */
--muted:   #8a7f74   /* texto secundário */
--border:  #e2dbd0   /* bordas em fundo claro */
```

**Hero gradient (imagem de fundo):** `linear-gradient(145deg, #d44d22, #a83210 38%, #5c1a08 68%, #1a100a)`

**Fontes (Google Fonts):**
- `Barlow Condensed` — display / headings (wght 700–900, uppercase)
- `Instrument Serif` — acentos serif / itálico em ember (ex.: palavras-chave nos h2)
- `Inter` — corpo de texto

**Padrões de animação:**
- `[data-reveal]` → revelado via `IntersectionObserver` com classe `.in` (padrão atual, `index.html`)
- `[data-animate]` → compat para subpages legadas, usa classe `.visible`
- `[data-parallax="speed"]` → parallax scroll com scale no hero visual
- `.hero__word` → word-by-word fade/slide no load do hero
- `.hero__rotate-text` → texto rotativo no hero (double `requestAnimationFrame`)

**CSS cache-busting:** query string `?v=N` no link do CSS em `index.html`. Incrementar ao fazer deploy de mudanças de CSS. Versão atual: **v7**.

**Convenções mobile (≤ 900px):**
- `<br>` dentro de `.pg-heading` são ocultados com `display: none` — texto flui naturalmente
- Sempre adicionar um espaço antes do `<br>` no HTML: `palavra. <br>próxima` — assim quando o br some não come as palavras
- Imagem `hero-man.png` aparece apenas no desktop; mobile mostra só o gradiente

**Agendamento:** Cal.com  
URL: `https://cal.com/lucas-zanatta-bettbr/diagnostico`  
Event slug: `diagnostico`

---

## Scraper de leads (scraper/)

### Pipeline completo
```
Google Maps (Playwright) → lead_analyzer.py (score 0–100) → crm_sync.py → Notion CRM
```

### Comandos principais
```bash
cd scraper

# Busca única
python maps_scraper.py --query "restaurante Curitiba" --max 30

# Todas as queries do config.py
python maps_scraper.py --all --max 20

# Sem sincronizar Notion
python maps_scraper.py --all --no-crm

# Modo visível (debug)
python maps_scraper.py --query "clínica Curitiba" --visible

# Setup do banco Notion (uma vez só)
python crm_sync.py --setup --page-id SEU_PAGE_ID
```

### Output
- `scraper/output/leads.json` — dados brutos
- `scraper/output/leads.csv` — leads com score e script de abordagem
- `scraper/output/scraper.log` — log completo

### Score de leads (0–100 pts)
| Critério | Peso |
|----------|------|
| Sem site | 25 |
| Avaliação < 4.0 | 20 |
| Poucas avaliações (< 30) | 15 |
| Não responde avaliações | 15 |
| Segmento de alto potencial | 15 |
| Sem telefone visível | 10 |

**Prioridade:** Alta ≥ 65 pts / Média ≥ 40 pts / Baixa < 40 pts

### Variáveis de ambiente (.env)
```env
NOTION_API_KEY=...
NOTION_DATABASE_ID=...
```

O `config.py` carrega o `.env` automaticamente via `pathlib` (sem python-dotenv).

### Banco Notion — campos do lead
`Nome do Negócio`, `Status`, `Prioridade`, `Score`, `Avaliação Google`, `Nº Avaliações`, `Telefone`, `Site`, `Google Maps`, `Endereço`, `Categoria`, `Dores Identificadas`, `Oportunidades`, `Script de Abordagem`, `Responde Avaliações`, `Tem Site`, `Fonte`, `Data de Cadastro`, `Próximo Contato`

---

## Decisões técnicas globais (portfólio de produtos)

### O que NÃO usar
- **Sem n8n** — toda orquestração via código Python/Node.js puro
- **Sem Evolution API** — descontinuada, fora dos Termos de Serviço da Meta

### WhatsApp → Meta WhatsApp Cloud API (oficial)

- Self-signup direto pelo Meta App Dashboard (sem BSP necessário)
- Única opção para novas integrações desde out/2025 (On-Premise descontinuado)
- **Coexistence** (mai/2025): número já em uso no WhatsApp Business App pode ser vinculado à Cloud API sem perder histórico de conversas
- Cobranças Meta: por conversa (janela 24h); 1.000 conversas/mês grátis; ~USD 0,008–0,015/conversa iniciada pelo negócio; conversas iniciadas pelo cliente dentro da janela são gratuitas
- Mensagens ativas (lembretes, relatórios): exigem **message templates** aprovados pela Meta (~24h)
- Webhook recebido em servidor Python (FastAPI)

**Setup por cliente:**
1. Meta Business Account (criar ou usar existente do cliente)
2. Criar app no Meta App Dashboard → use case "WhatsApp"
3. Adicionar número de telefone do cliente (Coexistence compatível)
4. Criar e submeter templates para aprovação
5. Configurar webhook no servidor Python

### Voz → Grok Voice Agent API (xAI)

Lançada em dez/2025. Substitui o stack Vapi + ElevenLabs separados.

| Recurso | Detalhe |
|---------|---------|
| Latência | < 1s até primeiro áudio |
| TTS | 5 vozes (Ara, Eve, Leo, Rex, Sal), 20+ idiomas |
| Expressividade | Tags `[laugh]` `[sigh]` `<whisper>` |
| STT | 25+ idiomas, diarização por falante, streaming |
| Tool calling | Nativo — funções Python diretamente |
| Busca em tempo real | X (Twitter) + web, built-in |
| Clonagem de voz | Disponível via console xAI |
| Compatibilidade | OpenAI Realtime API spec + LiveKit plugin oficial |
| Preço TTS | USD 4,20/1M chars (~90% mais barato que ElevenLabs) |
| Telefonia | Requer Twilio para número e roteamento de chamadas |

---

## Portfólio de produtos (prioridade de desenvolvimento)

### Top 5 por score

| # | Produto | Score | Stack base | Build |
|---|---------|-------|-----------|-------|
| 1 | Gestor de Reputação Automático | 15/15 | Google My Business API + Claude Haiku + Python (APScheduler) | 1–2 dias |
| 2 | Atendente WhatsApp Inteligente | 14/15 | Meta WhatsApp Cloud API + Claude Haiku + Python (FastAPI) + Redis | 2–3 dias |
| 3 | Gerador de Orçamentos (WhatsApp) | 14/15 | Meta WhatsApp Cloud API + Claude Haiku + Python + Google Sheets | 2–3 dias |
| 4 | Recepcionista por Voz 24/7 | 13/15 | Twilio + Grok Voice Agent API + Google Calendar API + Python | 3–4 dias |
| 5 | Redutor de No-Show | 13/15 | Meta WhatsApp Cloud API + Claude Haiku + Python + Google Calendar | 2–3 dias |

### Demais produtos do portfólio

| Produto | Score | Stack base |
|---------|-------|-----------|
| Relatório Diário (WhatsApp) | 13/15 | Google Sheets API → Claude → Meta WhatsApp Cloud API |
| Qualificador de Leads por Voz | 12/15 | Twilio + Grok Voice Agent API + Notion CRM + Python |
| Agente de Conteúdo (Instagram) | 10/15 | Claude + aprovação via WhatsApp + Buffer API |

### Estrutura de cada produto
```
produtos/{slug}/
  src/          — código base reutilizável
  demo/         — script de demo (o que falar + o que mostrar)
  README.md     — documentação e manual do cliente
```

### Roadmap
- **Semana 1:** Gestor de Reputação + Atendente WhatsApp
- **Semana 2:** Gerador de Orçamentos + Redutor de No-Show
- **Semana 3:** Recepcionista por Voz (mais complexo)
- **Contínuo:** Produtos adicionais conforme clientes reais aparecem

---

## Convenções de código

- **Idioma do código:** inglês para variáveis/funções; português para strings voltadas ao usuário e comentários de negócio
- **Comentários:** apenas quando o WHY não é óbvio — sem docstrings longas, sem comentários óbvios
- **Sem n8n, sem ferramentas low-code** — Python ou Node.js puro
- **Encoding Windows:** sempre `sys.stdout.reconfigure(encoding='utf-8')` no topo de scripts Python que rodam no Windows com emojis ou caracteres especiais
- **Sem emojis em logs** — usar texto plano para evitar erros cp1252 no Windows
- **Sem python-dotenv** — `config.py` carrega `.env` via pathlib nativo

---

## Segurança e credenciais

- `.env` é gitignored — nunca commitar
- Chaves da API ficam somente no `.env` local e nas variáveis de ambiente do servidor de produção
- Arquivos sensíveis no `.gitignore`: `scraper/output/`, `scraper/__pycache__/`, `*.pyc`, `.env`, `*.log`

---

## SEO

**Estado atual (mai/2026):**
- `sitemap.xml` submetido no Google Search Console
- Re-indexação da homepage solicitada (título antigo "Agenty SDR" será substituído)
- `assets/og-image.png` (1200×630px) no ar — WhatsApp/LinkedIn vão pegar o preview
- Todas as páginas têm: canonical, meta description única, `lang="pt-BR"`, JSON-LD (`LocalBusiness` na homepage, tipos específicos nas subpages)
- `robots.txt` aponta para o sitemap

**Regenerar og-image.png** quando mudar branding:
```bash
python tools/gen_og_image.py
```
Requer Playwright instalado (já presente no scraper).

---

## Tarefas pendentes

- [ ] Corrigir extração de `reviews_count` no scraper (retorna 0 — depurar com `--visible`)
- [ ] Atualizar `servicos.html` com os produtos reais do portfólio
- [ ] Conectar Google Calendar à conta Cal.com
- [ ] Configurar disponibilidade/agenda no Cal.com
- [ ] Configurar Google Analytics no site
- [ ] Desenvolver primeiros produtos do portfólio (começar pelo Gestor de Reputação)
- [ ] Criar caso de uso / depoimento da Cássia Marconi após setup do Gestor de Reputação
