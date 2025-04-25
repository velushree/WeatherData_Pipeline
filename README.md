# 🌤️ WeatherData_Pipeline

A complete end-to-end weather data pipeline that fetches weather data for cities, processes it using Kafka, stores it in MongoDB and Snowflake, and enables conversational Q&A using LangChain RAG models.

📌 Features

- 🌍 Fetches current and historical weather data for top global cities
- 🌀 Uses Kafka for real-time data streaming
- ⚙️ Apache Airflow for scheduled data processing and automation
- 🧠 RAG (Retrieval-Augmented Generation) chatbot powered by LangChain
- 🗃️ Stores data in MongoDB and Snowflake
- 🐳 Fully dockerized with `docker-compose`
- 🧪 Modular Python components for easy customization

Data Flow

Airflow DAGs --> Kafka Producer --> MongoDB/Snowflake
        ↘︎                             ↗︎
       Embedding + FAISS (RAG model) → Chatbot (LangChain)


🛠️ Tech Stack

Python, Pandas, FAISS
Apache Kafka & Airflow
MongoDB Atlas
Snowflake
Docker & Conda
LangChain + OpenAI Embeddings

-----

Getting Started

1. Clone the Repo

git clone https://github.com/<your-username>/WeatherData_Pipeline.git
cd WeatherData_Pipeline'

2. Set up environment
 
conda env create -f environment.yml
conda activate weather_env

3. Run with Docker
   
docker-compose up --build

4. Run kafka

python weather_data_responder.py

5. Run streamlit 

streamlit run app.py

-----

Chatbot Demo

“What was the weather in Tokyo last week?”

“Tell me about New York's recent climate”

