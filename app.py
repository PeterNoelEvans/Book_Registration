from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import sqlite3
from datetime import datetime
import csv
from io import StringIO
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Get all students
    c.execute('SELECT * FROM students')
    students = c.fetchall()
    
    # Get only available books that aren't currently borrowed
    c.execute('''
        SELECT books.id, books.title
        FROM books
        WHERE books.available = 1
        AND books.id NOT IN (
            SELECT book_id 
            FROM borrowings 
            WHERE return_date IS NULL
        )
        ORDER BY books.title
    ''')
    available_books = c.fetchall()
    
    conn.close()
    return render_template('index.html', 
                         students=students, 
                         books=available_books)

@app.route('/get_student_history/<int:student_id>')
def get_student_history(student_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Get currently borrowed books (where return_date is NULL)
    c.execute('''
        SELECT 
            borrowings.book_id,
            books.title,
            borrowings.borrow_date,
            borrowings.id
        FROM borrowings 
        JOIN books ON borrowings.book_id = books.id
        WHERE borrowings.student_id = ? AND borrowings.return_date IS NULL
        ORDER BY borrowings.borrow_date DESC
    ''', (student_id,))
    borrowed = c.fetchall()
    
    # Get returned books (where return_date is NOT NULL)
    c.execute('''
        SELECT 
            borrowings.id,
            books.title,
            borrowings.borrow_date,
            borrowings.return_date
        FROM borrowings 
        JOIN books ON borrowings.book_id = books.id
        WHERE borrowings.student_id = ? AND borrowings.return_date IS NOT NULL
        ORDER BY borrowings.return_date DESC
    ''', (student_id,))
    returned = c.fetchall()
    
    conn.close()
    
    return jsonify({
        'borrowed': borrowed,
        'returned': returned
    })

@app.route('/borrow_book', methods=['POST'])
def borrow_book():
    try:
        student_id = request.form['student_id']
        book_id = request.form['book_id']
        
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        # Check if book is actually available
        c.execute('''
            SELECT available 
            FROM books 
            WHERE id = ? 
            AND available = 1
            AND id NOT IN (
                SELECT book_id 
                FROM borrowings 
                WHERE return_date IS NULL
            )
        ''', (book_id,))
        
        if not c.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Book is not available for borrowing'
            })
        
        # Update to include timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update book availability
        c.execute('UPDATE books SET available = 0 WHERE id = ?', (book_id,))
        
        # Create borrowing record with timestamp
        c.execute('''
            INSERT INTO borrowings (student_id, book_id, borrow_date)
            VALUES (?, ?, ?)
        ''', (student_id, book_id, current_time))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Book borrowed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/return_book/<int:borrowing_id>', methods=['POST'])
