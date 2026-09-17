from fastapi import FastAPI, HTTPException

from app.models.schemas import QueryRequest
from app.services.question_service import QuestionService


app = FastAPI(
    title="AI Support Ticket Assistant",
    description="AI-powered support ticket analytics API",
    version="1.0.0"
)


question_service = QuestionService()


@app.get("/")
def root():

    return {
        "message": "AI Support Ticket Assistant API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post("/ask")
def ask_question(request: QueryRequest):

    try:

        result = question_service.ask(
            request.question
        )

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )