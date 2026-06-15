# -*- coding: utf-8 -*-
"""
SMOKE FINAL EM PROD - valida TUDO que foi entregue na jornada.
Rode apos `fly deploy` + Vercel auto-deploy.
"""
import requests
import urllib3
from datetime import datetime
urllib3.disable_warnings()

FRONT = "https://fretebr-web.vercel.app"
API = "https://fretebr-api.fly.dev/api"
BASE = "https://fretebr-api.fly.dev"
TS = str(int(datetime.now().timestamp()))

results = []
def check(name, cond, detail=""):
    s = "OK" if cond else "FAIL"
    results.append((name, s, detail))
    icon = "[OK]" if cond else "[FAIL]"
    print(f"{icon} {name} {detail}")

print("\n" + "="*70)
print("SMOKE FINAL DA JORNADA - PROD")
print("="*70)

# ===== 1. INFRAESTRUTURA =====
print("\n[1] Infraestrutura")
r = requests.get(f"{BASE}/health", timeout=15, verify=False)
check("Backend Fly online", r.status_code == 200)
r = requests.get(FRONT, timeout=15, verify=False)
check("Frontend Vercel online", r.status_code == 200, f"size={len(r.text)}B")
check("Title FreteBR (nao mais Dashboard)",
      "FreteBR" in r.text and "Dashboard" not in r.text)
check("lang=pt-BR", 'lang="pt-BR"' in r.text)

# ===== 2. METRICAS / OBSERVABILIDADE =====
print("\n[2] Observabilidade")
r = requests.get(f"{BASE}/metrics", timeout=15, verify=False)
check("/metrics Prometheus", r.status_code == 200 and "fretebr_" in r.text)
r = requests.get(f"{BASE}/metrics/summary", timeout=15, verify=False)
check("/metrics/summary JSON", r.status_code == 200)
r = requests.get(f"{BASE}/health", timeout=15, verify=False)
check("X-Request-ID header", bool(r.headers.get("X-Request-ID")))

# ===== 3. POLITICA DE SENHA =====
print("\n[3] Politica de senha")
r = requests.post(f"{API}/auth/signup",
    json={"email": f"weak_{TS}@x.com", "password": "123",
          "tipo": "shipper", "nome": "X"},
    verify=False, timeout=15)
check("Senha curta '123' rejeitada", r.status_code == 422)
r = requests.post(f"{API}/auth/signup",
    json={"email": f"weak2_{TS}@x.com", "password": "12345678",
          "tipo": "shipper", "nome": "X"},
    verify=False, timeout=15)
check("Senha sem letra rejeitada", r.status_code == 422)

# ===== 4. MENSAGENS PT-BR =====
print("\n[4] Mensagens em PT-BR")
r = requests.post(f"{API}/auth/login",
    json={"email": "nao@existe.com", "password": "qualquerCoisa1"},
    verify=False, timeout=15)
msg = r.json().get("detail", "")
check("Login errado em PT-BR", "E-mail ou senha incorretos" in msg, f"msg='{msg[:60]}'")

# ===== 5. FLUXO COMPLETO (cookies httpOnly) =====
print("\n[5] Fluxo completo com cookies httpOnly")
EMAIL_SH = f"final_sh_{TS}@test.com"
EMAIL_MO = f"final_mo_{TS}@test.com"
SENHA = "minhaSenha2026"

sh = requests.Session()
sh.headers.update({"Origin": FRONT})
r = sh.post(f"{API}/auth/signup",
    json={"email": EMAIL_SH, "password": SENHA, "tipo": "shipper", "nome": "Final Sh"},
    verify=False, timeout=15)
check("Shipper signup", r.status_code == 200)
check("Cookies httpOnly setados",
      "fretebr_access" in sh.cookies and "fretebr_refresh" in sh.cookies)

mo = requests.Session()
mo.headers.update({"Origin": FRONT})
r = mo.post(f"{API}/auth/signup",
    json={"email": EMAIL_MO, "password": SENHA, "tipo": "motorista", "nome": "Final Mo"},
    verify=False, timeout=15)
check("Motorista signup", r.status_code == 200)

# Postar frete
r = sh.post(f"{API}/fretes",
    json={"origem": "Sao Paulo", "destino": "Rio de Janeiro",
          "peso_kg": 300, "valor_r": 1200, "descricao": "smoke final"},
    verify=False, timeout=15)
check("Postar frete", r.status_code in (200, 201))
frete_id = r.json().get("id") if r.status_code in (200, 201) else None

# Motorista vai ver
r = mo.get(f"{API}/fretes", verify=False, timeout=15)
ok = r.status_code == 200
fretes = r.json() if ok else []
fretes = fretes if isinstance(fretes, list) else fretes.get("fretes", [])
check("Motorista lista fretes", ok and len(fretes) > 0, f"count={len(fretes)}")

