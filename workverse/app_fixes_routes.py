# WorkVerse - Route Fixes
# Replace/update these routes in app.py

# ============================================
# UPDATED: REVIEW SUBMISSIONS (ALLOWS RE-APPROVAL)
# ============================================

@app.route('/admin/submissions', methods=['GET', 'POST'])
@login_required
@admin_required
def review_submissions():
    """Review PPT submissions - FIXED: Allows re-approval/rejection"""
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

# ============================================
# UPDATED: UPLOAD PPT (ALLOWS RESUBMISSION)
# ============================================

@app.route('/upload_ppt/<int:simulation_id>', methods=['GET', 'POST'])
@login_required
def upload_ppt(simulation_id):
    """Upload PPT assignment - FIXED: Allows resubmission after rejection"""
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
    return render_template('upload_ppt.html', simulation=simulation, existing_submission=existing_submission)

# ============================================
# UPDATED: QUIZ (ALLOWS RETAKES)
# ============================================

@app.route('/quiz/<int:simulation_id>', methods=['GET', 'POST'])
@login_required
def quiz(simulation_id):
    """Take quiz - FIXED: Always allows retakes"""
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

# ============================================
# NEW: NOTIFICATIONS ROUTE
# ============================================

@app.route('/notifications')
@login_required
def notifications():
    """View user notifications"""
    notifications = get_user_notifications(current_user.id)
    mark_notifications_read(current_user.id)
    return render_template('notifications.html', notifications=notifications)

# ============================================
# NEW: EDIT QUIZ QUESTIONS
# ============================================

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

# ============================================
# NEW: EDIT USER INFORMATION
# ============================================

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
