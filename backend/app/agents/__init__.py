"""
Agentes Especialistas de IA
Interface para conversar com especialistas fictícios
"""

from app.agents.logistics_agent import LogisticsExpertAgent
from app.agents.commercial_agent import CommercialExpertAgent

__all__ = [
    "LogisticsExpertAgent",
    "CommercialExpertAgent"
]

# Instâncias globais dos agentes
logistics_expert = LogisticsExpertAgent()
commercial_expert = CommercialExpertAgent()


def get_logistics_response(topic: str) -> str:
    """Obtém resposta do especialista em logística"""

    responses = {
        "greeting": logistics_expert.initial_greeting(),
        "ask_operations": logistics_expert.ask_about_operations(),
        "propose_solution": logistics_expert.propose_solution("scaling"),
        "timeline": logistics_expert.timeline_proposal(),
        "commitment": logistics_expert.ask_commitment(),
        "closing": logistics_expert.closing_message(),
    }

    return responses.get(topic, logistics_expert.ask_about_operations())


def get_commercial_response(topic: str) -> str:
    """Obtém resposta do especialista em conexões comerciais"""

    responses = {
        "greeting": commercial_expert.initial_greeting(),
        "ask_state": commercial_expert.ask_about_current_state(),
        "pitch_deck": commercial_expert.pitch_deck_structure(),
        "negotiation": commercial_expert.negotiation_strategy(),
        "metrics": commercial_expert.metrics_tracking(),
        "incentives": commercial_expert.incentive_structure(),
        "closing": commercial_expert.closing_pitch(),
        "next_steps": commercial_expert.next_steps(),
    }

    return responses.get(topic, commercial_expert.ask_about_current_state())
