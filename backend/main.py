from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import database
import requests
import json

load_dotenv()
app = FastAPI()
database.init_db()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")
OPENROUTER_URL = os.getenv("OPENROUTER_BASE_URL")
CONTENT_LIMIT = int(os.getenv("CONTENT_LIMIT", 10000))

class LectureCreate(BaseModel):
    user_id: str
    title: str
    content: str

class QuestionRequest(BaseModel):
    user_id: str
    lecture_id: int
    question: str

@app.post("/upload")
def upload_lecture(lecture: LectureCreate):
    try:
        database.add_lecture(lecture.user_id, lecture.title, lecture.content)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lectures/{user_id}")
def get_user_lectures(user_id: str):
    lectures = database.get_lectures(user_id)
    return [{"id": l[0], "title": l[1]} for l in lectures]

@app.post("/ask")
def ask_question(req: QuestionRequest):
    lecture_content = database.get_lecture_content(req.user_id, req.lecture_id)
    if not lecture_content:
        raise HTTPException(status_code=404, detail="Lecture not found")

    truncated_content = lecture_content[:CONTENT_LIMIT]
    messages = [
        {"role": "system", "content": "You are a friendly professional student assistant at Innopolis University. If the user asks you a question, answer it based ONLY on the text of the lecture provided, if the user just starts talking to you, then communicate with him in a friendly way.. If the answer is not in the text, say: 'Information not found in this lecture.' Keep answers concise and in the same language as the question."},
        {"role": "user", "content": f"LECTURE TEXT:\n{truncated_content}\n\nQUESTION:\n{req.question}"}
    ]

    try:
        response = requests.post(
            url=OPENROUTER_URL,
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            data=json.dumps({"model": OPENROUTER_MODEL, "messages": messages}),
            timeout=120
        )
        answer = response.json()['choices'][0]['message']['content']
        
        database.save_interaction(req.user_id, req.lecture_id, req.question, answer)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}

@app.get("/history/{user_id}/{lecture_id}")
def get_lecture_history(user_id: str, lecture_id: int):
    history = database.get_history(user_id, lecture_id)
    return [{"question": h[0], "answer": h[1]} for h in history]