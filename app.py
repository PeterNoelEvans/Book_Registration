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
    
    # Get all students and available books
    c.execute('SELECT * FROM students')
    students = c.fetchall()
    
    c.execute('SELECT * FROM books WHERE available = 1')
    available_books = c.fetchall()
    
    conn.close()
    return render_template('index.html', 
                         students=students, 
                         books=available_books)

@app.route('/get_student_history/<int:student_id>')
def get_student_history(student_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Get currently borrowed books
    c.execute('''
        SELECT 
            books.id,
            books.title, 
            borrowings.borrow_date,
            'borrowed' as status
        FROM borrowings 
        JOIN books ON borrowings.book_id = books.id 
        WHERE borrowings.student_id = ? 
        AND borrowings.return_date IS NULL
    ''', (student_id,))
    borrowed_books = c.fetchall()
    
    # Get returned books
    c.execute('''
        SELECT 
            books.id,
            books.title, 
            borrowings.borrow_date,
            borrowings.return_date,
            'returned' as status
        FROM borrowings 
        JOIN books ON borrowings.book_id = books.id 
        WHERE borrowings.student_id = ? 
        AND borrowings.return_date IS NOT NULL
    ''', (student_id,))
    returned_books = c.fetchall()
    
    conn.close()
    
    return jsonify({
        'borrowed': borrowed_books,
        'returned': returned_books
    })

@app.route('/borrow_book', methods=['POST'])
def borrow_book():
    student_id = request.form['student_id']
    book_id = request.form['book_id']
    
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
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
    return redirect(url_for('index'))

@app.route('/return_book', methods=['POST'])
def return_book():
    student_id = request.form['student_id']
    book_id = request.form['book_id']
    
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Update with timestamp
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Update book availability
    c.execute('UPDATE books SET available = 1 WHERE id = ?', (book_id,))
    
    # Update borrowing record with return timestamp
    c.execute('''
        UPDATE borrowings 
        SET return_date = ? 
        WHERE student_id = ? 
        AND book_id = ? 
        AND return_date IS NULL
    ''', (current_time, student_id, book_id))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/delete_record', methods=['POST'])
def delete_record():
    record_id = request.form['record_id']
    
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    try:
        # Get book_id before deleting the record
        c.execute('SELECT book_id FROM borrowings WHERE id = ?', (record_id,))
        book_id = c.fetchone()[0]
        
        # Delete the borrowing record
        c.execute('DELETE FROM borrowings WHERE id = ?', (record_id,))
        
        # Reset book availability to 1 (available)
        c.execute('UPDATE books SET available = 1 WHERE id = ?', (book_id,))
        
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

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

if __name__ == '__main__':
    app.run(debug=True)
    
