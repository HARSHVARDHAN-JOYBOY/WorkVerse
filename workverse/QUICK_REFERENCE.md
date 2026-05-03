# WorkVerse - Quick Reference Guide

## Common Tasks

### Start the Application

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Run application
python app.py
```

Access at: http://127.0.0.1:5000

### Stop the Application

Press `Ctrl + C` in the terminal

### Database Operations

#### Connect to MySQL

```bash
mysql -u root -p
```

#### View All Users

```sql
USE workverse_db;
SELECT id, name, email, role FROM users;
```

#### Change User Password

```bash
# Generate hash
python generate_password_hash.py
```

```sql
UPDATE users 
SET password = 'new_hash_here' 
WHERE email = 'user@example.com';
```

#### Create New Admin

```sql
INSERT INTO users (name, email, password, role) 
VALUES ('New Admin', 'newadmin@example.com', 'password_hash_here', 'admin');
```

#### View Simulations

```sql
SELECT id, title, created_at FROM simulations;
```

#### View Submissions

```sql
SELECT s.id, u.name, sim.title, s.status, s.submitted_at
FROM submissions s
JOIN users u ON s.user_id = u.id
JOIN simulations sim ON s.simulation_id = sim.id
ORDER BY s.submitted_at DESC;
```

#### Delete Old Submissions

```sql
DELETE FROM submissions 
WHERE status = 'rejected' 
AND submitted_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### File Management

#### Clear Uploaded Files

```bash
# Linux/Mac
rm -rf uploads/*

# Windows
del /Q uploads\*.*
```

#### Check Upload Directory Size

```bash
du -sh uploads/
```

#### Find Large Files

```bash
find uploads/ -type f -size +10M
```

### Application Logs

#### View Flask Output

The application logs appear in the terminal where you run `python app.py`

#### Enable Debug Mode

In `app.py`:

```python
app.run(debug=True)
```

⚠️ Never use debug mode in production!

### Backup and Restore

#### Backup Database

```bash
mysqldump -u root -p workverse_db > backup_$(date +%Y%m%d).sql
```

#### Restore Database

```bash
mysql -u root -p workverse_db < backup_20240101.sql
```

#### Backup Uploads

```bash
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

#### Restore Uploads

```bash
tar -xzf uploads_backup_20240101.tar.gz
```

### User Management

#### Count Users

```sql
SELECT COUNT(*) as total_users FROM users WHERE role = 'user';
```

#### Most Active Users

```sql
SELECT u.name, u.email, COUNT(p.id) as enrollments
FROM users u
LEFT JOIN progress p ON u.id = p.user_id
WHERE u.role = 'user'
GROUP BY u.id
ORDER BY enrollments DESC
LIMIT 10;
```

#### Users with Certificates

```sql
SELECT u.name, u.email, COUNT(DISTINCT s.simulation_id) as certificates
FROM users u
JOIN submissions sub ON u.id = sub.user_id
JOIN simulations s ON sub.simulation_id = s.id
WHERE sub.status = 'approved'
GROUP BY u.id;
```

### Simulation Management

#### Simulations by Popularity

```sql
SELECT s.title, COUNT(p.user_id) as enrolled_users
FROM simulations s
LEFT JOIN progress p ON s.id = p.simulation_id
GROUP BY s.id
ORDER BY enrolled_users DESC;
```

#### Completion Rates

```sql
SELECT 
    s.title,
    COUNT(DISTINCT p.user_id) as total_enrolled,
    COUNT(DISTINCT CASE WHEN p.status = 'completed' THEN p.user_id END) as completed,
    ROUND(COUNT(DISTINCT CASE WHEN p.status = 'completed' THEN p.user_id END) * 100.0 / NULLIF(COUNT(DISTINCT p.user_id), 0), 2) as completion_rate
