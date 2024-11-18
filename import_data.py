import sqlite3

def import_students(filename):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            count = 0
            for line in file:
                # Split on | to get name and nickname
                parts = line.strip().split('|')
                if len(parts) == 2:
                    name, nickname = parts
                    c.execute('INSERT INTO students (name, nickname) VALUES (?, ?)', 
                            (name, nickname))
                    count += 1
        conn.commit()
        print(f"Successfully imported {count} students")
    except Exception as e:
        print(f"Error importing students: {e}")
    finally:
        conn.close()

def import_books(filename):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            count = 0
            for line in file:
                title = line.strip()
                if title:  # Only insert if title is not empty
                    c.execute('INSERT INTO books (title) VALUES (?)', (title,))
                    count += 1
        conn.commit()
        print(f"Successfully imported {count} books")
    except Exception as e:
        print(f"Error importing books: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting data import...")
    import_students('students.txt')
    import_books('books.txt')
    print("Import complete!")
