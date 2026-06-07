# Alembic Migrations - FreteBR

## Setup inicial (já feito)
```bash
python -m alembic init -t generic alembic
python -m alembic revision --autogenerate -m "initial schema"
python -m alembic stamp head    # marca DB existente como migrado
```

## Comandos comuns

### Gerar nova migration após mudar models
```bash
python -m alembic revision --autogenerate -m "descricao curta"
```

### Aplicar migrations pendentes
```bash
python -m alembic upgrade head
```

### Rollback uma migration
```bash
python -m alembic downgrade -1
```

### Ver versão atual
```bash
python -m alembic current
```

### Ver histórico
```bash
python -m alembic history
```

## DATABASE_URL

`env.py` lê `os.getenv("DATABASE_URL")` com fallback `sqlite:///./fretebr.db`.

Para Postgres:
```bash
export DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/fretebr"
python -m alembic upgrade head
```

## Notas

- `app/main.py` ainda chama `Base.metadata.create_all()` no startup.
  Após estabilizar Alembic em todos ambientes, **remover** essa linha e
  rodar `alembic upgrade head` no deploy.
- `target_metadata = Base.metadata` em `env.py` reflete todos models
  registrados em `app/models/__init__.py`.
