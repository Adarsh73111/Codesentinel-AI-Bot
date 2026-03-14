<div align="center">

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=32&pause=1000&color=6366F1&center=true&vCenter=true&width=600&lines=CodeSentinel+AI;Real-Time+Code+Review+Bot;Powered+by+Multi-Agent+AI" alt="Typing SVG" />

<br/>

**An AI-powered bot that automatically reviews your GitHub Pull Requests the moment they are opened — using a multi-agent debate engine, static analysis, and persistent developer memory.**

<br/>

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-8B5CF6?style=for-the-badge)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-App-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Adarsh73111/Codesentinel-AI-Bot)

<br/>

> 🤖 **See it live** → [codesentinel-test](https://github.com/Adarsh73111/codesentinel-test/pulls) — real PRs reviewed automatically by the bot

</div>

---

## 🎯 What is CodeSentinel AI Bot?

CodeSentinel AI Bot is a self-hosted, production-grade code review bot that installs on your GitHub repositories and automatically reviews every Pull Request using artificial intelligence. The moment a developer opens a PR, CodeSentinel springs into action — analyzing code for security vulnerabilities, performance bottlenecks, and code quality issues — then posts a detailed, formatted review comment directly on the PR. No waiting. No manual review needed.

What makes it genuinely unique is the **multi-agent debate engine**. Instead of a single AI pass, two specialized agents — a Security Expert and a Performance Expert — independently analyze the code and debate their findings. A third agent then synthesizes both perspectives into one cohesive, prioritized review. No existing tool does this.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔄 **Instant PR reviews** | Bot comments within 60 seconds of opening a PR |
| 🤖 **Multi-agent debate** | Security Agent vs Performance Agent running in parallel |
| 🔒 **Security scanning** | Bandit detects SQL injection, shell injection, hardcoded secrets |
| 📊 **Complexity analysis** | Radon scores every function A through F |
| 🌱 **Carbon estimator** | Flags algorithms with high compute cost at scale |
| 🧠 **Vector memory** | Never repeats the same suggestion to the same developer |
| 👤 **Developer profiling** | Tracks skill level and improvement over time |
| ♾️ **Runs 24/7** | AWS EC2 with auto-restart — never goes down |

---

## 🚀 Live Demo

> The bot is live and reviewing real PRs. Check it out:

**👉 [See live bot reviews here](https://github.com/Adarsh73111/codesentinel-test/pulls)**

> 🧪 **Test Repository** → [github.com/Adarsh73111/codesentinel-test](https://github.com/Adarsh73111/codesentinel-test) — this is the demo repo where CodeSentinel AI Bot is installed and reviewing every PR automatically

### Real PR reviewed automatically by CodeSentinel AI Bot:

![CodeSentinel AI Review in action](assets/pr-review-comment.png)

> The screenshot above shows **codesentinel-ai-bot** automatically posting a
> full code review comment on PR #2 — including summary, overall score,
> and positive aspects — within 60 seconds of the PR being opened.
> No human triggered this. The bot did it entirely on its own.

---

## 🏗️ Architecture
```
                    ┌─────────────────────────────────────┐
                    │           GitHub.com                 │
                    │     Developer opens a PR             │
                    └──────────────┬──────────────────────┘
                                   │ webhook event
                                   ▼
                    ┌─────────────────────────────────────┐
                    │         FastAPI Server               │
                    │      AWS EC2 (Ubuntu 24.04)          │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │        Static Analysis               │
                    │   Bandit + Radon + Carbon Score      │
                    └──────────────┬──────────────────────┘
                                   │
              ┌────────────────────┼─────────────────────┐
              │                                          │
   ┌──────────▼──────────┐              ┌───────────────▼──────────┐
   │   Security Agent    │              │   Performance Agent       │
   │  Finds vulns, risks │              │  Finds bottlenecks       │
   └──────────┬──────────┘              └───────────────┬──────────┘
              │                                          │
              └────────────────────┬─────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │        Debate Resolver               │
                    │   Synthesizes both agent reviews     │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │       Vector Memory Check            │
                    │  PostgreSQL + pgvector (no repeats)  │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │     GitHub PR Comment Posted         │
                    │        within 60 seconds             │
                    └─────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.12 |
| **Web Framework** | FastAPI + Uvicorn |
| **Task Queue** | Celery + Redis |
| **AI Models** | AWS Bedrock (Amazon Nova Micro) |
| **Security Scanner** | Bandit |
| **Complexity Analyzer** | Radon |
| **Vector Memory** | PostgreSQL + pgvector |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **GitHub Integration** | GitHub Apps API + Webhooks |
| **Reverse Proxy** | Nginx |
| **Process Manager** | Systemd |
| **Cloud** | AWS EC2 (Ubuntu 24.04 LTS) |

---

## ⚡ Quick Start

### Prerequisites

- AWS Account (free tier works perfectly)
- GitHub Account
- Python 3.12+
- PostgreSQL with pgvector extension
- Redis

### 1. Clone the repository
```bash
git clone https://github.com/Adarsh73111/Codesentinel-AI-Bot.git
cd Codesentinel-AI-Bot
```

### 2. Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp config/.env.example config/.env
nano config/.env
```

Fill in your values:
```env
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GITHUB_APP_ID=your_github_app_id
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_PRIVATE_KEY_PATH=/path/to/private-key.pem
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://user:password@localhost/codesentinel
```

### 4. Initialize database
```bash
python3 -c "from app.memory.database import init_db; init_db()"
```

### 5. Run the server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:8000/docs` for the interactive API documentation.

📋 **Full testing guide:** [TESTING.md](TESTING.md)

---

## 🐙 GitHub App Setup

1. Go to [github.com/settings/apps/new](https://github.com/settings/apps/new)
2. Fill in:
   - **App name:** your-codesentinel
   - **Homepage URL:** your server IP
   - **Webhook URL:** `http://your-server-ip/webhook/github`
   - **Webhook Secret:** same as in your `.env`
3. Under **Repository permissions** set:
   - Contents → Read only
   - Metadata → Read only
   - Pull requests → Read and write
4. Under **Subscribe to events** check: ✅ Pull request
5. Click **Create GitHub App**
6. Generate a private key → save as `config/private-key.pem`
7. Install the app on your target repository
8. Open a PR and watch CodeSentinel review it automatically!

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Server status |
| `GET` | `/health` | Health check |
| `POST` | `/webhook/github` | GitHub webhook receiver |
| `POST` | `/analysis/analyze` | Analyze code directly |
| `POST` | `/review` | Full multi-agent AI review |

### Test the full review engine directly:
```bash
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import subprocess\ndef run(cmd):\n    subprocess.call(cmd, shell=True)",
    "filename": "test.py",
    "developer": "your_github_username",
    "repo": "your_repo_name"
  }'
```

---

## 📁 Project Structure
```
Codesentinel-AI-Bot/
├── app/
│   ├── main.py                     # FastAPI application entry point
│   ├── webhook/
│   │   ├── router.py               # GitHub webhook handler
│   │   └── github_comments.py      # PR comment poster
│   ├── analysis/
│   │   ├── analyzer.py             # Static analysis engine
│   │   └── router.py               # Analysis API endpoint
│   ├── agents/
│   │   ├── security_agent.py       # Security review AI agent
│   │   ├── performance_agent.py    # Performance review AI agent
│   │   └── debate_resolver.py      # Multi-agent debate synthesizer
│   └── memory/
│       ├── database.py             # PostgreSQL + pgvector setup
│       └── memory_manager.py       # Vector memory system
├── config/
│   ├── .env.example                # Environment variables template
│   └── private-key.pem             # GitHub App key (gitignored)
├── assets/                         # Screenshots and demo images
├── requirements.txt
└── README.md
```

---

## 💡 Use Cases

- 👨‍💻 **Solo developers** — instant feedback on every PR, even at 2am
- 👥 **Small teams** — first-pass review before senior dev review
- 🎓 **Bootcamps and colleges** — automated feedback for student code
- 🌐 **Open source projects** — review contributor PRs automatically
- 🏢 **Startups** — ship faster with automated quality gates

---

## 🔗 Related Repositories

| Repository | Description |
|---|---|
| [Codesentinel-AI-Bot](https://github.com/Adarsh73111/Codesentinel-AI-Bot) | Main project — all source code |
| [codesentinel-test](https://github.com/Adarsh73111/codesentinel-test) | Live demo repo — see real bot reviews on PRs |

---

## ☁️ Deployment

This project runs on **AWS EC2 free tier** with zero cost for the infrastructure.

| Resource | Specification | Cost |
|---|---|---|
| EC2 Instance | m7i-flex.large (2 vCPU, 8GB RAM) | Free tier |
| Storage | 20GB gp3 EBS | Free tier |
| AI Model | AWS Bedrock Nova Micro | Near zero |
| Database | PostgreSQL on EC2 | Free |
| Each PR review | ~3 AI calls | < ₹1 |

---

## 📄 License

MIT License — free to use, modify and distribute.

---

## 👨‍💻 Author

**Adarsh Misra**

GitHub: [@Adarsh73111](https://github.com/Adarsh73111)

> Built from scratch in one session — EC2 provisioning, GitHub App integration,
> multi-agent AI debate engine, vector memory with pgvector, and automatic PR comments.
> Every component deployed and working on AWS free tier.

---

<div align="center">

### ⭐ If this project helped you, please give it a star!

**[⭐ Star Codesentinel-AI-Bot](https://github.com/Adarsh73111/Codesentinel-AI-Bot)**

</div>