# Fazer proposta
r = mo.post(
    f"{API}/matches/?frete_id={frete_id}&valor_proposta=1100&mensagem=smoke",
    verify=False, timeout=15)
check("Proposta criada", r.status_code in (200, 201))
match_id = r.json().get("id") if r.status_code in (200, 201) else None

# Aceitar
if match_id:
    r = sh.put(f"{API}/matches/{match_id}/accept", verify=False, timeout=15)
    check("Aceitar proposta", r.status_code == 200)

    # Chat
    r = mo.post(f"{API}/messages/match/{match_id}",
        json={"conteudo": "Oi! Pego amanha"}, verify=False, timeout=15)
    check("Motorista manda msg chat", r.status_code == 200)

    r = sh.get(f"{API}/messages/match/{match_id}", verify=False, timeout=15)
    check("Shipper le chat", r.status_code == 200)

    # Pagamento Pix MOCK
    r = sh.post(f"{API}/payments",
        json={"match_id": match_id, "amount": 1100.0},
        verify=False, timeout=15)
    ok = r.status_code in (200, 201)
    qr = r.json().get("qr_code_data", "") if ok else ""
    check("Criar Pix MOCK", ok)
    check("QR Pix BR valido", qr.startswith("00020126"))
    tx_id = r.json().get("transaction_id") if ok else None

    if tx_id:
        # Simulate paid
        r = sh.post(f"{API}/payments/{tx_id}/simulate-paid",
            verify=False, timeout=15)
        check("Simular pagamento", r.status_code == 200)

        # Recibo
        r = sh.get(f"{API}/payments/{match_id}/receipt",
            verify=False, timeout=15)
        check("Recibo gerado", r.status_code == 200)
        if r.status_code == 200:
            check("Recibo R$ correto",
                  r.json().get("amount") == 1100.0)

# ===== 6. FORGOT/RESET PASSWORD =====
print("\n[6] Forgot/reset password")
r = requests.post(f"{API}/auth/forgot-password",
    json={"email": EMAIL_SH}, verify=False, timeout=15)
check("/auth/forgot-password 200", r.status_code == 200)
debug_link = r.json().get("debug_reset_link", "")
check("Link de reset em staging", bool(debug_link))

if debug_link and "token=" in debug_link:
    token = debug_link.split("token=")[1]
    NOVA = "outraSenha9876"
    r = requests.post(f"{API}/auth/reset-password",
        json={"token": token, "new_password": NOVA},
        verify=False, timeout=15)
    check("Reset com token valido", r.status_code == 200)

    # Login com nova senha
    r = requests.post(f"{API}/auth/login",
        json={"email": EMAIL_SH, "password": NOVA},
        verify=False, timeout=15)
    check("Login com senha nova", r.status_code == 200)

# ===== 7. SEGURANCA =====
print("\n[7] Seguranca")
# Anti-enumeracao
r1 = requests.post(f"{API}/auth/login",
    json={"email": EMAIL_SH, "password": "errada1234"},
    verify=False, timeout=15).json().get("detail", "")
r2 = requests.post(f"{API}/auth/login",
    json={"email": "nao@existe.com", "password": "errada1234"},
    verify=False, timeout=15).json().get("detail", "")
check("Anti-enumeracao (msg igual)", r1 == r2)

# Token zoado
r = requests.get(f"{API}/auth/me",
    headers={"Authorization": "Bearer fake.token.xyz"},
    verify=False, timeout=15)
check("Token JWT zoado rejeitado", r.status_code == 401)

# Webhook MP sem secret
r = requests.post(f"{API}/payments/webhook/mercado-pago",
    json={}, verify=False, timeout=15)
check("Webhook MP sem signature -> 401",
      r.status_code in (401, 503), f"code={r.status_code}")

# ===== RESUMO =====
print("\n" + "="*70)
ok = sum(1 for _, s, _ in results if s == "OK")
fail = sum(1 for _, s, _ in results if s == "FAIL")
total = len(results)
print(f"RESULTADO: {ok}/{total} OK ({fail} FAIL)")

if fail > 0:
    print("\nFalhas (provavel = deploy nao rolou ainda):")
    for name, s, detail in results:
        if s == "FAIL":
            print(f"  - {name} {detail}")
    print("\nRode: cd C:\\Users\\Admin\\FreteBR; git push origin dev; cd backend; fly deploy -a fretebr-api")
else:
    print("\n*** PROD VALIDADO 100% ***")
    print(f"Frontend: {FRONT}")
    print(f"Backend:  {BASE}")
print()
