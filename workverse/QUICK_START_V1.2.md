# WorkVerse v1.2 - QUICK UPDATE GUIDE

## 🚀 INSTALLATION (3 STEPS)

### Step 1: Backup Everything
```bash
# Backup database
mysqldump -u root -p workverse_db > backup_$(date +%Y%m%d).sql

# Backup files
cp -r workverse workverse_backup
```

### Step 2: Update Database
```bash
cd workverse
mysql -u root -p workverse_db < database/update_v1.2.sql
```

### Step 3: Start Application
```bash
python app.py
```

That's it! All files are already updated.

---

## ✅ What's Fixed

### Issue 1: Admin Can Now Re-Approve/Re-Reject
- Admin can change submission status anytime
- No longer locked after first review

### Issue 2: Users Can Retake & Resubmit
- ✅ Users can retake quizzes unlimited times
- ✅ Users can resubmit PPT after rejection
- ✅ Users get notifications for reviews
- ✅ Admin sees "NEW" badges for resubmissions

### Issue 3: Admin Can Edit Everything
- ✅ Edit quiz questions
- ✅ Edit user information
- ✅ Edit buttons in all admin panels

---

## 🆕 New Features

1. **Notification System**
   - Real-time user notifications
   - Notification bell with unread count
   - Notification page at `/notifications`

2. **Resubmission Tracking**
   - Count of resubmissions displayed
   - "NEW" animated badge for admin
   - Resubmission history

3. **Edit Interfaces**
   - Edit quiz questions: `/admin/quiz/edit/<id>`
   - Edit user info: `/admin/user/edit/<id>`

---

## 📦 Files Included

**Updated Files:**
- ✅ `app.py` - All fixes integrated
- ✅ `database/update_v1.2.sql` - Schema updates
- ✅ `templates/review_submissions.html` - NEW indicators
- ✅ `templates/base.html` - Notification bell
- ✅ `templates/manage_quizzes.html` - Edit button
- ✅ `templates/manage_users.html` - Edit button

**New Files:**
- ✅ `templates/notifications.html`
- ✅ `templates/edit_quiz.html`
- ✅ `templates/edit_user.html`

---

## 🧪 Test Checklist

After updating, test these:

- [ ] User can see notification bell
- [ ] User receives notification after submission review
- [ ] User can retake quiz after failing
- [ ] User can resubmit PPT after rejection
- [ ] Admin sees "NEW" badge on resubmissions
- [ ] Admin can re-approve previously rejected submissions
- [ ] Admin can re-reject previously approved submissions
- [ ] Admin can edit quiz questions
- [ ] Admin can edit user information

---

## 🔧 Troubleshooting

**Problem:** Database update fails
```bash
# Check if tables exist
mysql -u root -p workverse_db -e "SHOW TABLES LIKE 'notifications';"
```

**Problem:** Notifications don't show
```bash
# Verify column exists
mysql -u root -p workverse_db -e "DESCRIBE submissions;"
# Should see: is_new_submission, resubmission_count
```

**Problem:** 404 on new routes
- Make sure all new routes are in app.py
- Restart the Flask application

---

## 📞 Quick Help

**Login Credentials (Default):**
- Admin: `admin@workverse.com` / `admin123`
- User: Create new account via registration

**Database:** `workverse_db`
**Port:** `5000` (default Flask)

---

## 🎯 Version Info

- **Version:** 1.2.0
- **Previous:** 1.1.0
- **Changes:** 3 critical bug fixes + notifications
- **Database:** Added 2 tables, 2 columns

---

**Ready to use! All fixes are already integrated.**
