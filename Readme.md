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
```bash
git clone https://github.com/PeterNoelEvans/Book_Registration.git
cd Book_Registration
```

2. Set up on a new machine:
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Run setup
python setup_check.py
```

3. Prepare your class data:
   - Edit `students.txt` with your student list (format: `Full Name    Nickname`)
   - Edit `books.txt` with your book list (one title per line)

4. Clean the data format:
```bash
python clean_data.py
```

5. Run the application:
```bash
python app.py
```

6. Open a web browser and go to:
```
http://127.0.0.1:5000
```

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
├── static/
│   └── exports/        # Export directory for files
│
├── docs/
│   └── export_feature.md  # Export feature documentation
│
├── students.txt        # Student list for current class
└── books.txt          # Book list for current class
```

[Rest of your existing README content...]

