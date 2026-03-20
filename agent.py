from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os

load_dotenv()

# 1. Connect to the Chinook database
db = SQLDatabase.from_uri("sqlite:///chinook.db")

# 2. Load Claude as the LLM
llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0
)

# 3. Create the SQL agent
agent = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True,
    handle_parsing_errors=True
)

# 4. Ask it a question
# 4. Ask multiple questions
questions = [
    "Who are the top 5 customers by total spending? Show their name and total amount spent.",
    "Which genre has the most tracks?",
    "Which country has the most customers?"
]

for question in questions:
    print("\n" + "="*50)
    print(f"QUESTION: {question}")
    print("="*50 + "\n")

    response = agent.invoke({"input": question})

    print("\n" + "="*50)
    print("FINAL ANSWER:")
    print(response["output"])
    print("="*50)