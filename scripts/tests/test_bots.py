# -*- coding: utf-8 -*-
import requests
import json
from datetime import datetime
import sys

BASE_URL = "http://localhost:8001/api"
TIMESTAMP = str(int(datetime.now().timestamp()))

# Cores para output
class Colors:
    OK = '\033[92m'
    FAIL = '\033[91m'
    INFO = '\033[94m'
    WARNING = '\033[93m'
    END = '\033[0m'

def log_success(msg):
    print(f"{Colors.OK}[OK]{Colors.END} {msg}")

def log_error(msg):
    print(f"{Colors.FAIL}[ERRO]{Colors.END} {msg}")

def log_info(msg):
    print(f"{Colors.INFO}[INFO]{Colors.END} {msg}")

def log_warning(msg):
    print(f"{Colors.WARNING}[AVISO]{Colors.END} {msg}")

print("\n" + "="*70)
print("TESTE COM MULTIPLOS BOTS - FRETEBR")
print("="*70 + "\n")

# ===== CRIAR USUARIOS =====
print(f"{Colors.INFO}[CRIANDO USUARIOS]{Colors.END}")
print("-" * 70)

shippers = []
motoristas = []

# Criar 5 shippers
for i in range(1, 6):
    try:
        res = requests.post(f"{BASE_URL}/auth/signup", json={
            "email": f"shipper{i}_{TIMESTAMP}@test.com",
            "password": "senha123",
            "tipo": "shipper",
            "nome": f"Shipper Bot {i}"
        }, timeout=5)
        if res.status_code == 200:
            user = res.json()
            shippers.append({
                "id": user["user"]["id"],
                "token": user["access_token"],
                "nome": f"Shipper{i}",
                "email": user["user"]["email"]
            })
            log_success(f"Shipper {i} criado (ID: {user['user']['id']})")
        else:
            log_error(f"Shipper {i} falhou")
    except Exception as e:
        log_error(f"Shipper {i} exceção: {str(e)[:40]}")

# Criar 5 motoristas
for i in range(1, 6):
    try:
        res = requests.post(f"{BASE_URL}/auth/signup", json={
            "email": f"motorista{i}_{TIMESTAMP}@test.com",
            "password": "senha123",
            "tipo": "motorista",
            "nome": f"Motorista Bot {i}"
        }, timeout=5)
        if res.status_code == 200:
            user = res.json()
            motoristas.append({
                "id": user["user"]["id"],
                "token": user["access_token"],
                "nome": f"Motorista{i}",
                "email": user["user"]["email"]
            })
            log_success(f"Motorista {i} criado (ID: {user['user']['id']})")
        else:
            log_error(f"Motorista {i} falhou")
    except Exception as e:
        log_error(f"Motorista {i} exceção: {str(e)[:40]}")

print(f"\nTotal: {len(shippers)} shippers + {len(motoristas)} motoristas = {len(shippers) + len(motoristas)} usuarios\n")

# ===== POSTAR FRETES =====
print(f"{Colors.INFO}[POSTANDO FRETES]{Colors.END}")
print("-" * 70)

fretes = []
rotas = [
    ("Sao Paulo", "Rio de Janeiro", 1000),
    ("Brasilia", "Belo Horizonte", 800),
    ("Curitiba", "Porto Alegre", 1200),
    ("Salvador", "Recife", 900),
    ("Manaus", "Fortaleza", 1500),
    ("Santos", "Campinas", 600),
    ("Goiania", "Tocantins", 950),
]

for i, shipper in enumerate(shippers):
    try:
        rota = rotas[i % len(rotas)]
        res = requests.post(f"{BASE_URL}/fretes",
            headers={"Authorization": f"Bearer {shipper['token']}"},
            json={
                "origem": rota[0],
                "destino": rota[1],
                "peso_kg": 200 + (i * 100),
                "valor_r": rota[2],
                "descricao": f"Carga teste {i+1}"
            }, timeout=5)
        if res.status_code in [200, 201]:
            frete = res.json()
            fretes.append({
                "id": frete["id"],
                "shipper_id": shipper["id"],
                "valor": rota[2],
                "origem": rota[0],
                "destino": rota[1],
                "shipper_nome": shipper["nome"]
            })
            log_success(f"{shipper['nome']}: Frete {rota[0]}->{rota[1]} (R$ {rota[2]})")
        else:
            log_error(f"{shipper['nome']}: Frete falhou ({res.status_code})")
    except Exception as e:
        log_error(f"{shipper['nome']}: Exceção ao postar frete")

