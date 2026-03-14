import json
import asyncio
import boto3
from app.agents.security_agent import run_security_agent
from app.agents.performance_agent import run_performance_agent

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="ap-south-1"
)

async def run_debate(code: str, analysis_results: dict) -> dict:
    loop = asyncio.get_event_loop()

    security_result, performance_result = await asyncio.gather(
        loop.run_in_executor(None, run_security_agent, code, analysis_results),
        loop.run_in_executor(None, run_performance_agent, code, analysis_results)
    )

    synthesis_prompt = f"""You are a senior tech lead synthesizing two code reviews.
Security Agent findings: {security_result}
Performance Agent findings: {performance_result}
Create a unified developer-friendly review.
Respond in this exact JSON format only:
{{
    "summary": "2 sentence overall assessment",
    "priority_issues": [
        {{
            "issue": "description",
            "severity": "HIGH/MEDIUM/LOW",
            "fix": "specific fix suggestion",
            "line": "line number if known"
        }}
    ],
    "positive_aspects": ["things done well"],
    "overall_score": "1-10 score as string"
}}"""

    body = json.dumps({
        "messages": [
            {"role": "user", "content": [{"text": synthesis_prompt}]}
        ],
        "inferenceConfig": {
            "maxTokens": 1000,
            "temperature": 0.3
        }
    })

    response = bedrock.invoke_model(
        modelId="apac.amazon.nova-micro-v1:0",
        body=body
    )

    text = json.loads(response["body"].read())["output"]["message"]["content"][0]["text"]

    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        final_review = json.loads(text[start:end])
    except:
        final_review = {
            "summary": text,
            "priority_issues": [],
            "positive_aspects": [],
            "overall_score": "5"
        }

    return {
        "security_agent": security_result,
        "performance_agent": performance_result,
        "final_review": final_review
    }
