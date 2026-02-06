-- Stock market Analysis - Database Schema


-- Table 1: Stock Info 
-- Information about each stock
CREATE TABLE IF NOT EXISTS stock_info (
    ticker VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    sector VARCHAR(50),
    market_cap BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Table 2: Stock Prices
-- Daily OHLC data from API 
CREATE TABLE IF NOT EXISTS stock_prices (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open_price DECIMAL(10, 2) NOT NULL,
    high_price DECIMAL(10, 2) NOT NULL,
    low_price DECIMAL(10, 2) NOT NULL,
    close_price DECIMAL(10, 2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker) REFERENCES stock_info(ticker),
    UNIQUE(ticker, date)  -- Prevents duplicates (one stock per day only once)
);


-- Table 3: Daily Returns (Analystics)
-- Calculated returns (percentage change)
CREATE TABLE IF NOT EXISTS daily_returns (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    daily_return_percent DECIMAL(10, 4),
    cumulative_return_percent DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker) REFERENCES stock_info(ticker),
    UNIQUE(ticker, date)
);


-- Table 4: Portfolio Performance (Aggregated)
-- Overall portfolio performance 
CREATE TABLE IF NOT EXISTS portfolio_performance (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_portfolio_value DECIMAL(12, 2) NOT NULL,
    best_performer VARCHAR(10),
    worst_performer VARCHAR(10),
    daily_return_percent DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_stock_prices_ticker ON stock_prices(ticker);
CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON stock_prices(date);
CREATE INDEX IF NOT EXISTS idx_daily_returns_ticker ON daily_returns(ticker);
CREATE INDEX IF NOT EXISTS idx_daily_returns_date ON daily_returns(date);


-- insert some of the top tech stocks into stock_info (Current market caps - February 2026)
INSERT INTO stock_info (ticker, company_name, sector, market_cap) VALUES
('NVDA', 'NVIDIA Corporation', 'Technology', 4301000000000),
('GOOG', 'Alphabet Inc.', 'Technology', 4099000000000),
('AAPL', 'Apple Inc.', 'Technology', 3982000000000),
('MSFT', 'Microsoft Corporation', 'Technology', 3036000000000),
('AMZN', 'Amazon.com Inc.', 'Consumer Cyclical', 2528000000000),
('META', 'Meta Platforms Inc.', 'Technology', 1738000000000),
('TSM', 'Taiwan Semiconductor Manufacturing', 'Technology', 1717000000000),
('NFLX', 'Netflix Inc.', 'Communication Services', 356000000000),  -- Replaces Saudi Aramco
('TSLA', 'Tesla Inc.', 'Automotive', 1563000000000),
('AVGO', 'Broadcom Inc.', 'Technology', 1477000000000)
ON CONFLICT (ticker) DO NOTHING;