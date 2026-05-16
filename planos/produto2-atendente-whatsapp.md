# Produto 2: Atendente WhatsApp Inteligente — Plano Detalhado

> Criado em: mai/2026 | Status: pronto para build

---

## Contexto e Motivação

Segundo pesquisa de mercado (mai/2026), 73% dos lojistas brasileiros usam WhatsApp como canal de vendas. O mercado de assistentes de WhatsApp com IA é maduro e competitivo, mas cheio de dores reais:

- **Wati** (líder de penetração): suporte desaparece pós-venda, cobra markup oculto de 20% sobre fees da Meta, usa dark patterns no cancelamento
- **Respond.io** (melhor produto): caro ($159–$279/mês), downtime frequente, focado em enterprise
- **Todos** os grandes players são genéricos — nenhum é pensado para o pequeno negócio local brasileiro

**Janela de oportunidade Agenty:** posicionamento local + personalização real + preço transparente + suporte humano (Lucas, Curitiba).

**Restrição crítica de Jan/2026:** A Meta baniu assistentes de IA de propósito geral no WhatsApp (ChatGPT, Perplexity etc.). Apenas **task-specific bots** são permitidos — o que é exatamente o que entregamos: bot especializado no negócio do cliente.

---

## Posicionamento do produto

**Não é** um chatbot genérico com FAQ. **É** um atendente digital treinado no negócio específico do cliente — conhece os serviços, preços, horários, tom de voz — e resolve as interações reais: responder, agendar, qualificar, escalar.

**Segmento primário:** beleza & bem-estar (salões, barbearias, clínicas de estética, pilates) — os 100 leads já prospectados.

---

## Análise competitiva

| Fator | Wati | Respond.io | **Agenty** |
|---|---|---|---|
| Preço real mensal | $180–290 (markup oculto) | $200–400 | R$99/mês (transparente) |
| Suporte | Desaparece pós-venda | Tickets ignorados | Lucas responde em 2h |
| Personalização | Templates genéricos | Configurável mas complexo | Treinado no negócio |
| Idioma/contexto | Global | Global | Curitiba, pt-BR, local |
| Cancelamento | Dark patterns | Difícil | Cancel via WhatsApp |
| Multimodal (voz/imagem) | Add-on caro | Parcial | Nativo desde v1 |

---

## Features priorizadas por impacto

### MVP — Semana 1

1. **Resposta 24/7 via knowledge base** — FAQ, preços, serviços, localização
2. **Agendamento automático** — Google Calendar, horários disponíveis, confirmação
3. **Qualificação de leads** — identifica intent, coleta nome/serviço/data
4. **Contexto de conversa** — lembra a janela de 24h via Redis
5. **Escalada para humano** — detecta frustração ou solicitação complexa, notifica dono
6. **Transcrição de áudio** — cliente manda voz, bot entende e responde

### V2 — Semana 2

7. **Análise de imagens** — foto de cabelo/pele → bot identifica contexto
8. **Lembrete de confirmação** — template Utility 24h antes do agendamento
9. **Relatório semanal** — resumo para o dono via WhatsApp
10. **Catálogo interativo** — menu com botões WhatsApp nativos

---

## Stack técnica

```
Cliente WhatsApp
      │
      ▼
Meta WhatsApp Cloud API v23.0
POST https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages
      │
      ▼
FastAPI (Python) — /webhook
  └── Responde 200 OK em < 5s (obrigatório pela Meta)
      │
      ├── Redis — histórico da conversa (TTL 24h = janela gratuita)
      ├── Claude Haiku 4.5 — geração de resposta (system prompt cacheado)
      │     └── Tools: check_availability, create_appointment, escalate
      ├── Google Calendar API — slots disponíveis + criação de evento
      ├── Whisper API — ogg/opus → texto
      │     └── CRÍTICO: download imediato do áudio (URL expira 24-48h)
      └── SQLite — leads, agendamentos, logs
```

### Justificativas

- **Meta Cloud API v23.0**: única opção legal (On-Premise descontinuado out/2025); Coexistence disponível (throughput cai de 80 → 20 mps, aceitável para PME)
- **Claude Haiku 4.5**: $1/M input + $5/M output; ~$0,0007/resposta; prompt caching = 90% desconto no system prompt
- **Redis TTL 24h**: alinhado com a janela gratuita da Meta
- **FastAPI**: async nativo; webhook deve responder 200 em <5s (exigência Meta)
- **SQLite**: sem overhead; cada cliente = instância isolada

---

## Fluxo de funcionamento

