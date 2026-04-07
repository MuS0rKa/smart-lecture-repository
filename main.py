from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import database
import requests
import json
import time

app = FastAPI()

database.init_db()

OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "qwen/qwen-2.5-72b-instruct"

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
    lecture_content = database.get_lecture_content(req.lecture_id)

    if not lecture_content:
        raise HTTPException(status_code=404, detail="Lecture not found")

    print(f"DEBUG: Отправка запроса в OpenRouter ({len(lecture_content)} симв.)")

    truncated_content = lecture_content[:50000] if len(lecture_content) > 50000 else lecture_content

    messages = [
        {
            "role": "system",
            "content": "You are a professional student assistant at Innopolis University. Answer the question based ONLY on the provided lecture text. If the answer is not in the text, say: 'Information not found in this lecture.' Keep answers concise and in the same language as the question."
        },
        {
            "role": "user",
            "content": f"LECTURE TEXT:\n{truncated_content}\n\nQUESTION:\n{req.question}"
        }
    ]

    try:
        max_retries = 3
        retry_count = 0
        response = None

        while retry_count <= max_retries:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": OPENROUTER_MODEL,
                    "messages": messages,
                    "max_tokens": 2000,
                    "temperature": 0.3,
                }),
                timeout=120
            )

            if response.status_code != 429:
                break

            retry_after = int(response.headers.get("Retry-After", 15))
            retry_count += 1
            print(f"Rate limited (429). Waiting {retry_after}s... (retry {retry_count}/{max_retries})")
            time.sleep(retry_after)

        response_data = response.json() if response else {}

        if response.status_code == 200 and "choices" in response_data:
            answer = response_data['choices'][0]['message']['content']
        elif response.status_code == 503:
            answer = "Model is loading. Please wait 30 seconds and try again."
        elif response.status_code == 401:
            answer = "Error: Invalid OpenRouter API key. Get a free key at: https://openrouter.ai/settings/keys"
        elif response.status_code == 429:
            answer = "Error: Rate limit exceeded. Please wait a minute and try again."
        else:
            error_msg = response_data.get('error', {})
            if isinstance(error_msg, dict):
                error_msg = error_msg.get('message', str(error_msg))
            answer = f"API Error ({response.status_code}): {error_msg}"
            print(f"DEBUG: Full response: {response_data}")

    except requests.exceptions.Timeout:
        answer = "Request timed out. Try again later."
    except Exception as e:
        answer = f"Request Error: {str(e)}"

    database.save_interaction(req.lecture_id, req.question, answer)

    return {"answer": answer}

@app.get("/history/{lecture_id}")
def get_lecture_history(lecture_id: int):
    history = database.get_history(lecture_id)
    return [{"question": h[0], "answer": h[1]} for h in history]