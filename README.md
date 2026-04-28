# Stil ✦

**Your creative style, remembered.**

Stil is a conversational AI assistant for content creators and brand designers.
Upload a photo, describe what you want, and Stil executes it — then remembers your
choices so the next session already knows your aesthetic. No re-explaining. Ever.

---

## The problem

A creator posts 3–5 times a week. That is 200+ pieces of content a year.

Here is what every editing session looks like today, regardless of which tool they open:

1. Open Lightroom, Canva, or any AI assistant
2. Apply your warm filter — *again*
3. Crop to square for Instagram — *again*
4. Set export to 1080×1080, JPEG, sRGB — *again*
5. Bump brightness +20 — *again*
6. Repeat for every photo, every session, every tool

None of these are creative decisions. They were made months ago.
But every tool starts from scratch because no tool holds the memory.

**This compounds into a bigger problem: visual drift.**
Post 1 looks like the creator. Post 47 sort of does. Post 180 barely does — not because
the aesthetic changed, but because 200 micro-decisions made under time pressure, across
three different tools, at varying energy levels, slowly diverge from the original intent.

The creator does not notice it happening turn by turn. They notice it six months later
when their feed no longer looks like theirs.

**The real problem is not re-explanation overhead. It is consistency at volume.**

---

## Why existing solutions don't solve it

This is where it gets important. A lot of teams are building "memory" features right now.
ChatGPT Memories, Claude Projects, Notion AI, Adobe Brand Kits, Lightroom presets.
They all store preferences. None of them solve consistency.

Here is why:

| | Today's editing tools | "Memory" features (most AI tools) | Stil |
|---|---|---|---|
| **What gets stored** | Nothing | What you *say* ("I like warm filters") | What you *do* (`apply_filter("warm")` from actual tool call) |
| **How it learns** | Doesn't | You configure it / tell it | Reads every tool call after every session |
| **Updates automatically** | No | No — you re-brief it when things change | Yes — after every session, from behavior |
| **Handles changed preferences** | — | You have to explicitly update it | Choices log always reflects the most recent action |
| **Detects feed inconsistency** | No | No | Yes — Feed Cohesion Score quantifies drift across your photos |
| **Grades creative intent** | No | No | Yes — sessions scored on whether the output served the actual creative goal |
| **Source of truth** | None | Your stated preferences | Your demonstrated editing behavior |

**The critical distinction:** A memory feature that stores "user likes warm filters"
is a sophisticated preset. It still requires you to declare your preference, and it does
not update unless you tell it to. If you switch to dramatic filters across the next ten
edits, the memory still "knows" you like warm.

Stil's choices log captures what you actually did — not what you said.
Every tool call (`apply_filter`, `crop_image`, `set_export_preset`) writes to the log
directly from the API response. The most recent edit always wins.
If you changed your mind, the system changes with you — automatically, from behavior,
without re-briefing.

**Where the intelligence comes from:**

1. **Behavioral ground truth** — the choices log records actual tool calls, not stated preferences
2. **AI-extracted intent** — after each session, Haiku reads the conversation and extracts higher-order patterns that don't surface from tool calls alone
3. **Priority ordering** — the system prompt always injects `choices_log` first, `style_signature` second; behavior beats declaration
4. **Drift detection** — Feed Cohesion Score gives a number (0–100) for something creators previously had no way to measure: "is my feed actually consistent?"
5. **Creative intent grading** — sessions scored not on task completion but on whether the output served the creative goal; this is the signal for whether style injection is working

---

## What Stil does

