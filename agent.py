import os
import json
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Load environment variables for API keys
load_dotenv()

# Setup API keys
google_api_key = os.getenv("GOOGLE_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")

# Initialize Gemini models
# text-embedding-004 is highly efficient for B2B semantic matching
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
# Using gemini-2.5-flash-preview-09-2025 for its large context window
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-09-2025", temperature=0)

@tool
def search_and_verify_leads(query: str, location: str):
    """
    Search for businesses using Serper and verify their suitability.
    This tool handles the multi-step retrieval and RAG process in a single atomic step.
    It returns a JSON string containing verified leads and agent evaluations.
    """
    import http.client
    
    # 1. Discovery Phase (Places API)
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({"q": query, "location": location, "num": 10})
    headers = {
        'X-API-KEY': serper_api_key, 
        'Content-Type': 'application/json'
    }
    
    conn.request("POST", "/places", payload, headers)
    discovery_data = json.loads(conn.getresponse().read().decode("utf-8"))
    places = discovery_data.get("places", [])

    results = []
    
    # 2. RAG & Embedding Analysis for each candidate
    for biz in places:
        name = biz.get("title")
        cid = biz.get("cid")
        
        if not cid:
            continue

        # Fetch Reviews for local evidence
        conn.request("POST", "/reviews", json.dumps({"cid": cid}), headers)
        review_data = json.loads(conn.getresponse().read().decode("utf-8"))
        reviews = [r.get("text", "") for r in review_data.get("reviews", []) if r.get("text")]

        if not reviews:
            results.append({"name": name, "status": "No evidence found", "score": 0})
            continue

        # --- RAG Implementation ---
        # Convert reviews into Document objects for FAISS
        docs = [Document(page_content=r) for r in reviews]
        vectorstore = FAISS.from_documents(docs, embeddings)
        
        # Semantic Search for dog-friendliness indicators
        search_results = vectorstore.similarity_search(
            "Is this place dog friendly? Do they have a patio or water bowls?", 
            k=5
        )
        context = "\n".join([d.page_content for d in search_results])

        # 3. Gemini Evaluation (Agentic Eval)
        eval_prompt = f"""
        You are a B2B lead researcher. Analyze the following reviews for '{name}' to determine if they are dog-friendly.
        
        Reviews for context:
        {context}
        
        Provide a dog-friendliness score from 0 to 10 and a brief explanation of your reasoning.
        """
        response = llm.invoke(eval_prompt)
        
        results.append({
            "name": name,
            "agent_eval": response.content,
            "cid": cid,
            "address": biz.get("address")
        })

    # The result MUST be returned as a string so the AgentExecutor can parse it
    return json.dumps(results, indent=2)

# --- LangChain Agent Configuration ---
tools = [search_and_verify_leads]

prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        "You are an expert B2B Lead Researcher using Google Gemini. "
        "Your task is to find and verify businesses based on specific criteria. "
        "Use the tools provided to gather evidence and assign confidence scores."
    ),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create the agent and executor
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    # Test execution
    user_input = "Find 3 dog-friendly coffee shops in Toronto and verify their pet policies."
    agent_executor.invoke({"input": user_input})