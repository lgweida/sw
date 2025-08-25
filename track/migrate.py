import os
import sqlite3
import psycopg2
from urllib.parse import urlparse
import logging
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_postgres_connection():
    """Get PostgreSQL connection from environment variable"""
    external_url = os.getenv('EXTERNAL_URL')
    if not external_url:
        raise ValueError("EXTERNAL_URL environment variable is not set")
    
    # Parse the connection URL
    result = urlparse(external_url)
    
    # Extract connection parameters
    dbname = result.path[1:]  # Remove leading slash
    user = result.username
    password = result.password
    host = result.hostname
    port = result.port or 5432
    
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        logger.info("Successfully connected to PostgreSQL database")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise

def get_sqlite_connection(sqlite_db_path='support_activities.db'):
    """Get SQLite connection"""
    try:
        conn = sqlite3.connect(sqlite_db_path)
        logger.info(f"Successfully connected to SQLite database: {sqlite_db_path}")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to SQLite database: {e}")
        raise

def get_activities():
    conn = sqlite3.connect('support_activities.db')
    df = pd.read_sql_query("SELECT * FROM activities ORDER BY date DESC", conn)
    print(df)
    conn.close()
    return df

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    sqlite_conn = None
    postgres_conn = None

    df = get_activities() 
    print(df)
    
    try:
        # Connect to both databases
        sqlite_conn = get_sqlite_connection()
        postgres_conn = get_postgres_connection()
        
        # Create cursor for both databases
        sqlite_cursor = sqlite_conn.cursor()
        postgres_cursor = postgres_conn.cursor()
        
        # Create table in PostgreSQL (if not exists)
        postgres_cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id TEXT PRIMARY KEY,
                date TEXT,
                title TEXT,
                category TEXT,
                details TEXT,
                links TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        logger.info("Created/verified activities table in PostgreSQL")
        
        # Read data from SQLite
        sqlite_cursor.execute('SELECT * FROM activities')
        rows = sqlite_cursor.fetchall()
        logger.info(f"Found {len(rows)} records in SQLite activities table")
        
        if not rows:
            logger.warning("No data found in SQLite activities table")
            return
        
        # Insert data into PostgreSQL
        insert_query = '''
            INSERT INTO activities (id, date, title, category, details, links, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                date = EXCLUDED.date,
                title = EXCLUDED.title,
                category = EXCLUDED.category,
                details = EXCLUDED.details,
                links = EXCLUDED.links,
                updated_at = EXCLUDED.updated_at
        '''
        
        # Convert SQLite rows to tuples (already in correct format)
        records = [tuple(row) for row in rows]
        
        # Insert in batches to handle large datasets
        batch_size = 100
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            postgres_cursor.executemany(insert_query, batch)
            logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")
        
        # Commit the transaction
        postgres_conn.commit()
        logger.info(f"Successfully migrated {len(records)} records to PostgreSQL")
        
        # Verify the migration
        postgres_cursor.execute('SELECT COUNT(*) FROM activities')
        postgres_count = postgres_cursor.fetchone()[0]
        logger.info(f"PostgreSQL now has {postgres_count} records in activities table")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        if postgres_conn:
            postgres_conn.rollback()
        raise
        
    finally:
        # Close connections
        if sqlite_conn:
            sqlite_conn.close()
        if postgres_conn:
            postgres_conn.close()
        logger.info("Database connections closed")

if __name__ == "__main__":
    # Optional: specify SQLite database path as command line argument
    import sys
    sqlite_db_path = sys.argv[1] if len(sys.argv) > 1 else 'database.db'
    print(f"Using SQLite database: {sqlite_db_path}")

    
    try:
        logger.info("Starting database migration from SQLite to PostgreSQL")
        migrate_data()
        logger.info("Migration completed successfully!")
    except Exception as e:
        logger.error(f"Migration failed with error: {e}")
        sys.exit(1)