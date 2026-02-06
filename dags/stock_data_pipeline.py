from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 2, 5),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'stock_market_pipeline',
    default_args=default_args,
    description='Daily stock market data collection and analytics',
    schedule_interval='0 22 * * *',  # Run daily at 22:00 (10 PM)
    catchup=False,  # Don't run for past dates
)

# Task 1: Fetch stock data from API
fetch_stock_data = BashOperator(
    task_id='fetch_stock_data',
    bash_command='python /opt/airflow/scripts/fetch_stock_data.py',
    dag=dag,
)

# Task 2: Calculate analytics (returns, portfolio)
calculate_analytics = BashOperator(
    task_id='calculate_analytics',
    bash_command='python /opt/airflow/scripts/calculate_metrics.py',
    dag=dag,
)

# Define task dependencies: fetch_data THEN calculate
fetch_stock_data >> calculate_analytics