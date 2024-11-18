import sqlite3
import os

def test_database():
    print("\n1. Testing Database...")
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("✓ Found tables:", [table[0] for table in tables])
        
        # Check table structures
        for table in ['students', 'books', 'borrowings']:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print(f"✓ {table} table columns:", [col[1] for col in columns])
            
        conn.close()
        print("✓ Database connection successful!")
        
    except Exception as e:
        print(f"✗ Database error: {e}")

def test_data_files():
    print("\n2. Testing Data Files...")
    files_to_check = ['students.txt', 'books.txt']
    
    for file in files_to_check:
        if os.path.exists(file):
            with open(file, 'r') as f:
                content = f.readlines()
            print(f"✓ Found {file} with {len(content)} entries")
        else:
            print(f"✗ Missing {file}")

def test_flask_setup():
    print("\n3. Testing Flask Setup...")
    try:
        from app import app
        print("✓ Flask app imported successfully")
        
        if os.path.exists('templates/index.html'):
            print("✓ Found index.html template")
        else:
            print("✗ Missing index.html template")
            
    except ImportError as e:
        print(f"✗ Flask import error: {e}")
        print("Make sure Flask is installed: pip install flask")

def test_data_import():
    print("\n4. Testing Data Import...")
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        print(f"✓ Found {student_count} students in database")
        
        cursor.execute("SELECT COUNT(*) FROM books")
        book_count = cursor.fetchone()[0]
        print(f"✓ Found {book_count} books in database")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Data import error: {e}")

if __name__ == "__main__":
    print("=== Library System Test ===")
    test_database()
    test_data_files()
    test_flask_setup()
    test_data_import()
