# Gestor de Reputação Automático — Agenty

Monitora avaliações do Google Maps a cada 2h. Responde as positivas automaticamente. Envia rascunho por e-mail para aprovação das negativas.

---

## Estrutura

```
gestor-reputacao/
├── src/
│   ├── main.py          # FastAPI + APScheduler — entry point
│   ├── gmb_client.py    # Google My Business API (listar + responder)
│   ├── claude_client.py # Claude Haiku — geração de respostas
│   ├── reviewer.py      # Orquestra o ciclo: busca → gera → age
│   ├── notifier.py      # E-mail HTML de aprovação
│   ├── db.py            # SQLite — estado de cada avaliação
│   ├── config.py        # Carrega .env
│   └── mock_reviews.py  # Dados fictícios para teste (MOCK_MODE=true)
├── data/
│   └── reviews.db       # Banco de dados (gerado na primeira execução)
├── oauth_setup.py       # Autoriza acesso ao Google (roda uma vez por cliente)
├── onboarding-template.md  # Guia de ativação para o cliente
├── demo/script.md       # Roteiro de demo comercial (5 min)
├── client_secrets.json  # Credenciais OAuth do Google Cloud (não commitar)
├── .env.example         # Template de variáveis de ambiente
├── requirements.txt
└── Procfile             # Deploy Railway: uvicorn src.main:app
```

---

## Setup por cliente (~45 minutos)

### 1. Pré-requisitos do cliente

- Perfil no Google Meu Negócio **verificado** (tem o selo ✓ no Maps)
- Acesso ao e-mail da conta Google do negócio
- E-mail para receber aprovações de avaliações negativas

### 2. Google Cloud Console (feito por Lucas, uma vez por projeto)

```
1. console.cloud.google.com → Novo projeto
2. Ativar: "Google My Business API"
3. Credenciais → Criar → OAuth 2.0 → App da Web
   URIs de redirecionamento: http://localhost:8080/
4. Baixar JSON → salvar como client_secrets.json nesta pasta
```

### 3. Autorização OAuth com a conta do cliente

```bash
python oauth_setup.py
```

O script abre o browser, o cliente faz login com a conta Google do negócio, clica em "Permitir" e o script salva automaticamente no `.env`:
- `GOOGLE_REFRESH_TOKEN`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_ACCOUNT_NAME`
- `GOOGLE_LOCATION_NAME`

### 4. Completar o `.env`

Copiar `.env.example` → `.env` e preencher os campos restantes:

```bash
cp .env.example .env
# Editar: ANTHROPIC_API_KEY, BUSINESS_NAME, BUSINESS_TYPE, BUSINESS_TONE
# Editar: APPROVAL_EMAIL, SMTP_USER, SMTP_PASSWORD, APP_BASE_URL
```

**Senha de App do Gmail** (para SMTP_PASSWORD):
```
Google Account → Segurança → Verificação em 2 etapas → Senhas de app
→ Selecionar app: Outro → Digitar "Agenty" → Gerar
```

### 5. Testar localmente com modo mock

```bash
pip install -r requirements.txt

# Ativar modo de simulação
echo "MOCK_MODE=true" >> .env

# Rodar
uvicorn src.main:app --reload --port 8000

# Em outro terminal — verificar saúde
curl http://localhost:8000/health
```

O ciclo roda imediatamente na inicialização. Verificar logs:
```
[INFO] 3 avaliacoes sem resposta encontradas
[INFO] Auto-respondido: Ana Paula Souza (5 estrelas)
[INFO] Rascunho enviado para aprovacao: Carlos Mendes (2 estrelas)
```

### 6. Deploy Railway

```bash
# Criar projeto no Railway
railway init
railway up

# Configurar variáveis de ambiente no dashboard Railway
# (todas as do .env, exceto PORT — Railway define automaticamente)

# Atualizar APP_BASE_URL no .env com a URL gerada pelo Railway
# Fazer novo deploy para aplicar
railway up
```

---

## Fluxo de funcionamento

```
[APScheduler — a cada 2h]
        │
        ▼
gmb_client.list_unanswered_reviews()
        │
        ├── db.upsert_review()   ← registra novas, ignora já vistas
        │
        ├── Avaliação >= AUTO_REPLY_MIN_RATING (padrão: 4 estrelas)
        │         └── claude_client.generate_response()
        │                   └── gmb_client.post_reply()
        │                             └── db.set_replied()
        │
        └── Avaliação < AUTO_REPLY_MIN_RATING
                  └── claude_client.generate_response()
                            └── db.set_draft() → token UUID
                                      └── notifier.send_approval_email()
                                                └── /approve/{token}
                                                          └── gmb_client.post_reply()
                                                                    └── db.set_replied()
```

---

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | Status do serviço |
| GET | `/approve/{token}` | Aprova e publica rascunho de avaliação negativa |

---

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|----------|------------|-----------|
| `ANTHROPIC_API_KEY` | Sim | Chave da API Anthropic |
| `GOOGLE_CLIENT_ID` | Sim | Preenchido pelo oauth_setup.py |
| `GOOGLE_CLIENT_SECRET` | Sim | Preenchido pelo oauth_setup.py |
| `GOOGLE_REFRESH_TOKEN` | Sim | Preenchido pelo oauth_setup.py |
| `GOOGLE_ACCOUNT_NAME` | Sim | Ex: `accounts/123456789` |
| `GOOGLE_LOCATION_NAME` | Sim | Ex: `accounts/123456789/locations/987654321` |
| `BUSINESS_NAME` | Sim | Nome do negócio |
| `BUSINESS_TYPE` | Sim | Tipo (ex: barbearia, salão de beleza) |
| `BUSINESS_CITY` | Não | Padrão: Curitiba |
| `BUSINESS_TONE` | Não | `profissional_cordial` \| `proximo_descontraido` \| `formal` |
| `APPROVAL_EMAIL` | Sim | E-mail para receber avaliações negativas |
| `SMTP_HOST` | Não | Padrão: smtp.gmail.com |
| `SMTP_PORT` | Não | Padrão: 587 |
| `SMTP_USER` | Sim | E-mail do Gmail de envio |
| `SMTP_PASSWORD` | Sim | Senha de App do Gmail |
| `APP_BASE_URL` | Sim | URL pública do Railway (para links de aprovação) |
| `CHECK_INTERVAL_HOURS` | Não | Padrão: 2 |
| `AUTO_REPLY_MIN_RATING` | Não | Padrão: 4 (4 e 5 estrelas = auto) |
| `PORT` | Não | Padrão: 8000 (Railway define automaticamente) |
| `MOCK_MODE` | Não | `true` para testar sem a API do Google |

---

## Custo de infra por cliente

| Item | Custo/mês |
|------|-----------|
| Railway (serviço Python) | ~R$ 15–25 |
| Claude Haiku (~200 avaliações) | ~R$ 0,80 |
| Google APIs | Gratuito |
| **Total** | **~R$ 16–26/mês** |
| **Margem líquida (R$ 150/mês)** | **~R$ 124–134/mês** |

---

## Rate limits da Google My Business API

- 10 edições (replies) por minuto por perfil
- 2.400 queries por minuto (global)
- O `reviewer.py` já inclui `time.sleep(7)` entre respostas (~8/min com margem)

---

*Agenty — Curitiba, PR — agenty.com.br*
