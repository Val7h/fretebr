# -*- coding: utf-8 -*-
"""
Testes da Sprint P3: observabilidade + cookies httpOnly + alembic.
"""
import os
import requests
from datetime import datetime

BASE = "http://localhost:8001"
API = f"{BASE}/api"
TS = str(int(datetime.now().timestamp()))

results = []
def check(name, cond, detail=""):
    s = "OK" if cond else "FAIL"
    results.append((name, s, detail))
    print(f"[{s}] {name} {detail}")

print("\n=== TESTE SPRINT P3 ===\n")

# ===== P3.1: QR code (frontend - so testamos que payload Pix tem formato BR Pix) =====
print("--- P3.1: Payload Pix do MOCK ---")
# signup + match + criar pagamento + ver formato
r = requests.post(f"{API}/auth/signup", json={
    "email": f"p3sh_{TS}@test.com", "password": "senha123",
    "tipo": "shipper", "nome": "P3 Ship"
})
sh = r.json(); sh_token = sh["access_token"]; sh_id = sh["user"]["id"]

r = requests.post(f"{API}/auth/signup", json={
    "email": f"p3mo_{TS}@test.com", "password": "senha123",
    "tipo": "motorista", "nome": "P3 Mot"
})
mo = r.json(); mo_token = mo["access_token"]

r = requests.post(f"{API}/fretes",
    headers={"Authorization": f"Bearer {sh_token}"},
    json={"origem": "SP", "destino": "RJ", "peso_kg": 100, "valor_r": 500, "descricao": "p3"})
frete_id = r.json()["id"]

r = requests.post(
    f"{API}/matches/?frete_id={frete_id}&valor_proposta=480&mensagem=p3",
    headers={"Authorization": f"Bearer {mo_token}"})
match_id = r.json()["id"]

requests.put(f"{API}/matches/{match_id}/accept",
    headers={"Authorization": f"Bearer {sh_token}"})

r = requests.post(f"{API}/payments",
    headers={"Authorization": f"Bearer {sh_token}"},
    json={"match_id": match_id, "amount": 480.0})
qr = r.json().get("qr_code_data", "") if r.status_code in [200, 201] else ""
check("Payload Pix gerado", len(qr) > 0, f"len={len(qr)}")
check("Payload contem prefixo BR Pix", qr.startswith("00020126"), f"prefix={qr[:8]}")

# ===== P3.2: Endpoints de metrics =====
print("\n--- P3.2: Endpoints de observabilidade ---")
r = requests.get(f"{BASE}/metrics")
check("/metrics retorna 200", r.status_code == 200, f"code={r.status_code}")
body = r.text if r.status_code == 200 else ""
check("/metrics tem formato Prometheus",
      "fretebr_requests_total" in body and "# TYPE" in body)
check("/metrics tem uptime", "fretebr_uptime_seconds" in body)

r = requests.get(f"{BASE}/metrics/summary")
check("/metrics/summary retorna 200", r.status_code == 200)
if r.status_code == 200:
    s = r.json()
    check("Summary tem uptime", "uptime_seconds" in s)
    check("Summary tem per_path", "per_path" in s and len(s["per_path"]) > 0,
          f"paths_count={len(s.get('per_path', {}))}")
    check("Summary tem total_requests", s.get("total_requests", 0) > 0,
          f"total={s.get('total_requests')}")

# ===== P3.3: Request ID =====
print("\n--- P3.3: X-Request-ID middleware ---")
r = requests.get(f"{BASE}/health")
rid = r.headers.get("X-Request-ID")
check("Resposta tem X-Request-ID", bool(rid), f"rid={rid}")

# Custom request ID e propagado
r = requests.get(f"{BASE}/health", headers={"X-Request-ID": "test-abc-123"})
check("X-Request-ID custom propagado",
      r.headers.get("X-Request-ID") == "test-abc-123",
      f"got={r.headers.get('X-Request-ID')}")

# ===== P3.4: Logout endpoint =====
print("\n--- P3.4: Logout ---")
r = requests.post(f"{API}/auth/logout")
check("POST /auth/logout retorna 200", r.status_code == 200, f"code={r.status_code}")

# ===== P3.5: get_current_user aceita Authorization OU cookie =====
print("\n--- P3.5: Auth via Authorization header (compat) ---")
r = requests.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {sh_token}"})
check("Auth via Bearer header funciona", r.status_code == 200)

# Sem token nem cookie
r = requests.get(f"{API}/auth/me")
check("Sem token retorna 401", r.status_code == 401)

# ===== P3.6: Alembic - migration file existe =====
print("\n--- P3.6: Alembic ---")
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
alembic_ini = os.path.join(backend_root, "alembic.ini")
versions_dir = os.path.join(backend_root, "alembic", "versions")
env_py = os.path.join(backend_root, "alembic", "env.py")
check("alembic.ini existe", os.path.exists(alembic_ini))
check("alembic/env.py existe", os.path.exists(env_py))
if os.path.exists(versions_dir):
    migrations = [f for f in os.listdir(versions_dir) if f.endswith(".py") and not f.startswith("__")]
    check("Pelo menos 1 migration gerada", len(migrations) >= 1, f"found={len(migrations)}")

# ===== RESUMO =====
print("\n" + "="*60)
ok = sum(1 for _, s, _ in results if s == "OK")
fail = sum(1 for _, s, _ in results if s == "FAIL")
total = len(results)
print(f"SPRINT P3: {ok}/{total} OK ({fail} FAIL)")
if fail > 0:
    print("\nFalhas:")
    for name, s, detail in results:
        if s == "FAIL":
            print(f"  - {name} {detail}")
print()
