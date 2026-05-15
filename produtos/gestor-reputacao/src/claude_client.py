import sys
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).parent))
import config

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

_TONE_DESC = {
    "profissional_cordial": "profissional e cordial, como um gerente atencioso e educado",
    "proximo_descontraido": "próximo e descontraído, como alguém que conhece bem os clientes",
    "formal":               "formal e respeitoso, como uma empresa tradicional e séria",
}

_system_cache: str | None = None


def _system_prompt() -> str:
    global _system_cache
    if _system_cache is None:
        tone = _TONE_DESC.get(config.BUSINESS_TONE, _TONE_DESC["proximo_descontraido"])
        _system_cache = f"""Você é o assistente de atendimento de {config.BUSINESS_NAME}, {config.BUSINESS_TYPE} em {config.BUSINESS_CITY}.
Tom de voz: {tone}.
Idioma: Português brasileiro.

Regras para responder avaliações do Google:
- Chame o avaliador pelo primeiro nome quando disponível
- Mencione um detalhe específico do texto da avaliação — nunca responda de forma genérica
- Avaliações positivas (4–5 estrelas): agradeça, reforce o ponto elogiado, convide a voltar
- Avaliações negativas (1–3 estrelas): reconheça sem admitir culpa — use "lamentamos que sua experiência não tenha sido a esperada"; ofereça canal de contato direto
- Entre 20 e 100 palavras
- Nunca mencione concorrentes, preços ou promoções
- Nunca admita uma falha específica"""
    return _system_cache


def generate_response(rating: int, author: str, review_text: str) -> str:
    label = "positiva" if rating >= 4 else "negativa" if rating <= 2 else "neutra"
    user_msg = (
        f"Avaliação {label} recebida:\n"
        f"Nota: {rating}/5\n"
        f"Autor: {author or 'Anônimo'}\n"
        f"Texto: \"{review_text or 'Sem texto'}\"\n\n"
        f"Gere a resposta para publicar no Google."
    )

    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=_system_prompt(),
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text.strip()
