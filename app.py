import streamlit as st
import requests
import utils 

st.set_page_config(page_title="Smart Lecture Repository", layout="wide")

st.title("Smart lecture repository")
st.markdown("Your personal educational materials AI assistant")

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
    st.sidebar.info("Upload the first file to get started.")
    selected_lecture_id = None

st.sidebar.divider()

st.sidebar.subheader("Add new lecture")
new_title = st.sidebar.text_input("Lecture title (how it will be saved)")

uploaded_file = st.sidebar.file_uploader(
    "Choose a file", 
    type=['pdf', 'docx', 'pptx', 'txt']
)

if st.sidebar.button("Process and Save"):
    if new_title and uploaded_file:
        with st.sidebar:
            with st.spinner("Extracting text from file..."):
                extracted_text = utils.extract_text(uploaded_file)
                
                if extracted_text:
                    payload = {"title": new_title, "content": extracted_text}
                    res = requests.post(f"{BASE_URL}/ask", json=payload, timeout=180)
                    if res.status_code == 200:
                        st.success(f"Saved! Extracted {len(extracted_text)} characters.")
                        st.rerun()
                    else:
                        st.error("Failed to save to database.")
                else:
                    st.error("Could not extract text from this file.")
    else:
        st.sidebar.warning("Please provide a title and upload a file!")

# Chat ---
if selected_lecture_id:
    st.subheader(f"We are discussing: {lecture_titles[selected_lecture_id]}")
    
    user_question = st.chat_input("Ask a question about this lecture")
    
    if user_question:
        with st.chat_message("user"):
            st.write(user_question)
            
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
    st.write("👈 Start by uploading a lecture file in the left panel.")

# Chat History 
st.divider()
st.subheader("Chat history")
try:
    history_res = requests.get(f"{BASE_URL}/history/{selected_lecture_id}")
    if history_res.status_code == 200:
        history = history_res.json()
    else:
        history = []
except:
    history = []

if isinstance(history, list) and len(history) > 0:
    for item in reversed(history):
        if isinstance(item, dict) and 'question' in item:
            with st.expander(f"Question: {item['question'][:50]}..."):
                st.write(f"**Answer:** {item.get('answer', 'No answer found')}")
else:
    st.info("No questions yet. Be the first to ask!")