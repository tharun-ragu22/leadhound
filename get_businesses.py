"""
Toronto Business Scraper - Google Places API
Writes directly to Supabase as it scrapes
pip install requests python-dotenv tqdm psycopg2-binary
"""

import os, time, requests
from tqdm import tqdm
from itertools import product
from dotenv import load_dotenv
import psycopg2

load_dotenv()
API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
DB_URL = os.getenv("POSTGRES_URL")

# --- Config ---
LAT_MIN, LAT_MAX = 43.58, 43.85
LNG_MIN, LNG_MAX = -79.65, -79.12
LAT_STEPS, LNG_STEPS = 6, 6
SEARCH_RADIUS_METERS = 2500
TARGET_COUNT = 2000

PLACE_TYPES = [
    "restaurant", "cafe", "store", "gym", "beauty_salon",
    "florist", "pet_store", "clothing_store", "book_store", "bakery",
]

# --- Grid ---
def generate_grid():
    lats = [LAT_MIN + (LAT_MAX - LAT_MIN) * i / (LAT_STEPS - 1) for i in range(LAT_STEPS)]
    lngs = [LNG_MIN + (LNG_MAX - LNG_MIN) * i / (LNG_STEPS - 1) for i in range(LNG_STEPS)]
    return list(product(lats, lngs))

# --- API calls ---
def nearby_search(lat, lng, place_type, page_token=None):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {"location": f"{lat},{lng}", "radius": SEARCH_RADIUS_METERS,
              "type": place_type, "key": API_KEY}
    if page_token:
        params["pagetoken"] = page_token
    data = requests.get(url, params=params, timeout=10).json()
    if data.get("status") not in ("OK", "ZERO_RESULTS"):
        print(f"  [warn] {data.get('status')} for {place_type} at ({lat:.2f},{lng:.2f})")
        return [], None
    return data.get("results", []), data.get("next_page_token")

def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": ("place_id,name,formatted_address,formatted_phone_number,"
           "website,rating,user_ratings_total,types,opening_hours,business_status,reviews"),
        "key": API_KEY,
    }
    data = requests.get(url, params=params, timeout=10).json()
    return data.get("result") if data.get("status") == "OK" else None

# --- Database operations ---
def save_business_to_db(cur, raw):
    """Insert business into businesses table"""
    geo = raw.get("geometry", {}).get("location", {})
    business_name = raw.get("name")
    
    # Get details immediately for this business
    details = get_place_details(raw.get("place_id"))
    
    if details:
        website = details.get("website")
        phone = details.get("formatted_phone_number")
        formatted_address = details.get("formatted_address")
        opening_hours = details.get("opening_hours", {}).get("weekday_text", [])
        reviews = details.get("reviews", [])
    else:
        website = phone = formatted_address = None
        opening_hours = []
        reviews = []
    
    # Insert into businesses table
    cur.execute("""
        INSERT INTO businesses 
            (place_id, name, formatted_address, vicinity, phone, website,
             rating, user_ratings_total, types, opening_hours, lat, lng, business_status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (place_id) DO NOTHING
    """, (
        raw.get("place_id"),
        business_name,
        formatted_address,
        raw.get("vicinity"),
        phone,
        website,
        raw.get("rating"),
        raw.get("user_ratings_total"),
        raw.get("types", []),
        opening_hours,
        geo.get("lat"),
        geo.get("lng"),
        raw.get("business_status")
    ))
    
    print(f"  ✓ Saved: {business_name}")
    
    # Insert reviews as chunks
    for review in reviews:
        if review.get("text"):
            cur.execute("""
                INSERT INTO business_chunks (business_id, chunk_type, chunk_text)
                VALUES (%s, %s, %s)
            """, (raw.get("place_id"), "review", review["text"]))
    
    # Insert description chunk
    description = f"{business_name} located at {raw.get('vicinity')}"
    cur.execute("""
        INSERT INTO business_chunks (business_id, chunk_type, chunk_text)
        VALUES (%s, %s, %s)
    """, (raw.get("place_id"), "description", description))
    
    time.sleep(0.05)  # rate limiting for details API

# --- Helpers ---
def is_chain(name, seen_names, threshold=4):
    return seen_names.get(name.lower(), 0) >= threshold

def check_if_exists(cur, place_id):
    """Check if business already exists in DB"""
    cur.execute("SELECT 1 FROM businesses WHERE place_id = %s", (place_id,))
    return cur.fetchone() is not None

# --- Main scrape ---
def scrape_toronto():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    grid = generate_grid()
    seen_names = {}
    total_added = 0
    bar = tqdm(total=TARGET_COUNT, desc="Collecting", unit="biz")

    try:
        for place_type in PLACE_TYPES:
            if total_added >= TARGET_COUNT:
                break
            for (lat, lng) in grid:
                if total_added >= TARGET_COUNT:
                    break
                page_token, page = None, 0
                while page < 3:
                    results, page_token = nearby_search(lat, lng, place_type, page_token)
                    for raw in results:
                        pid, name = raw.get("place_id"), raw.get("name", "")
                        
                        # Skip if already in DB, is a chain, or we hit target
                        if check_if_exists(cur, pid) or is_chain(name, seen_names):
                            continue
                        if total_added >= TARGET_COUNT:
                            break
                        
                        # Save to DB immediately
                        save_business_to_db(cur, raw)
                        conn.commit()  # commit after each business
                        
                        seen_names[name.lower()] = seen_names.get(name.lower(), 0) + 1
                        total_added += 1
                        bar.update(1)
                    
                    if not page_token or total_added >= TARGET_COUNT:
                        break
                    page += 1
                    time.sleep(2)
                time.sleep(0.1)
    
    finally:
        bar.close()
        cur.close()
        conn.close()
    
    return total_added

# --- Entry point ---
if __name__ == "__main__":
    if not API_KEY:
        raise ValueError("Set GOOGLE_PLACES_API_KEY in your .env")
    if not DB_URL:
        raise ValueError("Set POSTGRES_URL in your .env")

    total = scrape_toronto()
    print(f"\nAdded {total} businesses to database")  