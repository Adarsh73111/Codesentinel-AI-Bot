# 🧪 Testing Guide — CodeSentinel AI Bot

This guide walks you through every way to test CodeSentinel AI Bot
to confirm everything is working correctly.

---

## ✅ Pre-Test Checklist

Before running any test, make sure your server is running.
SSH into your EC2 instance and run:
```bash
cd ~/codesentinel && source venv/bin/activate
```

Then verify all services are active:
```bash
sudo systemctl status codesentinel --no-pager
sudo systemctl status nginx --no-pager
sudo systemctl status redis-server --no-pager
sudo systemctl status postgresql --no-pager
```

All four must show **active (running)** before proceeding.

If any service is down, restart it:
```bash
sudo systemctl restart codesentinel
sudo systemctl restart nginx
sudo systemctl restart redis-server
sudo systemctl restart postgresql
```

---

## 🔵 Test 1 — Server Health Check (Browser)

Open your browser and visit these three URLs one by one:

| URL | Expected Result |
|---|---|
| `http://3.7.106.40/` | JSON showing `"status": "CodeSentinel AI is running"` |
| `http://3.7.106.40/health` | JSON showing `"status": "healthy"` |
| `http://3.7.106.40/docs` | FastAPI interactive documentation page |

If all three load correctly your server is fully operational.

---

## 🔵 Test 2 — Direct API Review (Terminal)

This test directly calls the review engine without GitHub.
It proves the AI agents, static analysis, and memory system all work.

Run this command in your EC2 terminal:
```bash
curl -X POST http://127.0.0.1:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import subprocess\nimport pickle\ndef dangerous(user_input, data):\n    subprocess.call(user_input, shell=True)\n    obj = pickle.loads(data)\n    password = \"admin123\"\n    for i in range(1000):\n        for j in range(1000):\n            print(i,j)",
    "filename": "test.py",
    "developer": "Adarsh73111",
    "repo": "codesentinel-test"
  }'
```

### What you should see in the response:
```json
{
  "filename": "test.py",
  "developer": "Adarsh73111",
  "developer_profile": {
    "developer": "Adarsh73111",
    "total_reviews": 1,
    "skill_level": "intermediate"
  },
  "static_analysis": {
    "security_issues": [...],
    "complexity": [...],
    "syntax_valid": true
  },
  "ai_review": {
    "security_agent": {
      "overall_risk": "CRITICAL",
      "critical_issues": [...]
    },
    "performance_agent": {
      "efficiency_score": "2",
      "bottlenecks": [...]
    },
    "final_review": {
      "summary": "...",
      "priority_issues": [...],
      "overall_score": "3"
    }
  }
}
```

### What each field proves:

| Field | What it proves |
|---|---|
| `security_issues` | Bandit static scanner is working |
| `complexity` | Radon complexity analyzer is working |
| `security_agent` | Security AI agent is working |
| `performance_agent` | Performance AI agent is working |
| `final_review` | Debate resolver synthesis is working |
| `developer_profile` | PostgreSQL developer tracking is working |

---

## 🔵 Test 3 — Vector Memory Test (No Repeated Suggestions)

This test proves the memory system works correctly.
Run the exact same curl command from Test 2 **a second time** immediately.

### What you should see differently the second time:
```json
{
  "priority_issues": [
    {
      "issue": "subprocess call with shell=True",
      "severity": "HIGH",
      "skipped": "Already suggested to this developer"
    }
  ]
}
```

The `"skipped"` field appearing proves:
- The suggestion was saved to PostgreSQL with a vector embedding
- The similarity check found a match above the 0.85 threshold
- The memory system correctly skipped the duplicate

---

## 🔵 Test 4 — Full End to End GitHub PR Test

This is the most important test. It proves the complete system
works from GitHub to your server and back.

### Step 1 — Start live log monitoring

Open your EC2 terminal and run:
```bash
sudo journalctl -u codesentinel -f
```

Keep this terminal visible while doing the next steps.

### Step 2 — Go to the test repository
```
https://github.com/Adarsh73111/codesentinel-test
```

### Step 3 — Create a new branch

Click **"Branches"** → **"New branch"** → name it `test-new` → click **"Create branch"**

### Step 4 — Add a Python file with intentional issues

Go to the `test-new` branch → click **"Add file"** → **"Create new file"**

Name it `vulnerable_code.py` and paste this content:
```python
import subprocess
import os

def process_request(user_input):
    # Security issue: shell injection vulnerability
    result = subprocess.call(user_input, shell=True)

    # Security issue: hardcoded password
    password = "admin123"
    db_url = "postgresql://admin:password123@localhost/db"

    # Performance issue: nested loops
    data = []
    for i in range(1000):
        for j in range(1000):
            data.append(i * j)

    return result
```

