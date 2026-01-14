
import mysql.connector
from config import DB_CONFIG

def setup_db():
    print("Applying schema...")
    try:
        # Connect to server directly first to ensure DB exists
        conn = mysql.connector.connect(
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host']
        )
        cursor = conn.cursor()
        
        # Create DB if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        conn.commit()
        cursor.close()
        conn.close()
        
        # Now connect to DB and run schema
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        with open('schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
            
        # Split by ; for multiple statements
        commands = schema.split(';')
        
        for command in commands:
            if command.strip():
                try:
                    cursor.execute(command)
                except Exception as e:
                    print(f"Error executing command: {command[:50]}... -> {e}")
                    
        conn.commit()
        cursor.close()
        conn.close()
        print("Schema applied successfully!")
        
    except Exception as e:
        print(f"Setup failed: {e}")

if __name__ == "__main__":
    setup_db()
