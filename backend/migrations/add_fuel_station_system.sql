-- Migration: Add Fuel Station Referral System
-- Date: 2026-06-05

-- Tabela de Postos de Combustível
CREATE TABLE fuel_stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    cnpj VARCHAR(20) UNIQUE NOT NULL,
    endereco VARCHAR(500),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    telefone VARCHAR(20),
    email VARCHAR(255),
    dono_nome VARCHAR(255),
    dono_email VARCHAR(255),
    comissao_percentual DECIMAL(5, 2) DEFAULT 0.50,  -- 0.50% por indicação
    desconto_motorista DECIMAL(5, 2) DEFAULT 3.00,   -- 3% desconto no combustível
    status VARCHAR(20) DEFAULT 'pendente',  -- pendente, ativo, inativo
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Frentistas
CREATE TABLE fuel_station_attendants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID NOT NULL REFERENCES fuel_stations(id) ON DELETE CASCADE,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telefone VARCHAR(20),
    pix_key VARCHAR(255),  -- Para saques
    status VARCHAR(20) DEFAULT 'ativo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Códigos de Referência (um por frentista)
CREATE TABLE fuel_referral_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID NOT NULL REFERENCES fuel_stations(id) ON DELETE CASCADE,
    attendant_id UUID REFERENCES fuel_station_attendants(id) ON DELETE SET NULL,
    codigo VARCHAR(50) UNIQUE NOT NULL,  -- Ex: SHELL-SP-123-ABC
    descricao VARCHAR(255),
    status VARCHAR(20) DEFAULT 'ativo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Indicações via Posto
CREATE TABLE fuel_station_referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID NOT NULL REFERENCES fuel_stations(id) ON DELETE CASCADE,
    attendant_id UUID REFERENCES fuel_station_attendants(id) ON DELETE SET NULL,
    referral_code_id UUID REFERENCES fuel_referral_codes(id) ON DELETE SET NULL,
    motorista_id UUID REFERENCES users(id) ON DELETE SET NULL,
    comissao_valor DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pendente',  -- pendente, ativo (motorista usa), pago
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Tabela de Descontos do Motorista no Combustível
CREATE TABLE fuel_discounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    motorista_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    station_id UUID REFERENCES fuel_stations(id) ON DELETE SET NULL,
    referral_code_id UUID REFERENCES fuel_referral_codes(id) ON DELETE SET NULL,
    percentual_desconto DECIMAL(5, 2) DEFAULT 3.00,
    status VARCHAR(20) DEFAULT 'ativo',  -- ativo, inativo, expirado
    data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_expiracao TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Saques do Frentista
CREATE TABLE fuel_attendant_withdrawals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attendant_id UUID NOT NULL REFERENCES fuel_station_attendants(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pendente',  -- pendente, processando, concluido, falhou
    pix_key_used VARCHAR(255),
    transaction_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Índices
CREATE INDEX idx_fuel_stations_cidade ON fuel_stations(cidade);
CREATE INDEX idx_fuel_stations_estado ON fuel_stations(estado);
CREATE INDEX idx_fuel_stations_status ON fuel_stations(status);
CREATE INDEX idx_fuel_referral_codes_codigo ON fuel_referral_codes(codigo);
CREATE INDEX idx_fuel_referrals_station ON fuel_station_referrals(station_id);
CREATE INDEX idx_fuel_referrals_attendant ON fuel_station_referrals(attendant_id);
CREATE INDEX idx_fuel_referrals_motorista ON fuel_station_referrals(motorista_id);
CREATE INDEX idx_fuel_referrals_status ON fuel_station_referrals(status);
CREATE INDEX idx_fuel_discounts_motorista ON fuel_discounts(motorista_id);
CREATE INDEX idx_fuel_discounts_station ON fuel_discounts(station_id);
CREATE INDEX idx_fuel_withdrawals_attendant ON fuel_attendant_withdrawals(attendant_id);
CREATE INDEX idx_fuel_withdrawals_status ON fuel_attendant_withdrawals(status);

-- Adicionar coluna na tabela users para referência de código de combustível
ALTER TABLE users
ADD COLUMN fuel_referral_code_id UUID REFERENCES fuel_referral_codes(id) ON DELETE SET NULL;

-- Adicionar coluna na tabela de transações para desconto de combustível
ALTER TABLE transactions
ADD COLUMN fuel_discount_applied DECIMAL(10, 2) DEFAULT 0;
