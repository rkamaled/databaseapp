import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    'SERVER': os.getenv('DB_SERVER'),
    'DATABASE': os.getenv('DB_DATABASE'),
    'USERNAME': os.getenv('DB_USERNAME'),
    'PASSWORD': os.getenv('DB_PASSWORD'),
    'DRIVER': os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
}

def test():
    conn_str = f"DRIVER={{{DB_CONFIG['DRIVER']}}};SERVER={DB_CONFIG['SERVER']};DATABASE={DB_CONFIG['DATABASE']};UID={DB_CONFIG['USERNAME']};PWD={DB_CONFIG['PASSWORD']};"
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Basic count
        cursor.execute("SELECT COUNT(*) FROM life_labs_2025")
        total = cursor.fetchone()[0]
        print(f"Total rows: {total}")
        
        # Sample PIDs
        cursor.execute("SELECT DISTINCT pid FROM life_labs_2025 ORDER BY pid LIMIT 10")
        pids = [row[0] for row in cursor.fetchall()]
        print(f"Sample PIDs: {pids}")
        
        # Time points
        cursor.execute("SELECT DISTINCT time_point FROM life_labs_2025 ORDER BY time_point")
        timepoints = [row[0] for row in cursor.fetchall()]
        print(f"Time points: {timepoints}")
        
        # PID patterns
        cursor.execute("SELECT LEFT(pid, 1), COUNT(*) FROM life_labs_2025 GROUP BY LEFT(pid, 1) ORDER BY LEFT(pid, 1)")
        patterns = cursor.fetchall()
        print("PID patterns:")
        for pattern in patterns:
            print(f"  {pattern[0]}: {pattern[1]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
