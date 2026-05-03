from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import pymysql
import os
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Database connection helper
def get_db_connection():
    """Create and return MySQL database connection"""
    return pymysql.connect(
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DB_NAME'],
        cursorclass=pymysql.cursors.DictCursor
    )

# ============================================
# NOTIFICATION HELPER FUNCTIONS (V1.2)
# ============================================

def create_user_notification(user_id, message, notification_type='info'):
    """Create notification for user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO notifications (user_id, message, type)
        VALUES (%s, %s, %s)
    ''', (user_id, message, notification_type))
    conn.commit()
    conn.close()

def get_user_notifications(user_id, unread_only=False):
    """Get user notifications"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if unread_only:
        cursor.execute('''
            SELECT * FROM notifications 
            WHERE user_id = %s AND is_read = FALSE 
            ORDER BY created_at DESC
        ''', (user_id,))
    else:
        cursor.execute('''
            SELECT * FROM notifications 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 20
        ''', (user_id,))
    notifications = cursor.fetchall()
    conn.close()
    return notifications

def mark_notifications_read(user_id):
    """Mark all user notifications as read"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE notifications 
        SET is_read = TRUE 
        WHERE user_id = %s AND is_read = FALSE
    ''', (user_id,))
    conn.commit()
    conn.close()

def get_unread_count(user_id):
    """Get count of unread notifications"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) as count 
        FROM notifications 
        WHERE user_id = %s AND is_read = FALSE
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result['count'] if result else 0

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, name, email, role):
        self.id = id
        self.name = name
        self.email = email
        self.role = role
    
    def is_admin(self):
        return self.role == 'admin'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(user_data['id'], user_data['name'], user_data['email'], user_data['role'])
    return None

# Admin required decorator
def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# File upload helper
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ============================================
# CONTEXT PROCESSOR (V1.2)
# ============================================

@app.context_processor
def inject_notifications():
    """Inject notification count into all templates"""
    if current_user.is_authenticated:
        unread_count = get_unread_count(current_user.id)
        return dict(unread_notifications_count=unread_count)
    return dict(unread_notifications_count=0)

# ============================================
# PUBLIC ROUTES
# ============================================

@app.route('/')
def home():
    """Home page"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM simulations ORDER BY created_at DESC LIMIT 4')
    simulations = cursor.fetchall()
    conn.close()
    return render_template('home.html', simulations=simulations)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            flash('Email already registered. Please login.', 'danger')
            conn.close()
            return render_template('register.html')
        
        # Hash password and insert user
        hashed_password = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)',
            (name, email, hashed_password, 'user')
        )
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data['id'], user_data['name'], user_data['email'], user_data['role'])
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            
            # Redirect based on role
            if user.is_admin():
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

# ============================================
# USER ROUTES
# ============================================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all simulations
    cursor.execute('SELECT * FROM simulations ORDER BY created_at DESC')
    all_simulations = cursor.fetchall()
    
    # Get user's progress
    cursor.execute('''
        SELECT p.*, s.title, s.description 
        FROM progress p
        JOIN simulations s ON p.simulation_id = s.id
        WHERE p.user_id = %s
    ''', (current_user.id,))
    user_progress = cursor.fetchall()
    
    # Get pending submissions
    cursor.execute('''
        SELECT sub.*, s.title 
        FROM submissions sub
        JOIN simulations s ON sub.simulation_id = s.id
        WHERE sub.user_id = %s AND sub.status = 'pending'
    ''', (current_user.id,))
    pending_submissions = cursor.fetchall()
    
    # Get certificates (approved submissions)
    cursor.execute('''
        SELECT sub.*, s.title, s.description, p.completed_at
        FROM submissions sub
        JOIN simulations s ON sub.simulation_id = s.id
        JOIN progress p ON p.user_id = sub.user_id AND p.simulation_id = sub.simulation_id
        WHERE sub.user_id = %s AND sub.status = 'approved'
    ''', (current_user.id,))
    certificates = cursor.fetchall()
    
    conn.close()
    
    # Create a set of simulation IDs user has enrolled in
    enrolled_ids = {p['simulation_id'] for p in user_progress}
    
    return render_template('dashboard.html', 
                         simulations=all_simulations,
                         user_progress=user_progress,
                         pending_submissions=pending_submissions,
                         certificates=certificates,
                         enrolled_ids=enrolled_ids)

@app.route('/simulation/<int:simulation_id>')
@login_required
def simulation(simulation_id):
    """View simulation details and enroll"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get simulation details
    cursor.execute('SELECT * FROM simulations WHERE id = %s', (simulation_id,))
    simulation = cursor.fetchone()
    
    if not simulation:
        flash('Simulation not found.', 'danger')
        conn.close()
        return redirect(url_for('dashboard'))
    
    # Get lessons for this simulation
    cursor.execute('''
        SELECT * FROM lessons 
        WHERE simulation_id = %s 
        ORDER BY lesson_order
    ''', (simulation_id,))
    lessons = cursor.fetchall()
    
    # Check if user has progress for this simulation
    cursor.execute('''
        SELECT * FROM progress 
        WHERE user_id = %s AND simulation_id = %s
    ''', (current_user.id, simulation_id))
    progress = cursor.fetchone()
    
    # If no progress, create enrollment
    if not progress:
        cursor.execute('''
            INSERT INTO progress (user_id, simulation_id, status)
            VALUES (%s, %s, 'enrolled')
        ''', (current_user.id, simulation_id))
        conn.commit()
        
        cursor.execute('''
            SELECT * FROM progress 
            WHERE user_id = %s AND simulation_id = %s
        ''', (current_user.id, simulation_id))
        progress = cursor.fetchone()
    
    conn.close()
    
    return render_template('simulation.html', simulation=simulation, progress=progress, lessons=lessons)