FROM simulations s
LEFT JOIN progress p ON s.id = p.simulation_id
GROUP BY s.id;
```

### Quiz Management

#### Quiz Questions by Simulation

```sql
SELECT s.title, COUNT(q.id) as question_count
FROM simulations s
LEFT JOIN quizzes q ON s.id = q.simulation_id
GROUP BY s.id;
```

#### Average Quiz Scores

```sql
SELECT s.title, AVG(p.score) as avg_score
FROM simulations s
JOIN progress p ON s.id = p.simulation_id
WHERE p.score > 0
GROUP BY s.id;
```

### Troubleshooting

#### Cannot Connect to Database

1. Check MySQL is running:
   ```bash
   sudo systemctl status mysql  # Linux
   ```

2. Verify credentials in `config.py`

3. Test connection:
   ```bash
   mysql -u root -p
   ```

#### Permission Denied on Uploads

```bash
# Linux/Mac
chmod 775 uploads/

# Make sure the directory exists
mkdir -p uploads
```

#### Port Already in Use

Change port in `app.py`:

```python
app.run(debug=True, port=5001)
```

#### Module Not Found

```bash
pip install -r requirements.txt
```

#### Database Schema Out of Date

```bash
# Backup first!
mysqldump -u root -p workverse_db > backup.sql

# Re-import schema
mysql -u root -p < database/schema.sql
```

### Performance Tips

#### Clear Old Sessions (if implementing sessions table)

```sql
DELETE FROM sessions WHERE expiry < NOW();
```

#### Optimize Database

```sql
OPTIMIZE TABLE users, simulations, quizzes, progress, submissions;
```

#### Check Database Size

```sql
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS "Size (MB)"
FROM information_schema.TABLES 
WHERE table_schema = 'workverse_db';
```

### Development Tips

#### Reset Database (Development Only!)

```bash
# WARNING: This deletes all data!
mysql -u root -p -e "DROP DATABASE workverse_db;"
mysql -u root -p < database/schema.sql
```

#### Test Email (if implementing email features)

```python
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
# Configure mail settings
mail = Mail(app)

msg = Message('Test', recipients=['test@example.com'])
msg.body = 'Test email'
mail.send(msg)
```

#### Generate Test Data

```sql
-- Insert test users
INSERT INTO users (name, email, password, role) VALUES
('Test User 1', 'test1@example.com', 'hashed_password', 'user'),
('Test User 2', 'test2@example.com', 'hashed_password', 'user');

-- Enroll test users
INSERT INTO progress (user_id, simulation_id, status) VALUES
(2, 1, 'enrolled'),
(2, 2, 'quiz_completed'),
(3, 1, 'completed');
```

### Useful SQL Queries

#### Today's Activity

```sql
SELECT 
    COUNT(DISTINCT CASE WHEN DATE(created_at) = CURDATE() THEN id END) as new_users,
    COUNT(DISTINCT CASE WHEN DATE(created_at) = CURDATE() THEN user_id END) as new_enrollments
FROM users, progress;
```

#### Pending Reviews

```sql
SELECT COUNT(*) as pending_reviews 
FROM submissions 
WHERE status = 'pending';
```

#### Recent Activity Feed

```sql
SELECT 
    'enrollment' as type,
    u.name,
    s.title,
    p.created_at as timestamp
FROM progress p
JOIN users u ON p.user_id = u.id
JOIN simulations s ON p.simulation_id = s.id

UNION ALL

SELECT 
    'submission' as type,
    u.name,
    s.title,
    sub.submitted_at as timestamp
FROM submissions sub
JOIN users u ON sub.user_id = u.id
JOIN simulations s ON sub.simulation_id = s.id

ORDER BY timestamp DESC
LIMIT 20;
```

### Configuration Checklist

Before deploying to production, verify:

- [ ] Changed `SECRET_KEY` in config.py
- [ ] Updated database credentials
- [ ] Changed admin password
- [ ] Disabled debug mode
- [ ] Set proper file permissions
- [ ] Configured firewall
- [ ] Enabled HTTPS
- [ ] Set up backups
- [ ] Tested all features

### Support Resources

- README.md - Full documentation
- DEPLOYMENT.md - Production deployment guide
- TESTING_CHECKLIST.md - Testing procedures
- database/schema.sql - Database structure

### Quick Links

- Application: http://127.0.0.1:5000
- Admin Login: http://127.0.0.1:5000/login
- User Dashboard: http://127.0.0.1:5000/dashboard
- Admin Dashboard: http://127.0.0.1:5000/admin/dashboard
