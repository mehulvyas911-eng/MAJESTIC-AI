# 🔴 Majestic AI v1.0 — GitHub Deployment Guide

> Complete step-by-step guide to publish Majestic AI to GitHub.

---

## Prerequisites Checklist

Before starting, make sure you have:

- [ ] A **GitHub account** → https://github.com/signup
- [ ] **Git installed** → Check: `git --version` in terminal
- [ ] **Python 3.10+** installed

---

## Step 1 — Install Git (if not already)

```bash
# Check if Git is installed
git --version
```

If not installed, download from: **https://git-scm.com/download/win**  
Install with default options. Restart your terminal after.

---

## Step 2 — Configure Git Identity (one-time setup)

Open PowerShell or Command Prompt and run:

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

> Use the same email as your GitHub account.

---

## Step 3 — Create a New Repository on GitHub

1. Go to **https://github.com/new**
2. Fill in:
   - **Repository name:** `majestic-ai`
   - **Description:** `AI-Powered Cybersecurity Automation Platform | MCP + Flask`
   - **Visibility:** Choose `Public` or `Private`
   - ❌ Do NOT check "Add README" (you already have one)
   - ❌ Do NOT check "Add .gitignore" (you already have one)
3. Click **"Create repository"**
4. **Copy the repository URL** shown — it will look like:  
   `https://github.com/YOUR_USERNAME/majestic-ai.git`

---

## Step 4 — Initialize Git in Your Project

Open PowerShell and navigate to your project:

```powershell
cd "C:\Users\mehul\OneDrive\Desktop\MAJESTIC"

# Initialize git
git init

# Check what files will be tracked
git status
```

---

## Step 5 — Stage All Files

```powershell
# Add all files (respects .gitignore automatically)
git add .

# Verify what's staged
git status
```

You should see these files staged (green):
```
server.py
mcp_client.py
agents.py
cache_engine.py
error_engine.py
visual_engine.py
browser_agent.py
requirements.txt
README.md
.gitignore
claude_mcp_config.json
GITHUB_DEPLOYMENT.md
```

---

## Step 6 — Make Your First Commit

```powershell
git commit -m "🔴 Initial release: Majestic AI v1.0

- Flask REST API with 50+ endpoints on port 8888
- FastMCP client wrapper for Claude/GPT/Copilot
- 12 AI agent classes (IntelligentDecisionEngine, BugBountyAgent, CTFAgent, etc.)
- 150+ security tool integrations
- Selenium headless browser agent
- LRU cache, exponential backoff, graceful degradation"
```

---

## Step 7 — Connect to GitHub and Push

```powershell
# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/majestic-ai.git

# Rename branch to main (GitHub default)
git branch -M main

# Push to GitHub
git push -u origin main
```

> **First push will ask for credentials:**
> - Username: your GitHub username
> - Password: use a **Personal Access Token** (NOT your password) — see Step 8

---

## Step 8 — GitHub Personal Access Token (PAT)

GitHub no longer accepts passwords for git push. You need a token:

1. Go to → **https://github.com/settings/tokens/new**
2. Fill in:
   - **Note:** `majestic-ai-push`
   - **Expiration:** 90 days (or No expiration)
   - **Scopes:** Check ✅ `repo` (full control of private repositories)
3. Click **"Generate token"**
4. **Copy the token immediately** (you won't see it again!)
5. Use this token as your **password** when `git push` asks

> **Save your token** in a password manager or Notepad temporarily.

### Alternatively: Use GitHub CLI (easier)
```powershell
# Install GitHub CLI
winget install --id GitHub.cli

# Login (opens browser)
gh auth login

# Then just push normally — no tokens needed
git push -u origin main
```

---

## Step 9 — Verify on GitHub

1. Visit: `https://github.com/YOUR_USERNAME/majestic-ai`
2. You should see all your files listed
3. The README.md will render automatically as the homepage

---

## Step 10 — Add a GitHub Release Tag (Optional but Recommended)

```powershell
# Tag this version
git tag -a v1.0.0 -m "Majestic AI v1.0.0 - Initial Release"

# Push the tag
git push origin v1.0.0
```

Then on GitHub:
1. Click **"Releases"** → **"Create a new release"**
2. Select tag `v1.0.0`
3. Title: `Majestic AI v1.0.0`
4. Add description of features
5. Click **"Publish release"**

---

## Future Updates — Push Changes

Whenever you update your code:

```powershell
cd "C:\Users\mehul\OneDrive\Desktop\MAJESTIC"

git add .
git commit -m "feat: describe your changes here"
git push
```

---

## Recommended GitHub Repository Settings

After pushing, configure these on GitHub:

### Topics (for discoverability)
Go to your repo → ⚙️ Settings → Add topics:
```
cybersecurity  penetration-testing  bug-bounty  ctf  mcp  ai  flask  python  security-automation  osint
```

### Description
```
🔴 AI-Powered Cybersecurity Automation Platform | MCP Protocol | 150+ Security Tools | Flask REST API
```

### README Badge (add to top of README.md)
```markdown
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![MCP](https://img.shields.io/badge/MCP-Compatible-red)
![License](https://img.shields.io/badge/License-MIT-yellow)
```

---

## Full Command Summary (copy-paste all at once)

```powershell
cd "C:\Users\mehul\OneDrive\Desktop\MAJESTIC"
git init
git add .
git commit -m "Initial release: Majestic AI v1.0"
git remote add origin https://github.com/YOUR_USERNAME/majestic-ai.git
git branch -M main
git push -u origin main
```

> Replace `YOUR_USERNAME` with your actual GitHub username before running.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `git: command not found` | Install Git from https://git-scm.com |
| `Authentication failed` | Use Personal Access Token as password (Step 8) |
| `remote origin already exists` | Run `git remote remove origin` then add again |
| `rejected - non-fast-forward` | Run `git pull origin main --rebase` then push again |
| `nothing to commit` | Files match last commit — make a change first |

---

*Majestic AI v1.0 — For authorized security testing only.*
