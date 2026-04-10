💀 GhostDev
AI That Finishes Your Work Without You
GhostDev is an autonomous AI agent that silently watches your Git repository and acts as a ghost developer working behind you. It detects what you're trying to build, completes your unfinished code, fixes bugs, and pushes commits — automatically.
✨ Features
👁 Watches your repo — monitors file changes in real time
🧠 Understands intent — reads goals.txt, TODOs, commit history, README, and stub functions
✍️ Writes missing code — completes stub functions and implements TODO comments
🐛 Fixes bugs — detects and patches broken code
✅ Validates before committing — syntax check + flake8 lint, never pushes broken code
💾 Auto-commits — commits with 👻 GhostDev: message and pushes to origin
🚀 Quick Start
1. Clone the repo
git clone https://github.com/YOUR_USERNAME/ghostdev
cd ghostdev
2. Install dependencies
pip install -r requirements.txt
3. Set your API key
Get a free key at console.anthropic.com
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
4. Describe your goal
echo "create a login system with username and password validation" > goals.txt
5. Run GhostDev
Watch mode (activates after 30s of idle):
python3 ghost-dev.py
One-shot mode (run immediately and exit):
python3 ghost-dev.py --once
Dry run (preview changes without writing):
python3 ghost-dev.py --once --dry-run
🎮 Demo — See It In Action
Create a Python file with empty functions:
# login.py

def register_user(username, password):
    # TODO: hash password and store user
    pass

def login(username, password):
    # TODO: validate credentials and return session token
    pass

def logout(session_token):
    pass
Run GhostDev:
python3 ghost-dev.py --idle 10
Stop typing. Wait 10 seconds.
Watch GhostDev complete your code and push a commit automatically.
Check the git log:
git log --oneline
# 👻 GhostDev: complete login.py
⚙️ Options
Flag
Default
Description
--repo PATH
.
Path to git repo to watch
--idle N
30
Seconds of inactivity before activation
--once
off
Run one pass immediately and exit
--dry-run
off
Preview changes without writing or committing
🏗 Architecture
Git Repo
   ↓ (watchdog — real-time file events)
GhostWatcher — detects developer idle
   ↓
ContextHarvester — reads:
   • goals.txt
   • TODO/FIXME comments
   • Git commit history
   • Stub functions (ast parsing)
   • README.md
   ↓
Claude API (claude-opus-4-5, 200K context)
   ↓
CodeValidator — syntax + flake8 lint
   ↓
GitManager — stage → commit → push
🛠 Tech Stack
Layer
Technology
AI Brain
Anthropic Claude API (claude-opus-4-5)
File Watching
watchdog
Git Operations
subprocess + git CLI
Code Validation
py_compile + flake8 + pytest
Intent Parsing
Python ast module
Language
Python 3.10+
📁 File Structure
ghostdev/
├── ghost-dev.py          # Main entry point & daemon loop
├── watcher.py            # Real-time file system watcher
├── context_harvester.py  # Multi-signal intent extraction
├── ai_engine.py          # Claude API integration
├── code_validator.py     # Syntax & lint validation
├── git_manager.py        # Git stage, commit, push
├── goals.txt             # Describe what you're building
├── requirements.txt
└── README.md
🔑 Intent Signals
GhostDev doesn't just read one file — it harvests 6 intent signals to deeply understand what you're trying to build:
Signal
Source
Explicit goal
goals.txt
Inline TODOs
All .py files
Commit history
git log
Stub functions
AST parsing
Project description
README.md
Missing references
Import errors
📄 License
MIT — built for the GitAgent Hackathon 2026
