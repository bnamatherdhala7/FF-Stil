# Stil — Product Requirements Document

**Version:** 0.2 (revised)
**Status:** Working draft
**Last updated:** April 2026

---

## 0. The product bet in one paragraph

Stil bets that visual style — the aesthetic a creator has spent months or years
developing — is valuable enough to persist, portable enough to live outside any
single tool, and learnable enough to extract from natural conversation. If that
bet is right, Stil becomes the memory and intelligence layer that sits above
Lightroom, Canva, CapCut, and every other tool a creator uses. If it's wrong,
we'll know quickly: users won't return, style profiles will stay empty, and
the creative intent score in Insights will be flat.

This document explains the problem, the competitive gap, why this solution is
the right bet, and what we need to build and learn in v0.1.

---

## 1. Problem

### 1.1 Who we're building for

Content creators and brand designers who produce visual content for social media
professionally or semi-professionally. They post 3–5 times per week across
Instagram, TikTok, LinkedIn, and YouTube. They have a distinct visual identity —
specific colour palettes, tonal preferences, crop ratios, export formats — that
they've developed over months or years. They are not hobbyists. This is either
their livelihood or a serious side income.

There are **207 million content creators globally**. The creator economy is
valued at **$205–254 billion in 2025**, growing at ~23% CAGR toward $1.35T
by 2035 (Grand View Research, Precedence Research). Photography and videography
represents the largest creative service segment. Individual creators are the
largest end-user segment at 58.7% of the market. **87% of creators now use AI
in their creative workflows** (Artlist, 2025, n=6,500).

### 1.2 The specific frustration we're solving

The frustration is not "editing is slow." Good editing tools exist. The
frustration is **re-explanation overhead** — having to re-specify the same
creative decisions in every tool, every session, every time.

Concrete example: a creator with a warm, high-contrast, square-cropped Instagram
aesthetic has to:
- Set their Lightroom preset every import
- Re-select their Canva brand colours every project
- Re-enter their Instagram export dimensions every time
- Re-explain their style to every AI tool they try

The preferences are known. They've been decided. The tools just don't remember.

**46% of a creator's working time is spent on tasks other than content creation**
— formatting, distribution, and repetitive technical decisions they've already
made. Re-explaining style to AI tools is a measurable fraction of this overhead.

### 1.3 Why this problem is hard to solve with existing tools

See [COMPETITORS.md](COMPETITORS.md) for the full breakdown. The short version:

**Tools that learn style (Imagen AI, Aftershoot):**
- Require Lightroom — locked to one tool
- Need 2,500–5,000 past edited images to train — useless for new or casual users
- No conversational interface — batch processing only
- Built for professional photographers, not social media content creators

**Tools that hold brand memory (Typeface, Jasper, Adobe Firefly Style Kits):**
- Enterprise pricing: $49–$500+/month
- Require manual setup of a brand asset library
- Don't learn from usage — you configure them, they don't evolve
- Locked inside their own ecosystem

**Tools that are conversational (ChatGPT, Claude):**
- Stateless — forget everything at session end
- No editing tool integrations — advise but can't execute
- General-purpose memory where available, not visual-style-specific

**The gap:** No tool at individual creator pricing ($10–20/month) combines
persistent cross-session visual style memory + conversational interface +
works from day one without a training data library.

### 1.4 Market size

**TAM:** Creator economy $205B (2025) → $1.35T (2035) at 23% CAGR.
AI image editing tools: $5.1–6.3B (2025) → $39.7B by 2030 at ~39% CAGR
(Virtue Market Research, Market Research Future).

**SAM:** Individual creators + small brand teams using AI tools for social media
visuals. ~45 million professional creators globally; 87% already use AI in
their workflow. Estimated $750M–$1B of the AI editing market in 2025, growing
toward $6–8B by 2030.

**SOM (Year 1):** 0.1% of 45M professional creators = 45,000 users.
At $15/month = **$8.1M ARR**. Achievable with strong product-market fit
in the Instagram/TikTok creator segment.

