import streamlit as st
import requests
import utils

st.set_page_config(page_title="Smart Lecture Repository", layout="wide")

st.title("Smart lecture repository")
st.markdown("Your personal educational materials AI assistant")

BASE_URL = "http://127.0.0.1:8000"

st.sidebar.header("Navigation & History")

try:
    response = requests.get(f"{BASE_URL}/lectures")
    lectures = response.json()
except:
    lectures = []
    st.sidebar.error("The backend is not running!")

lecture_titles = {l['id']: l['title'] for l in lectures}

st.sidebar.subheader("Recent Questions")
selected_lecture_id = None  

if lecture_titles:
    selected_lecture_id = st.sidebar.selectbox(
        "Choose a lecture to study:",
        options=list(lecture_titles.keys()),
        format_func=lambda x: lecture_titles[x],
        key="lecture_selector"
    )
    
    try:
        history_res = requests.get(f"{BASE_URL}/history/{selected_lecture_id}")
        if history_res.status_code == 200:
            history_data = history_res.json()
            for item in reversed(history_data[-5:]): # Последние 5 вопросов
                st.sidebar.caption(f"Q: {item['question'][:40]}...")
        else:
            st.sidebar.info("No history for this lecture.")
    except:
        pass
else:
    st.sidebar.info("Upload a lecture to see history.")

    st.sidebar.divider()

st.sidebar.subheader("Add new lecture")
new_title = st.sidebar.text_input("Lecture title")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=['pdf', 'docx', 'pptx', 'txt'])

if st.sidebar.button("Process and Save"):
    if new_title and uploaded_file:
        with st.sidebar:
            with st.spinner("Extracting..."):
                extracted_text = utils.extract_text(uploaded_file)
                if extracted_text:
                    payload = {"title": new_title, "content": extracted_text}
                    res = requests.post(f"{BASE_URL}/upload", json=payload)
                    if res.status_code == 200:
                        st.success("Saved!")
                        st.rerun()
                    else:
                        st.error("Failed to save.")


if "messages" not in st.session_state:
    st.session_state.messages = []


if "last_lecture_id" not in st.session_state or st.session_state.last_lecture_id != selected_lecture_id:
    st.session_state.messages = []
    st.session_state.last_lecture_id = selected_lecture_id

if selected_lecture_id:
    st.subheader(f"Chatting about: {lecture_titles[selected_lecture_id]}")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_question := st.chat_input("Ask a question about this lecture..."):
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                payload = {"lecture_id": selected_lecture_id, "question": user_question}
                res = requests.post(f"{BASE_URL}/ask", json=payload)
                if res.status_code == 200:
                    answer = res.json()["answer"]
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error("Error from API.")
else:
    st.info("👈 Please select or upload a lecture in the sidebar to start.")