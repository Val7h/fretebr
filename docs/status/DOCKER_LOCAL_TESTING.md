# Docker Compose Local Testing - FreteBR

## Status: SEGUNDA 06/JUNHO - DevOps Setup

### 1. Setup Completo

Arquivos criados:
- ✅ `docker-compose.yml` - Orquestração de 3 serviços
- ✅ `backend/Dockerfile` - FastAPI image
- ✅ `frontend/Dockerfile` - React/Vite image
- ✅ `frontend/package.json` - Dependências Node
- ✅ `.env.example` - Template de variáveis
- ✅ `.env` - Arquivo local de desenvolvimento
- ✅ `.gitignore` - Exclusões de versionamento

### 2. Estrutura docker-compose.yml

**Serviços:**
1. `db` (postgres:14-alpine)
   - Database: fretebr
   - User: fretebr_user
   - Port: 5432
   - Volume: postgres_data

2. `backend` (FastAPI)
   - Build: ./backend
   - Port: 8000:8000
   - Depends on: db (service_healthy)
   - Volumes: ./backend (reload mode)
   - Health check: curl /health

3. `frontend` (React/Vite)
   - Build: ./frontend
   - Port: 3000:3000
   - Depends on: backend
   - Health check: wget

### 3. Variáveis de Ambiente

Root `.env`:
```
POSTGRES_DB=fretebr
POSTGRES_USER=fretebr_user
POSTGRES_PASSWORD=dev_password_local_123
DATABASE_URL=postgresql://fretebr_user:dev_password_local_123@db:5432/fretebr
SECRET_KEY=dev_secret_key_development_minimo_32_caracteres_123456
```

### 4. Como Usar

```bash
# Subir containers
docker-compose up --build

# Em outro terminal
# Verificar status
docker-compose ps

# Logs
docker-compose logs -f backend
docker-compose logs -f db
docker-compose logs -f frontend

# Stop
docker-compose down
docker-compose down -v  # Remove volumes também
```

### 5. Testes Planejados (QUARTA)

- ✅ Backend health check: `curl http://localhost:8000/health`
- ✅ Frontend loads: `curl http://localhost:3000`
- ✅ Database responsive: `docker-compose exec db psql -U fretebr_user -d fretebr -c "SELECT 1"`
- ✅ Auth flow end-to-end
- ✅ Signup/Login/JWT verification

### 6. Status Atual

🟡 **docker-compose up --build** em andamento...
- Pulling postgres:14-alpine
- Building backend image (python:3.11-slim)
- Building frontend image (node:20-alpine)

Próximo passo: Monitorar build completion e fazer testes básicos.
