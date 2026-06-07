-- Migration: Add Rating and Review System
-- Date: 2026-06-05

-- Tabela: rating_motorista (Shipper avalia Motorista)
CREATE TABLE IF NOT EXISTS rating_motorista (
    id SERIAL PRIMARY KEY,
    motorista_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    shipper_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    frete_id INTEGER REFERENCES fretes(id) ON DELETE SET NULL,
    match_id INTEGER REFERENCES matches(id) ON DELETE SET NULL,
    stars NUMERIC(3, 1) NOT NULL CHECK (stars >= 1 AND stars <= 5),
    review_text TEXT,
    categoria VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_rating_motorista_motorista_id ON rating_motorista(motorista_id);
CREATE INDEX idx_rating_motorista_shipper_id ON rating_motorista(shipper_id);
CREATE INDEX idx_rating_motorista_created_at ON rating_motorista(created_at);

-- Tabela: rating_shipper (Motorista avalia Shipper)
CREATE TABLE IF NOT EXISTS rating_shipper (
    id SERIAL PRIMARY KEY,
    shipper_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    motorista_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    frete_id INTEGER REFERENCES fretes(id) ON DELETE SET NULL,
    match_id INTEGER REFERENCES matches(id) ON DELETE SET NULL,
    stars NUMERIC(3, 1) NOT NULL CHECK (stars >= 1 AND stars <= 5),
    review_text TEXT,
    categoria VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_rating_shipper_shipper_id ON rating_shipper(shipper_id);
CREATE INDEX idx_rating_shipper_motorista_id ON rating_shipper(motorista_id);
CREATE INDEX idx_rating_shipper_created_at ON rating_shipper(created_at);

-- Tabela: user_reputation (Cache de reputação)
CREATE TABLE IF NOT EXISTS user_reputation (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    average_rating NUMERIC(3, 2) DEFAULT 5.0,
    total_ratings INTEGER DEFAULT 0,
    five_stars INTEGER DEFAULT 0,
    four_stars INTEGER DEFAULT 0,
    three_stars INTEGER DEFAULT 0,
    two_stars INTEGER DEFAULT 0,
    one_star INTEGER DEFAULT 0,
    is_verified VARCHAR(20) DEFAULT 'pending',
    badges VARCHAR(500),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_user_reputation_user_id ON user_reputation(user_id);
CREATE INDEX idx_user_reputation_average_rating ON user_reputation(average_rating DESC);
