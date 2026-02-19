from my_langchain_agent import agent, BusinessRecordList

from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Sample FastAPI App", version="0.1.0")


class Item(BaseModel):
    id: int
    name: str
    price: float


items_db: List[Item] = [
    Item(id=1, name="Keyboard", price=49.99),
    Item(id=2, name="Mouse", price=19.99),
]


@app.get("/")
def root() -> dict:
    return {"message": "FastAPI sample app is running"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/items", response_model=List[Item])
def list_items() -> List[Item]:
    return items_db


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.post("/items", response_model=Item, status_code=201)
def create_item(item: Item) -> Item:
    if any(existing.id == item.id for existing in items_db):
        raise HTTPException(status_code=400, detail="Item with this ID already exists")
    items_db.append(item)
    return item

@app.post("/query", response_model=BusinessRecordList)
def make_query(query: str) -> BusinessRecordList:
    result = agent.invoke({
        "messages": [
            {"role": "system", "content": 
             """You are a business finder for businesses in Toronto. When the user gives you a query,
             you will provide upto the 10 most relevant businesses. You may do less, if the other businesses are not relevant to the query.
             For each business you return the business name, address, phone number, and website, and why you think it matches the query."""},
            {"role": "user", "content": query}
            ]
    })
    return result["structured_response"]