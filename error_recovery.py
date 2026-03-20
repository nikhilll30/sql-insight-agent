from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os

load_dotenv()

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

# These are intentionally tricky questions
# Watch how the agent handles each one
tricky_questions = [
    # Ambiguous term - 'revenue' doesn't exist as a column
    "What is the total revenue for each country?",
    
    # Asks about a column that doesn't exist
    "Show me the customer ratings sorted by highest first.",
    
    # Multi-step reasoning required
    "Who is the employee that supports the most valuable customers?"
]

for question in tricky_questions:
    print("\n" + "="*60)
    print(f"QUESTION: {question}")
    print("="*60 + "\n")

    try:
        response = agent.invoke({"input": question})
        print("\n" + "-"*60)
        print("FINAL ANSWER:")
        print(response["output"])
        print("-"*60)
    except Exception as e:
        print(f"Agent failed completely: {e}")