@app.route('/quiz/<int:simulation_id>', methods=['GET', 'POST'])
@login_required
def quiz(simulation_id):
    """Take quiz - FIXED V1.2: Always allows retakes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get simulation details
    cursor.execute('SELECT * FROM simulations WHERE id = %s', (simulation_id,))
    simulation = cursor.fetchone()
    
    if not simulation:
        flash('Simulation not found.', 'danger')
        conn.close()
        return redirect(url_for('dashboard'))
    
    # Get progress
    cursor.execute('''
        SELECT * FROM progress 
        WHERE user_id = %s AND simulation_id = %s
    ''', (current_user.id, simulation_id))
    progress = cursor.fetchone()
    
    if not progress:
        flash('You must enroll in this simulation first.', 'warning')
        conn.close()
        return redirect(url_for('simulation', simulation_id=simulation_id))
    
    # Get quiz questions
    cursor.execute('SELECT * FROM quizzes WHERE simulation_id = %s', (simulation_id,))
    questions = cursor.fetchall()
    
    if not questions:
        flash('No quiz available for this simulation.', 'info')
        conn.close()
        return redirect(url_for('simulation', simulation_id=simulation_id))
    
    if request.method == 'POST':
        # Calculate score
        correct_answers = 0
        total_questions = len(questions)
        
        for question in questions:
            user_answer = request.form.get(f'question_{question["id"]}')
            if user_answer == question['correct_answer']:
                correct_answers += 1
        
        score = int((correct_answers / total_questions) * 100)
        
        # Get simulation passing percentage
        passing_percentage = simulation['passing_percentage']
        
        # Update progress
        cursor.execute('''
            UPDATE progress 
            SET score = %s, status = 'quiz_completed'
            WHERE user_id = %s AND simulation_id = %s
        ''', (score, current_user.id, simulation_id))
        conn.commit()
        conn.close()
        
        if score >= passing_percentage:
            flash(f'Congratulations! You scored {score}%. You can now upload your PPT assignment.', 'success')
            return redirect(url_for('upload_ppt', simulation_id=simulation_id))
        else:
            flash(f'You scored {score}%. You need at least {passing_percentage}% to pass. You can retake the quiz anytime!', 'warning')
            return redirect(url_for('simulation', simulation_id=simulation_id))
    
    conn.close()
    return render_template('quiz.html', simulation=simulation, questions=questions, progress=progress)

@app.route('/upload_ppt/<int:simulation_id>', methods=['GET', 'POST'])
@login_required
def upload_ppt(simulation_id):
    """Upload PPT assignment - FIXED V1.2: Allows resubmission after rejection"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get simulation
    cursor.execute('SELECT * FROM simulations WHERE id = %s', (simulation_id,))
    simulation = cursor.fetchone()
    
    if not simulation:
        flash('Simulation not found.', 'danger')
        conn.close()
        return redirect(url_for('dashboard'))
    
    # Check progress - must have passed quiz
    cursor.execute('''
        SELECT * FROM progress 
        WHERE user_id = %s AND simulation_id = %s
    ''', (current_user.id, simulation_id))
    progress = cursor.fetchone()
    
    passing_percentage = simulation['passing_percentage']
    
    if not progress or progress['score'] < passing_percentage:
        flash(f'You must pass the quiz with {passing_percentage}% or higher to upload assignment.', 'warning')
        conn.close()
        return redirect(url_for('simulation', simulation_id=simulation_id))
    
    # Check for existing submission
    cursor.execute('''
        SELECT * FROM submissions 
        WHERE user_id = %s AND simulation_id = %s
        ORDER BY submitted_at DESC
        LIMIT 1
    ''', (current_user.id, simulation_id))
    existing_submission = cursor.fetchone()
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'ppt_file' not in request.files:
            flash('No file selected.', 'danger')
            conn.close()
            return redirect(request.url)
        
        file = request.files['ppt_file']
        
        if file.filename == '':
            flash('No file selected.', 'danger')
            conn.close()
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{current_user.id}_{timestamp}_{filename}"
            
            # Ensure upload folder exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save file
            file.save(filepath)
            
            # Check if this is a resubmission
            is_resubmission = existing_submission and existing_submission['status'] == 'rejected'
            resubmission_count = existing_submission['resubmission_count'] + 1 if is_resubmission else 0
            
            if is_resubmission:
                # Update existing submission
                cursor.execute('''
                    UPDATE submissions 
                    SET ppt_file = %s, status = 'pending', feedback = NULL, 
                        submitted_at = NOW(), reviewed_at = NULL, 
                        resubmission_count = %s, is_new_submission = TRUE
                    WHERE user_id = %s AND simulation_id = %s
                ''', (filename, resubmission_count, current_user.id, simulation_id))
            else:
                # Create new submission
                cursor.execute('''
                    INSERT INTO submissions (user_id, simulation_id, ppt_file, status, resubmission_count, is_new_submission)
                    VALUES (%s, %s, %s, 'pending', %s, TRUE)
                ''', (current_user.id, simulation_id, filename, resubmission_count))
            
            # Update progress
            cursor.execute('''
                UPDATE progress 
                SET status = 'submitted'
                WHERE user_id = %s AND simulation_id = %s
            ''', (current_user.id, simulation_id))
            
            conn.commit()
            
            if is_resubmission:
                flash('Assignment resubmitted successfully! Admin will review it soon.', 'success')
            else:
                flash('Assignment submitted successfully! Admin will review it soon.', 'success')
            
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid file type. Only PPT/PPTX files are allowed.', 'danger')
    
    conn.close()
    return render_template('upload_ppt.html', simulation=simulation, progress=progress,existing_submission=existing_submission)

