"""Helpers reutilizáveis para registrar, logar e criar entidades."""
import requests
from .config import BASE_URL, unique_email, unique_cpf, unique_phone, DEFAULT_PASSWORD


def signup(role="shipper", **overrides):
    """Registra um novo usuário. role: 'shipper' ou 'driver'."""
    payload = {
        "email": unique_email(role),
        "password": DEFAULT_PASSWORD,
        "name": f"Usuario {role.title()}",
        "role": role,
        "phone": unique_phone(),
        "cpf": unique_cpf(),
    }
    payload.update(overrides)
    r = requests.post(f"{BASE_URL}/auth/signup", json=payload, timeout=10)
    return r, payload


def login(email, password=DEFAULT_PASSWORD):
    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    return r


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def create_user_and_token(role="shipper"):
    """Cria usuário e retorna (token, user_payload)."""
    r, payload = signup(role=role)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Signup falhou: {r.status_code} {r.text}")
    data = r.json()
    token = data.get("access_token") or data.get("token")
    if not token:
        # Tenta login se signup não retornou token
        lr = login(payload["email"])
        token = lr.json().get("access_token") or lr.json().get("token")
    return token, payload


def sample_frete_payload(**overrides):
    base = {
        "origem": "São Paulo, SP",
        "destino": "Rio de Janeiro, RJ",
        "peso_kg": 1500,
        "tipo_carga": "Geral",
        "valor_oferecido": 2500.00,
        "descricao": "Carga de teste E2E",
        "data_coleta": "2026-07-01",
    }
    base.update(overrides)
    return base
