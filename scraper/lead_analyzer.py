"""
Lead Analyzer — Agenty
Analisa cada negócio raspado, identifica dores/oportunidades,
calcula score de prioridade e gera script de abordagem comercial.
"""

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
import config
from maps_scraper import Business


class LeadAnalyzer:

    def analyze(self, biz: Business) -> dict:
        """Retorna um dict enriquecido com análise de lead."""
        dores = self._identify_dores(biz)
        oportunidades = self._identify_oportunidades(biz)
        score = self._calculate_score(biz, dores, oportunidades)
        priority = self._classify_priority(score)
        approach = self._generate_approach_script(biz, dores, oportunidades, priority)

        return {
            # Dados brutos
            "nome":               biz.name,
            "categoria":          biz.category,
            "endereco":           biz.address,
            "telefone":           biz.phone,
            "site":               biz.website,
            "avaliacao":          biz.rating,
            "num_avaliacoes":     biz.reviews_count,
            "responde_avaliacoes":biz.responds_to_reviews,
            "maps_url":           biz.maps_url,
            "horario":            biz.hours,
            "fonte_busca":        biz.query_source,
            "raspado_em":         biz.scraped_at,
            # Análise
            "dores":              " | ".join(dores) if dores else "Nenhuma dor identificada",
            "oportunidades":      " | ".join(oportunidades) if oportunidades else "",
            "score":              score,
            "prioridade":         priority,  # Alta, Média, Baixa
            "status":             "Novo",
            "script_abordagem":   approach,
            "notas":              "",
        }

    # ── Identificação de dores ───────────────────────────────────────────────

    def _identify_dores(self, biz: Business) -> list[str]:
        dores = []

        if biz.rating is not None:
            if biz.rating < 4.0:
                dores.append(f"Avaliação baixa ({biz.rating}⭐) — risco de perder clientes")
            elif biz.rating < 4.3:
                dores.append(f"Avaliação mediana ({biz.rating}⭐) — abaixo da concorrência")

        if biz.reviews_count < config.REVIEWS_LOW:
            dores.append(f"Poucas avaliações ({biz.reviews_count}) — baixa visibilidade no Maps")

        if not biz.website:
            dores.append("Sem site próprio — não encontrado no Google")

        if not biz.responds_to_reviews:
            dores.append("Não responde avaliações — clientes se sentem ignorados")

        if biz.phone == "":
            dores.append("Telefone não visível — clientes não conseguem contato")

        return dores

    # ── Identificação de oportunidades ──────────────────────────────────────

    def _identify_oportunidades(self, biz: Business) -> list[str]:
        ops = []
        cat_lower = (biz.category or "").lower()
        name_lower = (biz.name or "").lower()
        combined = cat_lower + " " + name_lower

        # Voice agent
        if any(kw in combined for kw in ["clínica", "dentista", "médico", "saúde", "fisio",
                                          "restaurante", "bar", "lanchonete",
                                          "salão", "barbear", "estética",
                                          "advogad", "academia", "pet", "veterinário"]):
            ops.append("Voice agent para agendamento 24/7")

        # Chatbot WhatsApp
        if not biz.responds_to_reviews or biz.reviews_count < config.REVIEWS_MED:
            ops.append("Chatbot WhatsApp para atendimento e qualificação")

        # Reputação online
        if biz.rating is not None and biz.rating < 4.3:
            ops.append("Automação de resposta a avaliações + gestão de reputação")

        # Presença digital
        if not biz.website:
            ops.append("Site + presença digital básica")

        # Análise de dados
        if any(kw in combined for kw in ["restaurante", "bar", "loja", "varejo", "lanchonete"]):
            ops.append("Análise de dados de vendas e previsão de demanda")

        # Agente de vendas
        if any(kw in combined for kw in ["imóvel", "imobiliária", "escola", "curso", "academia"]):
            ops.append("Agente de IA para qualificação e nutrição de leads")

        return ops

    # ── Score de prioridade ──────────────────────────────────────────────────

    def _calculate_score(self, biz: Business, dores: list, oportunidades: list) -> int:
        score = 0
        w = config.SCORE_WEIGHTS

        if not biz.website:
            score += w["no_website"]

        if biz.rating is not None and biz.rating < config.RATING_LOW:
            score += w["low_rating"]
        elif biz.rating is not None and biz.rating < config.RATING_MED:
            score += w["low_rating"] // 2

        if biz.reviews_count < config.REVIEWS_LOW:
            score += w["few_reviews"]
        elif biz.reviews_count < config.REVIEWS_MED:
            score += w["few_reviews"] // 2

        if not biz.responds_to_reviews:
            score += w["not_responding"]

        cat_lower = (biz.category or biz.name or "").lower()
        if any(kw in cat_lower for kw in config.HIGH_POTENTIAL_SEGMENTS):
            score += w["high_potential_seg"]

        if not biz.phone:
            score += w["no_phone_visible"]

        # Bônus por múltiplas dores
        if len(dores) >= 3:
            score = min(100, score + 10)

        return min(100, score)

    def _classify_priority(self, score: int) -> str:
        if score >= config.PRIORITY_HIGH_THRESHOLD:
            return "Alta"
        if score >= config.PRIORITY_MED_THRESHOLD:
            return "Média"
        return "Baixa"

    # ── Script de abordagem personalizado ────────────────────────────────────

    def _generate_approach_script(
        self,
        biz: Business,
        dores: list[str],
        oportunidades: list[str],
        priority: str,
    ) -> str:

        nome = biz.name or "amigo(a)"
        cat = biz.category or "negócio"

        # Gancho principal baseado na dor mais relevante
        gancho = self._get_main_hook(biz, dores)

        # Solução principal baseada na oportunidade mais relevante
        solucao = self._get_main_solution(oportunidades)

        # Monta script
        script = f"""SCRIPT DE ABORDAGEM — {nome} [{priority.upper()}]
{"="*60}

📞 ABERTURA (primeiros 10 segundos)
"Oi, bom dia! Posso falar com o(a) responsável por {nome}?"
[após confirmação]
"Meu nome é Lucas, sou da Agenty, consultoria de inteligência artificial aqui em Curitiba. Tudo bem?"

💡 GANCHO (identificar a dor)
"{gancho}"

🤝 APRESENTAÇÃO DA SOLUÇÃO
"{solucao}"

📅 PRÓXIMO PASSO
"O que eu gostaria de propor é uma conversa rápida de 30 minutos, sem compromisso, para entender melhor a sua realidade e mostrar o que seria possível. Você teria um horário essa semana ou na próxima?"

🛡️ OBJEC ÇÕES COMUNS

Se disser "já uso tecnologia / já tenho chatbot":
→ "Que ótimo! O que eu quero mostrar vai além disso — é uma IA que atende por voz, como um funcionário real. Posso te mandar um exemplo funcionando?"

Se disser "não tenho tempo / tô ocupado":
→ "Entendo! Pode ser por mensagem mesmo, o que é mais confortável pra você — WhatsApp ou e-mail?"

Se disser "não tenho dinheiro para isso":
→ "Faz sentido questionar. Por isso a primeira conversa é gratuita — para a gente ver se o investimento faz sentido para o seu porte. Sem compromisso nenhum."

Se disser "vou pensar":
→ "Claro! Posso te mandar um resumo por WhatsApp? Assim você já fica com a informação e a gente pode marcar quando for melhor pra você."

📋 INFORMAÇÕES DO LEAD
- Avaliação Google: {biz.rating if biz.rating else 'N/D'} ⭐ ({biz.reviews_count} avaliações)
- Site: {'Não tem' if not biz.website else biz.website}
- Telefone: {biz.phone or 'Não visível'}
- Responde avaliações: {'Sim' if biz.responds_to_reviews else 'Não'}
- Endereço: {biz.address or 'N/D'}
- Dores identificadas: {'; '.join(dores) if dores else 'Nenhuma'}
- Oportunidades: {'; '.join(oportunidades) if oportunidades else 'Nenhuma'}
- Score: {self._calculate_score(biz, dores, oportunidades)}/100
"""
        return script

    def _get_main_hook(self, biz: Business, dores: list[str]) -> str:
        """Gera o gancho principal baseado na dor mais urgente."""

        if biz.rating is not None and biz.rating < 4.0:
            return (
                f"Vi aqui no Google Maps que o {biz.name} tem uma avaliação de {biz.rating} estrelas. "
                "Sei que às vezes uma avaliação ruim não reflete a qualidade real do serviço — e isso é muito frustrante. "
                "A gente ajuda negócios como o seu a recuperar a reputação online e a responder avaliações de forma automática. "
                "Isso faz diferença na hora que o cliente está escolhendo onde ir."
            )

        if not biz.website:
            return (
                f"Pesquisei sobre o {biz.name} e vi que vocês ainda não têm site. "
                "Hoje, o cliente pesquisa no Google antes de ir — e sem site, você fica invisível para boa parte do mercado. "
                "A gente desenvolve presença digital integrada com IA para negócios como o seu."
            )

        if biz.reviews_count < 30:
            return (
                f"Vi que o {biz.name} tem poucos comentários no Google Maps. "
                "Isso muitas vezes acontece não por falta de clientes satisfeitos, mas porque as pessoas esquecem de avaliar. "
                "A gente tem um jeito automatizado de incentivar avaliações — sem spam, de forma natural."
            )

        # Gancho genérico por segmento
        cat_lower = (biz.category or "").lower()
        if any(kw in cat_lower for kw in ["clínica", "dentista", "saúde", "fisio"]):
            return (
                f"Trabalho com clínicas aqui em Curitiba e percebi que um dos maiores gargalos é o telefone — "
                "ligações de agendamento que chegam fora do horário ou quando a recepcionista está ocupada. "
                "Desenvolvemos um atendente virtual por voz que resolve isso 24 horas por dia."
            )
        if any(kw in cat_lower for kw in ["restaurante", "bar", "lanchonete"]):
            return (
                "Trabalhamos com restaurantes aqui em Curitiba e vemos muito que reservas se perdem quando o estabelecimento está cheio "
                "ou fora do horário. Um agente de voz com IA consegue capturar essas reservas automaticamente — "
                "o cliente liga, marca e já recebe confirmação, sem precisar de ninguém disponível."
            )

        return (
            f"Estou conversando com negócios como o {biz.name} aqui em Curitiba sobre como a inteligência artificial "
            "pode ajudar a atender mais clientes, perder menos tempo em tarefas repetitivas e faturar mais. "
            "Você já pensou em usar IA no seu negócio?"
        )

    def _get_main_solution(self, oportunidades: list[str]) -> str:
        """Gera a apresentação da solução baseada na principal oportunidade."""
        if not oportunidades:
            return (
                "A Agenty desenvolve soluções personalizadas de IA para pequenos negócios. "
                "Podemos começar com um diagnóstico gratuito para identificar onde a IA gera mais impacto para vocês."
            )

        top = oportunidades[0]

        if "Voice agent" in top or "agendamento" in top.lower():
            return (
                "A gente desenvolveu atendentes virtuais por voz — uma IA que atende o telefone do seu negócio, "
                "agenda consultas/reservas, responde dúvidas e só passa para um humano quando necessário. "
                "Funciona 24 horas, 7 dias por semana. O cliente nem percebe que é IA."
            )
        if "Chatbot" in top or "WhatsApp" in top:
            return (
                "Criamos chatbots treinados especificamente no seu negócio para WhatsApp. "
                "Ele responde perguntas, qualifica clientes e agenda — tudo automaticamente. "
                "Seu time para de perder tempo com as mesmas perguntas de sempre."
            )
        if "reputação" in top.lower():
            return (
                "Desenvolvemos um sistema que monitora suas avaliações e responde automaticamente "
                "com uma mensagem personalizada e empática — no mesmo dia, a qualquer hora. "
                "Isso melhora sua nota e mostra ao potencial cliente que você se importa."
            )

        return (
            "Desenvolvemos soluções de IA personalizadas para o seu tipo de negócio — "
            "desde atendimento automatizado até análise de dados. "
            "O primeiro passo é um diagnóstico gratuito de 30 minutos para ver o que faz mais sentido para você."
        )
