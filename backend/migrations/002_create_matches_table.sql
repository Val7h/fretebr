-- Migration: Create matches table
-- Created: 2026-06-20

CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    frete_id INTEGER NOT NULL REFERENCES fretes(id) ON DELETE CASCADE,
    shipper_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR NOT NULL DEFAULT 'pendente' CHECK (status IN ('pendente', 'aceito', 'em_entrega', 'finalizado', 'cancelado')),
    valor_final FLOAT NOT NULL,
    data_match TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_matches_frete FOREIGN KEY (frete_id) REFERENCES fretes(id) ON DELETE CASCADE,
    CONSTRAINT fk_matches_shipper FOREIGN KEY (shipper_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_matches_frete_id ON matches(frete_id);
CREATE INDEX idx_matches_shipper_id ON matches(shipper_id);
CREATE INDEX idx_matches_status ON matches(status);
