# Library Book Registration System

A simple Flask-based system for tracking book borrowing in a classroom setting. Students can borrow books, and teachers can track which books are currently borrowed and view borrowing history.

## Features

- Track student book borrowing
- View currently borrowed books
- View reading history for each student
- Simple web interface
- Easy setup for new classrooms

## Setup Requirements

- Python 3.x
- Flask
- SQLite3

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

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Your chosen license]

## Contact

[Your contact information]

## Acknowledgments

- Flask web framework
- SQLite database
- [Any other acknowledgments]

