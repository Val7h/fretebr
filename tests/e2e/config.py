"""Configuração compartilhada para testes E2E."""
import time
import random

BASE_URL = "http://localhost:8001"

def unique_email(prefix="user"):
    """Gera email único para evitar conflitos."""
    return f"{prefix}_{int(time.time()*1000)}_{random.randint(1000,9999)}@fretebr.test"

def unique_cpf():
    """Gera CPF fake único (apenas dígitos)."""
    return str(random.randint(10000000000, 99999999999))

def unique_phone():
    return f"119{random.randint(10000000, 99999999)}"

DEFAULT_PASSWORD = "Senha@123Forte"
