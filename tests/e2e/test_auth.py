"""E2E: Autenticação - signup, login, JWT, /auth/me."""
import requests
from .config import BASE_URL, DEFAULT_PASSWORD
from .helpers import signup, login, auth_header


def test_signup_shipper():
    r, payload = signup(role="shipper")
    assert r.status_code in (200, 201), f"signup falhou: {r.status_code} {r.text}"
    data = r.json()
    assert "access_token" in data or "token" in data or "id" in data


def test_signup_driver():
    r, payload = signup(role="driver")
    assert r.status_code in (200, 201), f"signup falhou: {r.status_code} {r.text}"


def test_signup_duplicate_email_falha():
    r1, payload = signup(role="shipper")
    assert r1.status_code in (200, 201)
    r2 = requests.post(f"{BASE_URL}/auth/signup", json=payload, timeout=10)
    assert r2.status_code in (400, 409, 422), "email duplicado deveria falhar"


def test_login_sucesso():
    r, payload = signup(role="shipper")
    assert r.status_code in (200, 201)
    lr = login(payload["email"], DEFAULT_PASSWORD)
    assert lr.status_code == 200, f"login falhou: {lr.text}"
    assert "access_token" in lr.json() or "token" in lr.json()


def test_login_senha_errada():
    r, payload = signup(role="shipper")
    lr = login(payload["email"], "SenhaErrada123!")
    assert lr.status_code in (400, 401, 403), "senha errada deveria falhar"


def test_login_email_inexistente():
    lr = login("naoexiste_xyz@fretebr.test", "qualquer")
    assert lr.status_code in (400, 401, 403, 404)


def test_auth_me_com_token():
    r, payload = signup(role="shipper")
    token = r.json().get("access_token") or r.json().get("token")
    if not token:
        token = login(payload["email"]).json().get("access_token")
    me = requests.get(f"{BASE_URL}/auth/me", headers=auth_header(token), timeout=10)
    assert me.status_code == 200, f"/auth/me falhou: {me.text}"
    body = me.json()
    assert body.get("email") == payload["email"]


def test_auth_me_sem_token():
    me = requests.get(f"{BASE_URL}/auth/me", timeout=10)
    assert me.status_code in (401, 403)


def test_auth_me_token_invalido():
    me = requests.get(
        f"{BASE_URL}/auth/me",
        headers=auth_header("token.falso.invalido"),
        timeout=10,
    )
    assert me.status_code in (401, 403)


if __name__ == "__main__":
    for fn_name in [n for n in dir() if n.startswith("test_")]:
        try:
            globals()[fn_name]()
            print(f"PASS  {fn_name}")
        except Exception as e:
            print(f"FAIL  {fn_name}: {e}")
