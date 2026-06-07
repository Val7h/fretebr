-- Migration: Add Referral System
-- Date: 2026-06-05

-- Tabela de referências
CREATE TABLE referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_motorista_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    referred_motorista_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    frete_id UUID REFERENCES fretes(id) ON DELETE SET NULL,
    comissao_valor DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending', -- pending, completed, rejected, expired
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    CONSTRAINT no_self_referral CHECK (referrer_motorista_id != referred_motorista_id)
);

-- Índices para performance
CREATE INDEX idx_referrals_referrer ON referrals(referrer_motorista_id);
CREATE INDEX idx_referrals_referred ON referrals(referred_motorista_id);
CREATE INDEX idx_referrals_frete ON referrals(frete_id);
CREATE INDEX idx_referrals_status ON referrals(status);

-- Adicionar coluna em matches para rastrear referrer
ALTER TABLE matches
ADD COLUMN referrer_motorista_id UUID REFERENCES users(id) ON DELETE SET NULL;

-- Tabela de saque de ganhos
CREATE TABLE referral_withdrawals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    motorista_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, completed, failed
    transaction_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_withdrawals_motorista ON referral_withdrawals(motorista_id);
CREATE INDEX idx_withdrawals_status ON referral_withdrawals(status);