| Feature | What it means for you |
|---|---|
| **Conversational editing** | Say "make this warmer and crop it square" — Stil picks the right tools and runs them. No menus, no presets. |
| **Behavioral memory** | Stil saves what you *do*, not what you say. Every tool call is logged. Next session, your style is injected automatically — before you type anything. |
| **Real image preview** | Before/after preview appears after every edit. Filters, brightness, contrast, and crop rendered by real Pillow image processing. |
| **Choices log** | Every filter, crop, brightness, and export choice is logged from actual tool calls. Most recent entry wins. If you change your mind, the system changes with you — no re-briefing. |
| **Style Active banner** | Every return session shows exactly which preferences are loaded (warm · square · instagram) before you type a word. The memory loop is visible. |
| **Feed Cohesion Score** | Upload photos from your grid. Get a 0–100 consistency score across color temperature, brightness, contrast, and saturation — with specific issues and a suggested fix. |
| **Style Transfer** | Upload any reference photo (competitor shot, mood board, editorial). Stil extracts its visual style and applies it to your photo in seconds. |
| **Brief-to-Edit Translator** | Paste a creative direction ("moody editorial, cool tones, portrait for instagram"). Stil generates a structured edit plan you can send directly to the editor. |
| **Client Brand Switcher** | Save named style profiles ("Summer campaign", "Brand B"). Switch between clients or campaigns with one click — no re-briefing. |
| **Camera profile (EXIF)** | Stil reads camera model, focal length, ISO, and aperture from image metadata. High-ISO shots get noise-aware suggestions automatically. |
| **Quality insights** | Sessions graded on tool accuracy, goal completion, and creative intent. The trend chart shows whether your profile is actually improving output over time. |
| **Smart asset search** | Describe what you need in plain English. Stil scores your library by keyword match and AI-generated tags. |

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
2. Fill in the **style seed card** — tone, platform, and one word for your aesthetic
   (e.g. "moody"). Seeds your profile before any conversation so session 1 is already personalised.
3. Upload a photo — Stil reads your dominant color palette and camera EXIF automatically
4. Type what you want: *"Apply a warm filter, bump brightness +20, crop square, export for Instagram"*
5. Watch the tool pills fire in real time as each action executes
6. A **before/after preview** appears showing the actual edit on your photo
7. A **✓ Style profile updated** confirmation appears — you can see the memory loop working
8. Your choices are saved to the sidebar — the style profile is live

### Every session after — no re-explanation needed

1. Upload a new photo
2. You will see a **✦ Style active** banner listing your remembered preferences — warm · square · instagram — before you type anything
3. Type: *"Edit my photo"* — that is all
4. Stil reads the choices log and applies your full aesthetic without being asked
5. Before/after preview shows the result

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

**The key architectural decision: Stil stores what you do, not what you say.**

```
You upload a photo and type: "Make it warmer, crop square, export for Instagram"
        ↓
Stil executes: apply_filter("warm") → crop_image("square") → set_export_preset("instagram")
        ↓
Two things happen in parallel:

  1. choices_log updated — deterministic, from tool calls directly
     apply_filter("warm")          → logs  filter: warm
     crop_image("square")          → logs  crop: square
     set_export_preset("instagram") → logs  export: instagram

     Most recent entry always wins. No AI involved. This is the ground truth.

  2. style_signature updated — AI-extracted
     Haiku reads the conversation and extracts tone, aesthetic intent,
     platform preferences — things that don't surface from tool calls alone.
     Example: "prefers clean, editorial warmth; avoids heavy vignettes."

Next session:
  You open Stil with a new photo.
  The system prompt already contains:
    "Preferred filter: warm (last used)"
    "Crop: square (last used)"
    "Export for: instagram (last used)"

  You type: "Edit my photo."
  Stil applies your full style without being asked.
```

**What this means when your preferences change:**
You switch to a cool filter this session. The choices_log updates immediately —
`filter: cool` becomes the new first entry. The next session's system prompt
reflects cool. You never had to say "I've changed my filter preference."

This is why the choices log is the ground truth — not the AI-extracted signature,
not what you said in any previous conversation. What you did last time, wins.

---

## Editing tools available

| Tool | What it does |
|---|---|
| `apply_filter` | warm, cool, vintage, dramatic, soft, vivid, bw |
| `adjust_brightness` | −100 (darker) to +100 (brighter) |
| `adjust_contrast` | −100 (flat) to +100 (high contrast) |
| `crop_image` | square, portrait, landscape, story, tiktok, reels, wide |
| `set_export_preset` | instagram, tiktok, reels, twitter, linkedin, web, print |
| `list_layers` | inspect the layer stack |

All visual edits produce a real before/after preview using Pillow image processing.
Color palette and EXIF extraction also use Pillow — zero additional API calls.

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
