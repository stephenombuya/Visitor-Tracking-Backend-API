-- Create Database
CREATE DATABASE IF NOT EXISTS visitor_tracking_db;
USE visitor_tracking_db;

-- Create Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

-- Create Visitors Table
CREATE TABLE visitors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    page_url VARCHAR(255) UNIQUE NOT NULL,
    visit_count INT DEFAULT 1,
    last_visited TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Optional: Add IP tracking for more detailed analytics
    last_ip_address VARCHAR(45),
    
    -- Optional: Geolocation data
    country VARCHAR(100),
    region VARCHAR(100)
);

-- Create Indexes for Performance
CREATE INDEX idx_page_url ON visitors(page_url);
CREATE INDEX idx_last_visited ON visitors(last_visited);

-- Create Stored Procedure for Visitor Count Update
DELIMITER //
CREATE PROCEDURE UpdateVisitorCount(IN p_page_url VARCHAR(255))
BEGIN
    INSERT INTO visitors (page_url, visit_count) 
    VALUES (p_page_url, 1)
    ON DUPLICATE KEY UPDATE 
        visit_count = visit_count + 1,
        last_visited = CURRENT_TIMESTAMP;
END //
DELIMITER ;

-- Create View for Visitor Analytics
CREATE VIEW visitor_analytics AS
SELECT 
    page_url,
    visit_count,
    last_visited,
    DATEDIFF(CURRENT_TIMESTAMP, created_at) AS days_tracked
FROM 
    visitors
ORDER BY 
    visit_count DESC;

-- Sample User Creation (use with password hashing in application)
INSERT INTO users (username, email, password_hash) 
VALUES 
    ('admin', 'admin@example.com', 'hashed_password_here');
