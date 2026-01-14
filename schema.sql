
DROP TABLE IF EXISTS bazi_records;
DROP TABLE IF EXISTS billionaires;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE billionaires (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    gender VARCHAR(10),
    birth_year INT,
    birth_month INT,
    birth_day INT,
    net_worth VARCHAR(50),
    industry VARCHAR(255),
    country VARCHAR(100),
    source VARCHAR(255),
    
    -- Calculated Bazi Data
    day_master VARCHAR(10),   -- e.g. 甲, 乙
    bazi_json TEXT,           -- Full pillars structure
    wuxing_counts JSON,       -- {"Gold": 2, "Wood": 1...}
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bazi_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    birth_date DATE,
    birth_time TIME,
    gender VARCHAR(10),
    state VARCHAR(100),
    bazi_json TEXT,
    ai_analysis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
