import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

username = os.getenv('MONGO_USER')
password = os.getenv('MONGO_PASSWORD')
client  = MongoClient(f'mongodb+srv://{username}:{password}@sandbox.czi2aa0.mongodb.net/?retryWrites=true&w=majority&appName=Sandbox')
db = client["weather_db"]
collection = db["weather_data"]

def store_in_db(doc):
    if doc:
        collection.insert_one(doc)
        print(f"stored weather data for {doc} successfully")