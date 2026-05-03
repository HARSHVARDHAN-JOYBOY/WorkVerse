-- WorkVerse Database Updates - Add New Features
-- Run this to update existing database

USE workverse_db;

-- Add passing_percentage column to simulations table
ALTER TABLE simulations 
ADD COLUMN passing_percentage INT DEFAULT 60 AFTER video_url;

-- Create lessons table for multiple content pages
CREATE TABLE IF NOT EXISTS lessons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    simulation_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    video_url VARCHAR(255),
    lesson_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE,
    INDEX idx_simulation_order (simulation_id, lesson_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Update existing simulations with default passing percentage
UPDATE simulations SET passing_percentage = 60 WHERE passing_percentage IS NULL;

-- Add sample lessons for existing simulations
INSERT INTO lessons (simulation_id, title, content, video_url, lesson_order) 
SELECT 
    id,
    CONCAT(title, ' - Introduction') as title,
    CONCAT('Welcome to the ', title, ' simulation.\n\n', content) as content,
    video_url,
    1
FROM simulations
WHERE NOT EXISTS (SELECT 1 FROM lessons WHERE lessons.simulation_id = simulations.id);

-- Optional: Add more lessons for Data Analyst simulation as example
INSERT INTO lessons (simulation_id, title, content, video_url, lesson_order) VALUES
(1, 'Data Analysis Tools', 
 'In this lesson, you will learn about essential data analysis tools:\n\n- Microsoft Excel for basic data manipulation\n- SQL for querying databases\n- Python with pandas for advanced analysis\n- Tableau for data visualization\n\nEach tool serves a specific purpose in the data analysis workflow.',
 'https://www.youtube.com/embed/RG5nBNv8e94',
 2),
 
(1, 'Statistical Concepts',
 'Understanding basic statistics is crucial for data analysis:\n\n- Mean, Median, Mode\n- Standard Deviation and Variance\n- Correlation and Causation\n- Hypothesis Testing\n- Confidence Intervals\n\nThese concepts help you draw meaningful conclusions from data.',
 'https://www.youtube.com/embed/xxpc-HPKN28',
 3);

-- Update progress to use simulation-specific passing percentage
-- (No schema change needed, will be handled in application logic)

SELECT 'Database updated successfully! New features added:' as Message;
SELECT '1. Passing percentage per simulation' as Feature;
SELECT '2. Lessons table for multiple content pages' as Feature;
SELECT '3. Sample lessons added to existing simulations' as Feature;
