# WorkVerse - Production Deployment Guide

This guide covers deploying WorkVerse to a production environment.

## Prerequisites

- Ubuntu Server 20.04 LTS or higher
- Root or sudo access
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)

## Step 1: Server Setup

### Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Install Required Software

```bash
# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install MySQL
sudo apt install mysql-server -y

# Install Nginx
sudo apt install nginx -y

# Install Git (if deploying from repository)
sudo apt install git -y
```

## Step 2: MySQL Configuration

### Secure MySQL Installation

```bash
sudo mysql_secure_installation
```

Follow the prompts to:
- Set root password
- Remove anonymous users
- Disallow root login remotely
- Remove test database

### Create Database and User

```bash
sudo mysql -u root -p
```

```sql
-- Create database
CREATE DATABASE workverse_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'workverse_user'@'localhost' IDENTIFIED BY 'strong_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON workverse_db.* TO 'workverse_user'@'localhost';
FLUSH PRIVILEGES;

-- Exit
EXIT;
```

### Import Database Schema

```bash
mysql -u workverse_user -p workverse_db < database/schema.sql
```

## Step 3: Application Setup

### Create Application Directory

```bash
sudo mkdir -p /var/www/workverse
sudo chown -R $USER:$USER /var/www/workverse
cd /var/www/workverse
```

### Deploy Application Files

```bash
# Option 1: Upload files via SCP/SFTP
# Option 2: Clone from Git repository
git clone <your-repository-url> .

# Or copy files manually
```

### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
pip install gunicorn  # WSGI server
```

### Configure Application

Edit `config.py`:

```python
# Production configuration
DB_HOST = 'localhost'
DB_USER = 'workverse_user'
DB_PASSWORD = 'strong_password_here'
DB_NAME = 'workverse_db'

# Generate strong secret key
SECRET_KEY = 'generate-a-strong-random-key-here'

# Security settings
SESSION_COOKIE_SECURE = True  # Enable for HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

### Generate Secret Key

```python
# In Python shell
import os
print(os.urandom(24).hex())
```

## Step 4: Gunicorn Configuration

### Create Gunicorn Service File

```bash
sudo nano /etc/systemd/system/workverse.service
```

Add the following:

```ini
[Unit]
Description=Gunicorn instance to serve WorkVerse
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/workverse
Environment="PATH=/var/www/workverse/venv/bin"
ExecStart=/var/www/workverse/venv/bin/gunicorn --workers 3 --bind unix:workverse.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

### Set Permissions

```bash
sudo chown -R www-data:www-data /var/www/workverse
sudo chmod -R 755 /var/www/workverse
```

### Start and Enable Service

```bash
sudo systemctl start workverse
sudo systemctl enable workverse
sudo systemctl status workverse
```

## Step 5: Nginx Configuration

### Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/workverse
```

Add the following:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/workverse/workverse.sock;
    }

    location /static {
        alias /var/www/workverse/static;
    }

    location /uploads {
        alias /var/www/workverse/uploads;
    }

    client_max_body_size 16M;
}
```

### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/workverse /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## Step 6: SSL Certificate (Let's Encrypt)

### Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Obtain Certificate

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow the prompts to:
- Enter email address
- Agree to terms
- Choose to redirect HTTP to HTTPS

### Auto-renewal

Certbot automatically sets up renewal. Test it:

```bash
sudo certbot renew --dry-run
```

## Step 7: Firewall Configuration

```bash
# Allow SSH
sudo ufw allow OpenSSH

# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Enable firewall
sudo ufw enable
sudo ufw status
```

## Step 8: Security Hardening

### Update Admin Password

```bash
# Generate new password hash
cd /var/www/workverse
source venv/bin/activate
python generate_password_hash.py
```

Update in MySQL:

```sql
UPDATE users 
SET password = 'new_hash_here' 
WHERE email = 'admin@workverse.com';
```

### Set Proper File Permissions

```bash
# Application files
sudo chown -R www-data:www-data /var/www/workverse
sudo chmod -R 755 /var/www/workverse

# Uploads directory (write permission)
sudo chmod -R 775 /var/www/workverse/uploads
```

### Configure Fail2Ban (Optional)

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Step 9: Logging and Monitoring

### Application Logs

```bash
# View Gunicorn logs
sudo journalctl -u workverse -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Set Up Log Rotation

```bash
sudo nano /etc/logrotate.d/workverse
```

```
/var/log/workverse/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload workverse > /dev/null 2>&1
    endscript
}
```

## Step 10: Backup Strategy

### Database Backup Script

```bash
sudo nano /usr/local/bin/backup-workverse-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/workverse"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

mysqldump -u workverse_user -p'password' workverse_db > \
    $BACKUP_DIR/workverse_db_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

```bash
sudo chmod +x /usr/local/bin/backup-workverse-db.sh
```

### Schedule Daily Backups

```bash
sudo crontab -e
```

Add:

```
0 2 * * * /usr/local/bin/backup-workverse-db.sh
```

## Step 11: Maintenance

### Update Application

```bash
cd /var/www/workverse
source venv/bin/activate

# Pull latest changes
git pull

# Install any new dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart workverse
```

### Update SSL Certificate

```bash
sudo certbot renew
sudo systemctl reload nginx
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status workverse

# View logs
sudo journalctl -u workverse -n 50
```

### Database Connection Issues

```bash
# Test MySQL connection
mysql -u workverse_user -p workverse_db

# Check config.py settings
cat config.py
```

### Permission Errors

```bash
# Fix permissions
sudo chown -R www-data:www-data /var/www/workverse
sudo chmod -R 755 /var/www/workverse
sudo chmod -R 775 /var/www/workverse/uploads
```

### Nginx Errors

```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

## Performance Optimization

### Gunicorn Workers

Calculate optimal workers:

```
workers = (2 × CPU cores) + 1
```

Edit `/etc/systemd/system/workverse.service`:

```ini
ExecStart=/var/www/workverse/venv/bin/gunicorn --workers 5 --bind unix:workverse.sock -m 007 app:app
```

### MySQL Optimization

Edit `/etc/mysql/mysql.conf.d/mysqld.cnf`:

```ini
[mysqld]
max_connections = 100
innodb_buffer_pool_size = 256M
query_cache_size = 16M
```

### Nginx Caching

Add to Nginx configuration:

```nginx
location /static {
    alias /var/www/workverse/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

## Monitoring Checklist

- [ ] Server CPU and memory usage
- [ ] Disk space
- [ ] Database performance
- [ ] Application logs
- [ ] Error rates
- [ ] SSL certificate expiry
- [ ] Backup success
- [ ] Firewall status

## Security Checklist

- [ ] Changed default admin password
- [ ] Using strong SECRET_KEY
- [ ] HTTPS enabled
- [ ] Firewall configured
- [ ] Regular backups enabled
- [ ] File permissions correct
- [ ] MySQL secured
- [ ] Fail2Ban configured (optional)

---

## Quick Commands Reference

```bash
# Restart application
sudo systemctl restart workverse

# View logs
sudo journalctl -u workverse -f

# Reload Nginx
sudo systemctl reload nginx

# Backup database
sudo /usr/local/bin/backup-workverse-db.sh

# Update SSL
sudo certbot renew

# Check service status
sudo systemctl status workverse
sudo systemctl status nginx
sudo systemctl status mysql
```

---

**Note**: Replace `your-domain.com` with your actual domain name and update all passwords with strong, unique values.
