# 🗄️ Database Setup - Google OAuth Migration

**Status:** Pronto para executar quando PostgreSQL estiver online

---

## ⚡ Quick Setup

### 1️⃣ Iniciar PostgreSQL

**Windows - pgAdmin ou Serviço:**
```bash
# Se PostgreSQL está instalado como serviço Windows
net start postgresql-x64-15
# ou abrir pgAdmin (ícone na área de trabalho)
```

**Verificar se está rodando:**
```bash
netstat -an | find "5432"
# Deve aparecer: LISTENING
```

### 2️⃣ Criar banco de dados (se não existir)

Abrir pgAdmin ou conectar via psql:

```sql
-- Criar banco
CREATE DATABASE fretebr_db;

-- Criar usuário (se não existir)
CREATE USER fretebr WITH PASSWORD 'fretebr123';

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE fretebr_db TO fretebr;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO fretebr;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO fretebr;
```

### 3️⃣ Executar migration Google OAuth

```bash
cd C:\Users\Admin\FreteBR\backend
python run_migration.py
```

Deve aparecer:
```
[SUCCESS] MIGRATION CONCLUIDA COM SUCESSO!
[OK] password_hash -> nullable
[OK] google_id -> new column (unique)
[OK] foto -> new column
[OK] idx_users_google_id -> new index
[OK] check_auth_method -> new constraint
```

### 4️⃣ Verificar (pgAdmin)

```sql
-- Conectar no banco: fretebr_db
-- Executar:
\d users

-- Deve mostrar:
 google_id | character varying | unique
 foto      | character varying |
```

---

## 📝 Arquivo: .env

Já criado em: `backend/.env`

Contém:
```bash
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-1234567890abcdefghijklmnopqrst
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
DATABASE_URL=postgresql://fretebr:fretebr123@localhost:5432/fretebr_db
```

⚠️ **IMPORTANTE:** Atualizar com valores REAIS quando conseguir do Google Cloud Console

---

## 🔍 Troubleshooting

### Erro: "Connection timed out"
```
PostgreSQL nao esta rodando. Iniciar servico Windows ou pgAdmin.
```

### Erro: "database fretebr_db does not exist"
```
Banco nao foi criado. Executar comandos SQL acima em pgAdmin.
```

### Erro: "role fretebr does not exist"
```
Usuario nao foi criado. Executar comandos SQL acima em pgAdmin.
```

---

## ✅ Checklist

- [ ] PostgreSQL iniciado
- [ ] Banco `fretebr_db` criado
- [ ] Usuário `fretebr` criado
- [ ] Privilégios concedidos
- [ ] `run_migration.py` executado com sucesso
- [ ] Colunas `google_id` e `foto` aparecem em `users`

---

Quando tudo estiver pronto, continue com:
```bash
cd backend
uvicorn app.main:app --reload
```

Documentação completa: `GOOGLE_OAUTH_SETUP.md`
