# WorkVerse - Version 1.2 Critical Fixes Update Guide

## 🚨 Issues Fixed in This Update

This update resolves three critical issues reported in WorkVerse v1.1:

### ✅ Issue 1: Admin Cannot Re-Approve/Re-Reject Submissions
**Problem:** Once admin approved or rejected a submission, they couldn't change the status.
**Solution:** Admin can now approve or reject submissions at any time, even after initial review.

### ✅ Issue 2: Users Cannot Retake Quiz or Resubmit PPT After Rejection
**Problem:** Users were blocked from retaking quizzes and resubmitting assignments after rejection.
**Solution:** 
- Users can now retake quizzes unlimited times
- Users can resubmit PPT files after rejection
- Users receive notifications when admin reviews their work
- Admin gets "NEW" indicators for resubmissions

### ✅ Issue 3: Admin Cannot Edit Quiz Questions or User Information
**Problem:** No interface to edit existing quiz questions or user details.
**Solution:**
- Added edit functionality for quiz questions
- Added edit functionality for user information (name, email, role)
- Separate edit pages with proper validation

---

## 📦 What's New in Version 1.2

### New Features:
1. **Notification System** - Users get real-time notifications for submission reviews
2. **Resubmission Tracking** - Track how many times users have resubmitted
3. **NEW Submission Indicators** - Admins see animated badges for new submissions
4. **Quiz Editing** - Edit questions, options, and correct answers
5. **User Editing** - Modify user details and roles
6. **Unlimited Quiz Retakes** - Users can improve their scores anytime
7. **Flexible Submission Reviews** - Admins can change review decisions

### New Database Tables:
- `notifications` - Stores user notifications
- `admin_notifications` - Tracks admin notifications

### New Database Columns:
- `submissions.resubmission_count` - Tracks resubmission attempts
- `submissions.is_new_submission` - Flags new submissions for admin

### New Routes:
- `/notifications` - View user notifications
- `/admin/quiz/edit/<quiz_id>` - Edit quiz questions
- `/admin/user/edit/<user_id>` - Edit user information

---

## 🔧 Installation Steps

### Step 1: Backup Your Data

**CRITICAL: Always backup before updating!**

```bash
# Backup database
mysqldump -u root -p workverse_db > workverse_backup_$(date +%Y%m%d_%H%M%S).sql

# Backup files
cp -r workverse workverse_backup_$(date +%Y%m%d_%H%M%S)
```

### Step 2: Stop the Application

```bash
# If running, stop the Flask app (Ctrl+C)
# Or kill the process
pkill -f "python app.py"
```

### Step 3: Update Database Schema

```bash
# Navigate to project directory
cd /path/to/workverse

# Run the update script
mysql -u root -p workverse_db < database/update_v1.2.sql
```

**Verify the update:**
```bash
mysql -u root -p workverse_db -e "SHOW TABLES;"
# Should see: notifications, admin_notifications

mysql -u root -p workverse_db -e "DESCRIBE submissions;"
# Should see: resubmission_count, is_new_submission columns
```

### Step 4: Update Application Files

#### A. Update app.py

Add the following helper functions after your imports and before routes:

```python
# Add these helper functions from app_fixes_helpers.py
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

# Add context processor
@app.context_processor
def inject_notifications():
    """Inject notification count into all templates"""
    if current_user.is_authenticated:
        unread_count = get_unread_count(current_user.id)
        return dict(unread_notifications_count=unread_count)
    return dict(unread_notifications_count=0)
```

#### B. Replace Routes

Replace these routes with the updated versions from `app_fixes_routes.py`:

1. **review_submissions** (line ~691)
2. **upload_ppt** (line ~382)
3. **quiz** (line ~310)

And add these NEW routes:

4. **notifications** (new route)
5. **edit_quiz_question** (new route)
6. **edit_user** (new route)

**See `app_fixes_routes.py` for complete code.**

#### C. Update Templates

1. **Replace** `templates/review_submissions.html` with `review_submissions_fixed.html`

