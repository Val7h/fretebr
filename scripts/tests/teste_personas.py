# -*- coding: utf-8 -*-
"""
TESTE COMO AGENTES USUARIOS REAIS.

4 personas testam o FreteBR em prod. Foco em UX/friccao, nao smoke tecnico.
Cada acao = um clique/digitacao real. Cada erro virou friccao reportavel.
"""
import requests
import urllib3
import time
from datetime import datetime

urllib3.disable_warnings()

FRONT = "https://fretebr-web.vercel.app"
API = "https://fretebr-api.fly.dev/api"
TS = str(int(datetime.now().timestamp()))

# Frustracao = problemas REAIS que afetariam um usuario
friccao = []
def frustra(persona, descr, severidade="MEDIA"):
    friccao.append((persona, severidade, descr))
    icon = {"BLOCKER": "[X]", "ALTA": "[!]", "MEDIA": "[~]", "BAIXA": "[.]"}.get(severidade, "?")
    print(f"  {icon} {severidade}: {descr}")

def ok(persona, descr):
    print(f"  [OK] {descr}")

def sessao():
    s = requests.Session()
    s.headers.update({"Origin": FRONT})
    s.verify = False
    return s

print("\n" + "="*72)
print("TESTE COMO AGENTES USUARIOS REAIS - 4 PERSONAS")
print("="*72)

# =============================================================
# PERSONA 1: JOAO, 45 ANOS, MOTORISTA EXPERIENTE, ANSIOSO
# =============================================================
print("\n[PERSONA 1] Joao, 45 anos, caminhoneiro 20 anos de estrada.")
print("            Quer ver se vale entrar - so cadastra se for facil.")

j = sessao()

# Joao tenta direto, sem ler nada - usa senha curta
r = j.post(f"{API}/auth/signup", json={
    "email": f"joao_{TS}@gmail.com",
    "password": "123",  # senha muito curta
    "tipo": "motorista",
    "nome": "Joao"  # so primeiro nome
}, timeout=15)
if r.status_code == 200:
    ok("J", "Cadastro aceito (mesmo com senha fraca - VALIDACAO INSUFICIENTE)")
    frustra("J", "Backend aceita senha '123' (sem politica minima)", "ALTA")
    j_token = r.json().get("access_token")
else:
    print(f"  [X] Signup falhou: {r.status_code} - {r.text[:100]}")
    j_token = None

# Joao quer ver fretes ANTES de configurar perfil
r = j.get(f"{API}/fretes", timeout=15)
if r.status_code == 200:
    fretes = r.json() if isinstance(r.json(), list) else r.json().get("fretes", [])
    if len(fretes) > 0:
        ok("J", f"Encontrou {len(fretes)} fretes disponiveis")
    else:
        frustra("J", "ZERO fretes no app - usuario abandona ('isso aqui ta vazio')", "BLOCKER")

# Joao tenta postar um frete (motorista nao pode - mas a UX deixa claro?)
r = j.post(f"{API}/fretes", json={
    "origem": "SP", "destino": "RJ", "peso_kg": 100,
    "valor_r": 500, "descricao": "test"
}, timeout=15)
if r.status_code == 403:
    msg = r.json().get("detail", "")
    if "shipper" in msg.lower() or "transportador" in msg.lower():
        ok("J", f"Bloqueado corretamente: {msg[:80]}")
    else:
        frustra("J", f"403 mas mensagem nao explica o motivo: '{msg[:80]}'", "MEDIA")
elif r.status_code == 200 or r.status_code == 201:
    frustra("J", "Motorista CONSEGUIU postar frete - falha grave de permissao", "BLOCKER")
else:
    frustra("J", f"Erro inesperado {r.status_code}: {r.text[:80]}", "ALTA")

# Joao tenta fazer proposta em frete inexistente (clicou em algo zoado)
r = j.post(f"{API}/matches/?frete_id=99999&valor_proposta=100", timeout=15)
if r.status_code == 404:
    ok("J", "Frete inexistente da 404 (correto)")
elif r.status_code >= 500:
    frustra("J", f"Erro 500 ao tentar frete inexistente (deveria ser 404): {r.status_code}", "ALTA")

