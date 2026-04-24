import pandas as pd
import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432,
    user="postgres", password="postgres", dbname="postgres"
)

df = pd.read_sql("SELECT * FROM whowillwin.matches", conn)

print(df)