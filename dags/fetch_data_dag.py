import os
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.environ['AIRFLOW_HOME'], 'scripts'))
from store_in_mongodb import store_in_db
from weather_history_util import fetch_weather_history

cities = ["New York", "London", "Tokyo", "Paris", "Los Angeles", "Chicago", "Beijing", "Mumbai", "Bangkok", "Dubai", "Singapore", "Toronto", "San Francisco", "Istanbul", "Seoul", "Mexico City", "Moscow", "Sydney", "Barcelona", "Rome", "Berlin", "Amsterdam", "Delhi", "Shanghai", "Cairo", "Jakarta", "Hong Kong", "Buenos Aires", "Lagos"]

default_args = {
    'owner': 'admin',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

def fetch_city_weather():
    for city in cities:
        doc = fetch_weather_history(city)
        for entry in doc:
            weather_summary = {"weather_summary": entry}
            store_in_db(weather_summary)  

with DAG(
    dag_id="fetch_weather_dag",
    default_args=default_args,
    start_date=datetime(2025, 4, 18),
    schedule_interval= '0 */6 * * *',
    catchup=False,
    description="Fetches weather data from API and sends to Kafka"
) as dag:

    fetch_weather_task = PythonOperator(
        task_id='fetch_weather',
        python_callable=fetch_city_weather,
        provide_context=True
    )

    fetch_weather_task 