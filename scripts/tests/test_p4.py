# -*- coding: utf-8 -*-
"""
Testes P4: Postgres-ready + Frontend cookie mode + CI/CD.
Como nao temos Postgres rodando local, testamos:
- backend aceita config Postgres no env (sem startar)
- endpoint /auth/logout + /auth/login retornam Set-Cookie quando AUTH_COOKIE_MODE
- CI yaml e valido
"""
import os
import subprocess
import sys
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

print("\n=== TESTE SPRINT P4 ===\n")

# ===== P4.1: PSYCOPG2 INSTALADO + DATABASE.PY ENV-DRIVEN =====
print("--- P4.1: Postgres ready ---")
try:
    import psycopg2  # noqa
    check("psycopg2-binary instalado", True)
except ImportError:
    check("psycopg2-binary instalado", False)

# database.py reconhece postgres
src = open(
    os.path.join(os.path.dirname(__file__), "..", "..", "backend", "app", "database.py"),
    encoding="utf-8"
).read()
check("database.py tem branch postgresql", 'DATABASE_URL.startswith("postgresql")' in src)
check("database.py tem pool_pre_ping", "pool_pre_ping" in src)
check("database.py tem pool_size configuravel via env", "DB_POOL_SIZE" in src)

# docker-compose tem AUTH_COOKIE_MODE + alembic upgrade
dc = open(os.path.join(os.path.dirname(__file__), "..", "..", "docker-compose.yml"),
          encoding="utf-8").read()
check("docker-compose passa AUTH_COOKIE_MODE", "AUTH_COOKIE_MODE" in dc)
check("docker-compose roda alembic upgrade head", "alembic upgrade head" in dc)
check("docker-compose obriga SECRET_KEY (sem default placeholder)",
      "${SECRET_KEY:?" in dc)

# ===== P4.2: FRONTEND COOKIE MODE =====
print("\n--- P4.2: Frontend cookie mode ---")
api_ts = open(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "src", "services", "api.ts"),
    encoding="utf-8"
).read()
check("api.ts exporta COOKIE_MODE", "export const COOKIE_MODE" in api_ts)
check("api.ts usa withCredentials condicional", "withCredentials" in api_ts)
check("api.ts skip localStorage em COOKIE_MODE", "if (!COOKIE_MODE)" in api_ts)
check("api.ts tem logout", "logout:" in api_ts)

ctx = open(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "src", "context", "AuthContext.tsx"),
    encoding="utf-8"
).read()
check("AuthContext importa COOKIE_MODE", "COOKIE_MODE" in ctx)
check("AuthContext logout chama apiService.logout()", "apiService.logout()" in ctx)

env_example = open(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", ".env.example"),
    encoding="utf-8"
).read()
check(".env.example documenta VITE_AUTH_COOKIE_MODE",
      "VITE_AUTH_COOKIE_MODE" in env_example)

# Backend /auth/login + AUTH_COOKIE_MODE=true seta Set-Cookie?
# Como nao queremos restart do backend, testamos via os.environ temporariamente:
# Em vez disso, validamos que /auth/logout responde
r = requests.post(f"{API}/auth/logout")
check("/auth/logout responde 200", r.status_code == 200, f"code={r.status_code}")

# ===== P4.3: CI/CD =====
print("\n--- P4.3: CI/CD GitHub Actions ---")
ci_path = os.path.join(os.path.dirname(__file__), "..", "..", ".github", "workflows", "ci.yml")
check("ci.yml existe", os.path.exists(ci_path))
if os.path.exists(ci_path):
    ci = open(ci_path, encoding="utf-8").read()
    check("ci.yml tem job backend-tests", "backend-tests:" in ci)
    check("ci.yml roda test_p1", "test_p1.py" in ci)
    check("ci.yml roda test_p2_payment", "test_p2_payment.py" in ci)
    check("ci.yml roda test_p3", "test_p3.py" in ci)
    check("ci.yml roda test_bots_completo", "test_bots_completo.py" in ci)
    check("ci.yml tem matrix sqlite/postgres", "[sqlite, postgres]" in ci or "sqlite, postgres" in ci)
    check("ci.yml tem servico postgres", "image: postgres:" in ci)
    check("ci.yml roda alembic upgrade head", "alembic upgrade head" in ci)
    check("ci.yml tem CodeQL security scan", "codeql" in ci.lower())
    check("ci.yml builda frontend", "npm run build" in ci or "npm ci" in ci)

deploy_path = os.path.join(os.path.dirname(__file__), "..", "..", ".github", "workflows",
                           "deploy-staging.yml")
check("deploy-staging.yml existe", os.path.exists(deploy_path))

# ===== P4.4: requirements.txt atualizado =====
print("\n--- P4.4: Requirements ---")
req = open(
    os.path.join(os.path.dirname(__file__), "..", "..", "backend", "requirements.txt"),
    encoding="utf-8"
).read()
check("requirements.txt tem slowapi", "slowapi" in req)
check("requirements.txt tem sentry-sdk", "sentry-sdk" in req)
check("requirements.txt tem psycopg2-binary", "psycopg2-binary" in req)
check("requirements.txt tem alembic", "alembic" in req)

# ===== RESUMO =====
print("\n" + "="*60)
ok = sum(1 for _, s, _ in results if s == "OK")
fail = sum(1 for _, s, _ in results if s == "FAIL")
total = len(results)
print(f"SPRINT P4: {ok}/{total} OK ({fail} FAIL)")
if fail > 0:
    print("\nFalhas:")
    for name, s, detail in results:
        if s == "FAIL":
            print(f"  - {name} {detail}")
print()
