import hmac
import hashlib
import json
import asyncio
from fastapi import APIRouter, Request, HTTPException, Header, BackgroundTasks
from typing import Optional
import os
from dotenv import load_dotenv
from app.analysis.analyzer import analyze_code
from app.agents.debate_resolver import run_debate
from app.memory.memory_manager import (
    save_suggestion,
    get_developer_profile,
    update_developer_profile,
    is_duplicate_suggestion
)
from app.webhook.github_comments import post_pr_review
import requests
import time
import jwt

load_dotenv("config/.env")

router = APIRouter()

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "codesentinel_secret_123")
APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

def get_jwt_token() -> str:
    with open(PRIVATE_KEY_PATH, 'r') as f:
        private_key = f.read()
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + 540,
        "iss": APP_ID
    }
    return jwt.encode(payload, private_key, algorithm="RS256")

def get_installation_id(repo_full_name: str) -> int:
    token = get_jwt_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(
        f"https://api.github.com/repos/{repo_full_name}/installation",
        headers=headers
    )
    return response.json()["id"]

async def process_pr(
    repo_full_name: str,
    pr_number: int,
    developer: str,
    diff_url: str
):
    try:
        print(f"Processing PR #{pr_number} from {developer} in {repo_full_name}")

        installation_id = get_installation_id(repo_full_name)

        token_payload = get_jwt_token()
        headers = {
            "Authorization": f"Bearer {token_payload}",
            "Accept": "application/vnd.github.v3+json"
        }

        install_token_resp = requests.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers=headers
        )
        install_token = install_token_resp.json()["token"]

        diff_headers = {
            "Authorization": f"token {install_token}",
            "Accept": "application/vnd.github.v3.diff"
        }
        diff_resp = requests.get(diff_url, headers=diff_headers)
        code = diff_resp.text[:3000]

        if not code.strip():
            code = "# No code changes detected in this PR"

        profile = get_developer_profile(developer)
        analysis = analyze_code(code, "pr_diff.py")
        debate_result = await run_debate(code, analysis)

        filtered_issues = []
        for issue in debate_result["final_review"].get("priority_issues", []):
            suggestion_text = issue.get("issue", "")
            if not is_duplicate_suggestion(developer, suggestion_text):
                save_suggestion(developer, repo_full_name, suggestion_text)
                filtered_issues.append(issue)
            else:
                issue["skipped"] = "Already suggested to this developer"
                filtered_issues.append(issue)

        debate_result["final_review"]["priority_issues"] = filtered_issues
        update_developer_profile(developer)

        review_result = {
            "filename": "pr_diff.py",
            "developer": developer,
            "developer_profile": profile,
            "static_analysis": analysis,
            "ai_review": debate_result
        }

        post_pr_review(
            installation_id,
            repo_full_name,
            pr_number,
            review_result
        )

        print(f"Successfully reviewed PR #{pr_number}")

    except Exception as e:
        print(f"Error processing PR: {e}")

@router.post("/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None)
):
    payload = await request.body()

    if x_hub_signature_256:
        if not verify_signature(payload, x_hub_signature_256, WEBHOOK_SECRET):
            raise HTTPException(status_code=401, detail="Invalid signature")

    data = json.loads(payload)
    action = data.get("action", "unknown")
    pr_number = data.get("pull_request", {}).get("number")
    repo_name = data.get("repository", {}).get("full_name", "N/A")
    developer = data.get("pull_request", {}).get("user", {}).get("login", "anonymous")
    diff_url = data.get("pull_request", {}).get("diff_url", "")

    print(f"Event: {x_github_event} | Action: {action} | PR: #{pr_number} | Repo: {repo_name}")

    if x_github_event == "pull_request" and action in ["opened", "synchronize"]:
        background_tasks.add_task(
            process_pr,
            repo_name,
            pr_number,
            developer,
            diff_url
        )

    return {
        "status": "received",
        "event": x_github_event,
        "action": action,
        "pr_number": pr_number,
        "repo": repo_name
    }
