import sqlite3
import os

# Path to your database
db_path = os.path.join('instance', 'app.db')

def update_db():
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}. Please run the app first to create it.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Updating database schema...")
        
        # Add new columns to 'users' table
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email_notifications BOOLEAN DEFAULT 1")
            print("✅ Added email_notifications column")
        except sqlite3.OperationalError:
            print("ℹ️ email_notifications already exists")

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN telegram_notifications BOOLEAN DEFAULT 0")
            print("✅ Added telegram_notifications column")
        except sqlite3.OperationalError:
            print("ℹ️ telegram_notifications already exists")

        # Create EmailShare table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_shares (
                id INTEGER PRIMARY KEY,
                file_id INTEGER,
                recipient_email VARCHAR(120) NOT NULL,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(file_id) REFERENCES files(id)
            )
        ''')
        print("✅ Verified email_shares table")

        # Create TelegramUser table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telegram_users (
                id INTEGER PRIMARY KEY,
                telegram_user_id VARCHAR(64) UNIQUE NOT NULL,
                username VARCHAR(64),
                linked_user_id INTEGER,
                FOREIGN KEY(linked_user_id) REFERENCES users(id)
            )
        ''')
        print("✅ Verified telegram_users table")

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0")
            cursor.execute("ALTER TABLE users ADD COLUMN verification_code VARCHAR(6)")
            print("✅ Added verification columns to users")
        except sqlite3.OperationalError:
            print("ℹ️ Verification columns already exist")

        try:
            cursor.execute("ALTER TABLE download_logs ADD COLUMN country VARCHAR(100) DEFAULT 'Unknown'")
            cursor.execute("ALTER TABLE download_logs ADD COLUMN user_agent VARCHAR(255)")
            print("✅ Added analytics columns to download_logs")
        except sqlite3.OperationalError:
            print("ℹ️ Analytics columns already exist")

        conn.commit()
        conn.close()
        print("\n🎉 Database update complete! You can now run your app.")
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")

if __name__ == "__main__":
    update_db()
