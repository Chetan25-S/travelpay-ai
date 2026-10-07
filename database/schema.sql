-- TravelPay AI database schema
-- Railway MySQL: run this against the database created by the Railway MySQL service.
-- Do NOT run CREATE DATABASE or USE here; Railway supplies the selected database.

CREATE TABLE IF NOT EXISTS users (
 user_id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(100) NOT NULL,
 country VARCHAR(100) NOT NULL,
 home_currency VARCHAR(10) NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS budgets (
 budget_id INT AUTO_INCREMENT PRIMARY KEY,
 user_id INT NOT NULL UNIQUE,
 total_budget DECIMAL(12,2) NOT NULL,
 spent_amount DECIMAL(12,2) DEFAULT 0,
 remaining_amount DECIMAL(12,2) DEFAULT 0,
 FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transactions (
 transaction_id INT AUTO_INCREMENT PRIMARY KEY,
 user_id INT NOT NULL,
 merchant_name VARCHAR(150) NOT NULL,
 upi_id VARCHAR(150),
 amount_inr DECIMAL(12,2) NOT NULL,
 amount_foreign DECIMAL(12,2) NOT NULL,
 foreign_currency VARCHAR(10) NOT NULL,
 category VARCHAR(50) DEFAULT 'Other',
 risk_level VARCHAR(20) DEFAULT 'LOW',
 ai_recommendation TEXT,
 status VARCHAR(30) DEFAULT 'PENDING',
 reference_code VARCHAR(50),
 transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ai_insights (
 insight_id INT AUTO_INCREMENT PRIMARY KEY,
 user_id INT NOT NULL,
 insight_type VARCHAR(50),
 message TEXT,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- There is intentionally NO fake local_prices table.
-- Price Advisor uses configured live evidence providers and reports
-- "insufficient evidence" instead of inventing a market price.
