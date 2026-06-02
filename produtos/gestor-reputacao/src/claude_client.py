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


def generate_response(
    business_name: str,
    business_type: str,
    business_city: str,
    tone: str,
    rating: int,
    author: str,
    review_text: str,
) -> str:
    tone_desc = _TONE_DESC.get(tone, _TONE_DESC["proximo_descontraido"])

    system = (
        f"Você é o assistente de atendimento de {business_name}, "
        f"{business_type} em {business_city}.\n"
        f"Tom de voz: {tone_desc}.\n"
        "Idioma: Português brasileiro.\n\n"
        "Regras para responder avaliações do Google:\n"
        "- Chame o avaliador pelo primeiro nome quando disponível\n"
        "- Mencione um detalhe específico do texto da avaliação — nunca responda de forma genérica\n"
        "- Avaliações positivas (4–5 estrelas): agradeça, reforce o ponto elogiado, convide a voltar\n"
        "- Avaliações negativas (1–3 estrelas): reconheça sem admitir culpa — "
        "use \"lamentamos que sua experiência não tenha sido a esperada\"; ofereça canal de contato direto\n"
        "- Entre 20 e 100 palavras\n"
        "- Nunca mencione concorrentes, preços ou promoções\n"
        "- Nunca admita uma falha específica"
    )

    label = "positiva" if rating >= 4 else "negativa" if rating <= 2 else "neutra"
    user_msg = (
        f"Avaliação {label} recebida:\n"
        f"Nota: {rating}/5\n"
        f"Autor: {author or 'Anônimo'}\n"
        f"Texto: \"{review_text or 'Sem texto'}\"\n\n"
        "Gere a resposta para publicar no Google."
    )

    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text.strip()
