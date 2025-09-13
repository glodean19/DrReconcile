"""
    ENGINE
"""

from sqlalchemy import create_engine

def get_engine():
    """
        SQLAlchemy enstablished the connection with the database by creating an engine 
        object based on the URL containing username, password, host and port.
        The engine connect the PostgreSQL psycopg2 driver to a 
        PostgreSQL-dialect database healthcare.
    """
    user = "myuser"
    password = "mypassword"
    host = "localhost"
    port = "5432"
    database = "healthcare"
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")
