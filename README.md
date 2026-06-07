# FreteBR - Marketplace de Fretes Brasileiro

Plataforma para conectar motoristas (caminhoneiros) e shippers (embarcadores) com matching, chat, pagamentos e avaliações.

## Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Next.js / React
- **Database**: PostgreSQL (prod) / SQLite (dev)
- **Auth**: JWT + Google OAuth

## Como rodar

### Backend (porta 8001)

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

API: http://localhost:8001
Docs (Swagger): http://localhost:8001/docs

### Frontend (porta 3001)

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:3001

### Docker Compose

```bash
docker-compose up
```

## Features implementadas

- Autenticação (signup, login, JWT, Google OAuth)
- Cadastro e perfil de motoristas e shippers
- Publicação de cargas e matching com motoristas
- Chat entre partes
- Sistema de avaliações (rating)
- Pagamentos integrados
- Programa de indicações (referral)
- Integração com postos de combustível

## Estrutura

```
FreteBR/
├── backend/            # API FastAPI
├── frontend/           # App Next.js
├── docs/               # Documentação
│   └── status/         # Histórico de relatórios e status
├── scripts/
│   └── tests/          # Scripts de teste manual / E2E
├── tests/              # Testes automatizados
├── docker-compose.yml
└── README.md
```

## Autor

Valth Menezes Guimarães (Val7h)

## Licença

Proprietary - FreteBR
