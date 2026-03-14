import json
import boto3

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="ap-south-1"
)

def run_performance_agent(code: str, analysis_results: dict) -> dict:
    complexity = analysis_results.get("complexity", [])

    prompt = f"""You are a senior performance engineer reviewing code.
Find performance bottlenecks and inefficiencies.
Code: {code}
Complexity: {complexity}
Respond in this exact JSON format only:
{{
    "agent": "performance",
    "bottlenecks": ["list of performance bottlenecks"],
    "optimizations": ["list of specific optimizations"],
    "scalability_issues": ["list of scalability concerns"],
    "efficiency_score": "1-10 score as string"
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
            "agent": "performance",
            "bottlenecks": [text],
            "optimizations": [],
            "scalability_issues": [],
            "efficiency_score": "5"
        }
