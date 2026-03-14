cat > ~/codesentinel/DOCKER_SETUP.md << 'EOF'
# 🐳 Docker Setup Guide — Run CodeSentinel AI Bot Locally

This guide lets you run CodeSentinel AI Bot on any operating system
using Docker. No need to manually install Python, PostgreSQL, or Redis.
Everything runs in containers automatically.

---

## ✅ What Docker Does For You

Without Docker you would need to manually install and configure:
- Python 3.12
- PostgreSQL with pgvector extension
- Redis
- All Python packages
- Database setup

With Docker you just run one command and everything starts automatically.

---

## 📋 Prerequisites

You only need two things installed on your computer:

### 1. Docker Desktop

| OS | Download Link |
|---|---|
| Windows | [docs.docker.com/desktop/install/windows](https://docs.docker.com/desktop/install/windows-install/) |
| Mac (Intel) | [docs.docker.com/desktop/install/mac](https://docs.docker.com/desktop/install/mac-install/) |
| Mac (Apple Silicon M1/M2/M3) | [docs.docker.com/desktop/install/mac](https://docs.docker.com/desktop/install/mac-install/) |
| Linux (Ubuntu) | [docs.docker.com/desktop/install/linux](https://docs.docker.com/desktop/install/linux-install/) |

After installing Docker Desktop — open it and make sure it is running.
You should see the Docker whale icon in your taskbar/menu bar.

Verify Docker is working:
```bash
docker --version
docker-compose --version
```

### 2. ngrok (for GitHub webhook testing)

Sign up free at [ngrok.com](https://ngrok.com) and download for your OS.

| OS | Install Command |
|---|---|
| Windows | Download from ngrok.com/download |
| Mac | `brew install ngrok/ngrok/ngrok` |
| Linux | `snap install ngrok` |

---

## 🔑 Prerequisites — GitHub App

You need your own GitHub App to use CodeSentinel.
If you are setting up fresh, follow these steps:

### Create a GitHub App

1. Go to [github.com/settings/apps/new](https://github.com/settings/apps/new)
2. Fill in:
   - **GitHub App name:** your-codesentinel-bot
   - **Homepage URL:** http://localhost:8000
   - **Webhook URL:** leave blank for now — we will fill this after ngrok starts
   - **Webhook Secret:** choose any secret string e.g. `mysecret123`
3. Under **Repository permissions** set:
   - Contents → Read only
   - Metadata → Read only
   - Pull requests → Read and write
4. Under **Subscribe to events** check: ✅ Pull request
5. Under **Where can this be installed** select: Only on this account
6. Click **Create GitHub App**
7. Note down your **App ID** and **Client ID**
8. Scroll down → click **Generate a private key** → save the downloaded `.pem` file

---

## 🚀 Quick Start (5 steps)

### Step 1 — Clone the repository
```bash
git clone https://github.com/Adarsh73111/Codesentinel-AI-Bot.git
cd Codesentinel-AI-Bot
```

### Step 2 — Set up your config folder
```bash
# Mac/Linux:
cp config/.env.example config/.env

# Windows (Command Prompt):
copy config\.env.example config\.env

# Windows (PowerShell):
Copy-Item config\.env.example config\.env
```

### Step 3 — Add your private key

Place your GitHub App private key file inside the `config` folder:
```
Codesentinel-AI-Bot/
└── config/
    ├── .env          ← your environment variables
    └── private-key.pem  ← your GitHub App private key here
```

### Step 4 — Fill in your .env file

Open `config/.env` and fill in your values:
```env
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
GITHUB_APP_ID=your_app_id_here
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_PRIVATE_KEY_PATH=/app/config/private-key.pem
ANTHROPIC_API_KEY=
REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql://codesentinel_user:codesentinel_pass@db:5432/codesentinel
DEBUG=True
```

> ⚠️ Important: Keep `REDIS_URL` and `DATABASE_URL` exactly as shown above.
> Docker handles the connections between containers automatically.

### Step 5 — Start everything
```bash
docker-compose up
```

First time this runs it will:
- Download Docker images for PostgreSQL and Redis
- Build your FastAPI application image
- Install all Python packages
- Start all three services

This takes about 3-5 minutes the first time.
After that it starts in under 30 seconds.

You will see:
```
codesentinel-app  | INFO: Application startup complete.
codesentinel-app  | INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## ✅ Verify Everything is Running

Open your browser and visit:

| URL | Expected Result |
|---|---|
| `http://localhost:8000` | `{"status": "CodeSentinel AI is running"}` |
| `http://localhost:8000/health` | `{"status": "healthy"}` |
| `http://localhost:8000/docs` | FastAPI interactive documentation |

If all three work — your bot is running perfectly!

---

## 🌐 Set Up ngrok for GitHub Webhooks

GitHub needs a public URL to send webhook events to your local server.
ngrok creates a secure tunnel from the internet to your laptop.

### Step 1 — Configure ngrok auth token
```bash
ngrok config add-authtoken your_ngrok_auth_token
```

Get your auth token from [dashboard.ngrok.com](https://dashboard.ngrok.com)

### Step 2 — Start ngrok tunnel

Open a new terminal window and run:
```bash
ngrok http 8000
```

You will see:
```
Forwarding  https://abc123def456.ngrok-free.app -> http://localhost:8000
```

Copy the `https://...ngrok-free.app` URL.

### Step 3 — Update GitHub App webhook URL

1. Go to your GitHub App settings:
```
https://github.com/settings/apps/your-app-name
```

2. Find **Webhook URL** and update it to:
```
https://abc123def456.ngrok-free.app/webhook/github
```

3. Click **Save changes**

> ⚠️ ngrok URL changes every time you restart it on the free plan.
> Always update your GitHub App webhook URL at the start of each testing session.

---

## 🧪 Test the Full Bot

### Test 1 — Direct API review

Open a new terminal and run:
```bash
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import subprocess\ndef run(cmd):\n    subprocess.call(cmd, shell=True)\n    password = \"admin123\"",
    "filename": "test.py",
    "developer": "your_github_username",
    "repo": "your_test_repo"
  }'
```

You should get back a full JSON review with security issues, performance analysis, and AI recommendations.

### Test 2 — Full GitHub PR flow

1. Go to your test repository on GitHub
2. Create a new branch
3. Add a Python file with some code
4. Open a Pull Request
5. Within 60 seconds — your bot will automatically post a review comment!

---

## 🔄 Daily Usage

Every time you want to test the bot:
```
1. Open Docker Desktop — make sure it is running
2. Run: docker-compose up
3. Run ngrok: ngrok http 8000
4. Copy ngrok URL
5. Update GitHub App webhook URL
6. Open a PR — bot reviews it!
```

To stop everything:
```bash
# Press Ctrl+C in the docker-compose terminal
# Or run in another terminal:
docker-compose down
```

---

## ☁️ AWS Bedrock Configuration

The AI agents use AWS Bedrock (Amazon Nova Micro model).
You need AWS credentials configured on your laptop.

### Install AWS CLI

| OS | Link |
|---|---|
| Windows | [aws.amazon.com/cli](https://aws.amazon.com/cli/) |
| Mac | `brew install awscli` |
| Linux | `sudo apt install awscli` |

### Configure AWS credentials
```bash
aws configure
```

Enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `ap-south-1`
- Default output format: `json`

### Get AWS credentials

1. Go to AWS Console → IAM → Users → your username
2. Click **Security credentials** tab
3. Click **Create access key**
4. Copy Access Key ID and Secret Access Key

### Give your user Bedrock access

1. Go to AWS Console → IAM → Users → your username
2. Click **Add permissions** → **Attach policies directly**
3. Search for `AmazonBedrockFullAccess`
4. Check it → click **Add permissions**

---

## 🛠️ Useful Docker Commands
```bash
# Start all services
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# Stop all services
docker-compose down

# Stop and delete all data (fresh start)
docker-compose down -v

# View logs
docker-compose logs

# View live logs
docker-compose logs -f

# View logs for specific service
docker-compose logs app
docker-compose logs db
docker-compose logs redis

# Rebuild after code changes
docker-compose up --build

# Check running containers
docker ps

# Restart a specific service
docker-compose restart app
```

---

## 🩺 Troubleshooting

### Docker Desktop not running
Make sure Docker Desktop application is open and the whale icon is visible in your taskbar. Docker commands won't work if Docker Desktop is closed.

### Port 8000 already in use
```bash
# Mac/Linux — find what is using port 8000:
lsof -i :8000

# Windows:
netstat -ano | findstr :8000

# Kill the process or change the port in docker-compose.yml:
ports:
  - "8001:8000"  # use port 8001 instead
```

### Database connection error
```bash
# Check if db container is healthy:
docker ps

# View database logs:
docker-compose logs db

# Restart database:
docker-compose restart db
```

### pgvector extension error
The docker-compose uses `pgvector/pgvector:pg16` image which has pgvector pre-installed. If you see vector extension errors:
```bash
docker-compose down -v
docker-compose up --build
```

### AWS Bedrock access denied
```bash
# Verify credentials are configured:
aws sts get-caller-identity

# Re-configure if needed:
aws configure
```

### ngrok webhook not arriving
- Make sure ngrok is running
- Make sure GitHub App webhook URL is updated with current ngrok URL
- Make sure GitHub App is installed on your test repository
- Check ngrok dashboard at `http://localhost:4040` for request logs

### Bot not posting comments
- Check your `private-key.pem` is in the `config` folder
- Check `GITHUB_APP_ID` in `.env` is correct
- Check GitHub App has Pull Request read/write permissions
- View app logs: `docker-compose logs app`

---

## 📁 Project Structure After Setup
```
Codesentinel-AI-Bot/
├── app/                        # Application code
│   ├── main.py
│   ├── webhook/
│   ├── analysis/
│   ├── agents/
│   └── memory/
├── config/
│   ├── .env                    # Your credentials (gitignored)
│   ├── .env.example            # Template
│   └── private-key.pem         # GitHub App key (gitignored)
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # All services configuration
├── .dockerignore               # Files excluded from Docker
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 🆚 Docker vs Manual Setup

| | Manual Setup | Docker Setup |
|---|---|---|
| Time to set up | 45 minutes | 5 minutes |
| Works on Windows | Difficult | ✅ Yes |
| Works on Mac | Yes | ✅ Yes |
| Works on Linux | Yes | ✅ Yes |
| Install PostgreSQL manually | Yes | ❌ Not needed |
| Install Redis manually | Yes | ❌ Not needed |
| Install pgvector manually | Yes | ❌ Not needed |
| Database setup | Manual SQL commands | ✅ Automatic |
| One command start | No | ✅ Yes |

---

## 🔗 Related Guides

- **Main README:** [README.md](README.md)
- **Testing Guide:** [TESTING.md](TESTING.md)
- **Local Setup Without Docker:** [LOCAL_SETUP.md](LOCAL_SETUP.md)
- **Live Demo:** [codesentinel-test](https://github.com/Adarsh73111/codesentinel-test/pulls)

---

## 🔗 Useful Links

- [Docker Desktop Download](https://www.docker.com/products/docker-desktop/)
- [ngrok Download](https://ngrok.com/download)
- [AWS CLI Download](https://aws.amazon.com/cli/)
- [GitHub App Setup](https://github.com/settings/apps/new)

---

*CodeSentinel AI Bot — runs anywhere with Docker*
EOF