@app.route('/certificate/<int:simulation_id>')
@login_required
def certificate(simulation_id):
    """View certificate"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get approved submission
    cursor.execute('''
        SELECT sub.*, s.title, s.description, p.completed_at, p.score
        FROM submissions sub
        JOIN simulations s ON sub.simulation_id = s.id
        JOIN progress p ON p.user_id = sub.user_id AND p.simulation_id = sub.simulation_id
        WHERE sub.user_id = %s AND sub.simulation_id = %s AND sub.status = 'approved'
    ''', (current_user.id, simulation_id))
    submission = cursor.fetchone()
    
    conn.close()
    
    if not submission:
        flash('Certificate not available. Your submission must be approved first.', 'warning')
        return redirect(url_for('dashboard'))
    
    return render_template('certificate.html', 
                         simulation=submission,
                         user_name=current_user.name,
                         completion_date=submission['completed_at'] or datetime.now())

# ============================================
# ADMIN ROUTES
# ============================================

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "user"')
    total_users = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM simulations')
    total_simulations = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM submissions WHERE status = "pending"')
    pending_submissions = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM submissions WHERE status = "approved"')
    approved_certificates = cursor.fetchone()['count']
    
    # Get recent submissions
    cursor.execute('''
        SELECT sub.*, u.name as user_name, s.title as simulation_title
        FROM submissions sub
        JOIN users u ON sub.user_id = u.id
        JOIN simulations s ON sub.simulation_id = s.id
        ORDER BY sub.submitted_at DESC
        LIMIT 10
    ''')
    recent_submissions = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_simulations=total_simulations,
                         pending_submissions=pending_submissions,
                         approved_certificates=approved_certificates,
                         recent_submissions=recent_submissions)

@app.route('/admin/simulations', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_simulations():
    """Manage simulations"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            title = request.form.get('title')
            description = request.form.get('description')
            content = request.form.get('content')
            video_url = request.form.get('video_url')
            passing_percentage = request.form.get('passing_percentage', 60)
            
            cursor.execute('''
                INSERT INTO simulations (title, description, content, video_url, passing_percentage)
                VALUES (%s, %s, %s, %s, %s)
            ''', (title, description, content, video_url, passing_percentage))
            conn.commit()
            flash('Simulation added successfully!', 'success')
        
        elif action == 'edit':
            sim_id = request.form.get('simulation_id')
            title = request.form.get('title')
            description = request.form.get('description')
            content = request.form.get('content')
            video_url = request.form.get('video_url')
            passing_percentage = request.form.get('passing_percentage', 60)
            
            cursor.execute('''
                UPDATE simulations 
                SET title = %s, description = %s, content = %s, video_url = %s, passing_percentage = %s
                WHERE id = %s
            ''', (title, description, content, video_url, passing_percentage, sim_id))
            conn.commit()
            flash('Simulation updated successfully!', 'success')
        
        elif action == 'delete':
            sim_id = request.form.get('simulation_id')
            cursor.execute('DELETE FROM simulations WHERE id = %s', (sim_id,))
            conn.commit()
            flash('Simulation deleted successfully!', 'success')
    
    cursor.execute('SELECT * FROM simulations ORDER BY created_at DESC')
    simulations = cursor.fetchall()
    conn.close()
    
    return render_template('manage_simulations.html', simulations=simulations)

