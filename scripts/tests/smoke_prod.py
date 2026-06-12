# -*- coding: utf-8 -*-
"""Smoke test E2E contra producao."""
import requests
import urllib3
from datetime import datetime

urllib3.disable_warnings()

API = "https://fretebr-api.fly.dev/api"
BASE = "https://fretebr-api.fly.dev"
TS = str(int(datetime.now().timestamp()))

results = []
def check(name, cond, detail=""):
    s = "OK" if cond else "FAIL"
    results.append((name, s, detail))
    print(f"[{s}] {name} {detail}")

print("\n=== SMOKE TEST PROD - https://fretebr-api.fly.dev ===\n")

# 1. Health
r = requests.get(f"{BASE}/health", timeout=15, verify=False)
check("/health 200", r.status_code == 200, f"body={r.text[:60]}")

# 2. Metrics
r = requests.get(f"{BASE}/metrics", timeout=15, verify=False)
check("/metrics Prometheus", r.status_code == 200 and "fretebr_" in r.text)

# 3. Signup shipper
r = requests.post(f"{API}/auth/signup", json={
    "email": f"prod_sh_{TS}@test.com", "password": "test123",
    "tipo": "shipper", "nome": "Prod Shipper"
}, timeout=15, verify=False)
ok = r.status_code == 200
check("Signup shipper", ok, f"code={r.status_code}")
sh_token = r.json().get("access_token") if ok else None

# 4. Signup motorista
r = requests.post(f"{API}/auth/signup", json={
    "email": f"prod_mo_{TS}@test.com", "password": "test123",
    "tipo": "motorista", "nome": "Prod Motorista"
}, timeout=15, verify=False)
ok = r.status_code == 200
check("Signup motorista", ok, f"code={r.status_code}")
mo_token = r.json().get("access_token") if ok else None

if not (sh_token and mo_token):
    print("\nFALHOU no signup - abortando demais testes")
else:
    # 5. /auth/me
    r = requests.get(f"{API}/auth/me",
        headers={"Authorization": f"Bearer {sh_token}"}, timeout=15, verify=False)
    check("/auth/me", r.status_code == 200)

    # 6. Postar frete
    r = requests.post(f"{API}/fretes",
        headers={"Authorization": f"Bearer {sh_token}"},
        json={"origem": "SP", "destino": "RJ", "peso_kg": 200,
              "valor_r": 500, "descricao": "smoke prod"},
        timeout=15, verify=False)
    ok = r.status_code in [200, 201]
    check("Postar frete", ok, f"code={r.status_code}")
    frete_id = r.json().get("id") if ok else None

    # 7. Listar fretes
    r = requests.get(f"{API}/fretes",
        headers={"Authorization": f"Bearer {mo_token}"}, timeout=15, verify=False)
    check("Listar fretes (motorista)", r.status_code == 200)

    if frete_id:
        # 8. Fazer proposta
        r = requests.post(
            f"{API}/matches/?frete_id={frete_id}&valor_proposta=450&mensagem=smoke",
            headers={"Authorization": f"Bearer {mo_token}"}, timeout=15, verify=False)
        ok = r.status_code in [200, 201]
        check("Fazer proposta", ok, f"code={r.status_code}")
        match_id = r.json().get("id") if ok else None

        if match_id:
            # 9. Aceitar
            r = requests.put(f"{API}/matches/{match_id}/accept",
                headers={"Authorization": f"Bearer {sh_token}"},
                timeout=15, verify=False)
            check("Aceitar proposta", r.status_code == 200)

            # 10. Chat
            r = requests.post(f"{API}/messages/match/{match_id}",
                headers={"Authorization": f"Bearer {mo_token}"},
                json={"conteudo": "Ola prod!"}, timeout=15, verify=False)
            check("Enviar mensagem", r.status_code == 200)

            r = requests.get(f"{API}/messages/match/{match_id}",
                headers={"Authorization": f"Bearer {sh_token}"},
                timeout=15, verify=False)
            check("Ler mensagens", r.status_code == 200)

            # 11. Notificacoes
            r = requests.get(f"{API}/notifications?limit=5",
                headers={"Authorization": f"Bearer {mo_token}"},
                timeout=15, verify=False)
            check("Notificacoes", r.status_code == 200)

            # 12. Pagamento Pix (MOCK)
            r = requests.post(f"{API}/payments",
                headers={"Authorization": f"Bearer {sh_token}"},
                json={"match_id": match_id, "amount": 450.0},
                timeout=15, verify=False)
            ok = r.status_code in [200, 201]
            qr = r.json().get("qr_code_data", "") if ok else ""
            check("Criar pagamento Pix MOCK", ok, f"qr_len={len(qr)}")
            check("QR Pix BR valido", qr.startswith("00020126"), f"prefix={qr[:8]}")

# Resumo
print("\n" + "="*55)
ok = sum(1 for _, s, _ in results if s == "OK")
fail = sum(1 for _, s, _ in results if s == "FAIL")
print(f"SMOKE PROD: {ok}/{len(results)} OK ({fail} FAIL)")
print(f"URL backend: https://fretebr-api.fly.dev")
