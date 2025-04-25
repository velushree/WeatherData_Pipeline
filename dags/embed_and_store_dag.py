import os
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.environ['AIRFLOW_HOME'], 'scripts'))
from store_embeddings import embed_pipeline

DATA_DIR = "/opt/airflow/data"

default_args = {
    'owner': 'admin',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id="store_weather_embeddings_dag",
    default_args=default_args,
    start_date=datetime(2025, 4, 18),
    schedule_interval= '0 */6 * * *',
    catchup=False,
    description="Fetches weather data from mongodb and then embedds it in chromadb"
) as dag:

    embedding_task = PythonOperator(
        task_id='embedding_task',
        python_callable = embed_pipeline,
        provide_context=True
    )
    
    embedding_task 
 