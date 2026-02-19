from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from test_search import search_businesses
import psycopg2
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

DB_URL = os.getenv("POSTGRES_URL")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)
class BusinessRecord(BaseModel):
    business_name: str = Field(description="The name of the business")
    address: str | None = Field(description="The address of the business")
    phone_number: str | None = Field(description="The phone number of the business")
    website: str | None = Field(description="The website of the business")
    reason: str = Field(description="The reason why you think this business matches the user query. Should be a short sentence, but should show your own thinking")

class BusinessRecordList(BaseModel):
    res: List[BusinessRecord]

@tool
def vector_search(query: str) -> str:
    """Search for businesses by semantic meaning using a natural language query."""
    results = search_businesses(query, limit=20)
    return str(results)

@tool
def filter_by_hours(day: str) -> str:
    """Filter businesses by opening hours. Input should be a day of the week e.g. Monday."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("""
        SELECT name, opening_hours 
        FROM businesses 
        WHERE opening_hours::text LIKE %s
    """, (f'%{day}%',))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return str(results)

@tool
def get_business_details(place_id: str) -> str:
    """Get full details for a specific business by its place_id."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("""
        SELECT name, formatted_address, phone, website, rating, opening_hours
        FROM businesses WHERE place_id = %s
    """, (place_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return str(result)

tools = [vector_search, filter_by_hours, get_business_details]

agent = create_agent(llm, tools, response_format=BusinessRecordList)

if __name__ == "__main__":
    query = input("What are you looking for? ")
    result = agent.invoke({
        "messages": [
            {"role": "system", "content": 
             """You are a business finder for businesses in Toronto. When the user gives you a query,
             you will provide upto the 10 most relevant businesses. You may do less, if the other businesses are not relevant to the query.
             For each business you return the business name, address, phone number, and website, and why you think it matches the query."""},
            {"role": "user", "content": query}
            ]
    })
    print("\n" + "="*50)
    print("FINAL ANSWER:")
    result : BusinessRecordList = result["structured_response"]
    for r in result.res:
        print(f'Name: {r.business_name}')
        print(f'Address: {r.address}')
        print(f'Phone Number: {r.phone_number}')
        print(f'Website: {r.website}')
        print(f'Reason for selection: {r.reason}')
        print("-"*20)
