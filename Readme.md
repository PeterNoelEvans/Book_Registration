# Library Book Registration System

A simple Flask-based system for tracking book borrowing in a classroom setting. Students can borrow books, and teachers can track which books are currently borrowed and view borrowing history.

## Features

- Track student book borrowing
- View currently borrowed books
- View reading history for each student
- Export unreturned books list
  - Excel format (.xlsx)
  - CSV format (.csv)
  - See [Export Documentation](docs/export_feature.md) for details
- Simple web interface
- Easy setup for new classrooms

## Setup Requirements

- Python 3.x
- Flask (for web application)
- Pandas (for data export)
- Openpyxl (for Excel export)

## Quick Start

1. Clone the repository:


git clone https://github.com/PeterNoelEvans/Book_Registration.git

cd Book_Registration

2. Install Flask:


pip install flask

3. Prepare your class data:
   - Edit `students.txt` with your student list (format: `Full Name    Nickname`)
   - Edit `books.txt` with your book list (one title per line)

4. Clean the data format:


python clean_data.py

5. Set up the database:


python setup_check.py

6. Run the application:


python app.py

7. Open a web browser and go to:


http://127.0.0.1:5000

## File Structure

```
Book_Registration/
│
├── app.py              # Main Flask application
├── database.py         # Database creation and management
├── import_data.py      # Data import functions
├── clean_data.py       # Data cleaning utility
├── setup_check.py      # Setup verification
│
├── templates/          
│   └── index.html      # Web interface template
│
├── students.txt        # Student list for current class
└── books.txt          # Book list for current class
```

## Data File Formats

### students.txt
```
Full Name    Nickname
John Smith    Johnny
Jane Doe    Jenny
```

### books.txt
```
Book Title 1
Book Title 2
Book Title 3
```

## Usage

1. Select a student from the dropdown menu
2. Select an available book
3. Click "Borrow Book" to register the loan
4. Use "Return Book" when the book is returned
5. View student's current loans and reading history on the right panel

## Setting Up in a New Classroom

1. Clone the repository
2. Update `students.txt` with new class list
3. Update `books.txt` with available books
4. Run setup scripts
5. Start the application

## Troubleshooting

### Common Issues

1. **Database errors**
   - Delete `library.db` and run `setup_check.py` again

2. **Import errors**
   - Ensure text files are properly formatted
   - Run `clean_data.py` to fix format issues

3. **Flask not found**
   - Run `pip install flask`

### Data Backup

- The database is local to each classroom
- Student and book lists can be backed up as needed
- Core application files are version-controlled through GitHub

## on a new machine

# 1. Clone the repository
git clone https://github.com/PeterNoelEvans/Book_Registration.git

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Run setup
python setup_check.py

Feel free to submit issues and enhancement requests!

## License

[Your chosen license]

## Contact

[Your contact information]

## Acknowledgments

- Flask web framework
- SQLite database
- [Any other acknowledgments]

## Export Feature
The system now supports exporting unreturned books lists. For detailed instructions, see the [Export Documentation](docs/export_feature.md).

Quick start:

```bash
# Ensure required packages are installed
pip install pandas openpyxl

# Create export directory
mkdir -p static/exports
```

### 1. Initial Setup
```bash
# Navigate to your project directory
cd Book_Registration

# Create virtual environment (if not already done)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### 2. Install Required Packages
```bash
# Install export-specific packages
pip install pandas openpyxl

# Update requirements.txt
pip freeze > requirements.txt
```

### 3. Create Export Directory
```bash
# Create directory for exported files
mkdir static
mkdir static/exports
```

@app.route('/get_unreturned_books')
def get_unreturned_books():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Get all unreturned books with student names
    c.execute('''
        SELECT 
            students.name,
            students.nickname,
            books.title,
            borrowings.borrow_date,
            borrowings.id,
            students.id as student_id,
            books.id as book_id
        FROM borrowings 
        JOIN students ON borrowings.student_id = students.id 
        JOIN books ON borrowings.book_id = books.id 
        WHERE borrowings.return_date IS NULL
        ORDER BY students.name, borrowings.borrow_date
    ''')
    
    unreturned = c.fetchall()
    conn.close()
    
    return jsonify(unreturned)

