# Export Feature Documentation

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
Add these routes to your `app.py`:

```python
from flask import send_file, jsonify, request
import pandas as pd
from datetime import datetime
import os
import sqlite3

# Create export directory if it doesn't exist
export_dir = os.path.join('static', 'exports')
os.makedirs(export_dir, exist_ok=True)

@app.route('/export_unreturned', methods=['GET'])
def export_unreturned():
    try:
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
        
        if not unreturned:
            return jsonify({'error': 'No unreturned books found'}), 404
            
        # Create DataFrame for export
        df = pd.DataFrame(unreturned, columns=['Student Name', 'Nickname', 'Book Title', 'Borrow Date'])
        
        # Generate unique filename with timestamp
        filename = f'unreturned_books_{datetime.now().strftime("%Y%m%d_%H%M")}'
        
        # Get requested format (default to excel)
        format = request.args.get('format', 'excel')
        
        if format == 'excel':
            excel_file = f"static/exports/{filename}.xlsx"
            df.to_excel(excel_file, index=False)
            return send_file(excel_file, as_attachment=True)
            
        elif format == 'csv':
            csv_file = f"static/exports/{filename}.csv"
            df.to_csv(csv_file, index=False)
            return send_file(csv_file, as_attachment=True)
        else:
            return jsonify({'error': 'Invalid format requested'}), 400
            
    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/get_unreturned_books')
def get_unreturned_books():
    """
    Retrieves all unreturned books with associated student information.
    
    Returns:
        JSON array of unreturned books with:
        - Student name and nickname
        - Book title
        - Borrow date
        - Record IDs for database operations
        
    Error Codes:
        500: Database error
        404: No unreturned books found
    """
    try:
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        # Get all unreturned books with student names and necessary IDs
        c.execute('''
            SELECT 
                students.name,          -- [0] Student's full name
                students.nickname,      -- [1] Student's nickname
                books.title,           -- [2] Book title
                borrowings.borrow_date, -- [3] Date borrowed
                borrowings.id,         -- [4] Borrowing record ID (for deletion)
                students.id,           -- [5] Student ID (for return/delete operations)
                books.id               -- [6] Book ID (for return operation)
            FROM borrowings 
            JOIN students ON borrowings.student_id = students.id 
            JOIN books ON borrowings.book_id = books.id 
            WHERE borrowings.return_date IS NULL
            ORDER BY students.name, borrowings.borrow_date
        ''')
        
        unreturned = c.fetchall()
        
        if not unreturned:
            return jsonify({'message': 'No unreturned books found', 'data': []}), 404
            
        return jsonify(unreturned)
        
    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    finally:
        if 'conn' in locals():
            conn.close()
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