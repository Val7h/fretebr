# -*- coding: utf-8 -*-
"""
Teste E2E do fluxo Pix completo (P2): criar pagamento -> simular pago -> recibo.
"""
import requests
import time
from datetime import datetime

BASE = "http://localhost:8001"
API = f"{BASE}/api"
TS = str(int(datetime.now().timestamp()))

results = []
def check(name, cond, detail=""):
    s = "OK" if cond else "FAIL"
    results.append((name, s, detail))
    print(f"[{s}] {name} {detail}")

print("\n=== TESTE SPRINT P2 - FLUXO PIX END-TO-END ===\n")

# Setup
print("--- Setup: criar shipper + motorista + frete + match aceito ---")
r = requests.post(f"{API}/auth/signup", json={
    "email": f"p2sh_{TS}@test.com", "password": "senha123",
    "tipo": "shipper", "nome": "P2 Ship"
})
sh = r.json()
sh_token = sh["access_token"]
sh_id = sh["user"]["id"]
check("Shipper criado", r.status_code == 200, f"id={sh_id}")

r = requests.post(f"{API}/auth/signup", json={
    "email": f"p2mo_{TS}@test.com", "password": "senha123",
    "tipo": "motorista", "nome": "P2 Mot"
})
mo = r.json()
mo_token = mo["access_token"]
mo_id = mo["user"]["id"]
check("Motorista criado", r.status_code == 200, f"id={mo_id}")

r = requests.post(f"{API}/fretes",
    headers={"Authorization": f"Bearer {sh_token}"},
    json={"origem": "SP", "destino": "RJ", "peso_kg": 200, "valor_r": 800, "descricao": "p2"}
)
frete_id = r.json()["id"]
check("Frete criado", r.status_code in [200, 201], f"id={frete_id}")

r = requests.post(
    f"{API}/matches/?frete_id={frete_id}&valor_proposta=750&mensagem=p2",
    headers={"Authorization": f"Bearer {mo_token}"}
)
match_id = r.json()["id"]
check("Proposta criada", r.status_code in [200, 201], f"match_id={match_id}")

r = requests.put(f"{API}/matches/{match_id}/accept",
    headers={"Authorization": f"Bearer {sh_token}"})
check("Match aceito", r.status_code == 200)

# ===== P2.1: CRIAR PAGAMENTO PIX (mock MP) =====
print("\n--- P2.1: Criar pagamento Pix (modo MOCK) ---")
r = requests.post(f"{API}/payments",
    headers={"Authorization": f"Bearer {sh_token}"},
    json={"match_id": match_id, "amount": 750.0}
)
check("POST /payments (shipper, match aceito)",
      r.status_code in [200, 201],
      f"code={r.status_code}, body={r.text[:120]}")
payment = r.json() if r.status_code in [200, 201] else {}
transaction_id = payment.get("transaction_id")
qr = payment.get("qr_code_data")
check("Retorna transaction_id", bool(transaction_id))
check("Retorna qr_code_data", bool(qr), f"qr_len={len(qr) if qr else 0}")

# ===== P2.2: STATUS INICIAL = PENDENTE =====
print("\n--- P2.2: Status inicial ---")
r = requests.get(f"{API}/payments/{transaction_id}",
    headers={"Authorization": f"Bearer {sh_token}"})
check("GET /payments/{id} retorna 200", r.status_code == 200)
status = r.json().get("status") if r.status_code == 200 else None
check("Status inicial = pendente", status == "pendente", f"got={status}")

# ===== P2.3: AUTORIZACAO =====
print("\n--- P2.3: Autorizacao ---")
# Outro usuario nao pode ver
r = requests.post(f"{API}/auth/signup", json={
    "email": f"p2hk_{TS}@test.com", "password": "senha123",
    "tipo": "motorista", "nome": "Hacker"
})
hk_token = r.json()["access_token"]

r = requests.get(f"{API}/payments/{transaction_id}",
    headers={"Authorization": f"Bearer {hk_token}"})
check("Outro usuario bloqueado", r.status_code == 403, f"code={r.status_code}")

# Motorista do match PODE ver (e parte da transacao)
r = requests.get(f"{API}/payments/{transaction_id}",
    headers={"Authorization": f"Bearer {mo_token}"})
check("Motorista do match autorizado", r.status_code == 200, f"code={r.status_code}")

# ===== P2.4: SIMULAR PAGAMENTO (modo MOCK) =====
print("\n--- P2.4: Simular pagamento concluido ---")
r = requests.post(f"{API}/payments/{transaction_id}/simulate-paid",
    headers={"Authorization": f"Bearer {sh_token}"})
check("POST /simulate-paid (sucesso)",
      r.status_code == 200,
      f"code={r.status_code}, body={r.text[:100]}")

# Idempotente
r = requests.post(f"{API}/payments/{transaction_id}/simulate-paid",
    headers={"Authorization": f"Bearer {sh_token}"})
check("Simulate idempotente (already_paid)",
      r.status_code == 200 and "already" in r.text.lower(),
      f"body={r.text[:100]}")

# ===== P2.5: STATUS = PAGO =====
print("\n--- P2.5: Status apos pagamento ---")
r = requests.get(f"{API}/payments/{transaction_id}",
    headers={"Authorization": f"Bearer {sh_token}"})
status = r.json().get("status") if r.status_code == 200 else None
check("Status = pago", status == "pago", f"got={status}")

# ===== P2.6: RECIBO =====
print("\n--- P2.6: Recibo ---")
r = requests.get(f"{API}/payments/{match_id}/receipt",
    headers={"Authorization": f"Bearer {sh_token}"})
check("GET /receipt", r.status_code == 200, f"code={r.status_code}")
if r.status_code == 200:
    rec = r.json()
    check("Recibo tem transaction_id", "transaction_id" in rec)
    check("Recibo tem amount", "amount" in rec and rec["amount"] == 750.0,
          f"amount={rec.get('amount')}")
    check("Recibo tem status pago", rec.get("status") == "pago")

# ===== RESUMO =====
print("\n" + "="*60)
ok = sum(1 for _, s, _ in results if s == "OK")
fail = sum(1 for _, s, _ in results if s == "FAIL")
total = len(results)
print(f"SPRINT P2: {ok}/{total} OK ({fail} FAIL)")
if fail > 0:
    print("\nFalhas:")
    for name, s, detail in results:
        if s == "FAIL":
            print(f"  - {name} {detail}")
print()