Commit directly to `test-new` branch.

### Step 5 — Open a Pull Request

Go back to the repo main page. You'll see a yellow banner saying
**"test-new had recent pushes"** → click **"Compare & pull request"**

Add a title like `Add vulnerable_code.py` then click **"Create pull request"**

### Step 6 — Watch the terminal

The moment you click Create pull request, your terminal should show:
```
Event: pull_request | Action: opened | PR: #3 | Repo: Adarsh73111/codesentinel-test
Processing PR #3 from Adarsh73111 in Adarsh73111/codesentinel-test
Posted review comment on PR #3
Successfully reviewed PR #3
```

### Step 7 — Check the PR on GitHub

Go back to the PR page on GitHub. Within **60 seconds** you will see
**codesentinel-ai-bot** has automatically posted a review comment like this:
```
CodeSentinel AI Review

Summary: The code has significant security vulnerabilities...

Overall Score: 3/10

Priority Issues
- HIGH: Shell injection vulnerability due to subprocess.call with shell=True
  Fix: Avoid shell=True, pass command as a list instead
- HIGH: Hardcoded credentials in source code
  Fix: Use environment variables or a secrets manager
- MEDIUM: Nested loops causing O(n²) complexity
  Fix: Use list comprehension or numpy for better performance

Positive Aspects
- Code structure is generally organized

Reviewed by CodeSentinel AI — Security + Performance agents
```

---

## 🔵 Test 5 — Webhook Delivery Verification

This test confirms GitHub is successfully communicating with your server.

Go to:
```
https://github.com/settings/apps/CodeSentinel-AI-Bot/advanced
```

Scroll down to **"Recent Deliveries"** section.

You will see a list of every webhook event sent to your server.
Each delivery shows:

| Field | What to check |
|---|---|
| Event type | Should show `pull_request` |
| Response code | Should show `200` in green |
| Timestamp | Should match when you opened the PR |

Click on any delivery to see the full payload sent by GitHub
and the response your server returned.

---

## 🔵 Test 6 — Static Analysis Only

Test just the static analysis engine without the AI agents:
```bash
curl -X POST http://127.0.0.1:8000/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import subprocess\ndef run(cmd):\n    subprocess.call(cmd, shell=True)",
    "filename": "test.py"
  }'
```

### Expected response:
```json
{
  "filename": "test.py",
  "security_issues": [
    {
      "severity": "HIGH",
      "description": "subprocess call with shell=True identified",
      "lineno": 3,
      "test_id": "B602"
    }
  ],
  "complexity": [...],
  "syntax_valid": true,
  "errors": []
}
```

---

## 🩺 Quick Diagnosis — If Something Fails

### Server not responding:
```bash
sudo systemctl restart codesentinel
sudo journalctl -u codesentinel -n 20 --no-pager
```

### Database errors:
```bash
sudo systemctl restart postgresql
sudo -u postgres psql -c "\l" | grep codesentinel
```

### Redis errors:
```bash
sudo systemctl restart redis-server
redis-cli ping
```
Should return `PONG`

### Webhook not arriving:
- Check Security Group has port 80 open to Anywhere
- Check Nginx is running
- Check GitHub App webhook URL is correct

### Bot not posting comments:
- Check GitHub App is installed on the test repo
- Check private key file exists: `ls -la ~/codesentinel/config/private-key.pem`
- Check App ID in `.env` is correct

---

## 📊 Test Results Summary

After running all tests, you should be able to confirm:

| Component | Test | Status |
|---|---|---|
| FastAPI server | Test 1 | ✅ |
| Nginx reverse proxy | Test 1 | ✅ |
| Static analysis (Bandit) | Test 2 + 6 | ✅ |
| Complexity analysis (Radon) | Test 2 + 6 | ✅ |
| Security AI agent | Test 2 | ✅ |
| Performance AI agent | Test 2 | ✅ |
| Debate resolver | Test 2 | ✅ |
| Vector memory system | Test 3 | ✅ |
| GitHub webhook receiver | Test 4 | ✅ |
| GitHub PR comment poster | Test 4 | ✅ |
| Webhook delivery | Test 5 | ✅ |

---

## 🔗 Related Links

- **Main Repository:** [Codesentinel-AI-Bot](https://github.com/Adarsh73111/Codesentinel-AI-Bot)
- **Live Demo Repository:** [codesentinel-test](https://github.com/Adarsh73111/codesentinel-test)
- **GitHub App:** [CodeSentinel-AI-Bot](https://github.com/settings/apps/CodeSentinel-AI-Bot)

---

*Built and deployed on AWS EC2 free tier — CodeSentinel AI Bot*
```

---

## How to add this to your repo:

Go to:
```
https://github.com/Adarsh73111/Codesentinel-AI-Bot
