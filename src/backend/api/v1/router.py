from fastapi import APIRouter

from src.backend.api.v1.endpoints import sidebar, topics, chapters, conversations
from src.backend.api.v1.endpoints import chat_curriculum, chat_teacher, chat_quiz
from src.backend.api.v1.endpoints import document, quiz, sections

api_router = APIRouter()

api_router.include_router(sidebar.router, prefix="/sidebar", tags=["sidebar"])
api_router.include_router(topics.router, prefix="/topics", tags=["topics"])
api_router.include_router(chapters.router, prefix="/chapters", tags=["chapters"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])

# JIT Document & Reading Progress
api_router.include_router(document.router, prefix="/chapters", tags=["document"])
api_router.include_router(sections.router, prefix="/sections", tags=["sections"])

# Secure Quiz
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])

# Agent Streaming Endpoints
api_router.include_router(chat_curriculum.router, prefix="/chat", tags=["curriculum"])
api_router.include_router(chat_teacher.router, prefix="/chat", tags=["teacher"])
api_router.include_router(chat_quiz.router, prefix="/chat", tags=["quiz-chat"])
