# 🏠 Local Setup Guide — Run CodeSentinel AI Bot Without AWS

This guide is for developers who previously ran CodeSentinel on AWS EC2
and had to delete their instance to avoid charges, or for anyone who wants
to run and test the bot completely locally for free using ngrok.

---

## 📋 What You Need

| Tool | Purpose | Cost |
|---|---|---|
| Python 3.12 | Run the application | Free |
| PostgreSQL | Database + vector memory | Free |
| Redis | Task queue | Free |
| ngrok | Public URL for GitHub webhooks | Free |
| AWS Account | Bedrock AI model access | Near zero |

---

## 💾 Step 0 — Save Your Credentials (If Migrating From AWS)

Before deleting your EC2 instance, save these from your server:

**Save your GitHub App private key:**
```bash
cat ~/codesentinel/config/private-key.pem
```
Copy the output and save it as `private-key.pem` on your laptop.

**Save your environment variables:**
```bash
cat ~/codesentinel/config/.env
```
Save these values somewhere safe:
- `GITHUB_APP_ID`
- `GITHUB_CLIENT_ID`
- `GITHUB_WEBHOOK_SECRET`

**Then safely delete from AWS in this order:**
1. Release Elastic IP — EC2 → Elastic IPs → Actions → Release
2. Terminate EC2 instance — EC2 → Instances → Actions → Terminate
3. Check for leftover EBS volumes — EC2 → Volumes → delete any remaining

---

## 🖥️ Step 1 — Install Python 3.12