# =============================================================
# PERSONA 2: MARCIA, 38 ANOS, LOJISTA, PRECISA URGENTE
# =============================================================
print("\n[PERSONA 2] Marcia, 38 anos, dona de loja de moveis.")
print("            Precisa entregar 2 sofas AMANHA. Tem pressa.")

m = sessao()

# Marcia cadastra como shipper (rapido)
r = m.post(f"{API}/auth/signup", json={
    "email": f"marcia_lojas_{TS}@email.com",
    "password": "senha_mais_forte_2026",
    "tipo": "shipper",
    "nome": "Marcia Silva Lojas"
}, timeout=15)
if r.status_code == 200:
    ok("M", "Cadastrou rapido")
    m_token = r.json().get("access_token")
else:
    print(f"  [X] {r.status_code}")
    m_token = None

# Marcia tenta postar frete SEM preencher campos obrigatorios
r = m.post(f"{API}/fretes", json={
    "origem": "Sao Paulo",
    # esqueceu destino, peso, valor
}, timeout=15)
if r.status_code in (400, 422):
    err = r.json()
    if isinstance(err.get("detail"), list):
        fields_missing = [e.get("loc", ["?"])[-1] for e in err["detail"]]
        ok("M", f"Validacao indica campos faltantes: {fields_missing[:3]}")
    else:
        msg = str(err.get("detail", ""))[:80]
        if any(w in msg.lower() for w in ["destino", "peso", "valor", "required", "field"]):
            ok("M", f"Erro claro: {msg}")
        else:
            frustra("M", f"Erro generico ao validar: '{msg}' - usuaria fica perdida", "ALTA")
elif r.status_code >= 500:
    frustra("M", f"500 com campos faltantes (deveria ser 400/422)", "BLOCKER")

# Marcia posta frete corretamente
r = m.post(f"{API}/fretes", json={
    "origem": "Sao Paulo - Vila Madalena",
    "destino": "Rio de Janeiro - Copacabana",
    "peso_kg": 80,
    "valor_r": 2000,
    "descricao": "2 sofas de couro - URGENTE entrega amanha"
}, timeout=15)
if r.status_code in (200, 201):
    frete_marcia = r.json().get("id")
    ok("M", f"Frete postado (ID {frete_marcia})")
else:
    print(f"  [X] Postagem falhou: {r.status_code} - {r.text[:100]}")
    frete_marcia = None

# Marcia tenta postar frete com VALOR NEGATIVO
r = m.post(f"{API}/fretes", json={
    "origem": "A", "destino": "B", "peso_kg": 10, "valor_r": -500, "descricao": "x"
}, timeout=15)
if r.status_code in (400, 422):
    ok("M", "Valor negativo bloqueado")
else:
    frustra("M", f"Frete com valor NEGATIVO foi {r.status_code} - aceita lixo!", "ALTA")

# Marcia tenta postar frete com peso ZERO
r = m.post(f"{API}/fretes", json={
    "origem": "A", "destino": "B", "peso_kg": 0, "valor_r": 100, "descricao": "x"
}, timeout=15)
if r.status_code in (400, 422):
    ok("M", "Peso zero bloqueado")
elif r.status_code in (200, 201):
    frustra("M", "Peso ZERO foi aceito - cria fretes invalidos", "MEDIA")

