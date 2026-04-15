# Stil

A conversational AI assistant for creative professionals.
Stil learns your visual style across sessions and applies it without being asked.

## Setup (5 minutes)

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt

cp .env.example .env
# Paste your Anthropic API key into .env
# Get one free at: https://console.anthropic.com

# Add images to assets/ folder
# Download 8-10 free images from unsplash.com
# Rename descriptively e.g: dark_high_contrast_abstract_bg.jpg

streamlit run app.py
# Opens at http://localhost:8501
```

## Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI — 4 tabs, real-time streaming |
| `agent.py` | Agentic loop — Claude + tools + style memory |
| `creative_tools.py` | Editing tool functions |
| `asset_library.py` | MCP server — asset search |
| `insights.py` | Session quality grader |
| `style_profile.json` | Auto-created after first session |
| `logs/` | Session history |
| `assets/` | Your image library |

## How it works

1. Open Edit tab → describe what you want: "Make this warmer, crop square, export for Instagram"
2. Stil executes the edits and remembers your style
3. Next session: type "edit this photo" → Stil applies your preferences automatically
4. Insights tab → see how well Stil is serving your creative intent
5. Assets tab → find the right image by describing what you need
