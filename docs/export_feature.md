# Book Registration Export Feature

## Table of Contents
- [Overview](#overview)
- [Environment Setup](#environment-setup)
- [Code Implementation](#code-implementation)
  - [Python Routes](#python-routes)
  - [HTML/JavaScript Changes](#htmljavascript-changes)
  - [Styling](#styling)
- [Usage](#usage)
- [File Locations](#file-locations)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)
- [Security Notes](#security-notes)

## Overview
The export feature allows you to generate spreadsheet files of unreturned books, useful for:
- Tracking overdue books
- Parent-teacher meetings
- Library inventory
- Administrative records

## Environment Setup

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
mkdir -p static/exports
```

## Code Implementation

### Python Routes
Add this to your `app.py`:

```python
from flask import send_file, jsonify
import pandas as pd
from datetime import datetime
import os

# Create export directory if it doesn't exist
export_dir = os.path.join('static', 'exports')
os.makedirs(export_dir, exist_ok=True)

@app.route('/export_unreturned', methods=['GET'])
def export_unreturned():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Get unreturned books data
    c.execute('''
        SELECT 
            students.name,
            students.nickname,
            books.title,
            borrowings.borrow_date
        FROM borrowings 
        JOIN students ON borrowings.student_id = students.id 
        JOIN books ON borrowings.book_id = books.id 
        WHERE borrowings.return_date IS NULL
        ORDER BY students.name, borrowings.borrow_date
    ''')
    
    unreturned = c.fetchall()
    conn.close()
    
    # Create DataFrame
    df = pd.DataFrame(unreturned, columns=['Student Name', 'Nickname', 'Book Title', 'Borrow Date'])
    
    # Generate filename with current date
    filename = f'unreturned_books_{datetime.now().strftime("%Y%m%d_%H%M")}'
    
    # Get export format from query parameter
    format = request.args.get('format', 'excel')
    
    if format == 'excel':
        # Export to Excel
        excel_file = f"static/exports/{filename}.xlsx"
        df.to_excel(excel_file, index=False)
        return send_file(excel_file, as_attachment=True)
        
    elif format == 'csv':
        # Export to CSV
        csv_file = f"static/exports/{filename}.csv"
        df.to_csv(csv_file, index=False)
        return send_file(csv_file, as_attachment=True)

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
```

### HTML/JavaScript Changes
Add this to your `templates/index.html`:

```html
<!-- Add to the body, near the top -->
<div class="header-buttons">
    <button onclick="showUnreturnedBooks()" class="unreturned-btn">Show Unreturned Books</button>
</div>

<!-- Add at the bottom of the body -->
<div id="unreturned-modal" class="modal">
    <div class="modal-content">
        <span class="close">&times;</span>
        <div class="modal-header">
            <h2>Unreturned Books</h2>
            <div class="export-buttons">
                <button onclick="exportUnreturned('excel')" class="export-btn excel">
                    Export to Excel
                </button>
                <button onclick="exportUnreturned('csv')" class="export-btn csv">
                    Export to CSV
                </button>
            </div>
        </div>
        <div id="unreturned-list"></div>
    </div>
</div>

<!-- Add JavaScript -->
<script>
    function exportUnreturned(format) {
        window.location.href = `/export_unreturned?format=${format}`;
    }
    
    function showUnreturnedBooks() {
        fetch('/get_unreturned_books')
            .then(response => response.json())
            .then(data => {
                const modal = document.getElementById('unreturned-modal');
                const unreturnedList = document.getElementById('unreturned-list');
                
                if (data.length === 0) {
                    unreturnedList.innerHTML = '<p>No unreturned books!</p>';
                } else {
                    unreturnedList.innerHTML = `
                        <table class="unreturned-table">
                            <thead>
                                <tr>
                                    <th>Student</th>
                                    <th>Book</th>
                                    <th>Borrowed Date</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.map(book => `
                                    <tr>
                                        <td>${book[0]} (${book[1]})</td>
                                        <td>${book[2]}</td>
                                        <td>${formatDateTime(book[3])}</td>
                                        <td>
                                            <button class="return-btn" onclick="returnBook(${book[5]}, ${book[6]})">
                                                Return
                                            </button>
                                            <button class="delete-btn" onclick="deleteRecord(${book[4]}, ${book[5]})">
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;
                }
                
                modal.style.display = "block";
            });
    }
    
    // Close modal when clicking the X
    document.querySelector('.close').onclick = function() {
        document.getElementById('unreturned-modal').style.display = "none";
    }
    
    // Close modal when clicking outside
    window.onclick = function(event) {
        const modal = document.getElementById('unreturned-modal');
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
</script>
```

### Styling
Add these styles to your `templates/index.html`:

```html
<style>
    .header-buttons {
        margin: 20px 0;
        text-align: center;
    }
    
    .unreturned-btn {
        background-color: #ff9800;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
    }
    
    .unreturned-btn:hover {
        background-color: #f57c00;
    }
    
    .modal {
        display: none;
        position: fixed;
        z-index: 1;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        overflow: auto;
        background-color: rgba(0,0,0,0.4);
    }
    
    .modal-content {
        background-color: #fefefe;
        margin: 5% auto;
        padding: 20px;
        border: 1px solid #888;
        width: 80%;
        max-width: 800px;
        border-radius: 5px;
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .export-buttons {
        display: flex;
        gap: 10px;
    }
    
    .export-btn {
        padding: 8px 15px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
    }
    
    .export-btn.excel {
        background-color: #217346;
        color: white;
    }
    
    .export-btn.csv {
        background-color: #4CAF50;
        color: white;
    }
    
    .export-btn:hover {
        opacity: 0.9;
    }
    
    .close {
        color: #aaa;
        float: right;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
    }
    
    .close:hover {
        color: black;
    }
    
    .unreturned-table {
        width: 100%;
        margin-top: 20px;
    }
    
    .unreturned-table th {
        background-color: #f8f9fa;
        padding: 12px;
        text-align: left;
    }
    
    .unreturned-table td {
        padding: 10px;
        border-bottom: 1px solid #ddd;
    }
</style>
```

## Usage
1. Click "Show Unreturned Books" button
2. View list of all unreturned books
3. Export options:
   - Click "Export to Excel" for .xlsx file
   - Click "Export to CSV" for .csv file
4. Files will be downloaded to your default download location

## File Locations
```
Book_Registration/
│
├── static/
│   └── exports/           # Export files directory
│       ├── unreturned_books_20240120_1430.xlsx
│       └── unreturned_books_20240120_1430.csv
│
├── templates/
│   └── index.html         # Contains export buttons
│
└── app.py                 # Export route handlers
```

## Troubleshooting

### Common Issues
1. **Missing Dependencies**
   ```bash
   pip install pandas openpyxl
   ```

2. **Permission Errors**
   - Ensure 'static/exports' directory exists
   - Check write permissions

3. **File Access Issues**
   - Close any open export files
   - Check if antivirus is blocking file creation

## Maintenance

Add to `.gitignore`:
```
static/exports/*
!static/exports/.gitkeep
```

## Security Notes
1. Ensure export directory is:
   - Outside web root
   - Protected from direct access
   - Regularly cleaned up
2. Consider implementing user authentication for exports
3. Regularly clean up old export files
```

</rewritten_file>