2. **Update** `templates/manage_quizzes.html` - Line ~74-83:
   Replace button group with:
   ```html
   <div class="btn-group ms-3">
       <a href="{{ url_for('edit_quiz_question', quiz_id=quiz.id) }}" 
          class="btn btn-sm btn-outline-primary">
           <i class="bi bi-pencil"></i> Edit
       </a>
       <button class="btn btn-sm btn-outline-danger" 
               onclick="deleteQuiz({{ quiz.id }})">
           <i class="bi bi-trash"></i>
       </button>
   </div>
   ```

3. **Update** `templates/manage_users.html` - Line ~53-58:
   Replace actions column with:
   ```html
   <td>
       <div class="btn-group" role="group">
           <a href="{{ url_for('edit_user', user_id=user.id) }}" 
              class="btn btn-sm btn-outline-primary">
               <i class="bi bi-pencil"></i> Edit
           </a>
           <button class="btn btn-sm btn-outline-danger" 
                   onclick="deleteUser({{ user.id }}, '{{ user.name }}')">
               <i class="bi bi-trash"></i> Delete
           </button>
       </div>
   </td>
   ```

4. **Update** `templates/base.html` - Line ~32-56:
   Add notification bell before user dropdown (see `base_navbar_notification_fix.txt`)

5. **Add NEW templates:**
   - `templates/notifications.html`
   - `templates/edit_quiz.html`
   - `templates/edit_user.html`

### Step 5: Test the Updates

```bash
# Start the application
python app.py
```

**Test Checklist:**

#### Test 1: Notification System
- [ ] Login as user
- [ ] Check notification bell in navbar
- [ ] Submit a PPT
- [ ] Login as admin and reject it with feedback
- [ ] Login as user again
- [ ] See notification bell with badge (1)
- [ ] Click notifications - see rejection message

#### Test 2: Resubmission Flow
- [ ] Login as user with rejected submission
- [ ] Can retake quiz (scores update)
- [ ] Can reupload PPT file
- [ ] Admin sees "NEW" badge with animation
- [ ] Admin sees "Resubmission #1" indicator
- [ ] Admin can approve the resubmission

#### Test 3: Re-Approval/Re-Rejection
- [ ] Login as admin
- [ ] Find approved submission
- [ ] Click "Re-Reject" - status changes
- [ ] Click "Re-Approve" - status changes back
- [ ] User gets notification each time

#### Test 4: Edit Quiz Question
- [ ] Login as admin
- [ ] Go to Manage Simulations
- [ ] Click "Quizzes" for any simulation
- [ ] Click "Edit" button on a question
- [ ] Modify question text, options, correct answer
- [ ] Save changes
- [ ] Verify changes appear in quiz

#### Test 5: Edit User Information
- [ ] Login as admin
- [ ] Go to Manage Users
- [ ] Click "Edit" button on a user
- [ ] Change name, email, or role
- [ ] Save changes
- [ ] Verify changes in user list

---

## 📝 Detailed Change Log

### Database Changes

**New Tables:**
```sql
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    type ENUM('info', 'success', 'warning', 'danger') DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE admin_notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE
);
```

**Modified Tables:**
```sql
ALTER TABLE submissions 
ADD COLUMN resubmission_count INT DEFAULT 0,
ADD COLUMN is_new_submission BOOLEAN DEFAULT TRUE;
```

### Application Logic Changes

#### review_submissions Route
- **Old:** Status could only be set once
- **New:** Status can be changed anytime (approve → reject → approve)
- **New:** Creates user notifications on status change
- **New:** Sets `is_new_submission = FALSE` after review
- **New:** Allows users to resubmit after rejection

#### upload_ppt Route
- **Old:** Blocked resubmission after any submission
- **New:** Checks for rejected status and allows resubmission
- **New:** Increments `resubmission_count` on resubmission
- **New:** Sets `is_new_submission = TRUE` for admin notification
- **New:** Updates existing submission record instead of creating duplicate

