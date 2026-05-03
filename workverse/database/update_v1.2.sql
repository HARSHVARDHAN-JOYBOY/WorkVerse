-- WorkVerse Database Updates - Fix Critical Issues
-- Run this to add notifications and update schema

USE workverse_db;

-- Create notifications table for user-admin communication
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    type ENUM('info', 'success', 'warning', 'danger') DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_read (user_id, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Add resubmission tracking to submissions table
ALTER TABLE submissions 
ADD COLUMN resubmission_count INT DEFAULT 0 AFTER feedback,
ADD COLUMN is_new_submission BOOLEAN DEFAULT TRUE AFTER resubmission_count;

-- Create admin notification tracking table
CREATE TABLE IF NOT EXISTS admin_notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
    INDEX idx_read (is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Update existing submissions to mark as not new (existing data)
UPDATE submissions SET is_new_submission = FALSE WHERE id > 0;

SELECT 'Database updated successfully! Added notifications system.' as Message;
