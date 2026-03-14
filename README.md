# CodeSentinel AI — Real-Time Code Review Bot

An AI-powered automated code review bot that analyzes GitHub Pull Requests in real time using a multi-agent debate engine, static analysis, and persistent developer memory.

## Features

- Automatic PR review the moment a pull request is opened
- Multi-agent AI debate — Security Agent vs Performance Agent
- Static analysis using Bandit (security) and Radon (complexity)
- Carbon cost estimator for inefficient algorithms
- Vector memory system — never repeats suggestions to the same developer
- Developer DNA profiling — tracks improvement over time
- Posts formatted review comments directly on GitHub PRs
- Runs 24/7 on AWS EC2 with zero manual intervention

## Tech Stack

- Python 3.12, FastAPI, Celery, Redis
- AWS EC2, AWS Bedrock (Amazon Nova)
- PostgreSQL + pgvector for vector memory
- sentence-transformers for embeddings
- Bandit, Radon for static analysis
- GitHub Apps API for webhook integration
- Nginx, Systemd for production deployment

## Architecture
```
GitHub PR → Webhook → FastAPI → Static Analysis
                                     ↓
                          Security Agent + Performance Agent (parallel)
                                     ↓
                              Debate Resolver (synthesis)
                                     ↓
                          Vector Memory Check (no duplicates)
                                     ↓
                          GitHub PR Comment Posted
```

## Quick Start

### Prerequisites

- AWS Account (free tier works)
- GitHub Account
- Python 3.12+
- PostgreSQL with pgvector extension

### Clone the repository
```bash
git clone https://github.com/Adarsh73111/codesentinel.git
cd codesentinel
```

### Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure environment
```bash
cp config/.env.example config/.env
```

Edit `config/.env` with your values:
```
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GITHUB_APP_ID=your_app_id
GITHUB_CLIENT_ID=your_client_id
GITHUB_PRIVATE_KEY_PATH=/path/to/private-key.pem
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://user:password@localhost/codesentinel
```

### Initialize database
```bash
python3 -c "from app.memory.database import init_db; init_db()"
```

### Run the server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Health status |
| GET | /health | Detailed health check |
| POST | /webhook/github | GitHub webhook receiver |
| POST | /analysis/analyze | Analyze code directly |
| POST | /review | Full AI review |

### Test the analyzer
```bash
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import subprocess\ndef run(cmd):\n    subprocess.call(cmd, shell=True)",
    "filename": "test.py",
    "developer": "your_github_username",
    "repo": "your_repo"
  }'
```

## GitHub App Setup

1. Go to github.com/settings/apps/new
2. Set webhook URL to `http://your-server-ip/webhook/github`
3. Set webhook secret to match your `.env`
4. Enable Pull Request permissions (Read & Write)
5. Subscribe to Pull Request events
6. Install the app on your target repository

## Deployment on AWS EC2

Full deployment guide available in [DEPLOYMENT.md](DEPLOYMENT.md)

## Project Structure
```
codesentinel/
├── app/
│   ├── main.py              # FastAPI application
│   ├── webhook/
│   │   ├── router.py        # GitHub webhook handler
│   │   └── github_comments.py # PR comment poster
│   ├── analysis/
│   │   ├── analyzer.py      # Static analysis engine
│   │   └── router.py        # Analysis API endpoint
│   ├── agents/
│   │   ├── security_agent.py    # Security review agent
│   │   ├── performance_agent.py # Performance review agent
│   │   └── debate_resolver.py   # Multi-agent synthesizer
│   └── memory/
│       ├── database.py      # PostgreSQL setup
│       └── memory_manager.py # Vector memory system
└── config/
    └── .env.example         # Environment template
```

## How It Works

1. Developer opens a Pull Request on GitHub
2. GitHub sends a webhook event to CodeSentinel
3. Static analysis runs immediately (Bandit + Radon)
4. Security Agent and Performance Agent run in parallel
5. Debate Resolver synthesizes both reviews
6. Vector memory checks for duplicate suggestions
7. Formatted review comment posted on the PR within 60 seconds

## License

MIT License — free to use, modify and distribute.

## Author

Built by Adarsh Misra — [@Adarsh73111](https://github.com/Adarsh73111)
