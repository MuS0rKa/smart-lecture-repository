from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import database

app = FastAPI()

database.init_db()

class LectureCreate(BaseModel):
    title: str
    content: str

class QuestionRequest(BaseModel):
    lecture_id: int
    question: str

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Lecture Repository"}

@app.post("/upload")
def upload_lecture(lecture: LectureCreate):
    try:
        database.add_lecture(lecture.title, lecture.content)
        return {"status": "success", "message": f"Lecture '{lecture.title}' uploaded."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/lectures")
def get_all_lectures():
    lectures = database.get_lectures()

    return [{"id": l[0], "title": l[1]} for l in lectures]

@app.post("/ask")
def ask_question(req: QuestionRequest):
    mock_answer = f"Это имитация ответа ИИ на вопрос: '{req.question}' по лекции ID {req.lecture_id}"
    
    database.save_interaction(req.lecture_id, req.question, mock_answer)
    
    return {"answer": mock_answer}