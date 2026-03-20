import streamlit as st
import requests

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
        with st.spinner("Claude is thinking..."):
            try:
                response = requests.post(
                    "https://sql-insight-agent.onrender.com/query",
                    json={"question": question},
                    timeout=120
                )
                data = response.json()

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
                else:
                    st.error(f"Unexpected response: {data}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the API.")
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