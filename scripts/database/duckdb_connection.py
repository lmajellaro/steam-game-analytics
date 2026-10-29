import duckdb

def get_connection(db_path):
    return duckdb.connect(db_path, read_only=True)