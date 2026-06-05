# FreteBR - Marketplace de Fretes Brasileiro

FreteBR é um marketplace para conectar motoristas e shippers em um sistema de fretes rápido e seguro.

## Stack Tech

- **Backend**: FastAPI (Python)
- **Frontend**: React/Next.js (Next)
- **Database**: PostgreSQL
- **Docker**: Docker Compose

## Estrutura do Projeto

```
fretebr/
├── backend/          # API FastAPI
│   ├── app/
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── crud/     # Database operations
│   │   ├── api/      # API endpoints
│   │   └── main.py   # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/         # React/Next.js app
├── docker-compose.yml
└── README.md
```

## Setup Local

### Pré-requisitos
- Python 3.11+
- PostgreSQL 14+
- Docker & Docker Compose

### Instalação (sem Docker)

1. Clone o repositório:
```bash
git clone https://github.com/Val7h/fretebr.git
cd fretebr
```

2. Configure o backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
cp .env.example .env
pip install -r requirements.txt
```

3. Inicie o servidor:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API estará disponível em: http://localhost:8000

### Com Docker Compose

```bash
docker-compose up
```

- Backend: http://localhost:8000
- Database: localhost:5432

## API Endpoints

### Auth
- `POST /api/auth/signup` - Registrar novo usuário
- `POST /api/auth/login` - Login e obter JWT token
- `GET /api/auth/me` - Obter dados do usuário logado

### Health
- `GET /health` - Health check

## Documentação da API

Acesse a documentação interativa em: http://localhost:8000/docs

## Branches

- `main` - Produção
- `dev` - Desenvolvimento
- `feature/*` - Features em desenvolvimento

## Status

🚀 Em desenvolvimento - Semana 1: Backend Setup

## Autor

Valth Menezes Guimarães (Val7h)

## Licença

Proprietary - FreteBR
