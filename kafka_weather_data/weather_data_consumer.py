import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'current_weather_data',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Listening for weather data responses...")

for msg in consumer:
    weather_response = msg.value
    print(f"Received weather data: {json.dumps(weather_response, indent=2)}")