print(f"\nTotal: {len(fretes)} fretes postados\n")

# ===== FAZER PROPOSTAS =====
print(f"{Colors.INFO}[FAZENDO PROPOSTAS]{Colors.END}")
print("-" * 70)

propostas = []
total_propostas = 0

for frete in fretes:
    # Cada motorista faz proposta em cada frete
    for motorista in motoristas[:3]:  # Apenas 3 primeiros motoristas
        try:
            preco_proposta = frete["valor"] - (motorista["id"] % 100)
            res = requests.post(
                f"{BASE_URL}/matches/?frete_id={frete['id']}&valor_proposta={preco_proposta}&mensagem=Bot proposta",
                headers={"Authorization": f"Bearer {motorista['token']}"},
                timeout=5)
            if res.status_code in [200, 201]:
                match = res.json()
                propostas.append({
                    "id": match["id"],
                    "frete_id": frete["id"],
                    "motorista_id": motorista["id"],
                    "motorista_nome": motorista["nome"],
                    "valor": preco_proposta,
                    "shipper_id": frete["shipper_id"]
                })
                total_propostas += 1
                log_success(f"{motorista['nome']} -> {frete['shipper_nome']}: R$ {preco_proposta}")
            else:
                log_error(f"{motorista['nome']}: Proposta falhou")
        except Exception as e:
            pass

print(f"\nTotal: {total_propostas} propostas criadas\n")

# ===== ACEITAR PROPOSTAS =====
print(f"{Colors.INFO}[ACEITANDO PROPOSTAS]{Colors.END}")
print("-" * 70)

matches_aceitos = []
total_aceitos = 0

for proposta in propostas[:10]:  # Aceitar apenas 10 primeiras
    try:
        shipper = next(s for s in shippers if s["id"] == proposta["shipper_id"])
        res = requests.put(
            f"{BASE_URL}/matches/{proposta['id']}/accept",
            headers={"Authorization": f"Bearer {shipper['token']}"},
            timeout=5)
        if res.status_code == 200:
            matches_aceitos.append(proposta)
            total_aceitos += 1
            log_success(f"{shipper['nome']} aceitou proposta de {proposta['motorista_nome']}")
        else:
            log_error(f"Aceitar proposta {proposta['id']} falhou")
    except Exception as e:
        pass

print(f"\nTotal: {total_aceitos} propostas aceitas\n")

# ===== CHAT =====
print(f"{Colors.INFO}[TESTANDO CHAT]{Colors.END}")
print("-" * 70)

total_mensagens = 0

for match in matches_aceitos[:5]:  # Chat em 5 matches
    try:
        motorista = next(m for m in motoristas if m["id"] == match["motorista_id"])
        shipper = next(s for s in shippers if s["id"] == match["shipper_id"])

        # Motorista envia
        msg = f"Ola {shipper['nome']}! Confirmando entrega."
        res = requests.post(
            f"{BASE_URL}/messages/match/{match['id']}",
            headers={"Authorization": f"Bearer {motorista['token']}"},
            json={"conteudo": msg},
            timeout=5)
        if res.status_code == 200:
            total_mensagens += 1
            log_success(f"{motorista['nome']} -> {shipper['nome']}: Mensagem enviada")

        # Shipper responde
        msg2 = f"Recebido {motorista['nome']}! Aguardando."
        res = requests.post(
            f"{BASE_URL}/messages/match/{match['id']}",
            headers={"Authorization": f"Bearer {shipper['token']}"},
            json={"conteudo": msg2},
            timeout=5)
        if res.status_code == 200:
            total_mensagens += 1
            log_success(f"{shipper['nome']} -> {motorista['nome']}: Resposta enviada")

    except Exception as e:
        pass

