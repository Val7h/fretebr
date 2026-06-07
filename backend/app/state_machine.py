"""
State Machine para Match: define transicoes validas.
Evita pular estados (ex: pendente -> finalizado sem aceitar).
"""
from fastapi import HTTPException, status

# Mapa: status_atual -> [status_validos_proximos]
MATCH_TRANSITIONS = {
    "pendente":    ["aceito", "rejeitado", "cancelado"],
    "aceito":      ["em_entrega", "cancelado"],
    "em_entrega":  ["finalizado", "cancelado"],
    "finalizado":  [],  # estado terminal
    "rejeitado":   [],  # estado terminal
    "cancelado":   [],  # estado terminal
}

TERMINAL_STATES = {"finalizado", "rejeitado", "cancelado"}


def can_transition(current: str, target: str) -> bool:
    """Retorna True se transicao current -> target eh valida."""
    if current not in MATCH_TRANSITIONS:
        return False
    return target in MATCH_TRANSITIONS[current]


def assert_transition(current: str, target: str):
    """Lanca HTTPException 400 se transicao invalida."""
    if not can_transition(current, target):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transicao invalida: {current} -> {target}. "
                   f"Estados validos a partir de '{current}': {MATCH_TRANSITIONS.get(current, [])}"
        )


def is_terminal(state: str) -> bool:
    return state in TERMINAL_STATES