---

## 2. The solution hypothesis

### 2.1 Core thesis

Visual style is **portable knowledge**. It doesn't belong to Lightroom or Canva
or any specific tool. It belongs to the creator. Stil is where that knowledge
lives — a style profile that updates with every session and can inform any tool
in the creator's workflow.

The v0.1 prototype tests whether this knowledge can be:
1. **Extracted** from natural conversation (does style extraction actually capture real preferences?)
2. **Persisted** meaningfully across sessions (does returning users see fewer re-explanations?)
3. **Applied** to produce better outputs (does injecting style into the system prompt move creative intent scores?)

If all three are true, the case for real tool integrations (v0.3) is validated.

### 2.2 Why conversational is the right interface

The alternatives — form-based onboarding, preset selectors, manual brand kit setup —
all put the burden of articulation on the user upfront. Most creators can't
fully articulate their style in a questionnaire. They know it when they see it.

A conversational interface solves this in two ways:
1. **Reactive learning**: Stil extracts preferences from what users do and say
   naturally, without asking them to describe their aesthetic in abstract terms.
2. **Low friction**: "Make this warmer and crop it square" is how creators already
   think. Translating that into a Lightroom preset menu is the friction we're removing.

### 2.3 Why this is the right time

Three things have changed in 2024–2025 that make this viable now:
1. **Claude Haiku** makes per-session AI cheap enough to stay well under $0.05/user/day
2. **Multimodal models** can actually see images and understand aesthetic quality,
   not just metadata
3. **MCP (Model Context Protocol)** gives a standard way to connect AI memory
   to real editing tools — the v0.3 integration path exists now

### 2.4 The risks and honest answers

**Risk: Style profile is too shallow to be useful**
Real test: do users who come back for a second session have to re-explain less?
If the creative intent score doesn't improve between session 1 and session 3
for the same user, the extraction isn't working.

**Risk: Users don't trust AI to know their style**
Mitigation: make the profile completely transparent and editable at all times.
Users see exactly what Stil thinks they like. They can correct it. This builds
trust through visibility, not through hidden magic.

**Risk: v0.1 has no real pixel editing — is this a toy?**
Honest answer: yes, for now. The v0.1 prototype is a concept validator, not a
shipping product. The question it's answering is: "does persistent style memory
in a conversational interface create value for creators?" If yes, the real
integrations (Lightroom API, Canva API) are the v0.3 investment.

