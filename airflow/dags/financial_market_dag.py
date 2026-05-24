from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'issa_amjadi',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'financial_market_pipeline',
    default_args=default_args,
    description='End-to-end financial market data pipeline',
    schedule_interval='0 6 * * *',  # runs every day at 6am
    catchup=False,
)

# Task 1 - Ingest stock data from API to S3
ingest_task = BashOperator(
    task_id='ingest_stock_data',
    bash_command='python /opt/airflow/dags/fetch_stock_data.py',
    dag=dag,
)

# Task 2 - Run dbt models to transform data in Snowflake
dbt_task = BashOperator(
    task_id='run_dbt_models',
    bash_command='dbt run --project-dir /opt/airflow/dags/financial_market_dbt',
    dag=dag,
)

# Task 3 - Run dbt tests to validate data quality
dbt_test_task = BashOperator(
    task_id='run_dbt_tests',
    bash_command='dbt test --project-dir /opt/airflow/dags/financial_market_dbt',
    dag=dag,
)

# Define task order
ingest_task >> dbt_task >> dbt_test_task