from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import duckdb

def write_test_data():
    conn = duckdb.connect("/opt/airflow/duckdb/my_database.duckdb")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS test_table (
        id INTEGER,
        name VARCHAR
    )
    """)
    conn.execute("INSERT INTO test_table VALUES (1, 'Alice'), (2, 'Bob')")
    conn.close()

with DAG(
    dag_id="duckdb_test",
    start_date=datetime(2026, 2, 1),
    schedule=None,  # <-- use 'schedule' instead of 'schedule_interval'
    catchup=False,
    max_active_runs=1,  # Prevent overlapping runs of this DAG
) as dag:

    task_write = PythonOperator(
        task_id="write_duckdb_data",
        python_callable=write_test_data
    )