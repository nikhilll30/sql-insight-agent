from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# Confirm the API key is loading correctly
api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API key loaded: {'YES' if api_key else 'NO - check your .env file'}")

# Connect to the Chinook database
engine = create_engine("sqlite:///chinook.db")

# 3 test queries to explore the data
queries = [
    "SELECT name FROM sqlite_master WHERE type='table';",
    "SELECT FirstName, LastName, Country FROM Customer LIMIT 5;",
    "SELECT Name, Composer, Milliseconds FROM Track LIMIT 5;"
]

with engine.connect() as conn:
    for query in queries:
        print(f"\n--- Query: {query[:50]}...")
        result = conn.execute(text(query))
        for row in result:
            print(row)