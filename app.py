import json
import requests
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# Load .env file
load_dotenv()

# Get API key from .env
API_KEY = os.getenv("API_KEY")

# Fallback if .env fails (optional, replace below with your key)
if not API_KEY:
    API_KEY = "YOUR_REAL_OPENWEATHER_KEY_HERE"

print("API KEY:", API_KEY)
if not API_KEY:
    raise ValueError("API_KEY not found! Add it to .env or in the fallback in app.py")

# Load orders
with open("orders.json", "r") as f:
    orders = json.load(f)

def fetch_weather(order):
    city = order["city"]
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"

    try:
        res = requests.get(url)
        data = res.json()

        # If API returns error
        if res.status_code != 200:
            print(f"Error for city: {city} → {data}")
            return order

        weather = data["weather"][0]["main"]

        # Mark delayed orders
        if weather in ["Rain", "Snow", "Extreme"]:
            order["status"] = "Delayed"
            order["message"] = (
                f"Hi {order['customer']}, your order to {city} is delayed "
                f"due to {weather.lower()}. We appreciate your patience!"
            )

        return order

    except Exception as e:
        print(f"Exception for city {city}: {e}")
        return order

# Process orders concurrently
with ThreadPoolExecutor() as executor:
    updated_orders = list(executor.map(fetch_weather, orders))

# Save updated orders
with open("updated_orders.json", "w") as f:
    json.dump(updated_orders, f, indent=2)

print("Done ✅")