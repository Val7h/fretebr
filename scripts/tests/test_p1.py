# -*- coding: utf-8 -*-
"""
Teste das melhorias P1: rate limit, refresh token, state machine, idempotency.
"""
import requests
import time
from datetime import datetime

BASE = "http://localhost:8001"
API = f"{BASE}/api"
TS = str(int(datetime.now().timestamp()))

results = []
def check(name, cond, detail=""):
    status = "OK" if cond else "FAIL"
    results.append((name, status, detail))
    print(f"[{status}] {name} {detail}")

print("\n=== TESTE SPRINT P1 ===\n")

# ===== P1.1: RATE LIMITING =====
print("--- P1.1: Rate Limiting em /login ---")

# Faz 7 tentativas erradas - 6+ devem retornar 429
bad_responses = []
for i in range(7):
    r = requests.post(f"{API}/auth/login", json={"email": "naoexiste@x.com", "password": "x"})
    bad_responses.append(r.status_code)

count_401 = bad_responses.count(401)
count_429 = bad_responses.count(429)
print(f"  Tentativas (7x login com credenciais invalidas): {bad_responses}")
check("Rate limit dispara apos N tentativas", count_429 >= 1, f"(429s: {count_429}, 401s: {count_401})")

time.sleep(1)

# ===== P1.2: REFRESH TOKEN =====
print("\n--- P1.2: Refresh Token ---")

# Signup
r = requests.post(f"{API}/auth/signup", json={
    "email": f"p1_{TS}@test.com",
    "password": "senha123",
    "tipo": "shipper",
    "nome": "Tester P1"
})
check("Signup retorna 200", r.status_code == 200, f"(code={r.status_code})")
data = r.json() if r.status_code == 200 else {}
access = data.get("access_token")
refresh = data.get("refresh_token")
check("Signup retorna access_token", bool(access))
check("Signup retorna refresh_token", bool(refresh))

# Usar refresh token
if refresh:
    r = requests.post(f"{API}/auth/refresh", json={"refresh_token": refresh})
    check("Refresh com token valido", r.status_code == 200, f"(code={r.status_code})")
    new_data = r.json() if r.status_code == 200 else {}
    check("Refresh retorna novo access_token", bool(new_data.get("access_token")))
    check("Refresh rotaciona refresh_token", bool(new_data.get("refresh_token")))

# Tentar usar refresh invalido
r = requests.post(f"{API}/auth/refresh", json={"refresh_token": "invalid.token.here"})
check("Refresh com token invalido retorna 401", r.status_code == 401, f"(code={r.status_code})")

# Tentar usar ACCESS token como refresh - deve falhar
if access:
    r = requests.post(f"{API}/auth/refresh", json={"refresh_token": access})
    check("Refresh com access_token rejeitado", r.status_code == 401, f"(code={r.status_code})")

# ===== P1.3: STATE MACHINE =====
print("\n--- P1.3: State Machine do Match ---")

# Setup: shipper + motorista + frete + proposta
r = requests.post(f"{API}/auth/signup", json={
    "email": f"p1mot_{TS}@test.com", "password": "123",
    "tipo": "motorista", "nome": "Mot P1"
})
mot_token = r.json()["access_token"]
shipper_token = data.get("access_token")

r = requests.post(f"{API}/fretes",
    headers={"Authorization": f"Bearer {shipper_token}"},
    json={"origem": "SP", "destino": "RJ", "peso_kg": 100, "valor_r": 500, "descricao": "test"}
)
frete_id = r.json()["id"] if r.status_code in [200, 201] else None
check("Frete criado", bool(frete_id))

if frete_id:
    r = requests.post(
        f"{API}/matches/?frete_id={frete_id}&valor_proposta=450&mensagem=test",
        headers={"Authorization": f"Bearer {mot_token}"}
    )
    match_id = r.json()["id"] if r.status_code in [200, 201] else None
    check("Proposta criada (status pendente)", bool(match_id))

    if match_id:
        # Aceitar (pendente -> aceito) - deve funcionar
        r = requests.put(f"{API}/matches/{match_id}/accept",
            headers={"Authorization": f"Bearer {shipper_token}"})
        check("Aceitar (pendente -> aceito)", r.status_code == 200, f"(code={r.status_code})")

        # Tentar aceitar de novo (aceito -> aceito) - deve dar 400
        r = requests.put(f"{API}/matches/{match_id}/accept",
            headers={"Authorization": f"Bearer {shipper_token}"})
        check("Re-aceitar bloqueado pelo state machine",
              r.status_code == 400,
              f"(code={r.status_code}, detail={r.text[:80]})")

        # Tentar rejeitar match ja aceito - deve dar 400
        r = requests.put(f"{API}/matches/{match_id}/reject",
            headers={"Authorization": f"Bearer {shipper_token}"})
        check("Rejeitar match aceito bloqueado",
              r.status_code == 400,
              f"(code={r.status_code})")

# ===== P1.4: WEBHOOK MP (idempotency + security) =====
print("\n--- P1.4: Webhook MP (security + idempotency) ---")

# Sem secret env -> 503
r = requests.post(f"{API}/payments/webhook/mercado-pago",
    headers={"Content-Type": "application/json"},
    json={"type": "payment", "data": {"id": "123"}})
check("Webhook sem secret env -> 503", r.status_code == 503, f"(code={r.status_code})")

# ===== RESUMO =====
print("\n" + "="*60)
print("RESUMO SPRINT P1")
print("="*60)
ok = sum(1 for _, s, _ in results if s == "OK")
fail = sum(1 for _, s, _ in results if s == "FAIL")
total = len(results)
print(f"OK: {ok}/{total}")
print(f"FAIL: {fail}/{total}")
if fail > 0:
    print("\nFalhas:")
    for name, status, detail in results:
        if status == "FAIL":
            print(f"  - {name} {detail}")
print()
