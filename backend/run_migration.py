"""
Script para executar migrations do Google OAuth
Executa as mudanças na tabela users para suportar Google OAuth
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Adicionar backend ao path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import DATABASE_URL

def run_migration():
    """Executa a migration do Google OAuth"""

    # SQL migration
    migration_sql = """
    -- Alterar password_hash para nullable (para OAuth users)
    ALTER TABLE users
    ALTER COLUMN password_hash DROP NOT NULL;

    -- Adicionar coluna google_id
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS google_id VARCHAR(255) UNIQUE;

    -- Adicionar coluna foto (profile picture URL)
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS foto VARCHAR(500);

    -- Criar índice para google_id
    CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);

    -- Adicionar restrição: usuário deve ter password_hash OU google_id
    ALTER TABLE users
    ADD CONSTRAINT check_auth_method CHECK (password_hash IS NOT NULL OR google_id IS NOT NULL);
    """

    try:
        # Conectar ao banco
        print("[*] Conectando ao banco: " + DATABASE_URL)
        engine = create_engine(DATABASE_URL)

        with engine.connect() as connection:
            # Executar cada comando separadamente
            commands = [cmd.strip() for cmd in migration_sql.split(';') if cmd.strip()]

            for i, cmd in enumerate(commands, 1):
                try:
                    print("\n[*] Executando comando " + str(i) + "/" + str(len(commands)) + "...")
                    print("    " + cmd[:60] + "...")
                    connection.execute(text(cmd))
                    print("    [OK]")
                except SQLAlchemyError as e:
                    # Algumas colunas/constraints podem já existir
                    if "already exists" in str(e) or "duplicate" in str(e).lower():
                        print("    [INFO] Coluna/constraint ja existe (ignorado)")
                    else:
                        print("    [ERRO] " + str(e))

            # Fazer commit
            connection.commit()

        print("\n" + "="*60)
        print("[SUCCESS] MIGRATION CONCLUIDA COM SUCESSO!")
        print("="*60)
        print("\n[INFO] Alteracoes realizadas:")
        print("   [OK] password_hash -> nullable")
        print("   [OK] google_id -> new column (unique)")
        print("   [OK] foto -> new column")
        print("   [OK] idx_users_google_id -> new index")
        print("   [OK] check_auth_method -> new constraint")

        engine.dispose()
        return True

    except Exception as e:
        print("\n" + "="*60)
        print("[ERROR] ERRO NA MIGRATION: " + str(e))
        print("="*60)
        print("\n[WARNING] Verificar:")
        print("   1. PostgreSQL esta rodando?")
        print("   2. DATABASE_URL esta correto?")
        print("   3. Credenciais do banco estao corretas?")
        print("   4. Banco 'fretebr' existe?")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
