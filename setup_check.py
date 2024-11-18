import os
import sqlite3

def check_requirements():
    print("=== Checking Setup Requirements ===")
    
    # Check if database exists (we don't want it to)
    if os.path.exists('library.db'):
        print("! Warning: library.db already exists")
        if input("Delete existing database? (yes/no): ").lower().startswith('y'):
            os.remove('library.db')
            print("✓ Removed old database")
    
    # Check for required files
    required_files = [
        'database.py',
        'import_data.py',
        'app.py',
        'templates/index.html',
        'students.txt',
        'books.txt'
    ]
    
    all_files_present = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ Found {file}")
        else:
            print(f"✗ Missing {file}")
            all_files_present = False
    
    return all_files_present

def create_fresh_setup():
    print("\n=== Creating Fresh Setup ===")
    try:
        # Create new empty database
        from database import create_database
        create_database()
        print("✓ Created fresh database")
        
        # Import clean data
        from import_data import import_students, import_books
        import_students('students.txt')
        import_books('books.txt')
        print("✓ Imported class data")
        
    except Exception as e:
        print(f"✗ Setup failed: {e}")

if __name__ == "__main__":
    print("=== Fresh Classroom Setup ===")
    
    if check_requirements():
        create_fresh_setup()
        print("\n=== Setup Complete ===")
        print("\nYou can now run:")
        print("python app.py")
    else:
        print("\n✗ Setup failed: Missing required files")
