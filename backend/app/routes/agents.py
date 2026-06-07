"""
Agent Chat Routes
Endpoints para conversar com agentes especialistas
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.auth import get_current_user
from app.schemas.user import UserResponse
from app.agents import logistics_expert, commercial_expert

router = APIRouter(prefix="/api/agents", tags=["agents"])


class ChatMessage(BaseModel):
    """Mensagem de chat com agente"""
    agent_type: str  # "logistics" ou "commercial"
    message: str
    context: dict = {}


class AgentResponse(BaseModel):
    """Resposta do agente"""
    agent_name: str
    agent_title: str
    message: str
    next_suggestions: list[str] = []


# ===== LOGISTICS AGENT =====

@router.post("/logistics/greeting")
def logistics_greeting(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Primeiro contato com especialista em logística
    """
    return AgentResponse(
        agent_name=logistics_expert.name,
        agent_title=logistics_expert.title,
        message=logistics_expert.initial_greeting(),
        next_suggestions=[
            "ask_operations",
            "ask_about_compliance",
            "ask_about_scaling",
            "see_timeline"
        ]
    )


@router.post("/logistics/operations")
def logistics_ask_operations(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perguntar sobre operações atuais"""
    return AgentResponse(
        agent_name=logistics_expert.name,
        agent_title=logistics_expert.title,
        message=logistics_expert.ask_about_operations(),
        next_suggestions=[
            "propose_compliance_solution",
            "propose_scaling_solution",
            "propose_quality_solution"
        ]
    )


@router.post("/logistics/solution")
def logistics_propose_solution(
    pain_point: str = "compliance",
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Propor solução para um pain point específico
    pain_point: "compliance", "scaling", ou "quality"
    """
    return AgentResponse(
        agent_name=logistics_expert.name,
        agent_title=logistics_expert.title,
        message=logistics_expert.propose_solution(pain_point),
        next_suggestions=[
            "see_timeline",
            "ask_about_commitment",
            "handle_objection"
        ]
    )


@router.post("/logistics/timeline")
def logistics_timeline(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ver timeline de 6 meses"""
    return AgentResponse(
        agent_name=logistics_expert.name,
        agent_title=logistics_expert.title,
        message=logistics_expert.timeline_proposal(),
        next_suggestions=[
            "ask_about_commitment",
            "ask_about_costs",
            "closing"
        ]
    )


@router.post("/logistics/commitment")
def logistics_ask_commitment(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perguntar sobre compromisso e termos"""
    return AgentResponse(
        agent_name=logistics_expert.name,
        agent_title=logistics_expert.title,
        message=logistics_expert.ask_commitment(),
        next_suggestions=[
            "answer_objection",
            "closing"
        ]
    )


@router.post("/logistics/objection")
def logistics_handle_objection(
    objection: str = "expensive",
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Responder objeção
    objection: "expensive", "timeline", ou "expertise"
    """
    return AgentResponse(
        agent_name=logistics_expert.name,
        agent_title=logistics_expert.title,
        message=logistics_expert.handle_objection(objection),
        next_suggestions=[
            "another_objection",
            "closing"
        ]
    )


@router.post("/logistics/closing")
def logistics_closing(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mensagem final de fechamento"""
    return AgentResponse(
        agent_name=logistics_expert.name,
        agent_title=logistics_expert.title,
        message=logistics_expert.closing_message(),
        next_suggestions=[
            "schedule_call",
            "contact_directly"
        ]
    )


# ===== COMMERCIAL AGENT =====

@router.post("/commercial/greeting")
def commercial_greeting(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Primeiro contato com especialista em conexões comerciais
    """
    return AgentResponse(
        agent_name=commercial_expert.name,
        agent_title=commercial_expert.title,
        message=commercial_expert.initial_greeting(),
        next_suggestions=[
            "ask_current_state",
            "see_pitch_deck",
            "ask_about_postos"
        ]
    )


@router.post("/commercial/current_state")
def commercial_ask_state(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perguntar sobre estado atual"""
    return AgentResponse(
        agent_name=commercial_expert.name,
        agent_title=commercial_expert.title,
        message=commercial_expert.ask_about_current_state(),
        next_suggestions=[
            "see_pitch_deck",
            "see_negotiation_strategy",
            "see_metrics"
        ]
    )


@router.post("/commercial/pitch_deck")
def commercial_pitch_deck(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ver estrutura de pitch deck"""
    return AgentResponse(
        agent_name=commercial_expert.name,
        agent_title=commercial_expert.title,
        message=commercial_expert.pitch_deck_structure(),
        next_suggestions=[
            "see_negotiation_strategy",
            "ask_about_costs"
        ]
    )


@router.post("/commercial/negotiation")
def commercial_negotiation(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ver estratégia de negociação"""
    return AgentResponse(
        agent_name=commercial_expert.name,
        agent_title=commercial_expert.title,
        message=commercial_expert.negotiation_strategy(),
        next_suggestions=[
            "see_metrics",
            "see_incentives",
            "closing"
        ]
    )


@router.post("/commercial/metrics")
def commercial_metrics(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ver como acompanhar métricas"""
    return AgentResponse(
        agent_name=commercial_expert.name,
        agent_title=commercial_expert.title,
        message=commercial_expert.metrics_tracking(),
        next_suggestions=[
            "see_incentives",
            "see_negotiation_strategy"
        ]
    )


@router.post("/commercial/incentives")
def commercial_incentives(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ver estrutura de incentivos"""
    return AgentResponse(
        agent_name=commercial_expert.name,
        agent_title=commercial_expert.title,
        message=commercial_expert.incentive_structure(),
        next_suggestions=[
            "see_negotiation_strategy",
            "closing"
        ]
    )


@router.post("/commercial/objection")
def commercial_handle_objection(
    objection: str = "no_network",
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Responder objeção
    objection: "no_network", "too_ambitious", ou "cost"
    """
    return AgentResponse(
        agent_name=commercial_expert.name,
        agent_title=commercial_expert.title,
        message=commercial_expert.handle_objection(objection),
        next_suggestions=[
            "another_objection",
            "closing"
        ]
    )


@router.post("/commercial/closing")
def commercial_closing(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pitch final para fechar"""
    return AgentResponse(
        agent_name=commercial_expert.name,
        agent_title=commercial_expert.title,
        message=commercial_expert.closing_pitch(),
        next_suggestions=[
            "ask_about_commitment",
            "next_steps"
        ]
    )


@router.post("/commercial/next_steps")
def commercial_next_steps(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Próximos passos"""
    return AgentResponse(
        agent_name=commercial_expert.name,
        agent_title=commercial_expert.title,
        message=commercial_expert.next_steps(),
        next_suggestions=[
            "schedule_call",
            "contact_directly"
        ]
    )


# ===== UTILITY =====

@router.get("/logistics/info")
def logistics_info():
    """
    Info sobre especialista em logística
    """
    return {
        "name": logistics_expert.name,
        "title": logistics_expert.title,
        "background": logistics_expert.background,
        "expertise": logistics_expert.expertise
    }


@router.get("/commercial/info")
def commercial_info():
    """
    Info sobre especialista em conexões comerciais
    """
    return {
        "name": commercial_expert.name,
        "title": commercial_expert.title,
        "background": commercial_expert.background,
        "expertise": commercial_expert.expertise
    }