@app.route('/admin/quizzes/<int:simulation_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_quizzes(simulation_id):
    """Manage quizzes for a simulation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get simulation
    cursor.execute('SELECT * FROM simulations WHERE id = %s', (simulation_id,))
    simulation = cursor.fetchone()
    
    if not simulation:
        flash('Simulation not found.', 'danger')
        conn.close()
        return redirect(url_for('manage_simulations'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            question = request.form.get('question')
            option1 = request.form.get('option1')
            option2 = request.form.get('option2')
            option3 = request.form.get('option3')
            option4 = request.form.get('option4')
            correct_answer = request.form.get('correct_answer')
            
            cursor.execute('''
                INSERT INTO quizzes (simulation_id, question, option1, option2, option3, option4, correct_answer)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (simulation_id, question, option1, option2, option3, option4, correct_answer))
            conn.commit()
            flash('Quiz question added successfully!', 'success')
        
        elif action == 'edit':
            quiz_id = request.form.get('quiz_id')
            question = request.form.get('question')
            option1 = request.form.get('option1')
            option2 = request.form.get('option2')
            option3 = request.form.get('option3')
            option4 = request.form.get('option4')
            correct_answer = request.form.get('correct_answer')
            
            cursor.execute('''
                UPDATE quizzes 
                SET question = %s, option1 = %s, option2 = %s, option3 = %s, option4 = %s, correct_answer = %s
                WHERE id = %s
            ''', (question, option1, option2, option3, option4, correct_answer, quiz_id))
            conn.commit()
            flash('Quiz question updated successfully!', 'success')
        
        elif action == 'delete':
            quiz_id = request.form.get('quiz_id')
            cursor.execute('DELETE FROM quizzes WHERE id = %s', (quiz_id,))
            conn.commit()
            flash('Quiz question deleted successfully!', 'success')
    
    cursor.execute('SELECT * FROM quizzes WHERE simulation_id = %s', (simulation_id,))
    quizzes = cursor.fetchall()
    conn.close()
    
    return render_template('manage_quizzes.html', simulation=simulation, quizzes=quizzes)

@app.route('/admin/lessons/<int:simulation_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_lessons(simulation_id):
    """Manage lessons for a simulation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get simulation
    cursor.execute('SELECT * FROM simulations WHERE id = %s', (simulation_id,))
    simulation = cursor.fetchone()
    
    if not simulation:
        flash('Simulation not found.', 'danger')
        conn.close()
        return redirect(url_for('manage_simulations'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            title = request.form.get('title')
            content = request.form.get('content')
            video_url = request.form.get('video_url')
            lesson_order = request.form.get('lesson_order', 0)
            
            cursor.execute('''
                INSERT INTO lessons (simulation_id, title, content, video_url, lesson_order)
                VALUES (%s, %s, %s, %s, %s)
            ''', (simulation_id, title, content, video_url, lesson_order))
            conn.commit()
            flash('Lesson added successfully!', 'success')
        
        elif action == 'edit':
            lesson_id = request.form.get('lesson_id')
            title = request.form.get('title')
            content = request.form.get('content')
            video_url = request.form.get('video_url')
            lesson_order = request.form.get('lesson_order', 0)
            
            cursor.execute('''
                UPDATE lessons 
                SET title = %s, content = %s, video_url = %s, lesson_order = %s
                WHERE id = %s
            ''', (title, content, video_url, lesson_order, lesson_id))
            conn.commit()
            flash('Lesson updated successfully!', 'success')
        
        elif action == 'delete':
            lesson_id = request.form.get('lesson_id')
            cursor.execute('DELETE FROM lessons WHERE id = %s', (lesson_id,))
            conn.commit()
            flash('Lesson deleted successfully!', 'success')
    
    cursor.execute('SELECT * FROM lessons WHERE simulation_id = %s ORDER BY lesson_order', (simulation_id,))
    lessons = cursor.fetchall()
    conn.close()
    
    return render_template('manage_lessons.html', simulation=simulation, lessons=lessons)

@app.route('/admin/submissions', methods=['GET', 'POST'])
@login_required
@admin_required
def review_submissions():
    """Review PPT submissions - FIXED V1.2: Allows re-approval/rejection & notifications"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        submission_id = request.form.get('submission_id')
        action = request.form.get('action')
        feedback = request.form.get('feedback', '')
        
        # Get submission details
        cursor.execute('SELECT user_id, simulation_id, status FROM submissions WHERE id = %s', (submission_id,))
        sub = cursor.fetchone()
        
        if not sub:
            flash('Submission not found.', 'danger')
            conn.close()
            return redirect(url_for('review_submissions'))
        
        if action == 'approve':
            # Update submission status
            cursor.execute('''
                UPDATE submissions 
                SET status = 'approved', feedback = %s, reviewed_at = NOW(), is_new_submission = FALSE
                WHERE id = %s
            ''', (feedback, submission_id))
            
            # Update progress to completed
            cursor.execute('''
                UPDATE progress 
                SET status = 'completed', completed_at = NOW()
                WHERE user_id = %s AND simulation_id = %s
            ''', (sub['user_id'], sub['simulation_id']))
            
            conn.commit()
            
            # Send notification to user
            cursor.execute('SELECT title FROM simulations WHERE id = %s', (sub['simulation_id'],))
            sim = cursor.fetchone()
            message = f'Congratulations! Your submission for "{sim["title"]}" has been approved. Your certificate is now available.'
            create_user_notification(sub['user_id'], message, 'success')
            
            flash('Submission approved successfully! User has been notified.', 'success')
        
        elif action == 'reject':
            # Update submission status (allow resubmission)
            cursor.execute('''
                UPDATE submissions 
                SET status = 'rejected', feedback = %s, reviewed_at = NOW(), is_new_submission = FALSE
                WHERE id = %s
            ''', (feedback, submission_id))
            
            # Update progress back to quiz_completed (allow resubmission)
            cursor.execute('''
                UPDATE progress 
                SET status = 'quiz_completed'
                WHERE user_id = %s AND simulation_id = %s
            ''', (sub['user_id'], sub['simulation_id']))
            
            conn.commit()
            
            # Send notification to user
            cursor.execute('SELECT title FROM simulations WHERE id = %s', (sub['simulation_id'],))
            sim = cursor.fetchone()
            message = f'Your submission for "{sim["title"]}" needs revision. Feedback: {feedback}. You can resubmit your work.'
            create_user_notification(sub['user_id'], message, 'warning')
            
            flash('Submission rejected. User has been notified and can resubmit.', 'warning')
    
    # Get all submissions with new submission indicator
    cursor.execute('''
        SELECT sub.*, u.name as user_name, u.email, s.title as simulation_title,
               sub.is_new_submission, sub.resubmission_count
        FROM submissions sub
        JOIN users u ON sub.user_id = u.id
        JOIN simulations s ON sub.simulation_id = s.id
        ORDER BY 
            sub.is_new_submission DESC,
            CASE sub.status 
                WHEN 'pending' THEN 1
                WHEN 'approved' THEN 2
                WHEN 'rejected' THEN 3
            END,
            sub.submitted_at DESC
    ''')
    submissions = cursor.fetchall()
    conn.close()
    
    return render_template('review_submissions.html', submissions=submissions)

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_users():
    """Manage users"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        
        if action == 'delete' and int(user_id) != current_user.id:
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
            conn.commit()
            flash('User deleted successfully!', 'success')
    
    # Get all users with their progress
    cursor.execute('''
        SELECT u.*, 
               COUNT(DISTINCT p.simulation_id) as enrolled_count,
               COUNT(DISTINCT CASE WHEN sub.status = 'approved' THEN sub.id END) as completed_count
        FROM users u
        LEFT JOIN progress p ON u.id = p.user_id
        LEFT JOIN submissions sub ON u.id = sub.user_id
        WHERE u.role = 'user'
        GROUP BY u.id
        ORDER BY u.created_at DESC
    ''')
    users = cursor.fetchall()
    conn.close()
    
    return render_template('manage_users.html', users=users)

# ============================================
# NEW ROUTES V1.2 - NOTIFICATIONS & EDITING
# ============================================

@app.route('/notifications')
@login_required
def notifications():
    """View user notifications"""
    notifications = get_user_notifications(current_user.id)
    mark_notifications_read(current_user.id)
    return render_template('notifications.html', notifications=notifications)

@app.route('/admin/quiz/edit/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_quiz_question(quiz_id):
    """Edit quiz question"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        question = request.form.get('question')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_answer = request.form.get('correct_answer')
        
        cursor.execute('''
            UPDATE quizzes 
            SET question = %s, option1 = %s, option2 = %s, option3 = %s, 
                option4 = %s, correct_answer = %s
            WHERE id = %s
        ''', (question, option1, option2, option3, option4, correct_answer, quiz_id))
        conn.commit()
        
        # Get simulation_id to redirect back
        cursor.execute('SELECT simulation_id FROM quizzes WHERE id = %s', (quiz_id,))
        result = cursor.fetchone()
        conn.close()
        
        flash('Quiz question updated successfully!', 'success')
        return redirect(url_for('manage_quizzes', simulation_id=result['simulation_id']))
    
    # GET request - show edit form
    cursor.execute('SELECT * FROM quizzes WHERE id = %s', (quiz_id,))
    quiz = cursor.fetchone()
    conn.close()
    
    if not quiz:
        flash('Quiz question not found.', 'danger')
        return redirect(url_for('manage_simulations'))
    
    return render_template('edit_quiz.html', quiz=quiz)

@app.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role')
        
        # Check if email already exists for another user
        cursor.execute('SELECT id FROM users WHERE email = %s AND id != %s', (email, user_id))
        if cursor.fetchone():
            flash('Email already exists!', 'danger')
            conn.close()
            return redirect(request.url)
        
        cursor.execute('''
            UPDATE users 
            SET name = %s, email = %s, role = %s
            WHERE id = %s
        ''', (name, email, role, user_id))
        conn.commit()
        conn.close()
        
        flash('User information updated successfully!', 'success')
        return redirect(url_for('manage_users'))
    
    # GET request - show edit form
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('manage_users'))
    
    return render_template('edit_user.html', user=user)

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
