from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
import duckdb

def init_db():
    conn = duckdb.connect("/opt/airflow/duckdb/steam_games.duckdb")

    with open("/opt/airflow/sql/ddl/steam_analysis_schema_init.sql") as f:
        conn.execute(f.read())

with DAG(
    dag_id="steam_analysis_schema_init",
    start_date=datetime(2026, 2, 1),
    schedule=None,  # <-- Manual execution only'
    catchup=False,
    max_active_runs=1,  # Prevent overlapping runs of this DAG
) as dag:
    
    init_database = PythonOperator(
        task_id="db_init",
        python_callable=init_db
    )
