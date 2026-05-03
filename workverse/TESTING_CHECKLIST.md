# WorkVerse - Testing Checklist

Use this checklist to verify all features are working correctly.

## Pre-Testing Setup

- [ ] Database created and schema imported
- [ ] Application running without errors
- [ ] Admin account accessible
- [ ] All dependencies installed

## 1. Authentication Testing

### User Registration
- [ ] Registration form loads correctly
- [ ] Can register with valid credentials
- [ ] Password validation works (minimum 6 characters)
- [ ] Email validation works
- [ ] Duplicate email prevented
- [ ] Password mismatch detected
- [ ] Success message displayed
- [ ] Redirected to login page

### User Login
- [ ] Login form loads correctly
- [ ] Can login with valid credentials
- [ ] Invalid credentials rejected
- [ ] Error messages displayed correctly
- [ ] Redirected to appropriate dashboard (user/admin)
- [ ] Session persists across page refreshes

### Admin Login
- [ ] Can login as admin (admin@workverse.com)
- [ ] Redirected to admin dashboard
- [ ] Admin menu items visible

### Logout
- [ ] Logout button works
- [ ] Session cleared
- [ ] Redirected to home page
- [ ] Cannot access protected pages after logout

## 2. User Dashboard Testing

### Dashboard Display
- [ ] Statistics cards show correct counts
- [ ] Enrolled simulations displayed
- [ ] Pending submissions shown
- [ ] Certificates listed correctly
- [ ] Available simulations visible

### Navigation
- [ ] Can navigate to simulations
- [ ] Can view progress
- [ ] Can access certificates
- [ ] All links functional

## 3. Simulation Testing

### View Simulation
- [ ] Simulation details load correctly
- [ ] Video player displays (if video URL provided)
- [ ] Learning content formatted correctly
- [ ] Progress card shows current status
- [ ] Enrollment created automatically

### Simulation Enrollment
- [ ] User enrolled when viewing simulation
- [ ] Progress record created in database
- [ ] Status shows as "enrolled"

### Progress Tracking
- [ ] Progress card updates correctly
- [ ] Different statuses display appropriate buttons
- [ ] Can navigate to quiz from simulation

## 4. Quiz Testing

### Quiz Display
- [ ] Quiz page loads correctly
- [ ] All questions displayed
- [ ] Four options per question
- [ ] Radio buttons work correctly
- [ ] Instructions visible

### Quiz Submission
- [ ] Can submit quiz answers
- [ ] Score calculated correctly
- [ ] Pass/fail determined correctly (60% threshold)
- [ ] Results displayed
- [ ] Progress updated in database

### Quiz Retake
- [ ] Can retake quiz if failed
- [ ] New attempt scored correctly
- [ ] Previous score updated

## 5. PPT Upload Testing

### Upload Page
- [ ] Upload page loads after quiz pass
- [ ] Cannot access without quiz completion
- [ ] File input accepts .ppt and .pptx
- [ ] Instructions displayed clearly

### File Upload
- [ ] Can select PPT file
- [ ] File size validation works (16MB max)
- [ ] File type validation works
- [ ] Upload progress indicated
- [ ] File saved with unique name
- [ ] Submission record created

### Upload Status
- [ ] Status shows as "pending"
- [ ] Can view uploaded file name
- [ ] Submission timestamp correct
- [ ] Cannot re-upload while pending (unless rejected)

## 6. Certificate Testing

### Certificate Access
- [ ] Certificate only accessible after approval
- [ ] Certificate page loads correctly
- [ ] User name displayed
- [ ] Simulation name displayed
- [ ] Completion date shown
- [ ] Certificate ID generated

### Certificate Printing
- [ ] Print function works
- [ ] Print preview shows certificate correctly
- [ ] No-print elements hidden in print view

## 7. Admin Dashboard Testing

### Dashboard Display
- [ ] Statistics cards show correct data
- [ ] Total users count accurate
- [ ] Total simulations count accurate
- [ ] Pending submissions count accurate
- [ ] Approved certificates count accurate

### Recent Activity
- [ ] Recent submissions displayed
- [ ] User names shown correctly
- [ ] Simulation titles correct
- [ ] Status badges accurate

### Navigation
- [ ] All admin menu items accessible
- [ ] Quick action buttons functional

## 8. Admin - Manage Simulations

### View Simulations
- [ ] All simulations listed
- [ ] Simulation details displayed correctly
- [ ] Action buttons visible

### Add Simulation
- [ ] Modal opens correctly
- [ ] Can enter all required fields
- [ ] Video URL optional
- [ ] Simulation created successfully
- [ ] Success message displayed
- [ ] List updates immediately

### Edit Simulation
- [ ] Edit modal populated with current data
- [ ] Can update all fields
- [ ] Changes saved correctly
- [ ] List updates after edit

### Delete Simulation
- [ ] Confirmation dialog shown
- [ ] Simulation deleted successfully
- [ ] Related quizzes deleted (cascade)
- [ ] Related progress deleted (cascade)

## 9. Admin - Manage Quizzes

### View Quizzes
- [ ] Quizzes for simulation displayed
- [ ] Question text visible
- [ ] All four options shown
- [ ] Correct answer highlighted
- [ ] Question number displayed

