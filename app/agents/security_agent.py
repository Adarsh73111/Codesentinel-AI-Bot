import json
import boto3

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="ap-south-1"
)

def run_security_agent(code: str, analysis_results: dict) -> dict:
    security_issues = analysis_results.get("security_issues", [])

    prompt = f"""You are a senior security engineer reviewing code.
Find security vulnerabilities and dangerous patterns.
Code: {code}
Static analysis found: {security_issues}
Respond in this exact JSON format only:
{{
    "agent": "security",
    "critical_issues": ["list of critical security problems"],
    "warnings": ["list of security warnings"],
    "recommendations": ["list of specific fixes"],
    "overall_risk": "LOW/MEDIUM/HIGH/CRITICAL"
}}"""

    body = json.dumps({
        "messages": [
            {"role": "user", "content": [{"text": prompt}]}
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
        return json.loads(text[start:end])
    except:
        return {
            "agent": "security",
            "critical_issues": [],
            "warnings": [text],
            "recommendations": [],
            "overall_risk": "MEDIUM"
        }