```
[Cliente manda mensagem WhatsApp]
        │
FastAPI recebe webhook POST /webhook
        ├── Áudio → Whisper transcreve (baixar media_id imediatamente!)
        ├── Imagem → URL para Claude com contexto
        └── Texto → fluxo padrão
        │
Redis: carrega histórico (últimas 10 msg)
        │
Claude Haiku gera resposta
  System prompt cacheado: negócio + regras + tom
  Tools: calendar, escalada
        ├── AGENDAMENTO → Google Calendar → retorna horários
        ├── ESCALADA → notifica dono via WhatsApp
        └── FAQ → responde do knowledge base
        │
Meta API envia resposta ao cliente
Redis salva troca (TTL 24h) | SQLite registra lead/agendamento
```

---

## Estrutura de arquivos

```
produtos/atendente-whatsapp/
├── src/
│   ├── main.py              # FastAPI + webhook GET/POST
│   ├── whatsapp_client.py   # send_text, send_interactive_buttons, send_template, download_media
│   ├── claude_client.py     # Haiku + prompt caching + tool calling
│   ├── calendar_client.py   # list_slots, create_event
│   ├── audio_client.py      # Whisper: ogg → texto
│   ├── conversation.py      # Redis: get_history, append, TTL
│   ├── intent_router.py     # FAQ / AGENDAMENTO / ESCALADA / FORA_ESCOPO
│   ├── db.py                # SQLite: conversations, appointments, leads
│   └── config.py            # .env loader
├── setup/
│   ├── meta_setup.md        # Passo a passo Meta App Dashboard
│   └── calendar_setup.py    # OAuth Google Calendar (uma vez por cliente)
├── demo/
│   └── script.md            # Roteiro de 5 min para call com prospect
├── requirements.txt
├── .env.example
├── railway.toml
└── README.md
```

---

## Prompt do sistema (cacheado por cliente)

```
Você é o assistente virtual de {nome_negocio}, {tipo_negocio} em Curitiba.
Tom de voz: {tom}
Idioma: Português brasileiro, informal, sem excessos.

SOBRE O NEGÓCIO:
{knowledge_base}  ← serviços, preços, horários, endereço, políticas, FAQs

REGRAS:
- Máximo 3 frases por resposta. Se precisar de mais, divida em mensagens.
- Nunca invente informações. Se não souber, diga que vai verificar.
- Agendamentos: confirme serviço + data + horário + nome antes de criar.
- Escalada: palavras gatilho → notificar {nome_dono} e avisar o cliente.
- Nunca mencione que é IA, salvo se perguntado diretamente.
```

---

## Tipos de mensagem e custo Meta (dados oficiais 2026)

| Tipo | Quando usar | Custo Meta |
|---|---|---|
| Texto livre | Dentro da janela 24h (cliente iniciou) | **Grátis** |
| Interactive (botões, listas) | Dentro da janela 24h | **Grátis** |
| Template Utility | Lembrete 24h antes do agendamento | ~$0,015/msg |
| Template Marketing | Promoções, broadcast | ~$0,0215/msg |

**1.000 conversas de serviço/mês são gratuitas.** Conversas iniciadas pelo cliente dentro da janela 24h = sempre grátis.

**Limite sem verificação Business:** 250 conversas/24h → verificar Business Account do cliente assim que assinar.

---

## Custo de infra por cliente

| Item | Custo/mês |
|---|---|
| Railway (processo Python persistente) | ~R$15–25 |
| Claude Haiku 4.5 (~200 conv × 5 msg) | ~R$0,70 |
| Whisper (~50 áudios a $0,006/min) | ~R$0,30 |
| Meta — conversas (dentro janela 24h) | R$0 |
| Meta — templates Utility (80 lembretes) | ~R$7 |
| Redis (Railway free tier) | R$0 |
| **Total** | **~R$23–32/mês** |
| **Margem líquida (R$99/mês)** | **~R$67–76/mês** |

---

## Roadmap de desenvolvimento (4 dias)

### Dia 1 — Webhook + Meta API (4–5h)
- [ ] `main.py` — FastAPI: `GET /webhook` (verificação Meta) + `POST /webhook` (async, responde 200 em <5s)
- [ ] `whatsapp_client.py` — `send_text`, `send_interactive_buttons` (máx 3 botões), `send_template`, `download_media`
- [ ] `config.py` — WHATSAPP_TOKEN, PHONE_NUMBER_ID, VERIFY_TOKEN, WABA_ID
- [ ] `conversation.py` — Redis: `get_history(phone)`, `append(phone, role, text)`, TTL=86400s
- [ ] Teste: receber + responder mensagem via ngrok → Meta Test Mode

