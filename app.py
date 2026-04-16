import streamlit as st
import requests

st.set_page_config(page_title="Research Assistant", page_icon="🤖")
st.title("🤖 RESEARCH ASSISTANT")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            r = requests.get(f"https://api.duckduckgo.com/?q={prompt}&format=json&no_html=1")
            if r.status_code == 200:
                data = r.json()
                answer = data.get('Answer') or data.get('AbstractText') or "I don't know"
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.markdown(f"Error: {e}")
    
    st.rerun()