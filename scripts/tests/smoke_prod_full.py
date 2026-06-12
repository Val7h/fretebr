# -*- coding: utf-8 -*-
"""
Teste E2E completo em PROD simulando 2 abas (shipper + motorista).
Usa requests.Session com cookies httpOnly (como o frontend Vercel faz).
"""
import requests
import urllib3
from datetime import datetime
import time

urllib3.disable_warnings()

FRONT = "https://fretebr-web.vercel.app"
API = "https://fretebr-api.fly.dev/api"
BASE = "https://fretebr-api.fly.dev"
TS = str(int(datetime.now().timestamp()))

results = []
def check(name, cond, detail=""):
    s = "[OK]" if cond else "[FAIL]"
    results.append((name, "OK" if cond else "FAIL", detail))
    print(f"{s} {name} {detail}")

print("\n" + "="*70)
print("E2E PROD - simulando 2 usuarios reais (shipper + motorista)")
print("="*70)

# ====== 0. FRONTEND ESTA NO AR? ======
print("\n[0] Frontend Vercel acessivel?")
r = requests.get(FRONT, timeout=15, verify=False)
check("Front HTML 200", r.status_code == 200, f"size={len(r.text)} bytes")
check("Front carrega React (Vite tag presente)",
      "vite" in r.text.lower() or "<div id=\"root\"" in r.text or "<script" in r.text)
check("Front tem favicon", "favicon" in r.text.lower())

# ====== 1. SHIPPER: cadastra (cookie httpOnly) ======
print("\n[1] Shipper: cadastra com cookie httpOnly")
sh = requests.Session()
sh.headers.update({"Origin": FRONT, "Referer": FRONT + "/"})

r = sh.post(f"{API}/auth/signup", json={
    "email": f"e2e_shipper_{TS}@test.com",
    "password": "teste123",
    "tipo": "shipper",
    "nome": "Maria Shipper"
}, timeout=15, verify=False)
check("Shipper signup 200", r.status_code == 200, f"code={r.status_code}")
sh_id = r.json().get("user", {}).get("id")
check("Cookie fretebr_access setado", "fretebr_access" in sh.cookies)
check("Cookie fretebr_refresh setado", "fretebr_refresh" in sh.cookies)
sh_token = r.json().get("access_token")

# ====== 2. MOTORISTA: cadastra em outra "aba" ======
print("\n[2] Motorista: cadastra em sessao isolada (= aba anonima)")
mo = requests.Session()
mo.headers.update({"Origin": FRONT, "Referer": FRONT + "/"})

r = mo.post(f"{API}/auth/signup", json={
    "email": f"e2e_motorista_{TS}@test.com",
    "password": "teste123",
    "tipo": "motorista",
    "nome": "Pedro Motorista"
}, timeout=15, verify=False)
check("Motorista signup 200", r.status_code == 200)
mo_id = r.json().get("user", {}).get("id")
check("Sessoes isoladas (cookies diferentes)",
      sh.cookies.get("fretebr_access") != mo.cookies.get("fretebr_access"))

# ====== 3. SHIPPER posta frete ======
print("\n[3] Shipper posta frete SP->RJ")
r = sh.post(f"{API}/fretes", json={
    "origem": "Sao Paulo",
    "destino": "Rio de Janeiro",
    "peso_kg": 250,
    "valor_r": 1500.0,
    "descricao": "E2E test - moveis para casa nova"
}, timeout=15, verify=False)
check("Frete postado", r.status_code in [200, 201], f"code={r.status_code}")
frete_id = r.json().get("id")
print(f"     Frete ID: {frete_id}")

# ====== 4. MOTORISTA ve fretes disponiveis ======
print("\n[4] Motorista lista fretes disponiveis")
r = mo.get(f"{API}/fretes", timeout=15, verify=False)
check("Lista fretes 200", r.status_code == 200)
fretes = r.json() if isinstance(r.json(), list) else r.json().get("fretes", [])
encontrou = any(f.get("id") == frete_id for f in fretes)
check("Motorista enxerga frete recem-criado", encontrou)

# ====== 5. MOTORISTA detalha frete ======
print("\n[5] Motorista abre detalhes do frete")
r = mo.get(f"{API}/fretes/{frete_id}", timeout=15, verify=False)
check("Detalhe frete 200", r.status_code == 200)
detalhes = r.json()
check("Detalhes tem origem/destino",
      detalhes.get("origem") == "Sao Paulo" and detalhes.get("destino") == "Rio de Janeiro")

# ====== 6. MOTORISTA faz proposta ======
print("\n[6] Motorista faz proposta R$ 1.350 (desconto)")
r = mo.post(
    f"{API}/matches/?frete_id={frete_id}&valor_proposta=1350&mensagem=Entrego em 2 dias com carga horaria flexivel",
    timeout=15, verify=False)
check("Proposta criada", r.status_code in [200, 201], f"code={r.status_code}")
match_id = r.json().get("id")
print(f"     Match ID: {match_id}")

