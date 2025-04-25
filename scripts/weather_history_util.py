import os
from geopy.geocoders import Nominatim
from meteostat import Point, Daily
from datetime import datetime, timedelta

def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="weather_bot")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f"Could not find coordinates for city: {city_name}")

def fetch_weather_history(city_name, days=30):
    end = datetime.now()
    start = end - timedelta(days=days)

    lat, lon = get_coordinates(city_name)
    location = Point(lat, lon)
    data = Daily(location, start, end)
    df = data.fetch()

    weather_strs = []

    for index, day in df.iterrows():
        weather_str = (
            f"The temperature of {city_name} on {index.strftime('%Y-%m-%d')} is {day['tavg']}°C. "
            f"Min Temp: {day['tmin']}°C, Max Temp: {day['tmax']}°C. "
            f"Precipitation: {day['prcp']} mm, Wind Speed: {day['wspd']} m/s, "
            f"Pressure: {day['pres']} hPa, Sunshine: {day['tsun']} hours, Snowfall: {day['snow']} mm."
        )
        weather_strs.append(weather_str)
    output_dir = "/opt/airflow/data"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{city_name.replace(' ', '_').lower()}.txt"
    file_path = os.path.join(output_dir, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        for line in weather_strs:
            f.write(line + "\n")

    print(f"Weather data for {city_name} saved to data/{filename}")
    return weather_strs