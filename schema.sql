-- Schéma SQL pour le Bot de Trading Scalping

-- Table des utilisateurs
CREATE TABLE users (
    telegram_id BIGINT PRIMARY KEY,
    username TEXT,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des clés API (chiffrées au niveau applicatif)
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    exchange TEXT NOT NULL, -- 'binance' ou 'bybit'
    api_key TEXT NOT NULL,
    api_secret TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table de l'historique des trades
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    pair TEXT NOT NULL,
    side TEXT NOT NULL, -- 'BUY' or 'SELL'
    entry_price DECIMAL,
    exit_price DECIMAL,
    amount DECIMAL,
    pnl DECIMAL,
    status TEXT DEFAULT 'OPEN', -- 'OPEN' or 'CLOSED'
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des préférences de trading
CREATE TABLE settings (
    user_id BIGINT PRIMARY KEY REFERENCES users(telegram_id) ON DELETE CASCADE,
    risk_per_trade DECIMAL DEFAULT 1.0, -- en pourcentage
    max_trades INTEGER DEFAULT 3,
    stop_loss_pct DECIMAL DEFAULT 1.5,
    take_profit_pct DECIMAL DEFAULT 2.0
);
