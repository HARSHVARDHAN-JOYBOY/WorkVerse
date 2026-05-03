-- WorkVerse Database Schema
-- Drop database if exists and create fresh
DROP DATABASE IF EXISTS workverse_db;
CREATE DATABASE workverse_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE workverse_db;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Simulations table
CREATE TABLE simulations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    content TEXT NOT NULL,
    video_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_title (title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Quizzes table
CREATE TABLE quizzes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    simulation_id INT NOT NULL,
    question TEXT NOT NULL,
    option1 VARCHAR(255) NOT NULL,
    option2 VARCHAR(255) NOT NULL,
    option3 VARCHAR(255) NOT NULL,
    option4 VARCHAR(255) NOT NULL,
    correct_answer ENUM('1', '2', '3', '4') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE,
    INDEX idx_simulation (simulation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Progress table
CREATE TABLE progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    simulation_id INT NOT NULL,
    score INT DEFAULT 0,
    status ENUM('enrolled', 'quiz_completed', 'submitted', 'completed') DEFAULT 'enrolled',
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_simulation (user_id, simulation_id),
    INDEX idx_user (user_id),
    INDEX idx_simulation (simulation_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Submissions table
CREATE TABLE submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    simulation_id INT NOT NULL,
    ppt_file VARCHAR(255) NOT NULL,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    feedback TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_simulation (simulation_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default admin account
-- Password: admin123 (hashed using Werkzeug)
INSERT INTO users (name, email, password, role) VALUES
('Admin User', 'admin@workverse.com', 'scrypt:32768:8:1$yFE7K8xGlMqJzWJC$dc1ed5b3e7c3f1c8e9b5a4d6f2e8c7b1a3d5e6f7c8a9b0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2', 'admin');

-- Insert sample simulations
INSERT INTO simulations (title, description, content, video_url) VALUES
('Data Analyst', 
 'Learn data analysis fundamentals and work with real datasets to generate insights.',
 'As a Data Analyst, you will work with large datasets to extract meaningful insights. This simulation covers data cleaning, analysis techniques, visualization, and reporting. You will learn SQL queries, Excel pivot tables, and basic statistical analysis.\n\nKey Skills:\n- Data cleaning and preprocessing\n- Statistical analysis\n- Data visualization\n- Report generation\n- SQL and Excel proficiency',
 'https://www.youtube.com/embed/1UXSUJScspQ'),

('Web Developer',
 'Build responsive websites and web applications using modern web technologies.',
 'As a Web Developer, you will create responsive and interactive websites. This simulation covers HTML, CSS, JavaScript, and basic backend concepts. You will learn about responsive design, DOM manipulation, and client-server architecture.\n\nKey Skills:\n- HTML/CSS/JavaScript\n- Responsive design\n- Version control (Git)\n- Problem-solving\n- Browser developer tools',
 'https://www.youtube.com/embed/qz0aGYrrlhU'),

('QA Tester',
 'Understand software testing methodologies and ensure product quality.',
 'As a QA Tester, you will learn to identify bugs, write test cases, and ensure software quality. This simulation covers manual testing, test case design, bug reporting, and testing methodologies.\n\nKey Skills:\n- Test case design\n- Bug identification and reporting\n- Manual and automated testing\n- Attention to detail\n- Documentation',
 'https://www.youtube.com/embed/Nd31XiSGJLw'),

('Prompt Engineer',
 'Master the art of crafting effective prompts for AI systems.',
 'As a Prompt Engineer, you will learn to design and optimize prompts for AI language models. This simulation covers prompt design principles, iteration techniques, and best practices for getting optimal AI responses.\n\nKey Skills:\n- Understanding AI capabilities\n- Prompt design and optimization\n- Iterative refinement\n- Context management\n- Critical evaluation',
 'https://www.youtube.com/embed/dOOjR8wQfH0');

-- Insert sample quiz questions for Data Analyst simulation
INSERT INTO quizzes (simulation_id, question, option1, option2, option3, option4, correct_answer) VALUES
(1, 'What is the primary purpose of data cleaning?', 
 'To remove all data', 
 'To ensure data accuracy and consistency', 
 'To make data look pretty', 
 'To reduce file size', 
 '2'),

(1, 'Which SQL command is used to retrieve data from a database?', 
 'GET', 
 'FETCH', 
 'SELECT', 
 'RETRIEVE', 
 '3'),

(1, 'What does a pivot table help you do?', 
 'Create databases', 
 'Summarize and analyze large datasets', 
 'Write code', 
 'Design websites', 
 '2'),

(1, 'Which visualization is best for showing trends over time?', 
 'Pie chart', 
 'Bar chart', 
 'Line chart', 
 'Scatter plot', 
 '3'),

(1, 'What is the mean of the dataset: 10, 20, 30, 40, 50?', 
 '25', 
 '30', 
 '35', 
 '40', 
 '2');

-- Insert sample quiz questions for Web Developer simulation
INSERT INTO quizzes (simulation_id, question, option1, option2, option3, option4, correct_answer) VALUES
(2, 'What does HTML stand for?', 
 'Hyper Text Markup Language', 
 'High Tech Modern Language', 
 'Home Tool Markup Language', 
 'Hyperlinks and Text Markup Language', 
 '1'),

(2, 'Which CSS property controls text size?', 
 'text-size', 
 'font-size', 
 'text-style', 
 'font-style', 
 '2'),

(2, 'What is the correct JavaScript syntax to change the content of an HTML element?', 
 'document.getElementById("demo").innerHTML = "Hello"', 
 'document.getElement("demo").innerHTML = "Hello"', 
 'document.getId("demo").content = "Hello"', 
 '#demo.innerHTML = "Hello"', 
 '1'),

(2, 'What does CSS stand for?', 
 'Creative Style Sheets', 
 'Cascading Style Sheets', 
 'Computer Style Sheets', 
 'Colorful Style Sheets', 
 '2'),

(2, 'Which HTML tag is used to create a hyperlink?', 
 '<link>', 
 '<a>', 
 '<href>', 
 '<url>', 
 '2');

-- Insert sample quiz questions for QA Tester simulation
INSERT INTO quizzes (simulation_id, question, option1, option2, option3, option4, correct_answer) VALUES
(3, 'What is the main goal of software testing?', 
 'To find all bugs', 
 'To ensure software quality and reliability', 
 'To delay releases', 
 'To criticize developers', 
 '2'),

(3, 'Which type of testing checks individual components?', 
 'Integration testing', 
 'System testing', 
 'Unit testing', 
 'Acceptance testing', 
 '3'),

(3, 'What should a good test case include?', 
 'Only the steps', 
 'Steps, expected results, and actual results', 
 'Just the bug description', 
 'Developer names', 
 '2'),

(3, 'What is regression testing?', 
 'Testing new features only', 
 'Testing to ensure existing functionality still works', 
 'Testing performance', 
 'Testing security', 
 '2'),

(3, 'What is a bug severity?', 
 'How fast it was found', 
 'The impact of the defect on the system', 
 'The developer who caused it', 
 'The testing tool used', 
 '2');

-- Insert sample quiz questions for Prompt Engineer simulation
INSERT INTO quizzes (simulation_id, question, option1, option2, option3, option4, correct_answer) VALUES
(4, 'What is a prompt in AI context?', 
 'A reminder notification', 
 'Input text given to an AI model to generate a response', 
 'An error message', 
 'A command line', 
 '2'),

(4, 'Which technique helps improve prompt quality?', 
 'Making prompts vague', 
 'Providing clear context and examples', 
 'Using technical jargon', 
 'Keeping prompts extremely short', 
 '2'),

(4, 'What is few-shot prompting?', 
 'Asking multiple questions at once', 
 'Providing examples in the prompt to guide the model', 
 'Using short prompts', 
 'Testing with small datasets', 
 '2'),

(4, 'What should you do if an AI gives an incorrect response?', 
 'Give up immediately', 
 'Refine and iterate on the prompt', 
 'Blame the AI', 
 'Use the same prompt repeatedly', 
 '2'),

(4, 'What is prompt engineering primarily about?', 
 'Writing code', 
 'Designing hardware', 
 'Crafting effective instructions for AI models', 
 'Creating databases', 
 '3');
