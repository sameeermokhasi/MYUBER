from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config.settings import settings

# This line creates the database connection URL from your settings file.
DATABASE_URL = settings.database_url

# The engine is the core interface to the database.
engine = create_engine(DATABASE_URL)

# A sessionmaker creates new database sessions, which are the primary
# interface for all database queries.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is the crucial line. We create a 'Base' class here.
# All of your database models (like the Ride model) will inherit from this class.
Base = declarative_base()

# This is a dependency for your API endpoints. It ensures that a database
# session is created for each request and then closed afterward.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