### Windows
Download from [python.org/downloads](https://www.python.org/downloads/)

During installation:
- ✅ Check **"Add Python to PATH"**
- ✅ Check **"Install pip"**

Verify installation:
```bash
python --version
pip --version
```

### Mac
```bash
brew install python@3.12
python3 --version
```

### Linux (Ubuntu)
```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip
python3 --version
```

---

## 🐘 Step 2 — Install PostgreSQL with pgvector

### Windows
1. Download from [postgresql.org/downloads](https://www.postgresql.org/downloads/)
2. Run the installer — remember the password you set for the `postgres` user
3. During install, also install **Stack Builder**
4. Use Stack Builder to install the **pgvector** extension

After installation, open **psql** or **pgAdmin** and run:
```sql
CREATE DATABASE codesentinel;
CREATE USER codesentinel_user WITH PASSWORD 'codesentinel_pass';
GRANT ALL PRIVILEGES ON DATABASE codesentinel TO codesentinel_user;
\c codesentinel
CREATE EXTENSION IF NOT EXISTS vector;
GRANT ALL ON SCHEMA public TO codesentinel_user;
```

### Mac
```bash
brew install postgresql@16
brew services start postgresql@16
psql postgres
```

Then run the SQL commands above.

### Linux (Ubuntu)
```bash
sudo apt install -y postgresql postgresql-contrib postgresql-16-pgvector
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres psql << 'EOF'
CREATE DATABASE codesentinel;
CREATE USER codesentinel_user WITH PASSWORD 'codesentinel_pass';
GRANT ALL PRIVILEGES ON DATABASE codesentinel TO codesentinel_user;
\c codesentinel
CREATE EXTENSION IF NOT EXISTS vector;
GRANT ALL ON SCHEMA public TO codesentinel_user;
EOF
```

---

## 🔴 Step 3 — Install Redis

### Windows
Download the installer from:
```
https://github.com/microsoftarchive/redis/releases
```
Download the `.msi` file and run it. Redis will install as a Windows service.

Verify:
```bash
redis-cli ping
```
Should return `PONG`

### Mac
```bash
brew install redis
brew services start redis
redis-cli ping
```

### Linux (Ubuntu)
```bash
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
redis-cli ping
```

---

## 📥 Step 4 — Clone the Repository
```bash
git clone https://github.com/Adarsh73111/Codesentinel-AI-Bot.git
cd Codesentinel-AI-Bot
```

---

## 🐍 Step 5 — Set Up Python Virtual Environment

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

---

## 📦 Step 6 — Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will take 2-3 minutes as it downloads all packages including
the sentence-transformers AI model.

---

## ⚙️ Step 7 — Configure Environment Variables
```bash
cp config/.env.example config/.env
```

Open `config/.env` and fill in your values:
```env
GITHUB_WEBHOOK_SECRET=codesentinel_secret_123
GITHUB_APP_ID=your_real_app_id_here
GITHUB_CLIENT_ID=your_real_client_id_here
GITHUB_PRIVATE_KEY_PATH=config/private-key.pem
ANTHROPIC_API_KEY=
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://codesentinel_user:codesentinel_pass@localhost/codesentinel
DEBUG=True
```

---

## 🔑 Step 8 — Add Your GitHub App Private Key

Place your saved `private-key.pem` file inside the `config` folder:
```
Codesentinel-AI-Bot/
└── config/
    ├── .env
    └── private-key.pem   ← place it here
```

If you lost your private key:
1. Go to [github.com/settings/apps/CodeSentinel-AI-Bot](https://github.com/settings/apps/CodeSentinel-AI-Bot)
2. Scroll to **Private keys** section
3. Click **Generate a private key** — downloads a new `.pem` file
4. Place it in the `config` folder

---

## 🗄️ Step 9 — Initialize the Database
```bash
python3 -c "from app.memory.database import init_db; init_db()"
```

Should print:
```
Database initialized successfully!
```

---

## 🌐 Step 10 — Install and Configure ngrok

ngrok creates a public URL that tunnels to your local server.
GitHub needs this to send webhook events to your laptop.

### Install ngrok

Go to [ngrok.com/download](https://ngrok.com/download) and download for your OS.

Or install via package manager:

**Mac:**
```bash
brew install ngrok/ngrok/ngrok
```

**Linux:**
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

### Set up ngrok auth token

1. Sign up for free at [ngrok.com](https://ngrok.com)
2. Go to your dashboard and copy your auth token
3. Run:
```bash
ngrok config add-authtoken your_auth_token_here
```

---

## 🚀 Step 11 — Start Everything

You need **three separate terminal windows** running simultaneously.

### Terminal 1 — Start Redis (if not running as a service)

**Windows:**
Redis should already be running as a Windows service after installation.
Verify with:
```bash
redis-cli ping
```

**Mac/Linux:**
```bash
redis-server
```

---

### Terminal 2 — Start FastAPI Server
```bash
cd Codesentinel-AI-Bot

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete.
```

---

### Terminal 3 — Start ngrok Tunnel
```bash
ngrok http 8000
```

You will see output like:
```
Forwarding  https://abc123def456.ngrok-free.app -> http://localhost:8000
```

**Copy the `https://...ngrok-free.app` URL — you need this in the next step.**

---

## 🐙 Step 12 — Update GitHub App Webhook URL

Every time you start a new ngrok session the URL changes.
You need to update your GitHub App webhook URL each time.

1. Go to:
```
https://github.com/settings/apps/CodeSentinel-AI-Bot
```

2. Find the **Webhook URL** field

3. Replace it with your new ngrok URL:
```
https://abc123def456.ngrok-free.app/webhook/github
```

4. Click **Save changes**

---

## ✅ Step 13 — Verify Everything is Working

Open your browser and visit:
```
http://localhost:8000
```

Should show:
```json
{
  "status": "CodeSentinel AI is running",
  "version": "1.0.0"
}
```

Also visit:
```
http://localhost:8000/docs
```

Should show the FastAPI interactive documentation page.

---

## 🧪 Step 14 — Test the Full Bot

**Test direct API review:**
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

**Test full GitHub PR flow:**

1. Go to your test repo on GitHub
2. Create a new branch
3. Add a Python file with some code
4. Open a Pull Request
5. Within 60 seconds — **codesentinel-ai-bot** will post a review comment automatically!

---

## ⚠️ Important Notes

### ngrok URL changes every session
Every time you restart ngrok, you get a new URL.
Always update your GitHub App webhook URL before testing.

To avoid this — upgrade to ngrok paid plan which gives a permanent URL.
Or deploy to a free host like Render or Railway for a permanent free URL.

### AWS Bedrock still needed
The AI agents use AWS Bedrock (Amazon Nova Micro).
Make sure your AWS credentials are configured locally:
```bash
aws configure
```

Enter your AWS Access Key ID and Secret Access Key.
Or attach an IAM role if running on any AWS service.

To get AWS credentials locally:
1. Go to AWS Console → IAM → Users → your user
2. Security credentials → Create access key
3. Copy Access Key ID and Secret Access Key
4. Run `aws configure` and enter them

### Install AWS CLI if not installed
**Windows/Mac/Linux:**
```
https://aws.amazon.com/cli/
```

---

## 🔁 Quick Start Checklist (Every Testing Session)

Every time you want to test the bot, do these steps in order:
```
1. Start Redis          → redis-cli ping (should return PONG)
2. Start FastAPI        → uvicorn app.main:app --host 0.0.0.0 --port 8000
3. Start ngrok          → ngrok http 8000
4. Copy ngrok URL       → https://xxxxx.ngrok-free.app
5. Update webhook URL   → github.com/settings/apps/CodeSentinel-AI-Bot
6. Open a PR            → watch the bot review it automatically!
```

---

## 🩺 Troubleshooting

### "Module not found" error
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Database connection error
```bash
# Check PostgreSQL is running
# Windows: check Services app
# Mac: brew services list
# Linux:
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### Redis connection error
```bash
redis-cli ping
# If no PONG:
sudo systemctl start redis-server  # Linux
brew services start redis           # Mac
```

### Webhook not arriving
- Check ngrok is running and URL is copied correctly
- Check GitHub App webhook URL is updated with new ngrok URL
- Check GitHub App is installed on your test repo

### Bot not posting comments
- Check your `private-key.pem` is in the `config` folder
- Check `GITHUB_APP_ID` in `.env` is correct
- Check GitHub App has Pull Request read/write permissions

### AWS Bedrock access denied
```bash
aws configure  # re-enter your credentials
```
Make sure your IAM user has `AmazonBedrockFullAccess` policy attached.

---

## 🆓 Free Hosting Alternatives (No AWS EC2 Needed)

If you want the bot running 24/7 without your laptop being on:

| Platform | Free Tier | Permanent URL | Notes |
|---|---|---|---|
| Render | ✅ Yes | ✅ Yes | Sleeps after 15min inactivity |
| Railway | ✅ Yes | ✅ Yes | $5 free credits/month |
| Fly.io | ✅ Yes | ✅ Yes | Good for small apps |
| Koyeb | ✅ Yes | ✅ Yes | Always on free tier |

For any of these — connect your GitHub repo, add environment variables, and deploy. No server management needed.

---

## 🔗 Related Links

- **Main Repository:** [Codesentinel-AI-Bot](https://github.com/Adarsh73111/Codesentinel-AI-Bot)
- **Live Demo Repository:** [codesentinel-test](https://github.com/Adarsh73111/codesentinel-test)
- **GitHub App Settings:** [CodeSentinel-AI-Bot App](https://github.com/settings/apps/CodeSentinel-AI-Bot)
- **ngrok Download:** [ngrok.com/download](https://ngrok.com/download)
- **AWS CLI:** [aws.amazon.com/cli](https://aws.amazon.com/cli/)

---

*CodeSentinel AI Bot — runs anywhere, costs nothing*
```

---

## Add this to your repo:

Go to:
```
https://github.com/Adarsh73111/Codesentinel-AI-Bot