# =============================================================
# PERSONA 3: 3 MOTORISTAS DISPUTAM O FRETE DA MARCIA
# =============================================================
print("\n[PERSONA 3] 3 motoristas (Carlos, Bruno, Daniel) propoem ao mesmo tempo")
if frete_marcia:
    cb = sessao(); cb.post(f"{API}/auth/signup", json={
        "email": f"carlos_{TS}@x.com", "password": "carlos2026", "tipo": "motorista", "nome": "Carlos"
    }, timeout=15)
    bb = sessao(); bb.post(f"{API}/auth/signup", json={
        "email": f"bruno_{TS}@x.com", "password": "bruno2026", "tipo": "motorista", "nome": "Bruno"
    }, timeout=15)
    db = sessao(); db.post(f"{API}/auth/signup", json={
        "email": f"daniel_{TS}@x.com", "password": "daniel2026", "tipo": "motorista", "nome": "Daniel"
    }, timeout=15)

    # Todos propoem proximos no tempo (Carlos: 1900, Bruno: 1850, Daniel: 2100)
    rc = cb.post(f"{API}/matches/?frete_id={frete_marcia}&valor_proposta=1900&mensagem=Saio amanha cedo, refrigerado", timeout=15)
    rb = bb.post(f"{API}/matches/?frete_id={frete_marcia}&valor_proposta=1850&mensagem=Tenho 4 caminhoes, pegamos na hora", timeout=15)
    rd = db.post(f"{API}/matches/?frete_id={frete_marcia}&valor_proposta=2100&mensagem=Seguro completo + GPS tempo real", timeout=15)

    propostas_ok = sum(1 for r in [rc, rb, rd] if r.status_code in (200, 201))
    if propostas_ok == 3:
        ok("3M", "Todas 3 propostas aceitas")
    else:
        frustra("3M", f"Apenas {propostas_ok}/3 propostas aceitas - race condition?", "ALTA")

    match_carlos = rc.json().get("id") if rc.status_code in (200, 201) else None
    match_bruno = rb.json().get("id") if rb.status_code in (200, 201) else None
    match_daniel = rd.json().get("id") if rd.status_code in (200, 201) else None

    # Marcia ve as 3 propostas
    r = m.get(f"{API}/matches/frete/{frete_marcia}", timeout=15)
    if r.status_code == 200:
        props = r.json() if isinstance(r.json(), list) else r.json().get("propostas", [])
        if len(props) >= 3:
            ok("M", f"Marcia ve as {len(props)} propostas")
        else:
            frustra("M", f"Marcia ve so {len(props)} de 3 propostas - sumiram!", "BLOCKER")

    # Marcia aceita a do Bruno (mais barato)
    if match_bruno:
        r = m.put(f"{API}/matches/{match_bruno}/accept", timeout=15)
        if r.status_code == 200:
            ok("M", "Aceitou proposta de Bruno (R$1850)")

            # Carlos e Daniel devem ser AUTOMATICAMENTE rejeitados
            time.sleep(0.5)
            r = m.get(f"{API}/matches/frete/{frete_marcia}", timeout=15)
            props = r.json() if isinstance(r.json(), list) else r.json().get("propostas", [])
            aceitas = [p for p in props if p.get("status") == "aceito"]
            rejeitadas = [p for p in props if p.get("status") == "rejeitado"]
            if len(aceitas) == 1 and len(rejeitadas) == 2:
                ok("M", "Outras 2 propostas auto-rejeitadas (correto)")
            else:
                frustra("M",
                    f"Apos aceitar: {len(aceitas)} aceitas, {len(rejeitadas)} rejeitadas (esperava 1+2)",
                    "ALTA")

    # Carlos tenta enviar mensagem mesmo apos sua proposta ser rejeitada
    if match_carlos:
        r = cb.post(f"{API}/messages/match/{match_carlos}",
            json={"conteudo": "Por que rejeitou? Posso baixar pra 1700"}, timeout=15)
        if r.status_code in (400, 403):
            ok("C", "Carlos bloqueado de chatear apos rejeicao")
        else:
            frustra("C",
                "Carlos com proposta rejeitada CONSEGUIU mandar mensagem - shipper sera spam'ado",
                "MEDIA")

# =============================================================
# PERSONA 4: ATACANTE TESTA SEGURANCA
# =============================================================
print("\n[PERSONA 4] Eve (atacante) - testa autorizacao e edge cases")

eve = sessao()
r = eve.post(f"{API}/auth/signup", json={
    "email": f"eve_{TS}@evil.com",
    "password": "eve2026hacker",
    "tipo": "motorista",
    "nome": "Eve"
}, timeout=15)
eve_id = r.json().get("user", {}).get("id") if r.status_code == 200 else None

