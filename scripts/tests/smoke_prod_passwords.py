# -*- coding: utf-8 -*-
"""Smoke test PROD dos novos endpoints: politica de senha + forgot/reset."""
import requests, urllib3
from datetime import datetime
urllib3.disable_warnings()

API = "https://fretebr-api.fly.dev/api"
TS = str(int(datetime.now().timestamp()))

results = []
def check(name, cond, detail=""):
    s = "OK" if cond else "FAIL"
    results.append((name, s, detail))
    print(f"[{s}] {name} {detail}")

print("\n=== SMOKE PROD - politica de senha + forgot/reset ===\n")

# 1. Senha fraca DEVE ser rejeitada
r = requests.post(f"{API}/auth/signup",
    json={"email": f"weak_{TS}@x.com", "password": "123",
          "tipo": "shipper", "nome": "X"},
    verify=False, timeout=15)
check("Senha '123' rejeitada", r.status_code == 422,
    f"code={r.status_code} (FAIL=200 significa deploy ainda nao rolou)")

# 2. Senha sem letra
r = requests.post(f"{API}/auth/signup",
    json={"email": f"nolet_{TS}@x.com", "password": "12345678",
          "tipo": "shipper", "nome": "X"},
    verify=False, timeout=15)
check("Senha so numeros '12345678' rejeitada", r.status_code == 422)

# 3. Senha sem numero
r = requests.post(f"{API}/auth/signup",
    json={"email": f"nonum_{TS}@x.com", "password": "apenastexto",
          "tipo": "shipper", "nome": "X"},
    verify=False, timeout=15)
check("Senha so letras rejeitada", r.status_code == 422)

# 4. Senha valida
EMAIL = f"user_{TS}@x.com"
SENHA_INICIAL = "minhaSenha2026"
r = requests.post(f"{API}/auth/signup",
    json={"email": EMAIL, "password": SENHA_INICIAL,
          "tipo": "shipper", "nome": "User Test"},
    verify=False, timeout=15)
check("Senha forte aceita", r.status_code == 200)

# 5. Forgot-password endpoint existe
r = requests.post(f"{API}/auth/forgot-password",
    json={"email": EMAIL}, verify=False, timeout=15)
check("/auth/forgot-password existe", r.status_code == 200,
    f"code={r.status_code} (FAIL=404 significa deploy ainda nao rolou)")

reset_link = ""
if r.status_code == 200:
    data = r.json()
    reset_link = data.get("debug_reset_link", "")
    check("Forgot retorna debug_reset_link em staging", bool(reset_link),
        f"link_len={len(reset_link)}")

# 6. Anti-enumeracao: email inexistente retorna mesma msg
r = requests.post(f"{API}/auth/forgot-password",
    json={"email": "nao_existe@xyz.com"}, verify=False, timeout=15)
check("Anti-enum: 200 p/ email inexistente", r.status_code == 200)

# 7. Reset com token valido
if reset_link and "token=" in reset_link:
    token = reset_link.split("token=")[1]
    NOVA_SENHA = "novaSenha9876"
    r = requests.post(f"{API}/auth/reset-password",
        json={"token": token, "new_password": NOVA_SENHA},
        verify=False, timeout=15)
    check("Reset com token valido", r.status_code == 200,
        f"code={r.status_code} body={r.text[:80]}")

    # 8. Login com nova senha
    r = requests.post(f"{API}/auth/login",
        json={"email": EMAIL, "password": NOVA_SENHA},
        verify=False, timeout=15)
    check("Login com SENHA NOVA", r.status_code == 200)

    # 9. Login com senha ANTIGA deve falhar
    r = requests.post(f"{API}/auth/login",
        json={"email": EMAIL, "password": SENHA_INICIAL},
        verify=False, timeout=15)
    check("Login com senha ANTIGA bloqueado", r.status_code == 401,
        f"code={r.status_code}")

# 10. Reset com token zoado
r = requests.post(f"{API}/auth/reset-password",
    json={"token": "fake.token.xyz", "new_password": "validaSenha1"},
    verify=False, timeout=15)
check("Token zoado rejeitado", r.status_code == 401)

# Resumo
ok_count = sum(1 for _, s, _ in results if s == "OK")
fail_count = sum(1 for _, s, _ in results if s == "FAIL")
print("\n" + "="*55)
print(f"RESULTADO: {ok_count}/{len(results)} OK ({fail_count} FAIL)")
if fail_count > 0:
    print("\nSe FAIL = deploy ainda nao rolou. Rode:")
    print("  cd C:\\Users\\Admin\\FreteBR\\backend")
    print("  fly deploy -a fretebr-api")
print()
