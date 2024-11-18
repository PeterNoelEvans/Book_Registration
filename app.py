from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime

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
    
    # Update book availability
    c.execute('UPDATE books SET available = 0 WHERE id = ?', (book_id,))
    
    # Create borrowing record
    c.execute('''
        INSERT INTO borrowings (student_id, book_id, borrow_date)
        VALUES (?, ?, ?)
    ''', (student_id, book_id, datetime.now().strftime('%Y-%m-%d')))
    
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/return_book', methods=['POST'])
def return_book():
    student_id = request.form['student_id']
    book_id = request.form['book_id']
    
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Update book availability
    c.execute('UPDATE books SET available = 1 WHERE id = ?', (book_id,))
    
    # Update borrowing record with return date
    c.execute('''
        UPDATE borrowings 
        SET return_date = ? 
        WHERE student_id = ? 
        AND book_id = ? 
        AND return_date IS NULL
    ''', (datetime.now().strftime('%Y-%m-%d'), student_id, book_id))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
    
