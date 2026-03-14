from fastapi import APIRouter
from pydantic import BaseModel
from app.analysis.analyzer import analyze_code

router = APIRouter()

class CodeInput(BaseModel):
    code: str
    filename: str = "code.py"

@router.post("/analyze")
async def analyze(input: CodeInput):
    results = analyze_code(input.code, input.filename)
    return results
