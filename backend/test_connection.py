import pyodbc
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get connection parameters from environment variables
DB_CONFIG = {
    'SERVER': os.getenv('DB_SERVER'),
    'DATABASE': os.getenv('DB_DATABASE'),
    'USERNAME': os.getenv('DB_USERNAME'),
    'PASSWORD': os.getenv('DB_PASSWORD'),
    'DRIVER': os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
}

def test_connection():
    """Test the database connection"""
    try:
        conn_str = (
            f"DRIVER={{{DB_CONFIG['DRIVER']}}};"
            f"SERVER={DB_CONFIG['SERVER']};"
            f"DATABASE={DB_CONFIG['DATABASE']};"
            f"UID={DB_CONFIG['USERNAME']};"
            f"PWD={DB_CONFIG['PASSWORD']};"
        )
        
        print("Attempting to connect to database...")
        print(f"Server: {DB_CONFIG['SERVER']}")
        print(f"Database: {DB_CONFIG['DATABASE']}")
        print(f"Driver: {DB_CONFIG['DRIVER']}")
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Try to execute a simple query
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        
        print("\nConnection successful!")
        print("\nSQL Server version:")
        print(row[0])
        
        cursor.close()
        conn.close()
        
    except pyodbc.Error as e:
        print("\nError connecting to database:")
        print(str(e))
    except Exception as e:
        print("\nAn error occurred:")
        print(str(e))

if __name__ == "__main__":
    test_connection()