def return_book(borrowing_id):
    try:
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        # First check if the borrowing record exists
        c.execute('SELECT book_id FROM borrowings WHERE id = ? AND return_date IS NULL', (borrowing_id,))
        result = c.fetchone()
        
        if not result:
            conn.close()
            return jsonify({
                'success': False, 
                'error': 'Borrowing record not found or already returned'
            })
            
        book_id = result[0]
        
        # Update the return date for the borrowing
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('''
            UPDATE borrowings 
            SET return_date = ? 
            WHERE id = ? AND return_date IS NULL
        ''', (current_time, borrowing_id))
        
        # Update the book's availability
        c.execute('UPDATE books SET available = 1 WHERE id = ?', (book_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error in return_book: {str(e)}")  # Add logging
        return jsonify({'success': False, 'error': str(e)})

@app.route('/delete_record', methods=['POST'])
def delete_record():
    try:
        record_id = request.form.get('record_id')
        if not record_id:
            return jsonify({'success': False, 'error': 'No record ID provided'})
            
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        # First check if the record exists
        c.execute('SELECT id FROM borrowings WHERE id = ?', (record_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Record not found'})
        
        # Delete the record
        c.execute('DELETE FROM borrowings WHERE id = ?', (record_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

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
        
    elif format == 'pdf':
        # Export to PDF (requires additional setup)
        pdf_file = f"static/exports/{filename}.pdf"
        # Convert DataFrame to PDF using a library like pdfkit or reportlab
        return send_file(pdf_file, as_attachment=True)

@app.route('/get_available_books/<int:student_id>')
def get_available_books(student_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Get books that are:
    # 1. Available in general
    # 2. Not currently borrowed by anyone
    # 3. Either never borrowed by this student OR marked as re-borrowable
    c.execute('''
        SELECT DISTINCT b.id, b.title
        FROM books b
        WHERE b.available = 1
        AND b.id NOT IN (
            -- Exclude books currently borrowed by anyone
            SELECT book_id 
            FROM borrowings 
            WHERE return_date IS NULL
        )
        AND (
            -- Include books never borrowed by this student
            b.id NOT IN (
                SELECT book_id 
                FROM borrowings 
                WHERE student_id = ?
            )
            OR 
            -- Include books previously borrowed by this student and marked as re-borrowable
            b.id IN (
                SELECT book_id 
                FROM borrowings 
                WHERE student_id = ? 
                AND return_date IS NOT NULL 
                AND re_borrowable = 1
            )
        )
        ORDER BY b.title
    ''', (student_id, student_id))
    
    available_books = c.fetchall()
    conn.close()
    
    return jsonify(available_books)

@app.route('/make_reborrowable/<int:borrowing_id>', methods=['POST'])
def make_reborrowable(borrowing_id):
    try:
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        # Get the book_id for this borrowing
        c.execute('SELECT book_id FROM borrowings WHERE id = ?', (borrowing_id,))
        result = c.fetchone()
        
        if not result:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Borrowing record not found'
            })
            
        book_id = result[0]
        
        # Update the borrowing record
        c.execute('''
            UPDATE borrowings 
            SET re_borrowable = 1 
            WHERE id = ?
        ''', (borrowing_id,))
        
        # Make sure the book is marked as available
        c.execute('''
            UPDATE books 
            SET available = 1 
            WHERE id = ?
        ''', (book_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error in make_reborrowable: {str(e)}")  # Add logging
        return jsonify({'success': False, 'error': str(e)})

@app.route('/update_database')
def update_database():
    try:
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        # Check if columns exist
        c.execute("PRAGMA table_info(borrowings)")
        columns = [column[1] for column in c.fetchall()]
        
        if 're_borrowable' not in columns:
            c.execute('''
                ALTER TABLE borrowings
                ADD COLUMN re_borrowable INTEGER DEFAULT 0
            ''')
            
        if 'review_confirmed' not in columns:
            c.execute('''
                ALTER TABLE borrowings
                ADD COLUMN review_confirmed INTEGER DEFAULT 0
            ''')
            
        conn.commit()
        conn.close()
        return 'Database updated successfully'
    except Exception as e:
        return f'Error updating database: {str(e)}'

@app.route('/reading_stats')
def reading_stats():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Get reading statistics for all students
    c.execute('''
        SELECT 
            students.name,
            students.nickname,
            COUNT(DISTINCT CASE 
                WHEN borrowings.return_date IS NOT NULL 
                AND borrowings.review_confirmed = 1 
                THEN borrowings.book_id 
            END) as books_read,
            COUNT(DISTINCT CASE 
                WHEN borrowings.return_date IS NULL 
                THEN borrowings.book_id 
            END) as books_borrowed
        FROM students
        LEFT JOIN borrowings ON students.id = borrowings.student_id
        GROUP BY students.id, students.name, students.nickname
        ORDER BY books_read DESC, name
    ''')
    
    stats = c.fetchall()
    conn.close()
    
    return render_template('reading_stats.html', stats=stats)

@app.route('/review_management')
def review_management():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Get all returned books that need review confirmation
    c.execute('''
        SELECT 
            borrowings.id,
            students.name,
            students.nickname,
            books.title,
            borrowings.borrow_date,
            borrowings.return_date,
            borrowings.review_confirmed
        FROM borrowings 
        JOIN students ON borrowings.student_id = students.id
        JOIN books ON borrowings.book_id = books.id
        WHERE borrowings.return_date IS NOT NULL
        ORDER BY borrowings.review_confirmed, borrowings.return_date DESC
    ''')
    
    reviews = c.fetchall()
    conn.close()
    
    return render_template('review_management.html', reviews=reviews)

@app.route('/confirm_review/<int:borrowing_id>', methods=['POST'])
def confirm_review(borrowing_id):
    try:
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        c.execute('''
            UPDATE borrowings 
            SET review_confirmed = 1 
            WHERE id = ?
        ''', (borrowing_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
    
