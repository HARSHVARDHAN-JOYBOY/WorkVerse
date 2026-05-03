#!/usr/bin/env python3
"""
Password Hash Generator for WorkVerse

Use this script to generate password hashes for creating new admin users
or updating existing passwords in the database.

Usage:
    python generate_password_hash.py
"""

from werkzeug.security import generate_password_hash
import sys

def main():
    print("=" * 60)
    print("WorkVerse - Password Hash Generator")
    print("=" * 60)
    print()
    
    password = input("Enter password to hash: ")
    
    if len(password) < 6:
        print("\n❌ Error: Password must be at least 6 characters long.")
        sys.exit(1)
    
    # Generate hash
    password_hash = generate_password_hash(password)
    
    print("\n" + "=" * 60)
    print("Password Hash Generated Successfully!")
    print("=" * 60)
    print()
    print("Password Hash:")
    print(password_hash)
    print()
    print("To create a new admin user, run this SQL command:")
    print("-" * 60)
    print(f"""
INSERT INTO users (name, email, password, role) 
VALUES ('Admin Name', 'admin@example.com', '{password_hash}', 'admin');
    """)
    print()
    print("To update an existing user's password:")
    print("-" * 60)
    print(f"""
UPDATE users 
SET password = '{password_hash}' 
WHERE email = 'user@example.com';
    """)
    print()
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        sys.exit(0)
