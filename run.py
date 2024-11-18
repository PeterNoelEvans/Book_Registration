from database import create_database
from import_data import import_students, import_books
from app import app

if __name__ == '__main__':
    # Import data if needed
    try:
        import_students('students.txt')
        import_books('books.txt')
        print("Data imported successfully!")
    except Exception as e:
        print(f"Error importing data: {e}")

    # Run the Flask app
    app.run(debug=True)
