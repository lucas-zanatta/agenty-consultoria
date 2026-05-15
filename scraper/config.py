"""
Configurações do scraper de Google Maps — Agenty CRM
"""

# ── Parâmetros de busca ───────────────────────────────────────────────────────

# Segmentos e palavras-chave para busca no Google Maps
SEARCH_QUERIES = [
    "restaurante Curitiba",
    "bar Curitiba",
    "clínica estética Curitiba",
    "clínica odontológica Curitiba",
    "fisioterapia Curitiba",
    "psicólogo Curitiba",
    "salão de beleza Curitiba",
    "barbearia Curitiba",
    "loja de roupas Curitiba",
    "academia Curitiba",
    "escola de idiomas Curitiba",
    "advocacia Curitiba",
    "contabilidade Curitiba",
    "imobiliária Curitiba",
    "pet shop Curitiba",
    "veterinário Curitiba",
    "oficina mecânica Curitiba",
    "empresa de limpeza Curitiba",
    "dedetizadora Curitiba",
    "curso profissionalizante Curitiba",
]

# Número máximo de resultados por query
MAX_RESULTS_PER_QUERY = 20

# Delay entre ações (segundos) — evita bloqueio
SCROLL_DELAY = 2.0
ACTION_DELAY = 1.5
PAGE_LOAD_WAIT = 3.0

# ── Scoring de leads ──────────────────────────────────────────────────────────

# Faixa de avaliação considerada ruim (dor de reputação)
RATING_LOW = 4.0
RATING_MED = 4.3

# Número de avaliações considerado baixo (oportunidade de crescimento)
REVIEWS_LOW = 30
REVIEWS_MED = 100

# Segmentos com maior potencial para voice agent
HIGH_POTENTIAL_SEGMENTS = [
    "clínica", "dentista", "médico", "saúde", "fisioterapia",
    "restaurante", "bar", "lanchonete",
    "salão", "barbearia", "beleza", "estética",
    "advogado", "advocacia", "contabilidade",
    "academia", "pilates", "yoga",
    "pet shop", "veterinário",
    "oficina", "mecânica",
]

# ── Classificação de prioridade ───────────────────────────────────────────────

# Score mínimo para cada prioridade
PRIORITY_HIGH_THRESHOLD = 65
PRIORITY_MED_THRESHOLD  = 40

# Pesos do score (total = 100 pontos possíveis)
SCORE_WEIGHTS = {
    "no_website":         25,   # Sem site = enorme oportunidade
    "low_rating":         20,   # Avaliação < 4.0 = dor de reputação
    "few_reviews":        15,   # Poucas avaliações = oportunidade de crescimento
    "not_responding":     15,   # Não responde avaliações = oportunidade de automação
    "high_potential_seg": 15,   # Segmento com alto potencial para IA
    "no_phone_visible":   10,   # Sem telefone visível = oportunidade de presença digital
}

# ── Notion CRM ────────────────────────────────────────────────────────────────
# Configure com suas credenciais (use variáveis de ambiente em produção)
import os

NOTION_API_KEY      = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID  = os.getenv("NOTION_DATABASE_ID", "")

# ── Output ────────────────────────────────────────────────────────────────────
OUTPUT_DIR  = "output"
OUTPUT_CSV  = "leads.csv"
OUTPUT_JSON = "leads.json"
LOG_FILE    = "scraper.log"
