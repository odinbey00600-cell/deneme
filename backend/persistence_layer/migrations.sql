CREATE TABLE IF NOT EXISTS generations (
  id SERIAL PRIMARY KEY,
  seed INT NOT NULL,
  starting_balance DOUBLE PRECISION NOT NULL,
  ending_balance DOUBLE PRECISION NOT NULL DEFAULT 0,
  status VARCHAR(32) NOT NULL DEFAULT 'running',
  created_at TIMESTAMPTZ DEFAULT now(),
  ended_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS genome_parameters (
  id SERIAL PRIMARY KEY,
  generation_id INT NOT NULL REFERENCES generations(id) ON DELETE CASCADE,
  parameters JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS trades (
  id BIGSERIAL PRIMARY KEY,
  generation_id INT NOT NULL REFERENCES generations(id) ON DELETE CASCADE,
  side VARCHAR(8) NOT NULL,
  qty DOUBLE PRECISION NOT NULL,
  price DOUBLE PRECISION NOT NULL,
  fee DOUBLE PRECISION NOT NULL,
  realized_pnl DOUBLE PRECISION NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS equity_history (
  id BIGSERIAL PRIMARY KEY,
  generation_id INT NOT NULL REFERENCES generations(id) ON DELETE CASCADE,
  equity DOUBLE PRECISION NOT NULL,
  mark_price DOUBLE PRECISION NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS metrics (
  id BIGSERIAL PRIMARY KEY,
  generation_id INT NOT NULL REFERENCES generations(id) ON DELETE CASCADE,
  sharpe DOUBLE PRECISION,
  expectancy DOUBLE PRECISION,
  max_drawdown DOUBLE PRECISION,
  liquidation_frequency DOUBLE PRECISION
);
CREATE TABLE IF NOT EXISTS liquidation_events (
  id BIGSERIAL PRIMARY KEY,
  generation_id INT NOT NULL REFERENCES generations(id) ON DELETE CASCADE,
  mark_price DOUBLE PRECISION NOT NULL,
  margin_ratio DOUBLE PRECISION NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_trade_generation_created ON trades(generation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_equity_generation_created ON equity_history(generation_id, created_at);
