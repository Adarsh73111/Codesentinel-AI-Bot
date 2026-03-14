import os
import jwt
import time
import requests
from github import Github, GithubIntegration
from dotenv import load_dotenv

load_dotenv("config/.env")

APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")

def get_installation_token(installation_id: int) -> str:
    with open(PRIVATE_KEY_PATH, 'r') as f:
        private_key = f.read()

    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + 540,
        "iss": APP_ID
    }

    token = jwt.encode(payload, private_key, algorithm="RS256")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers=headers
    )

    return response.json()["token"]

def post_pr_review(
    installation_id: int,
    repo_full_name: str,
    pr_number: int,
    review_result: dict
) -> bool:
    try:
        token = get_installation_token(installation_id)
        g = Github(token)
        repo = g.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)

        final_review = review_result.get("ai_review", {}).get("final_review", {})
        static = review_result.get("static_analysis", {})

        lines = []
        lines.append("## CodeSentinel AI Review")
        lines.append("")
        lines.append(f"**Summary:** {final_review.get('summary', 'No summary')}")
        lines.append("")
        lines.append(f"**Overall Score:** {final_review.get('overall_score', 'N/A')}/10")
        lines.append("")

        security_issues = static.get("security_issues", [])
        if security_issues:
            lines.append("### Security Issues Found")
            for issue in security_issues:
                lines.append(f"- **{issue['severity']}** (line {issue['lineno']}): {issue['description']}")
            lines.append("")

        priority_issues = final_review.get("priority_issues", [])
        if priority_issues:
            lines.append("### Priority Issues")
            for issue in priority_issues:
                if not issue.get("skipped"):
                    lines.append(f"- **{issue['severity']}**: {issue['issue']}")
                    lines.append(f"  - Fix: {issue['fix']}")
            lines.append("")

        positives = final_review.get("positive_aspects", [])
        if positives:
            lines.append("### Positive Aspects")
            for p in positives:
                lines.append(f"- {p}")
            lines.append("")

        lines.append("---")
        lines.append("*Reviewed by CodeSentinel AI — Security + Performance agents*")

        comment_body = "\n".join(lines)
        pr.create_issue_comment(comment_body)
        print(f"Posted review comment on PR #{pr_number}")
        return True

    except Exception as e:
        print(f"Error posting comment: {e}")
        return False
