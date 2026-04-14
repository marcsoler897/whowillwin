import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "postgres",
    "dbname": "postgres",
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)