**Risk: Canva adds style memory to their product**
Canva has 150M+ MAU and could ship "conversational style memory" in a quarter
if they decided to. Their moat-breaker would be distribution, not technology.
Stil's response: move faster, go deeper on creator-specific style signals,
and build the multi-tool portability that Canva structurally can't offer
(they won't build memory that feeds into Lightroom).

**Risk: Adobe ships this inside Creative Cloud**
Adobe's Style Kits (Firefly) are static, require 20+ images, and are locked
inside CC. Building true conversational style learning would cannibalise their
preset/plugin ecosystem. They'll be slow here. But if they ship it, the
response is the same: portability across tools Adobe doesn't own.

---

## 3. Target personas

### Persona 1 — The Solo Creator (primary)
- Posts 3–5x/week on Instagram and TikTok
- Has a recognisable aesthetic: warm tones, square crops, minimal text overlays
- Uses Lightroom for serious edits, Canva for quick social posts
- **Job to be done:** Apply my aesthetic without re-explaining it every time
- **Quote:** "I've told it I like warm tones a hundred times."
- **Success:** "It just knows what I want now."

### Persona 2 — The Freelance Brand Designer (secondary)
- Manages 3–5 client brand accounts simultaneously
- Each brand has distinct colours, fonts, platform presets
- **Job to be done:** Switch between client brand contexts without constant re-briefing
- **Quote:** "I brief it once per brand, and it stays on-brand forever."

### Persona 3 — The Small Business Owner (tertiary)
- Runs an e-commerce brand or local service business
- Not a designer. Posts on Instagram to drive sales.
- **Job to be done:** My social posts should look like my brand, not like a generic AI
- **Success:** "It actually looks like us."

---

## 4. MVP scope — v0.1

### Built and shipped

**Style profile — two-layer memory**
- `style_profile.json` with two components:
  1. `choices_log` — deterministic, written directly from tool calls (ground truth). Every `apply_filter`, `crop_image`, `set_export_preset`, `adjust_brightness` call is logged with a timestamp. Most recent entry wins in system prompt injection.
  2. `style_signature` — AI-extracted from session conversation text. Captures tone, aesthetic mood, notes that don't surface from tool calls alone.
- Priority in system prompt: choices_log > style_signature
- Visible in Style tab as metric cards + choices log bar in sidebar (last 5 sessions)
- Clear memory button resets completely

**Conversational editing with vision**
- Natural language input + optional image upload (multimodal)
- Image persists across all turns in a session — upload once, reference across the conversation
- Agent selects and runs editing tools: apply_filter, adjust_brightness,
  crop_image, set_export_preset, list_layers
- Real-time tool execution trace (streaming UI with firing/done pills)
- Images automatically compressed to stay within Anthropic 5MB limit (Pillow)
- Full Claude API conversation history passed across turns — no context loss
- Style preferences injected into system prompt for returning users

**Smart asset search**
- Natural language brief → ranked asset recommendations
- AI tags generated and cached per filename (never re-tagged)
- Results with thumbnails, tags, and rationale

**Quality insights**
- Sessions graded on: tool accuracy, goal completion, creative intent (each 1–5)
- Bar chart per turn, aggregate scores, plain-language health summary
- The creative intent dimension is the signal that matters — a session can score
  5 on task completion and 1 on creative intent (did exactly what was typed,
  missed what the user actually wanted)

### Out of scope for v0.1
- Real pixel-level image processing (requires Lightroom/Photoshop API)
- Video editing
- Multi-user / team accounts
- Cloud sync or mobile app
- Direct social media publishing
- Generative image creation

### Key v0.1 technical note: Lightroom integration
The roadmap references Lightroom as a v0.3 target. Adobe's Lightroom API is
**not publicly accessible** — it requires Adobe technology partnership. Any
Lightroom integration path depends on Adobe internal access, not engineering
effort. The realistic v0.3 integration targets are **Canva Apps SDK** (150M MAU,
public API, app marketplace) and **Cloudinary** (accessible REST API). Canva
is also the distribution channel — not just an integration target.

---

## 5. What v0.1 needs to validate

Before investing in v0.2/v0.3 (real integrations, video), v0.1 needs to answer:

| Question | How to measure |
|---|---|
| Does style extraction actually capture real preferences? | Style profile has ≥3 populated fields after 2 sessions |
| Do returning users re-explain less? | Session re-explanation rate < 15% by session 3 |
| Does style injection improve output quality? | Creative intent score improves from session 1 → session 3 |
| Is the conversational interface the right UX? | Session length 4–6 turns; D7 retention > 40% |
| Is $15/month a sensible price? | Willingness to pay survey + conversion on free trial |

---

## 6. Technical architecture

### Stack
- **Language:** Python 3.11+
- **UI:** Streamlit (localhost:8501)
- **AI runtime:** Anthropic API — `claude-haiku-4-5` for all tasks
- **Vision:** Multimodal messages (base64 image + text) with automatic compression
- **Asset server:** MCP protocol via FastMCP Python SDK
- **Storage:** Flat files (JSON, JSONL) — no database for v0.1

### Cost model

| Task | Model | Cost estimate |
|---|---|---|
| Agent loop (per session) | claude-haiku-4-5 | ~$0.01 |
| Style extraction (per session) | claude-haiku-4-5 | ~$0.002 |
| Asset tagging (one-time per image) | claude-haiku-4-5 | ~$0.001 |
| Insights grading (per turn) | claude-haiku-4-5 | ~$0.003 |

**Target: < $0.05 per active user per day.**
At $15/month subscription (~$0.50/day), gross margin is ~$14.50/user/month
before infrastructure. Strong unit economics if retention is solid.

---

## 7. Success metrics

### Primary (product quality)
- **Creative intent score ≥ 4.0/5.0** — Stil serves what users actually want
- **Style retention rate > 70%** — returning users whose profile was updated ≥ once in first week
- **Session re-explanation rate < 10%** — users not re-specifying already-known preferences

### Secondary (engagement)
- D7 retention: > 40%
- Sessions per week per active user: > 3
- Average session length: 4–6 turns

### Guardrails
- API cost per user per day: < $0.10
- Style extraction failure rate: < 5%
- Tool call accuracy (from insights): > 4.0/5.0

---

## 8. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Style profile too shallow to be useful | Medium | High | Richer extraction prompt; active extraction after every session; show profile transparently so users can correct it |
| Users don't trust AI to know their style | Medium | Medium | Full transparency — show raw profile; make it editable at all times |
| API costs exceed margins at scale | Low | High | Haiku model; caching; 6-turn session cap |
| Canva ships conversational style memory | Medium | High | Speed to market; multi-tool portability they can't offer; deeper creator-specific style signals |
| Adobe ships this in Creative Cloud | Low–Medium | High | Portability across tools Adobe doesn't own is structural differentiator |
| Style extraction hallucination | Low | Medium | Merge-not-overwrite strategy; user can review and edit profile |
| v0.1 feels like a toy without real editing | High | Medium | Clear framing as prototype/validator; focus on demonstrating the memory loop, not pixel editing |

---

## 9. Roadmap

### v0.1 — Concept validator (now)
Local Streamlit prototype. Style memory loop end-to-end. Multimodal vision.
Asset search. Quality insights. Validates the core thesis before investing
in real integrations.

### v0.2 — Richer style model
Deepen the style profile: colour palette extraction from uploaded images,
platform-specific crop/export preferences, aesthetic mood tags (editorial,
lifestyle, minimalist, etc.). Better onboarding flow to seed the profile
faster on session 1.

### v0.3 — Real tool integrations
Canva Apps SDK is the primary target: 150M MAU, public API, and a marketplace
that solves the distribution problem. A Stil Canva App puts style memory in
front of the platform creators already use daily.
Cloudinary as secondary: accessible REST API, real image transformations.
Lightroom requires Adobe technology partnership — not a v0.3 engineering task.

### v0.4 — Multi-brand support
Multiple style profiles per user. Switch between client brand contexts.
Primary target: freelance designers managing 3–5 client accounts.

### v0.5 — Web app + mobile
Hosted web app. Mobile-first UI for editing on the go.
Requires moving from flat-file storage to a proper database + auth layer.

---

## 10. Open questions

1. **Onboarding depth vs. friction:** How much do we ask upfront vs. let the
   profile build from usage? More upfront = better day-1 output quality but
   higher abandonment. Current hypothesis: ask for tone and primary platform
   only; let everything else emerge from sessions.

2. **Multi-tool portability:** v0.1 is standalone. But the real value of Stil's
   style profile is that it could inform any tool. How do we surface this before
   real integrations exist? Export as a "style brief" PDF? API endpoint?

3. **Asset library scope:** v0.1 assumes a local folder. Real creators store
   images in Google Photos, iCloud, Lightroom. Cloud integrations are a
   prerequisite for the product to be genuinely useful at v0.3+.

4. **Pricing model:** $15/month flat subscription vs. usage-based. At <$0.05/day
   cost, flat subscription has strong margins. Usage-based lowers barrier for
   casual users but complicates messaging. Current lean: flat subscription with
   a 7-day free trial, no credit card required.

5. **Platform focus:** Instagram-first vs. platform-agnostic? Instagram-first
   simplifies presets, messaging, and the export preset defaults in creative_tools.py.
   But TikTok is the faster-growing platform for the core creator persona.
   Current position: both, with Instagram as the primary example in all UX copy.
