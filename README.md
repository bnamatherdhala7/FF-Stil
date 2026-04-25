# Stil ✦

**Your creative style, remembered.**

Stil is a conversational AI assistant for content creators and brand designers.
Upload a photo, describe what you want, and Stil executes it — then remembers your
choices so the next session already knows your aesthetic.

---

## The problem

Every AI tool you open treats you like a stranger, even after years of use.

Here is what a typical creator's image editing session looks like today:

1. Open Lightroom (or Canva, or any AI tool)
2. Apply your warm filter — *again*
3. Crop to square — *again*
4. Set export to 1080×1080 for Instagram — *again*
5. Bump brightness up +20 — *again*

You have done this hundreds of times. The preferences are not secret or complicated —
warm tones, square crops, Instagram exports, slight brightness boost. You have decided
these things already. But no tool remembers them across sessions, and no tool carries
them across platforms.

**Lightroom presets stay in Lightroom. Canva templates stay in Canva.
Every AI assistant starts from zero every single time.**

The result: 46% of a creator's working time goes to tasks like this — repetitive
technical decisions they have already made, re-entered by hand because no tool holds
the memory.

Stil fixes this. You tell it once. It remembers forever.

---

## What Stil does

| Feature | What it means for you |
|---|---|
| **Conversational editing** | Say "make this warmer and crop it square" — Stil picks the right tools and runs them. No menus, no presets to configure. |
| **Style memory** | After every session, Stil silently extracts your preferences and saves them. Next time, they're already applied. |
| **Real image preview** | Upload a photo and see an actual before/after — filters, brightness, contrast, and crop applied using real image processing. |
| **Choices log** | Every filter, crop, brightness, and export choice is logged. The most recent choice always wins — no AI guessing needed. |
| **Style profile editor** | See exactly what Stil thinks your style is. Edit any field. Stil is transparent by design — no hidden magic. |
| **Color palette extraction** | Upload an image and Stil reads your dominant colors automatically, adding them to your style profile. |
| **Smart asset search** | Describe what you need in plain English. Stil scores your library by keyword match and AI-generated tags. |
| **Quality insights** | Every session is graded on three dimensions: tool accuracy, goal completion, and creative intent — the one that actually matters. |

---

## Quick start (5 minutes)

```bash
# 1. Clone and install
git clone https://github.com/bnamatherdhala7/FF-Stil.git
cd FF-Stil/stil
pip install -r requirements.txt

# 2. Add your Anthropic API key
cp .env.example .env
# Edit .env and paste your key: ANTHROPIC_API_KEY=sk-ant-...
# Get a key at: https://console.anthropic.com

# 3. (Optional) Add photos to assets/
# Free images at unsplash.com — name them descriptively:
# portrait_warm_natural_light.jpg, dark_high_contrast_abstract_bg.jpg

# 4. Run
streamlit run app.py
# Opens at http://localhost:8501
```

---

## How to use it

### First session — building your profile

1. Open the **Edit** tab
2. If it is your first time, fill in the **style seed card** — tone, platform, and one
   word that describes your aesthetic (e.g. "moody"). This gives Stil a starting point
   before any conversation.
3. Upload a photo — Stil extracts your dominant color palette automatically
4. Type what you want: *"Apply a warm filter, bump brightness +20, crop square,
   export for Instagram"*
5. Watch the tool pills fire in real time as each action executes
6. A **before/after preview** appears showing the actual edit applied to your photo
7. Your choices are saved to the sidebar — that is your style profile updating live

### Every session after — no re-explanation needed

1. Upload a new photo (or skip — Stil keeps the previous one in context)
2. Type: *"Edit this for my Instagram"*
3. Stil reads your choices log and applies your remembered aesthetic without asking

### Style tab — your profile, always visible and editable

- See your tone, crop preference, export targets, color palette, and aesthetic summary
- **Edit any field directly** — Stil does not lock you out of your own profile
- Raw `style_profile.json` is always visible in an expander
- Clear memory at any time with one button

### Insights tab — is Stil actually serving you?

- Click **Run evals** after a few sessions
- Three scores: tool accuracy (did it use the right tools?), goal completion (did it
  finish the task?), and **creative intent** (did the output serve what you actually wanted?)
- Creative intent is the score that matters — a session can score 5/5 on completion
  and 1/5 on intent if it did exactly what you typed but missed the creative purpose
- After 2+ sessions: a **trend chart** shows whether creative intent improves over time
  as your profile matures

### Assets tab — find the right photo fast

Search your image library in plain language: *"high contrast background for a social post"*
Stil returns ranked results with thumbnails, AI-generated tags, and a rationale for each match.

---

## How style memory works

```
You finish a session
        ↓
Two things happen:

  1. choices_log updated (deterministic — ground truth)
     apply_filter("warm") → logs  filter: warm
     crop_image("square")  → logs  crop: square
     Most recent entry always wins in the next session's system prompt.

  2. style_signature updated (AI-extracted)
     Haiku reads the conversation and extracts tone, aesthetic notes,
     export targets — things that don't surface from tool calls alone.

Next session:
  Priority 1 → choices_log (what you actually did last time)
  Priority 2 → style_signature (what Stil inferred about your taste)
```

The choices log is the ground truth. If you switch from warm to dramatic filters,
that change is captured immediately from the tool call — no AI inference, no drift.

---

## Editing tools available

| Tool | What it does |
|---|---|
| `apply_filter` | warm, cool, vintage, dramatic, soft, vivid, bw |
| `adjust_brightness` | −100 (darker) to +100 (brighter) |
| `adjust_contrast` | −100 (flat) to +100 (high contrast) |
| `crop_image` | square, portrait, landscape, story, tiktok, wide |
| `set_export_preset` | instagram, tiktok, reels, twitter, linkedin, web, print |
| `list_layers` | inspect the layer stack |

All edits produce a real before/after preview using Pillow image processing.

---

## Architecture

```
app.py             Streamlit UI — 4 tabs, streaming tool pills, before/after preview
agent.py           Agentic loop — Claude + tools + style memory + vision + conversation history
creative_tools.py  6 editing tools + PIL preview rendering
asset_library.py   MCP asset server — list, inspect, AI-tag, find
insights.py        Session grader — 3-dimension rubric, trend chart, health summary
style_profile.json Auto-created after first session (gitignored)
assets/            Your image library (descriptive filenames = search index)
logs/              JSONL session logs (gitignored)
```

**Model usage — all Haiku, all cheap:**

| Task | Model | Approx. cost |
|---|---|---|
| Agent loop (per session) | claude-haiku-4-5 | ~$0.01 |
| Style extraction (per session) | claude-haiku-4-5 | ~$0.002 |
| Insights grading (per turn) | claude-haiku-4-5 | ~$0.003 |
| Asset tagging (one-time per image) | claude-haiku-4-5 | ~$0.001 |

Target: **< $0.05 per user per day.** Color palette extraction uses Pillow only — no API call.

---

## Asset naming convention

The filename is the search index. No database, no vector embeddings.

```
portrait_warm_natural_light.jpg      →  "warm portrait natural light"
dark_high_contrast_abstract_bg.jpg   →  "high contrast background social post"
soft_pastel_gradient_bg.jpg          →  "soft pastel social media"
warm_golden_hour_outdoor.jpg         →  "warm golden hour lifestyle"
bright_colorful_flat_lay.jpg         →  "vibrant colorful product flat lay"
```

Words in the filename match the way you'd describe the photo in a creative brief.
Free images at [unsplash.com](https://unsplash.com) — download, rename descriptively, drop in `assets/`.

---

## Roadmap

| Version | Focus | Status |
|---|---|---|
| v0.1 | Style memory, choices log, multimodal vision, real filter preview, onboarding, style editor, color palette, insights | **Shipped** |
| v0.2 | Mood tags, session comparison, export style brief PDF | Next |
| v0.3 | Real tool integrations — Canva Apps SDK, Cloudinary API | Planned |
| v0.4 | Multi-brand — multiple style profiles, client brand switching | Planned |
| v0.5 | Web app + mobile — hosted, database-backed, mobile-first UI | Planned |

> **Note on Lightroom:** Adobe's Lightroom API requires an Adobe technology partnership
> and is not publicly accessible. v0.3 integration targets are Canva (public API,
> 150M MAU) and Cloudinary (accessible REST API).

---

## Contributing

See [CLAUDE.md](CLAUDE.md) for the full architecture guide and development rules.
See [PRD.md](PRD.md) for the full product requirements and strategy.
See [COMPETITORS.md](COMPETITORS.md) for the competitive landscape.

Built with [Anthropic Claude](https://anthropic.com) · [Streamlit](https://streamlit.io) · [FastMCP](https://github.com/jlowin/fastmcp) · [Pillow](https://python-pillow.org)
