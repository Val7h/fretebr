-- Create transactions table for Mercado Pago payment tracking
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    motorista_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    shipper_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount FLOAT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pendente',
    mp_payment_id VARCHAR(255) UNIQUE,
    qr_code_data TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_transaction_match FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
    CONSTRAINT fk_transaction_motorista FOREIGN KEY (motorista_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_transaction_shipper FOREIGN KEY (shipper_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX idx_transactions_match_id ON transactions(match_id);
CREATE INDEX idx_transactions_motorista_id ON transactions(motorista_id);
CREATE INDEX idx_transactions_shipper_id ON transactions(shipper_id);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_mp_payment_id ON transactions(mp_payment_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
