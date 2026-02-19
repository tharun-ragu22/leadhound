from my_langchain_agent import agent, BusinessRecordList

from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Sample FastAPI App", version="0.1.0")

class ModelInput(BaseModel):
    query_string: str

@app.post("/query", response_model=BusinessRecordList)
def make_query(model_input: ModelInput) -> BusinessRecordList:
    result = agent.invoke({
        "messages": [
            {"role": "system", "content": 
             """You are a business finder for businesses in Toronto. When the user gives you a query,
             you will provide upto the 10 most relevant businesses. You may do less, if the other businesses are not relevant to the query.
             For each business you return the business name, address, phone number, and website, and why you think it matches the query."""},
            {"role": "user", "content": model_input.query_string}
            ]
    })
    return result["structured_response"]