### Add Quiz Question
- [ ] Modal opens correctly
- [ ] Can enter question and options
- [ ] Can select correct answer
- [ ] Question created successfully
- [ ] List updates immediately

### Edit Quiz Question
- [ ] Edit modal populated correctly
- [ ] Can update question and options
- [ ] Can change correct answer
- [ ] Changes saved correctly

### Delete Quiz Question
- [ ] Confirmation dialog shown
- [ ] Question deleted successfully
- [ ] List updates immediately

## 10. Admin - Review Submissions

### View Submissions
- [ ] All submissions listed
- [ ] User information displayed
- [ ] Simulation name shown
- [ ] File download link works
- [ ] Status shown correctly
- [ ] Submission date displayed

### Approve Submission
- [ ] Review modal opens
- [ ] Can add feedback (optional)
- [ ] Submission approved successfully
- [ ] Status updated to "approved"
- [ ] Progress status updated to "completed"
- [ ] User can access certificate

### Reject Submission
- [ ] Review modal opens
- [ ] Can add feedback
- [ ] Submission rejected
- [ ] Status updated to "rejected"
- [ ] User can see rejection
- [ ] User can re-upload

### Download Submission
- [ ] Download link works
- [ ] File downloads correctly
- [ ] File opens in appropriate application

## 11. Admin - Manage Users

### View Users
- [ ] All users listed
- [ ] User information displayed
- [ ] Enrollment count accurate
- [ ] Completion count accurate
- [ ] Join date shown

### Delete User
- [ ] Confirmation dialog shown
- [ ] User deleted successfully
- [ ] Related data deleted (cascade)
- [ ] Cannot delete current admin user

### Statistics
- [ ] Total users count correct
- [ ] Total enrollments correct
- [ ] Total completions correct

## 12. Security Testing

### Authentication
- [ ] Cannot access user pages without login
- [ ] Cannot access admin pages without admin role
- [ ] Sessions expire appropriately
- [ ] Password hashing working

### Authorization
- [ ] Regular users cannot access admin pages
- [ ] Admin can access all pages
- [ ] Proper redirects for unauthorized access

### File Upload Security
- [ ] Only .ppt/.pptx accepted
- [ ] File size limit enforced
- [ ] Filenames sanitized
- [ ] Files stored securely

### SQL Injection
- [ ] Parameterized queries used
- [ ] No direct SQL string concatenation
- [ ] Special characters handled properly

## 13. UI/UX Testing

### Responsive Design
- [ ] Works on desktop (1920x1080)
- [ ] Works on laptop (1366x768)
- [ ] Works on tablet (768x1024)
- [ ] Works on mobile (375x667)

### Browser Compatibility
- [ ] Works in Chrome
- [ ] Works in Firefox
- [ ] Works in Safari
- [ ] Works in Edge

### Visual Design
- [ ] Colors consistent
- [ ] Fonts readable
- [ ] Icons display correctly
- [ ] Bootstrap components styled
- [ ] Custom CSS applied

### User Experience
- [ ] Navigation intuitive
- [ ] Forms easy to use
- [ ] Error messages clear
- [ ] Success messages displayed
- [ ] Loading states indicated

## 14. Performance Testing

### Page Load Times
- [ ] Home page loads < 2 seconds
- [ ] Dashboard loads < 3 seconds
- [ ] Simulation page loads < 3 seconds
- [ ] Admin pages load < 3 seconds

### Database Queries
- [ ] No N+1 query problems
- [ ] Queries optimized
- [ ] Indexes used appropriately

### File Uploads
- [ ] Large files (up to 16MB) upload successfully
- [ ] Upload progress indicated
- [ ] No timeout errors

## 15. Error Handling

### 404 Errors
- [ ] Custom 404 page displays
- [ ] Links to home/dashboard work

### 500 Errors
- [ ] Custom 500 page displays
- [ ] Errors logged appropriately

### Form Validation
- [ ] Client-side validation works
- [ ] Server-side validation works
- [ ] Error messages specific and helpful

### Database Errors
- [ ] Connection errors handled gracefully
- [ ] Query errors don't expose SQL
- [ ] User-friendly error messages

## 16. Data Integrity

### Referential Integrity
- [ ] Foreign keys enforced
- [ ] Cascade deletes work correctly
- [ ] No orphaned records

### Data Validation
- [ ] Email format validated
- [ ] Password requirements enforced
- [ ] File types validated
- [ ] Required fields enforced

## Test Environment Details

- **Date Tested**: _______________
- **Tested By**: _______________
- **Environment**: Development / Staging / Production
- **Database**: MySQL version _______________
- **Python**: Version _______________
- **Browser**: _______________

## Issues Found

| # | Issue | Severity | Status | Notes |
|---|-------|----------|--------|-------|
| 1 |       |          |        |       |
| 2 |       |          |        |       |
| 3 |       |          |        |       |

## Sign-off

- [ ] All critical tests passed
- [ ] All high-priority issues resolved
- [ ] Application ready for deployment

**Tester Signature**: _______________  
**Date**: _______________
