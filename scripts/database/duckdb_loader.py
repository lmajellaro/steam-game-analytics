from scripts.settings import DB_PATH
from scripts.utils.sql_loader import load_sql
import duckdb

##########################################
# Load data to the target staging table #
########################################
def load_df_to_duckdb(df, sql_statement_file):
    """
    Loads a Pandas DataFrame into DuckDB by:
    1. Registering the DataFrame as a temporary table
    2. Executing a SQL statement to transform and persist the data
    3. Cleaning up the temporary object

    Parameters:
    - df (DataFrame): Source data to be loaded
    - sql_statement_file (str): file location containing the SQL template with placeholder for source
    """

    source_df = 'tmp_df'

    print(f"Database path: {DB_PATH}")
    print(f"SQL file: {sql_statement_file}")
    print(f"Input dataframe rows: {len(df)}")
    print(f"Input dataframe columns: {list(df.columns)}")

    try:
        conn = duckdb.connect(DB_PATH)
        conn.register(source_df, df)

        print(f"Temporary dataframe '{source_df}' registered")

        print(f"Executing SQL from: {sql_statement_file}")

        query = load_sql(
            sql_statement_file,
            source_df=source_df
        )

        print("Executing SQL:")
        print(query)

        conn.execute(query)

        try:
            result = conn.execute("""
                SHOW TABLES
            """).fetchall()

            print("Tables currently in DuckDB:")
            print(result)

        except Exception as e:
            print(f"Could not retrieve table list: {e}")

    finally:
        if conn:
            try:
                conn.unregister(source_df)
            except:
                pass

            conn.close()
            
            print(f"The statement affected {len(df)} rows")
