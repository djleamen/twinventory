# main.py
from fastapi import FastAPI

app = FastAPI()

# Run uvicorn main:app --reload to run

@app.get("/")
def read_root():
    print("FastAPI is running via uvicorn!")
    return {"status": "success", "message": "FastAPI running via uv!"}


