# Stil ✦

**Your creative style, remembered.**

Stil is a conversational AI assistant for content creators and brand designers.
It learns your visual preferences — tone, crop ratios, export presets, aesthetic —
and applies them automatically every session without re-explanation.

---

## The problem in one sentence

Every AI tool you open treats you like a stranger, even after years of use.

You have a look. Warm tones. Square crops. Instagram exports. You've made these
decisions hundreds of times. But Lightroom presets don't follow you to Canva.
Canva templates don't follow you to CapCut. And every AI assistant you try
starts from zero every single session.

**Stil is the memory layer that sits across all of it.**

---

## What it does

| Capability | What happens |
|---|---|
| **Conversational editing** | Describe what you want. Stil picks the right tools and executes. |
| **Style memory** | Preferences extracted silently after every session. Never re-explain. |
| **Multimodal** | Upload a photo. Stil sees the actual image and tailors its edits. |
| **Smart asset search** | Describe what you need. Stil finds and ranks your image library. |
| **Quality insights** | Sessions graded on tool accuracy, goal completion, and creative intent. |

---

## Setup (5 minutes)

```bash
# 1. Clone and install
git clone https://github.com/bnamatherdhala7/FF-Stil.git
cd FF-Stil
pip install -r requirements.txt

# 2. Add your API key
cp .env.example .env
# Open .env and paste your Anthropic API key
# Get one at: https://console.anthropic.com

# 3. Add some photos to assets/ (optional)
# Download free images from unsplash.com
# Name them descriptively: portrait_warm_natural_light.jpg

# 4. Run
streamlit run app.py
# Opens at http://localhost:8501
```

---

## How to use it

**First session:**
1. Open the **Edit** tab
2. Upload a photo (or skip — just describe the edit)
3. Type: *"Make this warmer, crop it square, export for Instagram"*
4. Watch Stil execute the tools in real time
5. Your preferences are saved automatically

**Every session after:**
1. Type: *"Edit this photo"*
2. Stil applies your remembered style — no re-explanation needed

**Style tab** — see exactly what Stil knows about you. Edit or clear anytime.

**Insights tab** — run evals after a few sessions. Get a graded scorecard on
whether Stil is serving your actual creative intent.

**Assets tab** — search your image library in plain language:
*"high contrast background for a social post"*

---

## Architecture

```
app.py           Streamlit UI — 4 tabs, real-time streaming tool pills
agent.py         Agentic loop — Claude + tools + style memory + vision
creative_tools.py  5 editing functions: filter, brightness, crop, export, layers
asset_library.py   MCP asset server — list, inspect, tag, find
insights.py      Session grader — 3-dimension rubric + health summary
style_profile.json  Auto-created after first session (gitignored)
assets/          Your image library
logs/            JSONL session logs (gitignored)
```

**Model usage:**

| Task | Model | Why |
|---|---|---|
| Agent loop | claude-haiku-4-5 | Fast, cheap, responsive |
| Style extraction | claude-haiku-4-5 | Tiny structured prompt |
| Insights grading | claude-haiku-4-5 | One call per turn |
| Asset tagging | claude-haiku-4-5 | Cached — never re-run |

Target cost: **< $0.05 per user per day** at moderate usage.

---

## Asset naming convention

The filename is the search index. No database, no embeddings.

```
portrait_warm_natural_light.jpg
dark_high_contrast_abstract_bg.jpg
soft_pastel_gradient_bg.jpg
warm_golden_hour_outdoor.jpg
bright_colorful_flat_lay.jpg
```

Words in the filename match natural creative briefs.
Free images at [unsplash.com](https://unsplash.com) — download, rename, drop in.

---

## Roadmap

| Version | Focus |
|---|---|
| v0.1 (now) | Local prototype — style memory, conversational editing, asset search, insights |
| v0.2 | Short-form video — extend style profile to pacing, captions, aspect ratio |
| v0.3 | Real integrations — MCP connections to Lightroom, Canva, Cloudinary APIs |
| v0.4 | Multi-brand — multiple style profiles, client brand switching |
| v0.5 | Web app + mobile — hosted, mobile-first UI |

---

## Contributing

See [CLAUDE.md](CLAUDE.md) for the full architecture guide and development rules.

Built with [Anthropic Claude](https://anthropic.com) · [Streamlit](https://streamlit.io) · [FastMCP](https://github.com/jlowin/fastmcp)
