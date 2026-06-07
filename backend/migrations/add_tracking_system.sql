-- Migration: Add Real-Time Tracking System
-- Date: 2026-06-05

-- Tabela: frete_tracking (Histórico de localizações)
CREATE TABLE IF NOT EXISTS frete_tracking (
    id SERIAL PRIMARY KEY,
    frete_id INTEGER NOT NULL REFERENCES fretes(id) ON DELETE CASCADE,
    match_id INTEGER REFERENCES matches(id) ON DELETE SET NULL,
    motorista_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    latitude NUMERIC(10, 8) NOT NULL,
    longitude NUMERIC(11, 8) NOT NULL,
    address VARCHAR(500),
    accuracy NUMERIC(5, 2),
    status VARCHAR(50) DEFAULT 'em_transito',
    description VARCHAR(200),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_latest BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_frete_tracking_frete_id_timestamp ON frete_tracking(frete_id, timestamp);
CREATE INDEX idx_frete_tracking_motorista_id ON frete_tracking(motorista_id);
CREATE INDEX idx_frete_tracking_is_latest ON frete_tracking(is_latest);

-- Tabela: frete_current_location (Localização atual - para queries rápidas)
CREATE TABLE IF NOT EXISTS frete_current_location (
    id SERIAL PRIMARY KEY,
    frete_id INTEGER NOT NULL UNIQUE REFERENCES fretes(id) ON DELETE CASCADE,
    match_id INTEGER REFERENCES matches(id) ON DELETE SET NULL,
    motorista_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    latitude NUMERIC(10, 8) NOT NULL,
    longitude NUMERIC(11, 8) NOT NULL,
    address VARCHAR(500),
    eta_minutes INTEGER,
    distance_km NUMERIC(8, 2),
    status VARCHAR(50) DEFAULT 'em_transito',
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_online BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_frete_current_location_frete_id ON frete_current_location(frete_id);
CREATE INDEX idx_frete_current_location_motorista_id ON frete_current_location(motorista_id);
CREATE INDEX idx_frete_current_location_last_update ON frete_current_location(last_update);

-- Tabela: tracking_session (Sessão de rastreamento)
CREATE TABLE IF NOT EXISTS tracking_session (
    id SERIAL PRIMARY KEY,
    frete_id INTEGER NOT NULL REFERENCES fretes(id) ON DELETE CASCADE,
    motorista_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    total_locations INTEGER DEFAULT 0,
    total_distance_km NUMERIC(8, 2) DEFAULT 0
);

CREATE INDEX idx_tracking_session_frete_id ON tracking_session(frete_id);
CREATE INDEX idx_tracking_session_motorista_id ON tracking_session(motorista_id);
CREATE INDEX idx_tracking_session_is_active ON tracking_session(is_active);