### Dia 2 — Claude + Intent Router (3–4h)
- [ ] `claude_client.py` — system prompt cacheado, tool calling (check_availability, escalate)
- [ ] `kb_template.json` — estrutura da knowledge base (serviços, preços, horários, FAQs, tom)
- [ ] `intent_router.py` — FAQ / AGENDAMENTO / ESCALADA / FORA_ESCOPO
- [ ] Regra de escalada: palavras gatilho → alerta para o dono via WhatsApp
- [ ] Teste: 10 cenários simulados (beleza/barbearia), avaliar qualidade das respostas

### Dia 3 — Agendamento + Áudio (4–5h)
- [ ] `calendar_client.py` — `list_slots(service, date)`, `create_event(service, dt, name, phone)`
- [ ] `setup/calendar_setup.py` — OAuth2 Google Calendar (uma vez por cliente)
- [ ] `audio_client.py`:
  - GET /v23.0/{media_id} → URL temporária → download imediato (expira 24-48h!)
  - Transcrição Whisper → texto → fluxo normal
- [ ] Teste end-to-end: áudio "quero agendar quinta às 10h" → Calendar criado → confirmação

### Dia 4 — Templates + Demo + Deploy (3–4h)
- [ ] Submeter template "lembrete_consulta" (Utility) para aprovação Meta (~24h)
- [ ] `demo/script.md` — roteiro 5 min
- [ ] Teste completo com número real do Lucas (PC local + ngrok)
- [ ] `README.md` — guia de setup por cliente (~45 min)
- [ ] Deploy Railway para o primeiro cliente real

**Total estimado: 14–18h**

---

## Ambiente de desenvolvimento (PC local + ngrok)

```
Meta Webhook
    │
    ▼  https://abc123.ngrok-free.app/webhook
  ngrok (túnel HTTPS)
    │
    ▼
FastAPI localhost:8000
    │
Claude + Redis + Google Calendar (tudo local)
```

```bash
# Instalar dependências
pip install fastapi uvicorn redis anthropic openai google-api-python-client httpx python-dotenv

# Rodar servidor local
uvicorn src.main:app --reload --port 8000

# Expor via ngrok (outro terminal)
ngrok http 8000
# → URL pública para registrar no Meta App Dashboard
```

**Redis local (Windows):**
```bash
# Docker (recomendado)
docker run -d -p 6379:6379 redis
```

**Para produção:** Railway com URL permanente. Cada cliente = 1 serviço isolado.

---

## Variáveis de ambiente (.env por cliente)

```env
WHATSAPP_TOKEN=EAA...
PHONE_NUMBER_ID=123...
WABA_ID=456...
VERIFY_TOKEN=token_secreto

GOOGLE_REFRESH_TOKEN=...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

BUSINESS_NAME=Barbearia X
BUSINESS_TONE=descontraido e proximo
OWNER_PHONE=5541999999999
ESCALATION_KEYWORDS=reclamação,problema,errado,péssimo,horrível
```

---

## Setup por cliente (~45 min, feito por Lucas)

1. Meta Business Account (criar ou usar existente)
2. Criar App no Meta App Dashboard → use case "WhatsApp"
3. Adicionar número de telefone (Coexistence com app atual = histórico preservado)
4. Configurar webhook Railway como endpoint + eventos: messages, message_status
5. Preencher `knowledge_base.json` com o cliente
6. `setup/calendar_setup.py` → OAuth Google Calendar
7. Variáveis de ambiente no Railway dashboard
8. Teste ao vivo: mensagem → bot responde

---

## Script de demo (5 minutos)

1. **(30s)** "Você já perdeu cliente porque não respondeu o WhatsApp a tempo? Vou mostrar em 2 minutos o que a gente faz."
2. **(2min)** Demo ao vivo com celular:
   - "Qual horário disponível pra corte masculino na sexta?"
   - Bot retorna horários do Google Calendar
   - "Quero às 14h, nome João" → bot confirma e cria o evento
3. **(30s)** Manda áudio: "Qual o preço da hidratação?" → bot transcreve e responde
4. **(1min)** "Isso roda 24h, 7 dias. Nunca perde cliente. Você vê tudo pelo WhatsApp normalmente."
5. **(1min)** "Personalizo pro seu negócio — seus serviços, seus preços, seu jeito de falar. R$99/mês."

---

## Primeiro cliente alvo

Dos 100 leads prospectados (beleza CWB), perfil ideal:
- Alta prioridade no score (37 leads disponíveis)
- Sem site + nota < 4.3 = maior abertura
- Barbearia ou salão (ticket recorrente, agendamento = dor real)

Ligar pelos 37 de alta prioridade. Script de abordagem já gerado no `scraper/output/beleza_cwb.csv`.
