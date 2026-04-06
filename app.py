import streamlit as st
import requests

st.set_page_config(page_title="Smart Lecture Repository", layout="wide")

st.title("Smart lecture repository")
st.markdown("Your personal educational materials AI assistent")

BASE_URL = "http://127.0.0.1:8000"

st.sidebar.header("Management of educational materials")

try:
    response = requests.get(f"{BASE_URL}/lectures")
    lectures = response.json()
except:
    lectures = []
    st.sidebar.error("The backend is not running!")

lecture_titles = {l['id']: l['title'] for l in lectures}

if lecture_titles:
    selected_lecture_id = st.sidebar.selectbox(
        "Choose a lecture to study:",
        options=list(lecture_titles.keys()),
        format_func=lambda x: lecture_titles[x]
    )
else:
    st.sidebar.info("Download the first lecture to get started.")
    selected_lecture_id = None

st.sidebar.divider()
st.sidebar.subheader("Add new lecture")
new_title = st.sidebar.text_input("Lecture title")
new_content = st.sidebar.text_area("Lecture text", height=200)

if st.sidebar.button("Save to the database"):
    if new_title and new_content:
        payload = {"title": new_title, "content": new_content}
        res = requests.post(f"{BASE_URL}/upload", json=payload)
        if res.status_code == 200:
            st.sidebar.success("The lecture has been saved!")
            st.rerun()
    else:
        st.sidebar.warning("Fill in all the fields!")

if selected_lecture_id:
    st.subheader(f"We are discussing: {lecture_titles[selected_lecture_id]}")
    
    # Поле ввода вопроса
    user_question = st.chat_input("Ask a question about this lecture")
    
    if user_question:
        # Отображаем вопрос пользователя
        with st.chat_message("user"):
            st.write(user_question)
            
        # Отправляем вопрос на бэкенд
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                payload = {"lecture_id": selected_lecture_id, "question": user_question}
                res = requests.post(f"{BASE_URL}/ask", json=payload)
                if res.status_code == 200:
                    answer = res.json()["answer"]
                    st.write(answer)
                else:
                    st.error("Error when receiving the response.")
else:
    st.write("Start by uploading the lecture text in the left panel.")
