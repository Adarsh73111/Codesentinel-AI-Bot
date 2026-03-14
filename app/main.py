from fastapi import FastAPI
from app.webhook.router import router as webhook_router
from app.analysis.router import router as analysis_router
from app.agents.debate_resolver import run_debate
from app.analysis.analyzer import analyze_code
from app.memory.memory_manager import (
    save_suggestion,
    get_developer_profile,
    update_developer_profile,
    is_duplicate_suggestion
)
from app.memory.database import init_db
from pydantic import BaseModel
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="CodeSentinel AI",
    description="Real-Time AI Code Review Bot",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(webhook_router, prefix="/webhook")
app.include_router(analysis_router, prefix="/analysis")

class ReviewRequest(BaseModel):
    code: str
    filename: str = "code.py"
    developer: str = "anonymous"
    repo: str = "unknown"

@app.post("/review")
async def full_review(request: ReviewRequest):
    profile = get_developer_profile(request.developer)
    analysis = analyze_code(request.code, request.filename)
    debate_result = await run_debate(request.code, analysis)

    filtered_issues = []
    for issue in debate_result["final_review"].get("priority_issues", []):
        suggestion_text = issue.get("issue", "")
        if not is_duplicate_suggestion(request.developer, suggestion_text):
            save_suggestion(request.developer, request.repo, suggestion_text)
            filtered_issues.append(issue)
        else:
            issue["skipped"] = "Already suggested to this developer"
            filtered_issues.append(issue)

    debate_result["final_review"]["priority_issues"] = filtered_issues
    update_developer_profile(request.developer)

    return {
        "filename": request.filename,
        "developer": request.developer,
        "developer_profile": profile,
        "static_analysis": analysis,
        "ai_review": debate_result
    }

@app.get("/")
async def root():
    return {
        "status": "CodeSentinel AI is running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
