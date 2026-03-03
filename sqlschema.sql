-- HealthAssist AI - Supabase PostgreSQL Database Schema
-- Run this SQL in your Supabase SQL Editor

-- ============================================
-- TABLE 1: users
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    mobile VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    security_question VARCHAR(255),
    security_answer VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_mobile ON users(mobile);

-- ============================================
-- TABLE 2: active_sessions
-- ============================================
CREATE TABLE IF NOT EXISTS active_sessions (
    id SERIAL PRIMARY KEY,
    mobile VARCHAR(10) NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mobile) REFERENCES users(mobile) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_mobile ON active_sessions(mobile);

-- ============================================
-- TABLE 3: history
-- ============================================
CREATE TABLE IF NOT EXISTS history (
    id SERIAL PRIMARY KEY,
    mobile VARCHAR(10) NOT NULL,
    category VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mobile) REFERENCES users(mobile) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_history_mobile ON history(mobile);
CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_history_category ON history(category);