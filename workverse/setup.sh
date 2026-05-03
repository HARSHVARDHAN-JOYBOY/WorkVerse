#!/bin/bash

# WorkVerse - Automated Setup Script
# This script helps you set up the WorkVerse application quickly

echo "=========================================="
echo "   WorkVerse - Setup Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "⚠️  MySQL not found in PATH. Make sure MySQL is installed and running."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ MySQL found"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create uploads directory if it doesn't exist
echo ""
echo "Creating uploads directory..."
mkdir -p uploads
echo "✓ Uploads directory created"

# Database setup
echo ""
echo "=========================================="
echo "   Database Setup"
echo "=========================================="
echo ""
echo "Please ensure MySQL is running before proceeding."
echo ""
read -p "Do you want to set up the database now? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter MySQL username (default: root): " db_user
    db_user=${db_user:-root}
    
    read -sp "Enter MySQL password: " db_password
    echo
    
    echo ""
    echo "Importing database schema..."
    mysql -u "$db_user" -p"$db_password" < database/schema.sql
    
    if [ $? -eq 0 ]; then
        echo "✓ Database setup completed successfully"
    else
        echo "❌ Database setup failed. Please run manually:"
        echo "   mysql -u root -p < database/schema.sql"
    fi
fi

# Update config if needed
echo ""
echo "=========================================="
echo "   Configuration"
echo "=========================================="
echo ""
echo "⚠️  Important: Update config.py with your database credentials"
echo ""
echo "Default settings:"
echo "  DB_USER: root"
echo "  DB_PASSWORD: password"
echo "  DB_NAME: workverse_db"
echo ""
read -p "Do you want to use default settings? (y/n) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Please edit config.py manually before running the application."
fi

# Final instructions
echo ""
echo "=========================================="
echo "   Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Activate virtual environment (if not already active):"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo ""
echo "2. Update config.py with your database credentials (if needed)"
echo ""
echo "3. Run the application:"
echo "   python app.py"
echo ""
echo "4. Open browser and navigate to:"
echo "   http://127.0.0.1:5000"
echo ""
echo "5. Login with admin credentials:"
echo "   Email: admin@workverse.com"
echo "   Password: admin123"
echo ""
echo "⚠️  Remember to change the admin password after first login!"
echo ""
echo "=========================================="
echo "For more information, see README.md"
echo "=========================================="
