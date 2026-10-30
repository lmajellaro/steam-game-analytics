#import os
import sys
sys.path.insert(0, "/opt/airflow")

from scripts.settings import (
 #   DB_PATH,
 #   BASE_SQL_PATH,
    UPSERT_PIPELINE_LOG_SCRIPT,
    # STAGING
    RAW_GAME_DETAILS_SCRIPT,
    RAW_CURRENT_PLAYERS_SCRIPT,
    RAW_STEAMSPY_GAME_STATS_SCRIPT,
    RAW_STEAM_REVIEWS_SCRIPT,
    RAW_STEAM_NEWS_SCRIPT,
    RAW_STEAM_ACHIEVEMENT_STATS_SCRIPT,
    # GOLD
    UPSERT_GAME_GENRE_SCRIPT,
    UPSERT_GAME_INFO_SCRIPT,
    UPSERT_GENRE_SCRIPT,
    UPSERT_STEAM_GAME_DAILY_STATS_SCRIPT,
    UPSERT_STEAM_GAME_NEWS_SCRIPT
)

from scripts.utils.sql_loader import load_sql

from scripts.database.duckdb_loader import load_df_to_duckdb
from scripts.database.duckdb_executor import execute_duckdb_sql
from scripts.database.pipeline_logging import update_pipeline_status

from scripts.steamspy.steamspy_app_ids import get_unique_steamspy_app_ids
from scripts.steamspy.steamspy_game_stats import fetch_steamspy_game_stats_async
from scripts.steam_api.steam_game_details import fetch_steam_game_details_async
from scripts.steam_api.steam_current_players import fetch_steam_current_players_data_asynch
from scripts.steam_api.steam_reviews import fetch_steam_reviews_async
from scripts.steam_api.steam_news import fetch_steam_news_async
from scripts.steam_api.steam_achievement_stats import fetch_steam_achievement_stats_async

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from pathlib import Path

# ======== Define functions for the tasks ========

#################################################
# Mark pipeline execution as running            #
#################################################
def mark_pipeline_running_task(**context):

    update_pipeline_status(
        context['dag'].dag_id,
        context['ds'],
        "running",
        UPSERT_PIPELINE_LOG_SCRIPT
    )

#################################################
# Mark pipeline execution as successful         #
#################################################
def mark_pipeline_success_task(**context):

    update_pipeline_status(
        context['dag'].dag_id,
        context['ds'],
        "success",
        UPSERT_PIPELINE_LOG_SCRIPT
    )

#################################################
# Retrieve Steam AppIDs and share through XCom #
#################################################
def get_steamspy_app_ids_task(**context):
    """
    Retrieves the list of Steam AppIDs from SteamSpy
    and existing database records.

    Returns:
    - list: Unique Steam AppIDs
    """
    dag_id = context['dag'].dag_id
    run_date = context['ds']

    try:
        app_ids = get_unique_steamspy_app_ids()
        print(f"Retrieved {len(app_ids)} unique app_ids")
        return app_ids
    
    except Exception as e:

        print(f"Current players task failed: {e}")

        update_pipeline_status(
            dag_id,
            run_date,
            "failed",
            UPSERT_PIPELINE_LOG_SCRIPT
        )

        raise

#####################################################
# Fetch and load Steam game details into DuckDB     #
#####################################################
def fetch_steam_game_details_task(**context):
    """
    Fetches detailed Steam game metadata from the API
    and loads the raw responses into DuckDB staging tables.
    """
    dag_id = context['dag'].dag_id
    run_date = context['ds']
    
    try:
        # Retrieve app_ids from XCom
        app_ids = context["ti"].xcom_pull(
            task_ids="get_steamspy_app_ids"
        )

        print(f"Received {len(app_ids)} app_ids from XCom")

        # Fetch game details
        df = fetch_steam_game_details_async(app_ids)

        print(f"Fetched {len(df)} game detail records")

        # Load into DuckDB
        load_df_to_duckdb(df, RAW_GAME_DETAILS_SCRIPT)

    except Exception as e:

        print(f"Current players task failed: {e}")

        update_pipeline_status(
            dag_id,
            run_date,
            "failed",
            UPSERT_PIPELINE_LOG_SCRIPT
        )

        raise

