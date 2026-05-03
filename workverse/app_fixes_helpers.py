# WorkVerse - Critical Fixes Implementation Guide
# Add these functions and routes to app.py

# ============================================
# HELPER FUNCTIONS FOR NOTIFICATIONS
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

# ============================================
# CONTEXT PROCESSOR FOR NOTIFICATIONS
# ============================================

@app.context_processor
def inject_notifications():
    """Inject notification count into all templates"""
    if current_user.is_authenticated:
        unread_count = get_unread_count(current_user.id)
        return dict(unread_notifications_count=unread_count)
    return dict(unread_notifications_count=0)
