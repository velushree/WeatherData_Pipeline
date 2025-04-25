import json
import uuid
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_weather_request(city: str) -> str:
    request_id = str(uuid.uuid4())
    payload = {
        "city": city,
        "request_id": request_id
    }

    producer.send('weather_requests', payload)
    producer.flush()
    print(f"Request sent for {city}, ID: {request_id}")
    return request_id