# WorkVerse - Job Role Simulation Platform

A comprehensive web-based learning platform that helps students understand real-world job roles through interactive simulations, quizzes, and practical assignments.

## Features

### For Users
- 🔐 Secure registration and login
- 📚 Interactive job role simulations with video tutorials
- 📝 Knowledge assessment through quizzes
- 📊 PPT assignment submissions
- 🏆 Digital certificates upon completion
- 📈 Progress tracking dashboard

### For Admins
- 👥 User management
- 🎯 Simulation content management
- ❓ Quiz question management
- ✅ Review and approve/reject submissions
- 📊 Analytics and reports
- 🎓 Certificate generation

## Technology Stack

- **Backend**: Python Flask 3.0.0
- **Database**: MySQL
- **Authentication**: Flask-Login
- **Frontend**: HTML5, CSS3, Bootstrap 5.3
- **JavaScript**: Vanilla JS
- **Security**: Werkzeug password hashing

## Project Structure

```
workverse/
│
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
│
├── database/
│   └── schema.sql         # Database schema and sample data
│
├── templates/
│   ├── base.html          # Base template
│   ├── home.html          # Home page
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # User dashboard
│   ├── simulation.html    # Simulation detail page
│   ├── quiz.html          # Quiz page
│   ├── upload_ppt.html    # PPT upload page
│   ├── certificate.html   # Certificate page
│   ├── admin_dashboard.html      # Admin dashboard
│   ├── manage_simulations.html   # Simulation management
│   ├── manage_quizzes.html       # Quiz management
│   ├── review_submissions.html   # Submission review
│   ├── manage_users.html         # User management
│   ├── 404.html           # 404 error page
│   └── 500.html           # 500 error page
│
├── static/
│   ├── css/
│   │   └── style.css      # Custom styles
│   └── js/
│       └── script.js      # Custom JavaScript
│
└── uploads/               # File upload directory (created automatically)
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project

```bash
cd workverse
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up MySQL Database

1. Start MySQL server
2. Create database and import schema:

```bash
# Login to MySQL
mysql -u root -p

# Import the schema
mysql -u root -p < database/schema.sql
```

Or manually:

```sql
-- Open MySQL and run:
source database/schema.sql
```

This will:
- Create the `workverse_db` database
- Create all required tables
- Insert sample simulations and quiz questions
- Create default admin account

### Step 5: Configure Database Connection

Edit `config.py` if needed to match your MySQL settings:

```python
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'password'  # Change to your MySQL password
DB_NAME = 'workverse_db'
```

### Step 6: Run the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000/`

## Default Login Credentials

### Admin Account
- **Email**: admin@workverse.com
- **Password**: admin123

### Create User Account
Register a new account at: `http://127.0.0.1:5000/register`

## Usage Guide

### For Users

1. **Register**: Create an account with name, email, and password
2. **Login**: Access your dashboard
3. **Browse Simulations**: View available job role simulations
4. **Enroll**: Click on a simulation to start learning
5. **Learn**: Watch videos and read learning content
6. **Take Quiz**: Complete the assessment (60% required to pass)
7. **Upload PPT**: Submit your assignment after passing the quiz
8. **Get Certificate**: Receive certificate after admin approval

### For Admins

1. **Login**: Use admin credentials
2. **Dashboard**: View statistics and recent activities
3. **Manage Simulations**: Add, edit, or delete simulations
4. **Manage Quizzes**: Add questions for each simulation
5. **Review Submissions**: Approve or reject user PPT submissions
6. **Manage Users**: View and manage registered users

## Database Schema

### Tables

1. **users** - User accounts (admin and regular users)
2. **simulations** - Job role simulation content
3. **quizzes** - Quiz questions for simulations
4. **progress** - User progress tracking
5. **submissions** - PPT file submissions

### Relationships

- One user can have multiple progress records
- One simulation can have multiple quiz questions
- One user can submit multiple assignments
- Foreign keys maintain referential integrity

## File Upload

- **Allowed Formats**: .ppt, .pptx
- **Max File Size**: 16MB
- **Upload Directory**: `/uploads`
- Files are automatically secured with unique names

## Security Features

- ✅ Password hashing using Werkzeug
- ✅ Session management with Flask-Login
- ✅ CSRF protection
- ✅ Secure file upload validation
- ✅ Role-based access control
- ✅ SQL injection prevention (parameterized queries)

## Configuration

### Environment Variables (Optional)

Create a `.env` file for production:

```env
SECRET_KEY=your-secret-key-here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_NAME=workverse_db
```

### Application Settings

Edit `config.py`:

```python
SECRET_KEY = 'your-secret-key'
QUIZ_PASS_PERCENTAGE = 60  # Minimum score to pass
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max upload size
```

## Troubleshooting

### Database Connection Error

```
Error: Can't connect to MySQL server
```

**Solution**: 
- Verify MySQL is running
- Check credentials in `config.py`
- Ensure `workverse_db` database exists

### Module Not Found

```
ModuleNotFoundError: No module named 'flask'
```

**Solution**:
```bash
pip install -r requirements.txt
```

### Upload Directory Error

```
FileNotFoundError: [Errno 2] No such file or directory: 'uploads'
```

**Solution**: The directory is created automatically, but you can create it manually:
```bash
mkdir uploads
```

### Port Already in Use

```
Address already in use
```

**Solution**: Change the port in `app.py`:
```python
app.run(debug=True, port=5001)
```

## Production Deployment

### Important Security Updates for Production

1. **Change Secret Key**:
   ```python
   SECRET_KEY = os.urandom(24)
   ```

2. **Disable Debug Mode**:
   ```python
   app.run(debug=False)
   ```

3. **Use Environment Variables**:
   - Store sensitive data in environment variables
   - Never commit credentials to version control

4. **Enable HTTPS**:
   - Use SSL certificates
   - Set `SESSION_COOKIE_SECURE = True`

5. **Update Admin Password**:
   - Change default admin password immediately

### Recommended Deployment Stack

- **Web Server**: Nginx
- **WSGI Server**: Gunicorn
- **Database**: MySQL 8.0+
- **SSL**: Let's Encrypt

## Features Breakdown

### Quiz System
- Multiple choice questions (4 options)
- Automatic scoring
- Pass/fail based on configurable threshold
- Retake capability

### Certificate System
- Printable certificates
- Unique certificate IDs
- Completion date tracking
- Professional design

### Progress Tracking
- Enrollment status
- Quiz scores
- Submission status
- Completion tracking

## Browser Compatibility

- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers

## Support

For issues or questions:
1. Check troubleshooting section
2. Review database schema
3. Verify all dependencies are installed
4. Check MySQL connection settings

## License

This project is created for educational purposes.

## Credits

- **Framework**: Flask
- **UI**: Bootstrap 5
- **Icons**: Bootstrap Icons
- **Database**: MySQL

---

## Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up database
mysql -u root -p < database/schema.sql

# 3. Run application
python app.py

# 4. Access application
# Open browser: http://127.0.0.1:5000

# 5. Login as admin
# Email: admin@workverse.com
# Password: admin123
```

---

**WorkVerse** - Empowering careers through simulation. Learn | Practice | Certify
