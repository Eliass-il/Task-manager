from fastapi import FastAPI
from src.api.auth import router as auth_router
from src.api.tasks import router as tasks_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/")
def check():
    return {"Works": "Fine"}

