import time
import json
import streamlit as st
from dotenv import load_dotenv
from components.rag_model import get_chatbot_response
from langchain_core.messages import HumanMessage
from langchain.embeddings import HuggingFaceEmbeddings
from kafka import KafkaConsumer
from kafka_weather_data.weather_data_producer import send_weather_request

# Load environment variables
load_dotenv()

# Embeddings setup (optional, used for RAG)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Supported cities list
cities = [
    "New York", "London", "Tokyo", "Paris", "Los Angeles", "Chicago", "Beijing", "Mumbai", "Bangkok", "Dubai",
    "Singapore", "Toronto", "San Francisco", "Istanbul", "Seoul", "Mexico City", "Moscow", "Sydney", "Barcelona",
    "Rome", "Berlin", "Amsterdam", "Delhi", "Shanghai", "Cairo", "Jakarta", "Hong Kong", "Buenos Aires", "Lagos"
]

def wait_for_weather_response(request_id, timeout=15):
    consumer = KafkaConsumer(
        'current_weather_data',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        consumer_timeout_ms=timeout * 1000
    )

    start = time.time()
    for msg in consumer:
        if msg.value.get("request_id") == request_id:
            return msg.value["weather"]
        if time.time() - start > timeout:
            break
    return None

# UI setup
st.title("🌦️ WeatherBot")
st.markdown("Ask about **weather forecasts** or **self-care tips** :")
st.markdown("### 🌍 Supported Cities for weather prediction")
st.markdown(", ".join([f"`{city}`" for city in cities]))

# Session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Styling (just padding tweaks)
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Input UI
col1, col2 = st.columns([3, 1.2]) 
with col1:
    city = st.text_input("", key="city_input", placeholder="Enter a city to get live weather:", label_visibility="collapsed")
with col2:
    submit = st.button("Get Current Weather")

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Handle button press
if submit and city:
    req_id = send_weather_request(city)
    st.session_state["pending_request"] = req_id
    st.session_state["waiting_city"] = city
    st.success(f"Weather request sent for {city}!")

# Fetch and show weather from Kafka
if "pending_request" in st.session_state and "waiting_city" in st.session_state:
    city_name = st.session_state["waiting_city"]
    st.write(f"Fetching current weather for **{city_name}**...")

    weather_data = wait_for_weather_response(st.session_state["pending_request"])

    if weather_data:
        st.success(f"Current Weather in {city_name}")
        st.write(f"**Temperature**: {weather_data['main']['temp']}°C")
        st.write(f"**Humidity**: {weather_data['main']['humidity']}%")
        st.write(f"**Wind Speed**: {weather_data['wind']['speed']} m/s")
        st.write(f"**Condition**: {weather_data['weather'][0]['description']}")
    else:
        st.error("No weather data received.")

    del st.session_state["pending_request"]
    del st.session_state["waiting_city"]

# chat input
user_input = st.chat_input("Ask me anything about wellness or travel tips...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    chat_history = [
        HumanMessage(content=msg["content"])
        for msg in st.session_state.messages
        if msg["role"] == "user"
    ]
    response = get_chatbot_response(user_input, chat_history)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()