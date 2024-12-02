import sqlite3

def create_database():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Create students table
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (id INTEGER PRIMARY KEY,
                  name TEXT NOT NULL,
                  nickname TEXT)''')
    
    # Create books table
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY,
                  title TEXT NOT NULL,
                  available BOOLEAN DEFAULT 1)''')
    
    # Create borrowing records table
    c.execute('''CREATE TABLE IF NOT EXISTS borrowings
                 (id INTEGER PRIMARY KEY,
                  student_id INTEGER,
                  book_id INTEGER,
                  borrow_date DATETIME,
                  return_date DATETIME,
                  FOREIGN KEY (student_id) REFERENCES students (id),
                  FOREIGN KEY (book_id) REFERENCES books (id))''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database and tables created successfully!")
