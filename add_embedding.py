import os
import time
import requests
import psycopg2
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_URL = os.getenv("POSTGRES_URL")

def get_embedding(text, retries=3):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    body = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]}
    }
    
    for attempt in range(retries):
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.json()["embedding"]["values"]
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = (2 ** attempt) * 5  # 5s, 10s, 20s
                print(f"\nRate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    
    raise Exception(f"Failed after {retries} retries")

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

cur.execute("SELECT id, chunk_text FROM business_chunks WHERE embedding IS NULL")
rows = cur.fetchall()
print(f"Embedding {len(rows)} chunks...")

for i, (row_id, chunk_text) in enumerate(tqdm(rows)):
    if not chunk_text or not chunk_text.strip():
        continue

    try:
        embedding = get_embedding(chunk_text)
        
        cur.execute(
            "UPDATE business_chunks SET embedding = %s WHERE id = %s",
            (embedding, row_id)
        )
        
        if i % 100 == 0:
            conn.commit()
            
        time.sleep(0.5)  # slower: 2 requests per second instead of 10
    except Exception as e:
        print(f"\nError on chunk {row_id}: {e}")
        conn.commit()  # save progress before error
        continue

conn.commit()
cur.close()
conn.close()
print("Done!")