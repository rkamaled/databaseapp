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

def test_simple():
    conn_str = f"DRIVER={{{DB_CONFIG['DRIVER']}}};SERVER={DB_CONFIG['SERVER']};DATABASE={DB_CONFIG['DATABASE']};UID={DB_CONFIG['USERNAME']};PWD={DB_CONFIG['PASSWORD']};"
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Test 1: Simple count without any filters
        print("=== Test 1: Simple count ===")
        cursor.execute("SELECT COUNT(DISTINCT pid) FROM life_labs_2025")
        count = cursor.fetchone()[0]
        print(f"Total unique PIDs: {count}")
        
        # Test 2: Count with PID filter only
        print("\n=== Test 2: PID filter only ===")
        cursor.execute("""
            SELECT COUNT(DISTINCT pid) 
            FROM life_labs_2025 
            WHERE UPPER(LEFT(pid, 1)) IN ('A', 'B', 'C', 'P', 'S')
        """)
        filtered_count = cursor.fetchone()[0]
        print(f"PIDs with A,B,C,P,S: {filtered_count}")
        
        # Test 3: Count with time point filter only
        print("\n=== Test 3: Time point filter only ===")
        cursor.execute("""
            SELECT COUNT(DISTINCT pid) 
            FROM life_labs_2025 
            WHERE time_point IN (1,2,3,4,5,6,7,8,9)
        """)
        timepoint_count = cursor.fetchone()[0]
        print(f"PIDs with any of timepoints 1-9: {timepoint_count}")
        
        # Test 4: Count with both filters
        print("\n=== Test 4: Both filters ===")
        cursor.execute("""
            SELECT COUNT(DISTINCT pid) 
            FROM life_labs_2025 
            WHERE UPPER(LEFT(pid, 1)) IN ('A', 'B', 'C', 'P', 'S')
              AND time_point IN (1,2,3,4,5,6,7,8,9)
        """)
        both_count = cursor.fetchone()[0]
        print(f"PIDs with both filters: {both_count}")
        
        # Test 5: Check how many time points each PID has
        print("\n=== Test 5: Time point distribution ===")
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT time_point) as time_point_count,
                COUNT(*) as pid_count
            FROM life_labs_2025 
            WHERE UPPER(LEFT(pid, 1)) IN ('A', 'B', 'C', 'P', 'S')
            GROUP BY pid
            ORDER BY time_point_count
        """)
        timepoint_dist = cursor.fetchall()
        print("Time point distribution:")
        for row in timepoint_dist:
            print(f"  {row[0]} timepoints: {row[1]} PIDs")
        
        # Test 6: Check if any PIDs have exactly 9 time points
        print("\n=== Test 6: PIDs with exactly 9 time points ===")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM (
                SELECT pid
                FROM life_labs_2025 
                WHERE UPPER(LEFT(pid, 1)) IN ('A', 'B', 'C', 'P', 'S')
                GROUP BY pid
                HAVING COUNT(DISTINCT time_point) = 9
            ) t
        """)
        exact_9_count = cursor.fetchone()[0]
        print(f"PIDs with exactly 9 time points: {exact_9_count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple()
