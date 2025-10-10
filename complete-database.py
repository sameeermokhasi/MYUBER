import psycopg
from psycopg import sql
import sys

# --- Database Configuration ---
DB_NAME = "mini_uber_db"
DB_USER = "postgres"
DB_PASS = "Venkatraman123"
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database():
    """Creates the database if it doesn't exist."""
    try:
        # Connect to postgres database to create our database
        conn = psycopg.connect(
            f"user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT} dbname=postgres",
            autocommit=True
        )
        cur = conn.cursor()
        
        # Check if database exists
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
    """Establishes a connection to the mini_uber_db database."""
    try:
        return psycopg.connect(
            f"user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT} dbname={DB_NAME}",
            autocommit=True
        )
    except psycopg.OperationalError as e:
        print(f"❌ CRITICAL: Database connection failed: {e}")
        raise

def setup_schema_and_data():
    """Drops old tables and creates a fresh schema with all features."""
    
    # --- Table Creation Commands ---
    commands = [
        "DROP TABLE IF EXISTS rides CASCADE;",
        "DROP TABLE IF EXISTS users CASCADE;",
        "DROP TABLE IF EXISTS drivers CASCADE;",
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );""",
        """
        CREATE TABLE drivers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            vehicle_details VARCHAR(255),
            online_status VARCHAR(20) DEFAULT 'offline',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );""",
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
        );""",
        """
        CREATE INDEX idx_rides_user_id ON rides(user_id);
        """,
        """
        CREATE INDEX idx_rides_driver_id ON rides(driver_id);
        """,
        """
        CREATE INDEX idx_rides_status ON rides(status);
        """
    ]
    
    # --- Sample Data ---
    sample_data = [
        "INSERT INTO users (id, name, email, phone) VALUES (101, 'Rohan Sharma', 'rohan@example.com', '555-0101');",
        "INSERT INTO users (id, name, email, phone) VALUES (102, 'Anjali Verma', 'anjali@example.com', '555-0102');",
        "INSERT INTO drivers (id, name, email, vehicle_details) VALUES (201, 'Priya Singh', 'priya@example.com', 'Maruti Swift (DL-01-AB-1234)');",
        "INSERT INTO drivers (id, name, email, vehicle_details) VALUES (202, 'Raj Kumar', 'raj@example.com', 'Honda City (DL-02-CD-5678)');"
    ]

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                print("🗑️  Dropping old tables...")
                for command in commands[:3]:  # Drop commands
                    cur.execute(command)
                print("✓ Old tables dropped")
                
                print("🏗️  Creating fresh schema...")
                for command in commands[3:]:  # Create commands
                    cur.execute(command)
                print("✓ Tables and indexes created")
                
                print("📝 Inserting sample data...")
                for data in sample_data:
                    cur.execute(data)
                print("✓ Sample data inserted")
                
                # --- Reset ID Counters ---
                print("🔄 Resetting primary key sequences...")
                cur.execute("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));")
                cur.execute("SELECT setval('drivers_id_seq', (SELECT MAX(id) FROM drivers));")
                # For rides, use setval with is_called=false since table is empty
                cur.execute("SELECT setval('rides_id_seq', 1, false);")
                print("✓ Sequences reset")

        print("✅ Database has been completely reset and is ready to use!")
        return True
    except Exception as e:
        print(f"❌ Error during schema setup: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_setup():
    """Verifies that the database setup was successful."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check tables exist
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name;
                """)
                tables = [row[0] for row in cur.fetchall()]
                print(f"\n📋 Tables created: {', '.join(tables)}")
                
                # Check sample data
                cur.execute("SELECT COUNT(*) FROM users;")
                user_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM drivers;")
                driver_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM rides;")
                ride_count = cur.fetchone()[0]
                
                print(f"👥 Users: {user_count}")
                print(f"🚗 Drivers: {driver_count}")
                print(f"🚕 Rides: {ride_count}")
                
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🚗 Mini Uber Database Setup")
    print("=" * 60)
    
    if not create_database():
        sys.exit("❌ Database creation failed. Exiting.")
    
    if not setup_schema_and_data():
        sys.exit("❌ Schema setup failed. Exiting.")
    
    if verify_setup():
        print("\n" + "=" * 60)
        print("🎉 Database setup completed successfully!")
        print("=" * 60)
        print("\n💡 Next steps:")
        print("   1. Start the server: python server.py")
        print("   2. Start the driver client: python driver_client.py")
        print("   3. Start the user client: python user_client.py")
    else:
        sys.exit("❌ Verification failed. Please check the errors above.")

if __name__ == '__main__':
    main()