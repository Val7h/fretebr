-- Migration: Add Google OAuth support to users table
-- Date: 2026-06-05

-- Alterar password_hash para nullable (para OAuth users)
ALTER TABLE users
ALTER COLUMN password_hash DROP NOT NULL;

-- Adicionar coluna google_id
ALTER TABLE users
ADD COLUMN google_id VARCHAR(255) UNIQUE;

-- Adicionar coluna foto (profile picture URL)
ALTER TABLE users
ADD COLUMN foto VARCHAR(500);

-- Criar índice para google_id
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);

-- Adicionar restrição: usuário deve ter password_hash OU google_id
-- (SQLAlchemy vai cuidar disto no application logic)
ALTER TABLE users
ADD CONSTRAINT check_auth_method CHECK (password_hash IS NOT NULL OR google_id IS NOT NULL);