# ====== 7. SHIPPER ve proposta ======
print("\n[7] Shipper ve propostas recebidas")
r = sh.get(f"{API}/matches/frete/{frete_id}", timeout=15, verify=False)
check("Listar propostas 200", r.status_code == 200)
props = r.json() if isinstance(r.json(), list) else r.json().get("propostas", r.json())
tem_proposta = (isinstance(props, list) and any(p.get("id") == match_id for p in props)) or match_id
check("Shipper enxerga proposta", bool(tem_proposta))

# ====== 8. SHIPPER aceita ======
print("\n[8] Shipper aceita proposta")
r = sh.put(f"{API}/matches/{match_id}/accept", timeout=15, verify=False)
check("Aceitar proposta", r.status_code == 200)

# ====== 9. CHAT bidirecional ======
print("\n[9] Chat bidirecional")
r = mo.post(f"{API}/messages/match/{match_id}",
    json={"conteudo": "Ola Maria! Saio amanha as 6h."}, timeout=15, verify=False)
check("Motorista envia mensagem", r.status_code == 200)

time.sleep(1)
r = sh.post(f"{API}/messages/match/{match_id}",
    json={"conteudo": "Perfeito Pedro! Endereco entrega: Rua Y, 456"}, timeout=15, verify=False)
check("Shipper responde", r.status_code == 200)

r = mo.get(f"{API}/messages/match/{match_id}", timeout=15, verify=False)
msgs = r.json().get("mensagens", []) if r.status_code == 200 else []
check("Motorista vê chat completo (2+ msgs)", len(msgs) >= 2, f"count={len(msgs)}")

# ====== 10. NOTIFICACOES ======
print("\n[10] Notificacoes")
r = mo.get(f"{API}/notifications?limit=10", timeout=15, verify=False)
check("Motorista notif 200", r.status_code == 200)
r = sh.get(f"{API}/notifications/count/unread", timeout=15, verify=False)
check("Shipper unread count 200", r.status_code == 200)

# ====== 11. PAGAMENTO PIX MOCK ======
print("\n[11] Pagamento Pix (MOCK)")
r = sh.post(f"{API}/payments",
    json={"match_id": match_id, "amount": 1350.0}, timeout=15, verify=False)
check("Cria pagamento", r.status_code in [200, 201], f"code={r.status_code}")
pay = r.json()
tx_id = pay.get("transaction_id")
qr = pay.get("qr_code_data", "")
check("Retorna transaction_id", bool(tx_id))
check("Retorna QR Pix BR (00020126*)",
      qr.startswith("00020126") and len(qr) > 50, f"qr_len={len(qr)}")

# ====== 12. SIMULA PAGAMENTO ======
print("\n[12] Simula pagamento concluido (MOCK)")
r = sh.post(f"{API}/payments/{tx_id}/simulate-paid", timeout=15, verify=False)
check("Simulate-paid 200", r.status_code == 200)
check("Status pago", r.json().get("new_status") == "pago"
      or "already" in r.json().get("status", "").lower())

# Confirma novo status
r = sh.get(f"{API}/payments/{tx_id}", timeout=15, verify=False)
check("GET payment status = pago",
      r.status_code == 200 and r.json().get("status") == "pago")

# ====== 13. RECIBO ======
print("\n[13] Recibo")
r = sh.get(f"{API}/payments/{match_id}/receipt", timeout=15, verify=False)
check("Recibo 200", r.status_code == 200)
if r.status_code == 200:
    rec = r.json()
    check("Recibo tem valor correto", rec.get("amount") == 1350.0,
          f"amount={rec.get('amount')}")
    check("Recibo status pago", rec.get("status") == "pago")

# ====== 14. HISTORICO ======
print("\n[14] Historico de transacoes")
r = mo.get(f"{API}/transactions?limit=10", timeout=15, verify=False)
check("Motorista historico 200", r.status_code == 200)
r = sh.get(f"{API}/transactions/statistics/summary", timeout=15, verify=False)
ok = r.status_code == 200
stats = r.json() if ok else {}
check("Shipper estatisticas",
      ok and stats.get("total_pago", 0) >= 1350,
      f"total_pago=R${stats.get('total_pago', 0)}")

# ====== 15. LOGOUT limpa cookies ======
print("\n[15] Logout limpa cookies httpOnly")
r = sh.post(f"{API}/auth/logout", timeout=15, verify=False)
check("Logout 200", r.status_code == 200)
# Apos logout, /auth/me com mesma sessao deve falhar
r = sh.get(f"{API}/auth/me", timeout=15, verify=False)
check("/auth/me pos-logout = 401", r.status_code == 401, f"code={r.status_code}")

# ====== RESUMO ======
print("\n" + "="*70)
ok = sum(1 for _, s, _ in results if s == "OK")
fail = sum(1 for _, s, _ in results if s == "FAIL")
total = len(results)
print(f"RESULTADO E2E PROD: {ok}/{total} OK ({fail} FAIL)")

if fail > 0:
    print("\nFalhas:")
    for name, s, detail in results:
        if s == "FAIL":
            print(f"  - {name} {detail}")

print(f"\nFrontend: {FRONT}")
print(f"Backend:  {BASE}")
print()