#### quiz Route
- **Old:** Not explicitly clear if retakes were allowed
- **New:** Explicitly allows unlimited retakes
- **New:** Updates score each time quiz is taken
- **New:** No restrictions on retaking

---

## 🆘 Troubleshooting

### Issue: Database update fails
**Solution:**
```bash
# Check if tables already exist
mysql -u root -p workverse_db -e "SHOW TABLES;"

# If notifications table exists, update script may have run already
# Check columns exist:
mysql -u root -p workverse_db -e "DESCRIBE submissions;"
```

### Issue: Import errors for new functions
**Solution:** Make sure all helper functions are added to app.py before the routes.

### Issue: Template errors (variable not found)
**Solution:** Ensure `@app.context_processor inject_notifications()` is added to app.py.

### Issue: Notification count not showing
**Solution:**
```python
# Verify context processor is working
@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        unread_count = get_unread_count(current_user.id)
        print(f"Unread count for {current_user.id}: {unread_count}")  # Debug
        return dict(unread_notifications_count=unread_count)
    return dict(unread_notifications_count=0)
```

### Issue: Routes not found (404 error)
**Solution:** Make sure all new routes are added to app.py:
- `/notifications`
- `/admin/quiz/edit/<int:quiz_id>`
- `/admin/user/edit/<int:user_id>`

---

## 🔄 Rollback Instructions

If you need to rollback:

### Step 1: Restore Database
```bash
mysql -u root -p workverse_db < workverse_backup_YYYYMMDD_HHMMSS.sql
```

### Step 2: Restore Files
```bash
rm -rf workverse
cp -r workverse_backup_YYYYMMDD_HHMMSS workverse
```

### Step 3: Restart Application
```bash
cd workverse
python app.py
```

---

## 📋 File Checklist

Files included in this update:

**Database:**
- ✅ `database/update_v1.2.sql` - Schema updates

**Application Code:**
- ✅ `app_fixes_helpers.py` - Helper functions to add
- ✅ `app_fixes_routes.py` - Updated and new routes

**Templates:**
- ✅ `templates/review_submissions_fixed.html` - Replace existing
- ✅ `templates/notifications.html` - NEW
- ✅ `templates/edit_quiz.html` - NEW
- ✅ `templates/edit_user.html` - NEW
- ✅ `manage_quizzes_button_fix.txt` - Update guide
- ✅ `manage_users_button_fix.txt` - Update guide
- ✅ `base_navbar_notification_fix.txt` - Update guide

**Documentation:**
- ✅ `UPDATE_GUIDE_V1.2.md` - This file

---

## ✨ Summary of Improvements

| Feature | Before v1.2 | After v1.2 |
|---------|-------------|------------|
| **Admin Review Flexibility** | One-time only | Unlimited changes |
| **User Retake Quiz** | Unclear | ✅ Unlimited |
| **User Resubmit PPT** | ❌ Blocked | ✅ Allowed after rejection |
| **User Notifications** | ❌ None | ✅ Real-time updates |
| **Admin Submission Alerts** | ❌ None | ✅ NEW badges |
| **Edit Quiz Questions** | ❌ Not possible | ✅ Full edit interface |
| **Edit User Info** | ❌ Not possible | ✅ Full edit interface |
| **Resubmission Tracking** | ❌ None | ✅ Count displayed |

---

## 🎯 Next Steps After Update

1. **Test thoroughly** - Go through all test cases
2. **Clear browser cache** - Ctrl+Shift+Delete
3. **Check logs** - Monitor for any errors
4. **Train admins** - Show them new features
5. **Notify users** - Inform about resubmission capability

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review application logs: `tail -f /path/to/logs/app.log`
3. Verify database schema: `SHOW TABLES; DESCRIBE submissions;`
4. Check Flask debug output in terminal

---

**Version:** 1.2.0  
**Release Date:** May 2026  
**Compatibility:** WorkVerse 1.1 and later  
**Author:** WorkVerse Development Team
