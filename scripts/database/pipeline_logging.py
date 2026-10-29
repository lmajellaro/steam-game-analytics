from scripts.settings import DB_PATH
from scripts.utils.sql_loader import load_sql
from datetime import datetime, timezone
import duckdb

# ======== Pipeline progress tracking ========

def update_pipeline_status(dag_id, run_date, status, sql_statement_file):

    conn = None

    try:
        conn = duckdb.connect(DB_PATH)

        # Prepare values
        last_success_ts = datetime.now(timezone.utc) if status.lower() == "success" else None
        # Run DML
        dml_query = load_sql(sql_statement_file)
        conn.execute(dml_query, [dag_id, run_date, status, last_success_ts])

    finally:
        if conn:
            conn.close()