if frete_marcia:
    # Eve tenta ver propostas do frete da Marcia (que nao eh dela)
    r = eve.get(f"{API}/matches/frete/{frete_marcia}", timeout=15)
    if r.status_code == 403:
        ok("E", "Bloqueada de ver propostas alheias (403)")
    elif r.status_code == 200:
        props = r.json()
        if isinstance(props, list) and len(props) > 0:
            frustra("E",
                "[ALERTA] VAZAMENTO: Eve vê propostas de frete que nao eh dela!",
                "BLOCKER")
        else:
            ok("E", "200 mas sem dados (provavelmente lista vazia - OK)")

    # Eve tenta aceitar uma proposta que nao eh sua
    if match_bruno:
        r = eve.put(f"{API}/matches/{match_bruno}/accept", timeout=15)
        if r.status_code == 403:
            ok("E", "Bloqueada de aceitar proposta alheia (403)")
        else:
            frustra("E",
                f"[ALERTA] BLOCKER: Eve aceitou proposta alheia (code {r.status_code})",
                "BLOCKER")

# Eve tenta brute force no login (rate limit ativa?)
print("  [Eve testa rate limit no login com 6 tentativas erradas]")
attempts = 0
for i in range(6):
    r = eve.post(f"{API}/auth/login", json={
        "email": "victima@test.com",
        "password": f"chute_{i}"
    }, timeout=15)
    attempts += 1
    if r.status_code == 429:
        ok("E", f"Rate limit ATIVOU apos {i+1} tentativas (slowapi funciona)")
        break
else:
    frustra("E", f"6 tentativas de login sem rate limit - vulneravel a brute force", "ALTA")

# Eve tenta SQL injection no email
r = eve.post(f"{API}/auth/login", json={
    "email": "' OR '1'='1",
    "password": "x"
}, timeout=15)
if r.status_code in (401, 400, 422, 429):
    ok("E", f"SQLi no login bloqueado ({r.status_code})")
else:
    frustra("E", f"SQLi retornou {r.status_code} - investigar", "ALTA")

# Eve tenta token JWT invalido
eve_bad = sessao()
eve_bad.headers["Authorization"] = "Bearer fake.token.here"
r = eve_bad.get(f"{API}/auth/me", timeout=15)
if r.status_code == 401:
    ok("E", "Token JWT invalido rejeitado (401)")
else:
    frustra("E", f"Token JWT lixo retornou {r.status_code}", "ALTA")

# =============================================================
# RELATORIO FINAL
# =============================================================
print("\n" + "="*72)
print("RELATORIO DE UX/SEGURANCA - VISAO DOS USUARIOS")
print("="*72)

blockers = [(p, d) for p, s, d in friccao if s == "BLOCKER"]
altas = [(p, d) for p, s, d in friccao if s == "ALTA"]
medias = [(p, d) for p, s, d in friccao if s == "MEDIA"]
baixas = [(p, d) for p, s, d in friccao if s == "BAIXA"]

print(f"\nTotal de friccoes encontradas: {len(friccao)}")
print(f"  [X] BLOCKER (impede uso): {len(blockers)}")
print(f"  [!] ALTA (afeta UX seria): {len(altas)}")
print(f"  [~] MEDIA (irrita): {len(medias)}")
print(f"  [.] BAIXA (perfeccionismo): {len(baixas)}")

if blockers:
    print("\n=== [X] BLOCKERS (impedem usuario de usar) ===")
    for p, d in blockers:
        print(f"  [{p}] {d}")

if altas:
    print("\n=== [!] ALTA (afeta retencao) ===")
    for p, d in altas:
        print(f"  [{p}] {d}")

if medias:
    print("\n=== [~] MEDIA (gera reclamacao) ===")
    for p, d in medias:
        print(f"  [{p}] {d}")

# Avaliacao de prontidao
if len(blockers) == 0 and len(altas) <= 2:
    print("\n[OK] VEREDITO: Pronto pro beta - friccoes sao melhorias, nao bloqueios")
elif len(blockers) == 0:
    print(f"\n[!]  VEREDITO: Pronto pro beta com {len(altas)} ressalvas serias - documente pros usuarios")
else:
    print(f"\n[X] VEREDITO: {len(blockers)} BLOCKERS - corrigir antes de convidar usuarios")

print()