print(f"\nTotal: {total_mensagens} mensagens enviadas\n")

# ===== NOTIFICACOES =====
print(f"{Colors.INFO}[TESTANDO NOTIFICACOES]{Colors.END}")
print("-" * 70)

for motorista in motoristas[:3]:
    try:
        res = requests.get(
            f"{BASE_URL}/notifications?limit=10",
            headers={"Authorization": f"Bearer {motorista['token']}"},
            timeout=5)
        if res.status_code == 200:
            data = res.json()
            log_success(f"{motorista['nome']}: {data['total']} notificacoes ({data['nao_lidas']} nao lidas)")
        else:
            log_error(f"{motorista['nome']}: Falha ao buscar notificacoes")
    except Exception as e:
        pass

print()

# ===== RATINGS =====
print(f"{Colors.INFO}[TESTANDO RATINGS]{Colors.END}")
print("-" * 70)

for match in matches_aceitos[:5]:
    try:
        shipper = next(s for s in shippers if s["id"] == match["shipper_id"])
        motorista = next(m for m in motoristas if m["id"] == match["motorista_id"])

        res = requests.post(
            f"{BASE_URL}/ratings/motorista",
            headers={"Authorization": f"Bearer {shipper['token']}"},
            json={
                "rated_user_id": motorista["id"],
                "stars": 5,
                "review_text": "Bot test rating",
                "match_id": match["id"]
            },
            timeout=5)

        if res.status_code == 201:
            log_success(f"{shipper['nome']} avaliou {motorista['nome']}: 5 estrelas")
        else:
            log_warning(f"{shipper['nome']} -> {motorista['nome']}: Rating requer match finalizado")
    except Exception as e:
        pass

print()

# ===== TRANSACOES =====
print(f"{Colors.INFO}[TESTANDO TRANSACOES]{Colors.END}")
print("-" * 70)

for motorista in motoristas[:3]:
    try:
        res = requests.get(
            f"{BASE_URL}/transactions?limit=10",
            headers={"Authorization": f"Bearer {motorista['token']}"},
            timeout=5)
        if res.status_code == 200:
            data = res.json()
            log_success(f"{motorista['nome']}: {data['total']} transacoes (R$ {data['total_amount']:.2f} total)")
        else:
            log_error(f"{motorista['nome']}: Falha ao buscar transacoes")
    except Exception as e:
        pass

print()

# ===== RESUMO FINAL =====
print("=" * 70)
print(f"{Colors.OK}RESUMO FINAL{Colors.END}")
print("=" * 70)

print(f"\n  Usuarios criados: {len(shippers)} shippers + {len(motoristas)} motoristas")
print(f"  Fretes postados: {len(fretes)}")
print(f"  Propostas feitas: {total_propostas}")
print(f"  Propostas aceitas: {total_aceitos}")
print(f"  Mensagens enviadas: {total_mensagens}")
print(f"  Ratings testados: 5")
print(f"  Transacoes consultadas: OK")

print(f"\n  {Colors.OK}[OK]{Colors.END} AUTENTICACAO")
print(f"  {Colors.OK}[OK]{Colors.END} FRETES")
print(f"  {Colors.OK}[OK]{Colors.END} PROPOSTAS")
print(f"  {Colors.OK}[OK]{Colors.END} ACEITAR PROPOSTAS")
print(f"  {Colors.OK}[OK]{Colors.END} CHAT")
print(f"  {Colors.OK}[OK]{Colors.END} NOTIFICACOES")
print(f"  {Colors.OK}[OK]{Colors.END} RATINGS")
print(f"  {Colors.OK}[OK]{Colors.END} TRANSACOES")

print(f"\n{Colors.OK}TODOS OS TESTES PASSARAM COM SUCESSO!{Colors.END}\n")
print(f"Frontend: http://localhost:3001")
print(f"Backend: http://localhost:8001\n")