#####################################################
# Fetch and load current player counts into DuckDB  #
#####################################################
def fetch_current_players_task(**context):
    """
    Fetches current Steam player counts from the API
    and loads the raw responses into DuckDB staging tables.
    """
    dag_id = context['dag'].dag_id
    run_date = context['ds']

    try:
        app_ids = context["ti"].xcom_pull(
            task_ids="get_steamspy_app_ids"
        )

        print(f"Received {len(app_ids)} app_ids from XCom")

        df = fetch_steam_current_players_data_asynch(app_ids)

        print(f"Fetched {len(df)} current player records")

        load_df_to_duckdb(df, RAW_CURRENT_PLAYERS_SCRIPT)

    except Exception as e:

        print(f"Current players task failed: {e}")

        update_pipeline_status(
            dag_id,
            run_date,
            "failed",
            UPSERT_PIPELINE_LOG_SCRIPT
        )

        raise

###############################################################
# Fetch and load SteamSpy stats into DuckDB                  #
###############################################################
def fetch_steamspy_stats_task(**context):

    dag_id = context['dag'].dag_id
    run_date = context['ds']

    try:

        app_ids = context["ti"].xcom_pull(
            task_ids="get_steamspy_app_ids"
        )

        print(f"Received {len(app_ids)} app_ids from XCom")

        df = fetch_steamspy_game_stats_async(app_ids)

        print(f"Fetched {len(df)} SteamSpy records")

        load_df_to_duckdb(
            df,
            RAW_STEAMSPY_GAME_STATS_SCRIPT
        )

    except Exception as e:

        print(f"SteamSpy task failed: {e}")

        update_pipeline_status(
            dag_id,
            run_date,
            "failed",
            UPSERT_PIPELINE_LOG_SCRIPT
        )

        raise

###############################################################
# Fetch and load Steam reviews into DuckDB                  #
###############################################################
def fetch_steam_reviews_task(**context):

    dag_id = context['dag'].dag_id
    run_date = context['ds']

    try:

        app_ids = context["ti"].xcom_pull(
            task_ids="get_steamspy_app_ids"
        )

        print(f"Received {len(app_ids)} app_ids from XCom")

        df = fetch_steam_reviews_async(app_ids)

        print(f"Fetched {len(df)} SteamSpy records")

        if df.empty or len(df.columns) == 0:
            raise ValueError(
        "SteamSpy returned no usable records. "
        "Skipping DuckDB load to avoid processing an empty dataset."
        )

        load_df_to_duckdb(
            df,
            RAW_STEAM_REVIEWS_SCRIPT
        )

    except Exception as e:

        print(f"SteamSpy task failed: {e}")

        update_pipeline_status(
            dag_id,
            run_date,
            "failed",
            UPSERT_PIPELINE_LOG_SCRIPT
        )

        raise

###############################################################
# Fetch and load Steam News into DuckDB                  #
###############################################################
def fetch_steam_news_task(**context):

    dag_id = context['dag'].dag_id
    run_date = context['ds']

    try:

        app_ids = context["ti"].xcom_pull(
            task_ids="get_steamspy_app_ids"
        )

        print(f"Received {len(app_ids)} app_ids from XCom")

        df = fetch_steam_news_async(app_ids)

        print(f"Fetched {len(df)} SteamSpy records")

        load_df_to_duckdb(
            df,
            RAW_STEAM_NEWS_SCRIPT
        )

    except Exception as e:

        print(f"SteamSpy task failed: {e}")

        update_pipeline_status(
            dag_id,
            run_date,
            "failed",
            UPSERT_PIPELINE_LOG_SCRIPT
        )

        raise

###############################################################
# Fetch and load Steam Achievement into DuckDB                  #
###############################################################
def fetch_steam_achievement_task(**context):

    dag_id = context['dag'].dag_id
    run_date = context['ds']

    try:

        app_ids = context["ti"].xcom_pull(
            task_ids="get_steamspy_app_ids"
        )

        print(f"Received {len(app_ids)} app_ids from XCom")

        df = fetch_steam_achievement_stats_async(app_ids)

        print(f"Fetched {len(df)} SteamSpy records")

        load_df_to_duckdb(
            df,
            RAW_STEAM_ACHIEVEMENT_STATS_SCRIPT
        )

    except Exception as e:

        print(f"SteamSpy task failed: {e}")

        update_pipeline_status(
            dag_id,
            run_date,
            "failed",
            UPSERT_PIPELINE_LOG_SCRIPT
        )

        raise

