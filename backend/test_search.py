import os
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_URL = os.getenv("POSTGRES_URL")

def get_query_embedding(text):
    """Embed a search query - note taskType is different from document embedding"""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    body = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]},
        "taskType": "RETRIEVAL_QUERY"  # different from RETRIEVAL_DOCUMENT
    }
    resp = requests.post(url, json=body, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()["embedding"]["values"]

def search_businesses(query, limit=10):
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    query_vector = get_query_embedding(query)
    
    # Group by business and get the best matching chunk per business
    cur.execute("""
        WITH ranked_chunks AS (
            SELECT 
                b.place_id,
                b.name,
                b.formatted_address,
                b.rating,
                b.website,
                c.chunk_type,
                c.chunk_text,
                c.embedding <=> %s::vector AS distance,
                ROW_NUMBER() OVER (PARTITION BY b.place_id ORDER BY c.embedding <=> %s::vector) AS rank
            FROM business_chunks c
            JOIN businesses b ON b.place_id = c.business_id
            WHERE c.embedding IS NOT NULL
        )
        SELECT 
            place_id,
            name,
            formatted_address,
            rating,
            website,
            chunk_type,
            chunk_text,
            distance
        FROM ranked_chunks
        WHERE rank = 1  -- only keep the best matching chunk per business
        ORDER BY distance
        LIMIT %s
    """, (query_vector, query_vector, limit))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return results

# Test it
if __name__ == "__main__":
    query = input("Search: ")
    results = search_businesses(query)
    
    print(f"\nTop {len(results)} results:\n")
    for i, (_, name, address, rating, website, chunk_type, chunk_text, distance) in enumerate(results, 1):
        print(f"{i}. {name}")
        print(f"   {address}")
        print(f"   Rating: {rating} | {website}")
        print(f"   Matched on: {chunk_type}")
        print(f"   Text: {chunk_text[:150]}...")
        print(f"   Distance: {distance:.3f}\n")