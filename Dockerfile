# Base image
FROM apache/airflow:2.8.1-python3.9

USER airflow

# Installes Dependencies
RUN pip install --no-cache-dir kafka-python requests pymongo meteostat geopy sentence-transformers langchain langchain_community faiss-cpu 

# Copy DAGs and scripts
COPY ./dags /opt/airflow/dags
COPY ./scripts /opt/airflow/scripts