import ast
import subprocess
import json
import tempfile
import os
from radon.complexity import cc_visit
from radon.metrics import mi_visit

def analyze_code(code: str, filename: str = "code.py") -> dict:
    results = {
        "filename": filename,
        "security_issues": [],
        "complexity": [],
        "carbon_estimate": None,
        "syntax_valid": True,
        "errors": []
    }

    try:
        ast.parse(code)
    except SyntaxError as e:
        results["syntax_valid"] = False
        results["errors"].append(f"Syntax error: {str(e)}")
        return results

    try:
        complexity = cc_visit(code)
        for block in complexity:
            results["complexity"].append({
                "name": block.name,
                "complexity": block.complexity,
                "rank": block.letter,
                "lineno": block.lineno
            })
    except Exception as e:
        results["errors"].append(f"Complexity error: {str(e)}")

    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        result = subprocess.run(
            ['bandit', '-f', 'json', '-q', tmp_path],
            capture_output=True,
            text=True
        )
        os.unlink(tmp_path)

        if result.stdout:
            bandit_data = json.loads(result.stdout)
            for issue in bandit_data.get("results", []):
                results["security_issues"].append({
                    "severity": issue["issue_severity"],
                    "confidence": issue["issue_confidence"],
                    "description": issue["issue_text"],
                    "lineno": issue["line_number"],
                    "test_id": issue["test_id"]
                })
    except Exception as e:
        results["errors"].append(f"Security scan error: {str(e)}")

    try:
        high_complexity = [
            c for c in results["complexity"]
            if c["complexity"] > 5
        ]
        if high_complexity:
            avg_complexity = sum(
                c["complexity"] for c in high_complexity
            ) / len(high_complexity)
            results["carbon_estimate"] = {
                "score": round(avg_complexity * 0.8, 2),
                "note": f"{len(high_complexity)} functions with high complexity detected"
            }
    except Exception as e:
        results["errors"].append(f"Carbon estimate error: {str(e)}")

    return results
