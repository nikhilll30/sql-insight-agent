from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="SQL Insight Agent",
    description="Ask your database anything in plain English",
    version="1.0.0",
    root_path_in_servers=False
)

# Initialize the agent once when the server starts
# (not on every request — that would be slow)
print("Loading database and agent...")

db = SQLDatabase.from_uri("sqlite:///chinook.db")

llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0
)

agent = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True,
    handle_parsing_errors=True
)

print("Agent ready!")

# Define what a request looks like
class QueryRequest(BaseModel):
    question: str

# Define what a response looks like
class QueryResponse(BaseModel):
    question: str
    answer: str
    time_taken_seconds: float

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "SQL Insight Agent is running"}

# Main query endpoint
@app.post("/query", response_model=QueryResponse)
def query_database(request: QueryRequest):
    
    # Validate the question isn't empty
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    start_time = time.time()
    
    try:
        response = agent.invoke({"input": request.question})
        answer = response["output"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
    
    time_taken = round(time.time() - start_time, 2)
    
    return QueryResponse(
        question=request.question,
        answer=answer,
        time_taken_seconds=time_taken
    )

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to SQL Insight Agent",
        "docs": "Visit /docs to try the API interactively",
        "endpoints": {
            "health": "GET /health",
            "query": "POST /query"
        }
    }