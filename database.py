import psycopg
from psycopg import sql
import sys

# --- Database Configuration ---
DB_NAME = "MYUBER_db"
DB_USER = "postgres"
DB_PASS = "0987" # Make sure this is your actual password for the postgres user
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database():
    """Creates the database if it doesn't exist."""
    try:
        conn = psycopg.connect(
            f"user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT} dbname=postgres",
            autocommit=True
        )
        cur = conn.cursor()
        
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        if not cur.fetchone():
            print(f"📦 Creating database '{DB_NAME}'...")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"✅ Database '{DB_NAME}' created successfully!")
        else:
            print(f"✓ Database '{DB_NAME}' already exists.")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection/creation failed: {e}")
        return False

def get_db_connection():
    """Establishes a connection to the MYUBER database."""
    return psycopg.connect(
        f"user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT} dbname={DB_NAME}"
    )

def setup_schema_and_data():
    """Creates tables and inserts sample data."""
    commands = [
        """
        DROP TABLE IF EXISTS rides CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
        DROP TABLE IF EXISTS drivers CASCADE;
        """,
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE drivers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            vehicle_details VARCHAR(255),
            online_status VARCHAR(50) DEFAULT 'offline',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE rides (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            driver_id INTEGER REFERENCES drivers(id),
            source_location VARCHAR(255) NOT NULL,
            dest_location VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL,
            fare NUMERIC(10, 2),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP WITH TIME ZONE
        );
        """,
        "INSERT INTO users (name, email, phone) VALUES ('Alice', 'alice@example.com', '111-222-3333');",
        "INSERT INTO users (name, email, phone) VALUES ('Bob', 'bob@example.com', '444-555-6666');",
        "INSERT INTO drivers (name, email, vehicle_details, online_status) VALUES ('Charlie', 'charlie@driver.com', 'Toyota Camry (KA-01-C-1234)', 'online');",
        "INSERT INTO drivers (name, email, vehicle_details, online_status) VALUES ('Diana', 'diana@driver.com', 'Honda Civic (KA-02-D-5678)', 'offline');",
    ]
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                print("🔄 Setting up database schema and sample data...")
                for command in commands:
                    cur.execute(command)
        print("✅ Schema and sample data created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error during schema setup: {e}")
        return False

def verify_setup():
    """Verifies that the database and tables were created correctly."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                print("\n🔍 Verifying setup...")
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
                tables = [row[0] for row in cur.fetchall()]
                print(f"✓ Tables found: {', '.join(tables)}")
                
                cur.execute("SELECT COUNT(*) FROM users;")
                user_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM drivers;")
                driver_count = cur.fetchone()[0]
                
                print(f"👥 Users: {user_count}")
                print(f"🚗 Drivers: {driver_count}")
                
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🚗 MYUBER Database Setup")
    print("=" * 60)
    
    if not create_database():
        sys.exit("❌ Database creation failed. Exiting.")
    
    if not setup_schema_and_data():
        sys.exit("❌ Schema setup failed. Exiting.")
    
    if verify_setup():
        print("\n" + "=" * 60)
        print("🎉 Database setup completed successfully!")
        print("=" * 60)

if __name__ == '__main__':
    main()