"""E2E: Segurança - autorização, tokens, escopo de acesso."""
import requests
from .config import BASE_URL
from .helpers import create_user_and_token, auth_header, sample_frete_payload


# Token JWT estruturalmente válido mas expirado/assinatura falsa
EXPIRED_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiIxIiwiZXhwIjoxMDAwMDAwMDAwfQ."
    "abcDEFghiJKLmnoPQRstuVWXyz1234567890aaaa"
)

PROTECTED_ENDPOINTS = [
    ("GET", "/auth/me"),
    ("POST", "/fretes"),
    ("GET", "/matches"),
]


def test_endpoint_protegido_sem_token():
    for method, path in PROTECTED_ENDPOINTS:
        r = requests.request(method, f"{BASE_URL}{path}", json={}, timeout=10)
        assert r.status_code in (401, 403), (
            f"{method} {path} sem token deveria 401/403, veio {r.status_code}"
        )


def test_token_expirado_retorna_401():
    r = requests.get(
        f"{BASE_URL}/auth/me",
        headers=auth_header(EXPIRED_TOKEN),
        timeout=10,
    )
    assert r.status_code in (401, 403), f"token expirado deveria 401/403, veio {r.status_code}"


def test_token_malformado_retorna_401():
    r = requests.get(
        f"{BASE_URL}/auth/me",
        headers=auth_header("isso.nao.eh.jwt"),
        timeout=10,
    )
    assert r.status_code in (401, 403)


def test_shipper_nao_ve_propostas_de_outro_shipper():
    # Shipper A cria frete e recebe propostas
    shipper_a_token, _ = create_user_and_token("shipper")
    driver_token, _ = create_user_and_token("driver")

    fr = requests.post(
        f"{BASE_URL}/fretes",
        json=sample_frete_payload(),
        headers=auth_header(shipper_a_token),
        timeout=10,
    )
    assert fr.status_code in (200, 201)
    frete_id = fr.json()["id"]

    pr = requests.post(
        f"{BASE_URL}/matches",
        json={"frete_id": frete_id, "valor_proposto": 2400.0, "mensagem": "x"},
        headers=auth_header(driver_token),
        timeout=10,
    )
    if pr.status_code == 404:
        pr = requests.post(
            f"{BASE_URL}/propostas",
            json={"frete_id": frete_id, "valor_proposto": 2400.0, "mensagem": "x"},
            headers=auth_header(driver_token),
            timeout=10,
        )
    assert pr.status_code in (200, 201)

    # Shipper B (outro) tenta ver as propostas do frete do A
    shipper_b_token, _ = create_user_and_token("shipper")
    r = requests.get(
        f"{BASE_URL}/fretes/{frete_id}/matches",
        headers=auth_header(shipper_b_token),
        timeout=10,
    )
    assert r.status_code in (401, 403, 404), (
        f"shipper B nao deveria ver propostas do frete de A, veio {r.status_code}"
    )


def test_motorista_nao_pode_aceitar_proposta():
    # Setup: shipper cria frete, driver1 faz proposta
    shipper_token, _ = create_user_and_token("shipper")
    driver1_token, _ = create_user_and_token("driver")
    driver2_token, _ = create_user_and_token("driver")

    fr = requests.post(
        f"{BASE_URL}/fretes",
        json=sample_frete_payload(),
        headers=auth_header(shipper_token),
        timeout=10,
    )
    frete_id = fr.json()["id"]

    pr = requests.post(
        f"{BASE_URL}/matches",
        json={"frete_id": frete_id, "valor_proposto": 2400.0, "mensagem": "x"},
        headers=auth_header(driver1_token),
        timeout=10,
    )
    if pr.status_code == 404:
        pr = requests.post(
            f"{BASE_URL}/propostas",
            json={"frete_id": frete_id, "valor_proposto": 2400.0, "mensagem": "x"},
            headers=auth_header(driver1_token),
            timeout=10,
        )
    match_id = pr.json().get("id")

    # Motorista (driver2) tenta aceitar - deve falhar
    ar = requests.post(
        f"{BASE_URL}/matches/{match_id}/accept",
        headers=auth_header(driver2_token),
        timeout=10,
    )
    if ar.status_code == 404:
        ar = requests.patch(
            f"{BASE_URL}/matches/{match_id}",
            json={"status": "accepted"},
            headers=auth_header(driver2_token),
            timeout=10,
        )
    assert ar.status_code in (401, 403, 404), (
        f"motorista nao deveria poder aceitar, veio {ar.status_code}"
    )


def test_motorista_nao_pode_criar_frete():
    driver_token, _ = create_user_and_token("driver")
    r = requests.post(
        f"{BASE_URL}/fretes",
        json=sample_frete_payload(),
        headers=auth_header(driver_token),
        timeout=10,
    )
    assert r.status_code in (401, 403), (
        f"motorista nao deveria criar frete, veio {r.status_code}"
    )


if __name__ == "__main__":
    for fn_name in [n for n in dir() if n.startswith("test_")]:
        try:
            globals()[fn_name]()
            print(f"PASS  {fn_name}")
        except Exception as e:
            print(f"FAIL  {fn_name}: {e}")
