import streamlit as st
import requests
import os
import time

API_URL = os.getenv(
    "API_URL", "https://sql-insight-agent.onrender.com"
).rstrip("/")

def check_backend_status():
    """Checks the backend's status endpoint, returns True if up, False if down/asleep."""
    try:
        response = requests.get(
            f"{API_URL}/health",
            timeout=5
        )
        if response.status_code == 200 and response.json().get("status") == "ok":
            return True
    except Exception:
        pass
    return False

def wake_up_backend_if_needed():
    """Wakes up the backend if it is asleep by polling the health endpoint."""
    if check_backend_status():
        return True
    
    max_retries = 20
    retry_delay = 3
    
    status_text = st.empty()
    for attempt in range(1, max_retries + 1):
        status_text.warning(
            f"⏳ The database assistant is waking up from its sleep cycle on Render's free tier...\n"
            f"This can take 30-60 seconds. Please keep this page open. (Attempt {attempt}/{max_retries})"
        )
        if check_backend_status():
            status_text.success("✅ Connected to the database assistant! Processing your query...")
            time.sleep(1)
            status_text.empty()
            return True
        time.sleep(retry_delay)
        
    status_text.error("❌ The server took too long to wake up. Please refresh the page and try again.")
    return False


st.set_page_config(
    page_title="SQL Insight Agent",
    page_icon="🔍",
    layout="centered"
)

st.title("🔍 SQL Insight Agent")
st.markdown("Ask your database anything in plain English — powered by Claude AI")
st.divider()

# Example questions as clickable buttons
st.markdown("**Try one of these:**")
col1, col2 = st.columns(2)

with col1:
    if st.button("👥 Top 5 customers by spending"):
        st.session_state.question = "Who are the top 5 customers by total spending?"
    if st.button("🎵 Most popular genre"):
        st.session_state.question = "Which genre has the most tracks?"

with col2:
    if st.button("🌍 Country with most customers"):
        st.session_state.question = "Which country has the most customers?"
    if st.button("💰 Revenue by country"):
        st.session_state.question = "What is the total revenue for each country?"

st.divider()

# Question input
question = st.text_input(
    "Or type your own question:",
    value=st.session_state.get("question", ""),
    placeholder="e.g. Who is the best selling artist?"
)

# Ask button
if st.button("Ask", type="primary", use_container_width=True):
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        if wake_up_backend_if_needed():
            with st.spinner("Claude is thinking..."):
                try:
                    response = requests.post(
                        f"{API_URL}/query",
                        json={"question": question},
                        timeout=120
                    )
                    
                    if response.status_code != 200:
                        st.error(f"Server returned an error (Status {response.status_code}): {response.text}")
                    else:
                        try:
                            data = response.json()
                        except Exception:
                            st.error("Received an invalid (non-JSON) response from the server. The server might be restarting or experiencing an internal error.")
                            st.code(response.text[:1000], language="html")
                            data = {}

                        if "answer" in data:
                            st.success("Answer:")
                            st.markdown(f"### {data['answer']}")
                            st.caption(f"⏱ Answered in {data['time_taken_seconds']} seconds")

                            # Save to history
                            if "history" not in st.session_state:
                                st.session_state.history = []
                            st.session_state.history.append({
                                "question": question,
                                "answer": data["answer"]
                            })
                        elif data:
                            st.error(f"Unexpected response format: {data}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to the API. Please check your internet connection or try again later.")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

# Query history
if "history" not in st.session_state:
    st.session_state.history = []

st.divider()
if st.session_state.history:
    st.markdown("**Recent questions:**")
    for item in reversed(st.session_state.history[-5:]):
        with st.expander(f"Q: {item['question']}"):
            st.write(item["answer"])
