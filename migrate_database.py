import sqlite3
from datetime import datetime, date

def migrate_database():
    print("Starting database migration...")
    
    # Connect to existing database
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    try:
        # 1. Backup existing data
        print("Backing up current borrowing records...")
        c.execute('SELECT * FROM borrowings')
        existing_records = c.fetchall()
        
        # 2. Create temporary table with new structure
        print("Creating temporary table...")
        c.execute('''CREATE TABLE borrowings_new
                     (id INTEGER PRIMARY KEY,
                      student_id INTEGER,
                      book_id INTEGER,
                      borrow_date DATETIME,
                      return_date DATETIME,
                      FOREIGN KEY (student_id) REFERENCES students (id),
                      FOREIGN KEY (book_id) REFERENCES books (id))''')
        
        # 3. Migrate existing data with timestamps
        print("Migrating existing records...")
        for record in existing_records:
            old_id, student_id, book_id, old_borrow_date, old_return_date = record
            
            # Convert dates to datetime (add 00:00:00 for time)
            if isinstance(old_borrow_date, str):
                new_borrow_date = f"{old_borrow_date} 00:00:00"
            elif isinstance(old_borrow_date, date):
                new_borrow_date = f"{old_borrow_date.strftime('%Y-%m-%d')} 00:00:00"
            else:
                new_borrow_date = None
                
            if old_return_date:
                if isinstance(old_return_date, str):
                    new_return_date = f"{old_return_date} 00:00:00"
                elif isinstance(old_return_date, date):
                    new_return_date = f"{old_return_date.strftime('%Y-%m-%d')} 00:00:00"
            else:
                new_return_date = None
            
            c.execute('''INSERT INTO borrowings_new 
                        (id, student_id, book_id, borrow_date, return_date)
                        VALUES (?, ?, ?, ?, ?)''',
                     (old_id, student_id, book_id, new_borrow_date, new_return_date))
        
        # 4. Drop old table and rename new table
        print("Updating table structure...")
        c.execute('DROP TABLE borrowings')
        c.execute('ALTER TABLE borrowings_new RENAME TO borrowings')
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        print("Database has been rolled back to previous state.")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    # Create backup first
    import shutil
    from datetime import datetime
    
    # Backup the database
    backup_name = f'library_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    print(f"Creating backup: {backup_name}")
    shutil.copy2('library.db', backup_name)
    
    # Run migration
    if migrate_database():
        print("\nYou can now use the updated database with timestamps!")
        print(f"A backup of your old database was created: {backup_name}")
    else:
        print("\nMigration failed. Please check the error messages above.")
        print(f"Your original database is safe in: {backup_name}") 