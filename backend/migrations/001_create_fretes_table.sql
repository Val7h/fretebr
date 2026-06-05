-- Create fretes table migration
-- This creates the fretes table for the FreteBR marketplace

CREATE TABLE IF NOT EXISTS fretes (
    id SERIAL PRIMARY KEY,
    motorista_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    origem VARCHAR NOT NULL,
    destino VARCHAR NOT NULL,
    peso_kg FLOAT NOT NULL,
    valor_r FLOAT NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'disponível',
    descricao VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index for motorista_id for faster queries
CREATE INDEX IF NOT EXISTS idx_fretes_motorista_id ON fretes(motorista_id);

-- Create index for status for filtering available fretes
CREATE INDEX IF NOT EXISTS idx_fretes_status ON fretes(status);
