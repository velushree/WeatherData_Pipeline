import os
import json
import requests
from kafka import KafkaConsumer, KafkaProducer
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('WEATHER_API_KEY')

def fetch_weather(city):
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'  
    }
    
    base_url = f"https://api.openweathermap.org/data/2.5/weather"
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch weather for {city}: {response.status_code} - {response.text}")
        return None

consumer = KafkaConsumer(
    'weather_requests',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='weather_responder_group' 
)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print(" Weather responder is running and listening for requests...")

for msg in consumer:
    req = msg.value
    city = req["city"]
    request_id = req["request_id"]

    print(f"Received request: {city} (ID: {request_id})")

    weather_data = fetch_weather(city)
    if weather_data:
        response = {
            "request_id": request_id,
            "weather": weather_data
        }
        print("Sending response to 'current_weather_data'")
        print(json.dumps(response, indent=2))
        producer.send("current_weather_data", response)
        producer.flush()
    else:
        print("No data fetched. Skipping...")