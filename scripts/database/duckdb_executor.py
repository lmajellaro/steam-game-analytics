import duckdb
from scripts.settings import DB_PATH
from scripts.utils.sql_loader import load_sql

def execute_duckdb_sql(sql_file):

    conn = duckdb.connect(DB_PATH)
    
    query = load_sql(sql_file)
    
    conn.execute(query)
    
    conn.close()