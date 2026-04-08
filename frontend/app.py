import streamlit as st
import requests
import utils
import os

st.set_page_config(page_title="Smart Lecture Repository", layout="wide")
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

if "user_id" not in st.session_state:
    st.session_state.user_id = ""

if not st.session_state.user_id:
    st.title("👨‍🎓 Welcome to Smart Lecture Repository")
    username = st.text_input("Enter your nickname to start:")
    if st.button("Login"):
        if username:
            st.session_state.user_id = username
            st.rerun()
        else:
            st.warning("Please enter a name")
    st.stop()

user_id = st.session_state.user_id
st.title(f"Smart lecture repository - Hi, {user_id}!")

st.sidebar.header(f"User: {user_id}")
if st.sidebar.button("Log out"):
    st.session_state.user_id = ""
    st.rerun()

try:
    response = requests.get(f"{BASE_URL}/lectures/{user_id}")
    if response.status_code == 200:
        lectures = response.json()
    else:
        lectures = []
except Exception as e:
    st.sidebar.error(f"Backend error: {e}")
    lectures = []

st.sidebar.subheader("Your Lectures")
lecture_titles = {l['id']: l['title'] for l in lectures}

if lecture_titles:
    selected_lecture_id = st.sidebar.selectbox(
        "Choose a lecture to study:",
        options=list(lecture_titles.keys()),
        format_func=lambda x: lecture_titles[x],
        key="lecture_selector"
    )
else:
    st.sidebar.info("No lectures yet. Upload one below! 👇")
    selected_lecture_id = None

st.sidebar.divider()
st.sidebar.subheader("Add new lecture")
new_title = st.sidebar.text_input("Lecture title")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=['pdf', 'docx', 'txt'])

if st.sidebar.button("Process and Save"):
    if new_title and uploaded_file:
        with st.sidebar:
            with st.spinner("Extracting..."):
                extracted_text = utils.extract_text(uploaded_file)
                if extracted_text:
                    payload = {"user_id": user_id, "title": new_title, "content": extracted_text}
                    res = requests.post(f"{BASE_URL}/upload", json=payload)
                    if res.status_code == 200:
                        st.success("Saved!")
                        st.rerun()
                    else:
                        st.error("Failed to save.")

st.divider()

if selected_lecture_id:
    st.subheader(f"💬 Chatting about: {lecture_titles[selected_lecture_id]}")
    
    if "messages" not in st.session_state or st.session_state.get("last_lecture_id") != selected_lecture_id:
        st.session_state.messages = []
        st.session_state.last_lecture_id = selected_lecture_id

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_question := st.chat_input("Ask a question about this lecture..."):
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                payload = {
                    "user_id": user_id, 
                    "lecture_id": selected_lecture_id, 
                    "question": user_question
                }
                res = requests.post(f"{BASE_URL}/ask", json=payload)
                if res.status_code == 200:
                    answer = res.json()["answer"]
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"API Error: {res.text}")
else:
    st.info("👈 Please upload your first lecture in the sidebar to start chatting with AI.")