# ================================
# ======== DAG definition ========
# ================================

default_args = {
    "owner": "airflow",
    "retries": 3,
    "retry_delay": timedelta(minutes=3)
}

def staging_checkpoint_task():
    """
    Synchronization checkpoint between staging
    and downstream transformation tasks.
    """
    print("Staging checkpoint reached.")
    return "Staging checkpoint reached."

with DAG(
    dag_id="steam_analysis_schema_pipeline",
    start_date=datetime(2026, 1, 1),
    # Enable the schedule after initializing the live target database
    # running the initialization DAG steam_analysis_schema_init
    # schedule="@daily",
    schedule=None,
    catchup=False,
    max_active_runs=1,  # Prevent overlapping runs of this DAG
    default_args=default_args,
    tags=["steam", "async", "duckdb"]
) as dag:

    mark_pipeline_running = PythonOperator(
        task_id="mark_pipeline_running",
        python_callable=mark_pipeline_running_task,
    )
    
    get_steamspy_app_ids = PythonOperator(
        task_id="get_steamspy_app_ids",
        python_callable=get_steamspy_app_ids_task,
    )
    
    fetch_steam_game_details = PythonOperator(
        task_id="fetch_steam_game_details",
        python_callable=fetch_steam_game_details_task,
    )
    
    fetch_current_players = PythonOperator(
        task_id="fetch_current_players",
        python_callable=fetch_current_players_task,
    )

    fetch_steamspy_stats = PythonOperator(
    task_id="fetch_steamspy_stats",
    python_callable=fetch_steamspy_stats_task,
    )

    fetch_steam_reviews = PythonOperator(
    task_id="fetch_steam_reviews",
    python_callable=fetch_steam_reviews_task,
    )

    fetch_steam_news = PythonOperator(
    task_id="fetch_steam_news",
    python_callable=fetch_steam_news_task,
    )

    fetch_steam_achievement = PythonOperator(
    task_id="fetch_steam_achievement",
    python_callable=fetch_steam_achievement_task,
    )
    
    mark_pipeline_success = PythonOperator(
        task_id="mark_pipeline_success",
        python_callable=mark_pipeline_success_task,
    )

    staging_checkpoint = PythonOperator(
        task_id="staging_checkpoint",
        python_callable=staging_checkpoint_task,
    )

    # GOLD LAYER TRANSFORMATIONS

    upsert_game_genre = PythonOperator(
    task_id="upsert_game_genre",
    python_callable=execute_duckdb_sql,
    op_kwargs={
        "sql_file": UPSERT_GAME_GENRE_SCRIPT
        }
    )

    upsert_game_info = PythonOperator(
    task_id="upsert_game_info",
    python_callable=execute_duckdb_sql,
    op_kwargs={
        "sql_file": UPSERT_GAME_INFO_SCRIPT
        }
    )

    upsert_genre = PythonOperator(
    task_id="upsert_genre",
    python_callable=execute_duckdb_sql,
    op_kwargs={
        "sql_file": UPSERT_GENRE_SCRIPT
        }
    )

    upsert_steam_game_daily_stats= PythonOperator(
    task_id="upsert_steam_game_daily_stats",
    python_callable=execute_duckdb_sql,
    op_kwargs={
        "sql_file": UPSERT_STEAM_GAME_DAILY_STATS_SCRIPT
        }
    )

    upsert_steam_game_news= PythonOperator(
    task_id="upsert_steam_game_news",
    python_callable=execute_duckdb_sql,
    op_kwargs={
        "sql_file": UPSERT_STEAM_GAME_NEWS_SCRIPT
        }
    )
    
    

# Dependencies
mark_pipeline_running >> get_steamspy_app_ids

# Don't execute all the API request tasks in parallel to avoid getting the requests rejected by Steam
get_steamspy_app_ids >> fetch_current_players >> fetch_steamspy_stats >> fetch_steam_game_details >> fetch_steam_news >> fetch_steam_reviews >> fetch_steam_achievement >> staging_checkpoint

# DuckDB doesn't allow parallel tasks to access the same database
staging_checkpoint >> upsert_game_genre >> upsert_game_info >> upsert_genre >> upsert_steam_game_daily_stats >> upsert_steam_game_news >> mark_pipeline_success