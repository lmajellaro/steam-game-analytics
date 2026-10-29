FROM apache/airflow:3.1.6

COPY requirements-common.txt requirements-airflow.txt ./

RUN pip install --no-cache-dir  -r requirements-airflow.txt
USER airflow