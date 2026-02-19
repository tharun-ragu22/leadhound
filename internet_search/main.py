import http.client
import json
from dotenv import load_dotenv
import os

class PlaceRecord:
    name: str
    address: str
    latitude: float
    longitude: float

load_dotenv()
search_api_key = os.getenv('SERPER_API_KEY')

conn = http.client.HTTPSConnection("google.serper.dev")
payload = json.dumps({
  "q": "dog-friendly cafes",
  "location": "Toronto, Ontario, Canada",
  "gl": "ca",
  "page": 1
})
headers = {
  'X-API-KEY': search_api_key,
  'Content-Type': 'application/json'
}
conn.request("POST", "/places", payload, headers)
res = conn.getresponse()
data = res.read()
results = json.loads(data.decode("utf-8"))

places = results.get("places", [])

print(f"Found {len(places)} places.\n")

# 3. Iterate through the places to extract lead data
for business in places:
    name = business.get("title")
    address = business.get("address")
    rating = business.get("rating")
    
    print(f"Business: {name}")
    print(f"Address: {address}")
    print(f"Rating: {rating}")
    print("-" * 20)