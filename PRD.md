# Stil — Product Requirements Document
### A working prototype for conversational agentic experiences in creative workflows

**Version:** 1.0 (VP review)
**Status:** Active · Prototype shipped
**Last updated:** May 2026

---

## Executive Summary

Creative professionals repeat the same editing decisions hundreds of times per year. They re-specify the same filter, the same crop, the same export format in every session across every tool — not because these are creative decisions, but because no tool holds the memory. The result is not just wasted time. It is visual drift: slow, invisible degradation of feed consistency that creators only notice six months later.

Stil is a working prototype of a conversational AI assistant that solves this by learning from what creators *do*, not what they *say*. It executes editing actions through an agentic loop, records every tool call as behavioral ground truth, and injects that profile automatically into the next session. It also ships the first prototype of a creative intent eval system — grading not just whether a task was completed, but whether the output served what the creator actually wanted.

The deeper purpose of this prototype is to validate the architectural decisions that a production agentic harness for creative professionals will need to make. Every design choice in Stil — how memory is layered, how evals are structured, how the prompt is injected — maps to a requirement for a unified agentic experience at scale. This document explains those decisions, what they validate, and where they lead.

---

## 1. Strategic Context — Why This Matters Now

### 1.1 Adobe's agentic bet

Adobe is investing in agentic AI experiences across Firefly, Express, and Creative Cloud. The central hypothesis is that agents — systems that reason, call tools, and loop until complete — will replace single-turn AI assistance for creative professionals. This is the right bet.

But agentic experiences in creative workflows face a problem that text-based agents do not: **visual consistency**. A writing agent that forgets context produces a slightly worse paragraph. A creative agent that forgets context produces a feed that no longer looks like the creator's brand. The stakes are different because the output is cumulative and visible.

Stil was built to prototype the answer to a specific question: **What does a production agentic harness need to get right for creative memory, prompt architecture, evals, and telemetry to actually serve creators?**

### 1.2 The Firefly Agentic opportunity

FF Agentic sits at the intersection of three converging forces:

- **207 million content creators globally**, 87% already using AI tools (Artlist, 2025, n=6,500)
- **AI image editing growing at 39% CAGR** — $5.1B (2025) → $39.7B (2030)
- **No tool at creator pricing** currently combines persistent cross-session style memory + conversational execution + real image feedback that works from day one

The opportunity is not to build another AI editing tool. It is to establish Adobe as the platform where a creator's visual style is a persistent, portable asset — one that travels across Firefly, Express, Lightroom, and Canva, and compounds with every editing session.

### 1.3 What this prototype demonstrates

Stil ships a working end-to-end agentic loop with style memory, real image processing, platform export previews, feed consistency scoring, and a creative intent eval system. It is a proof of concept built in weeks, not months — demonstrating the builder's approach: prototype first, learn through shipping, iterate on evidence.

The prototype answers:
- Can behavioral memory (from tool calls) outperform declared memory (from user statements)?
- Can creative intent be graded separately from task completion — and does the distinction matter?
- Can a conversational interface handle complex multi-step creative workflows without user re-briefing?

All three: yes.

---

## 2. Research Foundation

### 2.1 Qualitative signals — creator workflow research

The core problem was identified through qualitative research with content creators across Instagram, TikTok, and LinkedIn-first workflows, combined with public creator discourse on Reddit, YouTube, and photography communities. Key findings:

**"I've told every AI tool I like warm tones. None of them remember."**
— Recurring verbatim across creator interviews. Stateless AI assistance creates invisible overhead: not the 30 seconds of re-specifying preferences, but the cognitive load of tracking which tool knows what and catching drift before it reaches the feed.

**"I only notice my feed is inconsistent six months later, when I scroll back."**
— Visual drift is invisible in the moment and painful in retrospect. Creators have no real-time signal for feed consistency. They track it manually, irregularly, and subjectively.

**"I can't explain my aesthetic. I know it when I see it."**
— The most common failure mode of preset-based and form-based style configuration. Creators cannot fully articulate their visual preferences in abstract terms upfront. They can confirm or correct what they see. This insight drove the conversational, reactive learning design over form-based onboarding.

**Supporting signals from public creator discourse:**

> *"Every time you start a new conversation with AI, it forgets everything from the last conversation. You're constantly re-explaining your brand, re-correcting the same mistakes, and getting inconsistent output."*
> — Creator productivity research, 2025

> *"We spend more time editing AI content to match our voice than it would take to write from scratch. We keep making the same edits over and over because the AI doesn't learn."*
> — Creator brand consistency research, 2025

> *"I'm no longer starting from scratch because [AI editing] is simply using pattern recognition based on how I've already edited."*
> — Photographer reviewing AI editing tool, 2024 *(This is the expectation Stil's behavioral memory is built to deliver.)*

> *"That 'warm and moody' preset… you end up spending more time tweaking sliders than you would have if you just started from scratch."*
> — Lightroom preset failure analysis, signatureedits.com

> *"Surveys have said that photographers report that over 50% of their working hours are spent on editing alone."*
> — Photographer workflow research, 2024

**The pattern across all sources:** The phrase "starting from scratch" appears verbatim across AI tool reviews, Lightroom forums, and creator strategy content. It is the single most common vocabulary creators use to describe this pain. "Stateless" has entered mainstream creator discourse as the named cause. The problem is not speed — it is that the tool has no memory of the creator.

**Three creator archetypes with distinct needs:**

| Archetype | Volume | Primary pain | Current tools |
|---|---|---|---|
| Solo Creator | 3–5 posts/week, 200+/year | Re-explaining style every session | Lightroom + Canva + CapCut |
| Freelance Brand Designer | 3–5 client accounts | Context-switching between brand voices | Canva + Adobe CC |
| Small Business Owner | 1–3 posts/week | Consistency without design skills | Canva, CapCut |

### 2.2 Quantitative signals — the scale of the problem

- **200+ editing decisions per creator per year** that are not creative choices — they are re-execution of already-decided preferences
- **46% of creator working time** goes to non-creative tasks: formatting, distribution, repetitive re-entry (creator economy research, 2024–2025)
- **87% of creators already use AI** in their workflows — adoption is not the barrier; consistency enforcement is
- **Creator economy: $205–254B (2025) → $1.35T (2035)** at 23% CAGR — the size of the market makes even a small consistency improvement commercially meaningful
- **AI image editing TAM: $5.1B → $39.7B** at 39% CAGR through 2030

### 2.3 Research-driven design decisions

Each major design decision in Stil traces back to a specific research finding:

| Finding | Design decision | Where it lives |
|---|---|---|
| Creators can't articulate style upfront | Reactive learning from tool calls, not form | choices_log written from API responses |
| Drift is invisible in the moment | Objective consistency measurement | Feed Cohesion Score (0–100) |
| Task completion ≠ creative intent | Separate eval dimension for creative goal | creative_intent rubric in insights.py |
| No tool survives context switch | Behavioral memory beats declared memory | choices_log priority over style_signature |
| Creators need to trust the system | Full profile transparency + editability | Style tab: all fields editable, raw JSON visible |

---

## 3. The Problem

> **The one sentence:** Every creative editing tool starts from zero every session — no tool holds the memory of what you chose last time, so creators repeat the same decisions hundreds of times a year and slowly drift from their own aesthetic without noticing.

### 3.1 Who this is for

Content creators and brand designers who produce visual content professionally or semi-professionally. They post 3–5 times per week across Instagram, TikTok, and LinkedIn. They have a distinct visual aesthetic — specific colour temperatures, crop ratios, export formats — developed over months or years. This is either their livelihood or a serious side income.

**207 million content creators globally.** The creator economy is valued at $205–254B in 2025, growing at ~23% CAGR toward $1.35T by 2035. 87% of creators already use AI in their workflows (Artlist, 2025, n=6,500).

### 3.2 The specific problem with image editing today

A creator posts 3–5 times a week. That is 200+ pieces of content a year. Here is what every editing session looks like, regardless of which tool they open:

1. **Open their tool** — Lightroom, Canva, CapCut, or an AI assistant
2. **Re-select the warm filter** — the same one they chose last time
3. **Re-crop to square** — every portrait needs this for Instagram
4. **Re-enter export settings** — 1080×1080, JPEG, sRGB, 85% quality
5. **Re-adjust brightness** — they always go +20 for their style
6. **Repeat for every photo, every session, every tool**

None of these are creative decisions. They were made months ago. But every tool starts from zero because no tool holds the memory.

**This is not an editing speed problem. It is a consistency problem.**

The deeper consequence is visual drift. Post 1 looks exactly like the creator. Post 47 is close. Post 180 barely is — not because their aesthetic changed, but because 200 micro-decisions made under time pressure, across three different tools, with varying energy levels, slowly diverge from the original creative intent. The creator does not notice it happening turn by turn. They notice it six months later when their feed no longer looks like theirs.

**46% of a creator's working time goes to tasks other than content creation** — formatting, distribution, and exactly this kind of repetitive technical re-entry.

### 3.3 Why existing tools do not solve this

**Tools that learn style (Imagen AI, Aftershoot):**
- Require Lightroom — locked to one tool
- Need 2,500–5,000 past edited images to train — inaccessible for most creators
- Batch processing only, no conversational interface
- Built for professional photographers, not social creators

**Tools that hold brand memory (Typeface, Jasper, Adobe Firefly Style Kits):**
- Enterprise pricing: $49–$500+/month
- Manual setup — you configure them, they do not learn from usage
- Locked inside their own ecosystems
- No image editing capability

**Tools that are conversational (ChatGPT, Claude, Gemini):**
- Stateless by default — forget everything at session end
- Cannot execute editing actions — they advise, they do not do
- General-purpose memory, not visual-style-specific
- No before/after preview of any edit

**The gap:** No tool at individual creator pricing ($10–20/month) combines persistent cross-session visual style memory + conversational execution + real image feedback + works from day one without a training data library.

### 3.4 What Skills and memory features do — and exactly what they miss

Every major AI platform is now shipping memory. ChatGPT Memories, Claude Projects, Notion AI, Gemini context. Adobe has Brand Kits, Style Presets, Lightroom presets. These are real features. They genuinely reduce the re-explanation burden. But they do not solve consistency — and it is worth being precise about why.

**What a skill or memory feature does:**
- Stores a declaration: *"I prefer warm tones"*
- Injects that declaration into future sessions as context
- Reduces the time spent re-explaining preferences from scratch

**What a skill or memory feature does not do:**
- Detect that you have been using cool tones for the past 20 sessions while the stored preference still says "warm"
- Update automatically when behavior changes — you must go back and edit the memory yourself
- Grade whether the output actually served your creative intent, vs. just completing the stated task
- Measure whether your feed is drifting from its original aesthetic over time

**The declaration trap:**
A skill that holds "user likes warm filters" is a sophisticated preset. When you said "warm" in January and have been using cool since March, the skill still confidently injects warm. No signal fires. The drift is invisible. You re-brief it manually when you notice — by which point the damage to feed consistency is already done.

**Memory features store what you say. Stil stores what you do.**

| Dimension | Skill / memory feature | Stil |
|---|---|---|
| Source of truth | What you said (*declared*) | What you did (*tool call: `apply_filter("warm")`*) |
| Updates when behavior changes | No — requires manual re-briefing | Yes — choices_log updated after every session |
| Detects preference drift | No | Yes — frequency analysis: *"cool (last 3 sessions) — usual style warm (8/11 sessions)"* |
| Measures feed consistency | No | Feed Cohesion Score: 0–100 across color temp, brightness, contrast, saturation |
| Grades creative intent | No | Per session: creative_intent score separate from task completion |
| Intelligence layer | Stored declaration | Frequency-analyzed behavioral log + AI-extracted aesthetic intent |

**The gap this creates:** A creator's style naturally evolves. Seasonal campaigns, client briefs, mood shifts. Every memory system built on declarations requires the creator to *manage the memory as a second job* — tracking what changed, updating the stored preferences, catching the moments when the declared preference and actual behavior diverge. Stil's behavioral log updates automatically, because it reads the tool call, not the creator's words about the tool call.

**Two signals that no memory feature generates today:**
1. *Feed drift signal* — "Your last 8 photos show 23% brightness variance across your feed. This is where your consistency is breaking." No declared-preference system can compute this. It requires actual image analysis across real photos.
2. *Creative intent signal* — A session that scores 5/5 on task completion and 1/5 on creative intent means the tool did exactly what was typed and completely missed the creative purpose. No completion metric catches this. It requires grading intent separately from execution.

---

## 4. The Solution

### 4.1 What Stil looks like for a creator

**First session — building the profile**

> A photographer opens Stil. She uploads a portrait she just shot.
> She types: *"Make this warmer, bump brightness a bit, crop square, export for Instagram."*
>
> Stil reads the image. Four tools fire in sequence — `apply_filter("warm")`,
> `adjust_brightness(+20)`, `crop_image("square")`, `set_export_preset("instagram")`.
> A before/after preview appears. The right panel shows her edited photo cropped for
> Instagram (1:1), Reels (9:16), Twitter (16:9), and LinkedIn (4:5) — ready to export.
> A confirmation bar: *"✓ Style profile updated."*

One session. Four choices. The profile now knows her aesthetic.

**Second session — no re-explanation**

> She opens Stil the next day with a new photo.
> A banner at the top: *"✦ Style active — warm · square · instagram · built from 4 edits."*
>
> She types: *"Edit my photo."*
>
> That is all. Stil reads the choices log, applies her full style, shows the before/after
> and platform exports. She never said "warm filter." She never said "square crop."
> The system already knew.

**Ten sessions later — catching drift**

> She opens the Feed tab. Uploads 8 recent photos from her grid.
> Score: 61/100. *"Mostly consistent."*
> Issues: *"Brightness is inconsistent across your feed"* · *"Saturation varies — some vivid, others muted."*
>
> She did not notice this happening. Stil did.

### 4.2 The full loop

```
Creator uploads a photo and describes what they want
                ↓
Stil reads style_profile.json
→ injects choices_log (recent tool calls, frequency-analyzed) + style_signature
  (AI-extracted intent) into system prompt as ordered context
                ↓
Claude reasons about which tools to call, using style profile as ground truth
                ↓
apply_filter("warm") → adjust_brightness(+20) → crop_image("square")
→ set_export_preset("instagram")
                ↓
Pillow applies actual edits → before/after preview shown
→ Platform export grid: 4 crops generated (Instagram, Reels, Twitter, LinkedIn)
                ↓
Session saved to logs/session_TIMESTAMP.jsonl
                ↓
Two things happen in parallel:
  1. choices_log updated from tool calls (deterministic — no AI involved)
  2. style_signature updated by Haiku from conversation (captures intent beyond tool calls)
                ↓
Next session: warm · square · instagram already injected — before the user types anything
```

### 4.3 Why conversational is the right interface

The alternative — a form, a preset selector, a brand kit configuration screen — puts the burden of articulation on the user upfront. Most creators cannot fully describe their aesthetic in a questionnaire. They know it when they see it.

Conversational interfaces solve this in two ways:
- **Reactive learning** — Stil extracts preferences from what users do naturally, without asking them to describe their aesthetic in abstract terms
- **Low friction** — "Make this warmer and crop it square" is how creators already think. The conversation is the workflow, not an interface on top of it.

### 4.4 Transparency as a trust mechanism

The style profile is always visible in the sidebar and Style tab. Users see exactly what Stil thinks they like. They can edit any field directly — tone, crop, export targets, aesthetic notes. They can clear it entirely. Nothing is hidden.

This is deliberate. Creators will not trust a system that makes assumptions they cannot inspect or correct. Transparency is how Stil earns trust, not magic.

---

## 5. Architecture Decisions That Inform the Harness

*This section maps Stil's design decisions directly to the requirements a production agentic harness for creative workflows will need to resolve. Each decision was made intentionally and validated through the prototype.*

### 5.1 Memory — two layers, explicit priority ordering

**The decision:** Memory in Stil is not a single store. It is two layers with a defined priority:

```
Layer 1 — choices_log (behavioral ground truth)
  Source: actual tool call parameters, written directly from API response
  Update: after every session, deterministic, no AI involved
  Priority: highest — injected first into the system prompt

Layer 2 — style_signature (AI-extracted intent)
  Source: Haiku reads conversation transcript, extracts aesthetic patterns
  Update: after every session, merged (never overwritten)
  Priority: fills gaps where choices_log has no entry
```

**Why it matters for the harness:** A unified harness for creative agents needs to decide what source of truth it trusts. Declared preferences (from user settings, past conversations) drift when behavior changes. Behavioral signals (from tool calls) update automatically. The harness should expose both layers and define the priority ordering explicitly — not leave it to individual agents to resolve.

**The intelligence layer:** Stil's `build_system_prompt()` does not just use the most recent tool call. It runs frequency analysis across the choices log:
- 8/9 sessions used warm filter → "warm (8/9 sessions — consistent preference)"
- Last session used cool, dominant is warm → "cool (last session) — usual style is warm (6/9 sessions); apply cool unless user says otherwise"

This distinction — recent vs. dominant — is the difference between a system that follows the last click and one that understands the underlying preference pattern. The harness needs to expose this at the infrastructure level, not leave it to prompt engineering.

### 5.2 Prompt Architecture — token budget, injection order, priority rules

**The decision:** The system prompt in Stil is strictly budgeted and ordered:

```
Base persona + task instructions:  max 200 tokens
Style injection (choices_log):     max 60 tokens — injected first
Style injection (style_signature): max 40 tokens — fills gaps
Camera profile (EXIF context):     max 20 tokens — contextual
Total:                             < 320 tokens
```

Injection order encodes priority. The harness must define:
1. **What goes in the system prompt vs. user turn vs. tool result context**
2. **What the token budget is per memory type**
3. **Who owns the priority rules** — the harness, or each agent

**Lesson from the prototype:** When style_signature is injected without priority ordering relative to choices_log, the AI gives equal weight to stated preferences and behavioral evidence. The session quality drops because the model has no signal about which source to trust when they conflict. Priority rules must be architectural, not ad hoc.

### 5.3 Evals and Telemetry — creative intent as a first-class signal

**The decision:** Stil grades sessions on three dimensions, not one:

```
tool_accuracy:    did the agent use the right editing tools? (1–5)
goal_completion:  did it finish the task as described?      (1–5)
creative_intent:  did the output serve what was actually    (1–5)
                  wanted — not just what was typed?
```

The third dimension is the critical one. A session can score 5/5 on completion and 1/5 on intent — Stil did exactly what was typed but missed the creative purpose. A creator who says "make it pop" and receives a technically correct +40 brightness adjustment that blows out the highlights has experienced a completion without intent. The eval must capture this.

**Why this matters for the harness:**
- Task completion metrics will always look good. An agentic system that never fails to fire tools will score 5/5 on completion indefinitely.
- Creative intent is the signal that tells you whether the agent is actually serving the user — not just executing instructions.
- The trend chart (creative intent score per session over time) is the feedback signal for whether the style profile is improving output. Without this, there is no way to know if memory is working.

**Telemetry requirements derived from this prototype:**
- Every session needs a structured JSONL log: messages, tool calls, tool results
- Evals must run post-session on the log, not in real-time (to avoid latency)
- The eval model (Haiku) should be separate from the agent model — same model evaluating itself produces optimistic scores
- Trend data (session → score) is more valuable than per-turn data — the harness should surface this by default

### 5.4 Tool Architecture — what the agent can and cannot do

**The decision:** Stil's tools are defined in a structured format (Anthropic tool-use API) that separates:
- **Tool definition** (name, description, input schema) — consumed by the model
- **Tool execution** (Python function) — called by the harness
- **Tool result** (JSON) — returned to the model for next-turn reasoning

This separation is intentional. The model decides *which* tool to call and *what parameters* to pass. The harness executes the tool. The result informs the next decision. Remove the model's ability to reason about tool results and the loop collapses — it becomes a rule engine, not an agent.

**Current tools:** `apply_filter`, `adjust_brightness`, `adjust_contrast`, `crop_image`, `set_export_preset`, `list_layers`

**Harness implication:** Tool definitions should be owned by the harness, not hardcoded in each agent. A unified harness for Firefly, Express, and Lightroom would expose editing actions as a shared tool library — individual agents select from it, the harness executes, results flow back.

### 5.5 CHS (Creative History Service) — session logging as the source of eval data

**The decision:** Every session writes to `logs/session_TIMESTAMP.jsonl` — a structured record of every message, every tool call, every tool result. This is not a nice-to-have. It is the source of truth for the evals system.

```jsonl
{"type": "message", "data": {"role": "user", "content": "..."}}
{"type": "tool_call", "data": {"tool": "apply_filter", "input": {...}, "result": {...}}}
{"type": "message", "data": {"role": "assistant", "content": "..."}}
```

The insights grader reads these logs, pairs user/assistant turns, and grades each turn against the rubric. Without the log, there is no eval. Without the eval, there is no feedback loop for whether the memory system is working.

**Harness implication:** A production CHS needs to:
1. Log every agentic session at the tool-call level, not just the message level
2. Expose logs to an eval pipeline (not the agent itself)
3. Aggregate creative intent scores by user over time — this is the primary health metric for the memory system
4. Surface anomalies: sessions where completion is high but intent is low indicate prompt architecture failures, not model failures

---

## 6. Features Built — v0.1

### Core agentic editing loop

- Natural language input → agent selects and executes editing tools
- Full multimodal support: upload a photo, Stil sees it and carries context across all turns
- Images compressed to stay within model limits (auto-resize + JPEG compression)
- Real before/after preview: Pillow applies actual filter, brightness, contrast, crop
- **Platform export grid**: after every edit, the right panel shows the image cropped for Instagram (1:1), Reels (9:16), Twitter (16:9), LinkedIn (4:5) — no extra API calls, pure Pillow geometry
- Multiple image upload: same tool trace applied to all uploaded images, all previews shown
- Max 6 turns per session (cost guardrail)
- Full conversation history passed across turns — no context loss

### Editing tools

| Tool | Options |
|---|---|
| `apply_filter` | warm, cool, vintage, dramatic, soft, vivid, bw |
| `adjust_brightness` | −100 to +100 |
| `adjust_contrast` | −100 to +100 |
| `crop_image` | square, portrait, landscape, story, tiktok, reels, wide |
| `set_export_preset` | instagram, tiktok, reels, twitter, linkedin, web, print |
| `list_layers` | layer stack inspection |

### Style memory

- Two-layer profile: choices_log (deterministic, from tool calls) + style_signature (AI-extracted)
- Frequency analysis across the log — dominant preference vs. recent divergence, both surfaced
- Priority in system prompt: choices_log → style_signature → camera context
- Color palette: Pillow extracts dominant colors from uploaded images, stored and shown as swatches
- Camera profile: EXIF metadata (camera, focal length, aperture, ISO) injected as context
  — high-ISO shots receive noise-aware editing suggestions automatically

### Quality insights and evals

- Sessions graded: tool accuracy, goal completion, creative intent (each 1–5, via Haiku)
- Bar chart per turn, aggregate scores per dimension, plain-English health summary
- Session trend chart: creative intent score over time — the primary validation metric
- `creative_intent` is the dimension that matters: task completion and creative intent
  are measured separately because they diverge in practice

### Feed Cohesion Score

- Upload 3–10 photos from a creator's feed
- Stil measures color temperature, brightness, contrast, and saturation variance across all photos
- Returns a 0–100 consistency score, identifies which dimensions are breaking cohesion,
  and recommends a specific fix
- Pure Pillow math — zero API calls, zero cost

### Style Transfer

- Upload a reference photo (competitor, mood board, editorial)
- Stil extracts its visual fingerprint (filter type, brightness delta, contrast delta, tone)
- Applies the extracted style to a target photo using the same Pillow pipeline
- Before/after shown side by side

### Brief-to-Edit Translator

- Paste a creative direction in plain English
- One Haiku call translates it into a structured edit plan (filter, brightness, contrast, crop, platform)
- Edit plan shown as pills; "Send to editor" fires it directly into the agent

### Client Brand Switcher

- Save named style profiles: "Summer campaign," "Brand B," "Editorial Q2"
- Load any saved profile in one click — full choices_log and style_signature restored
- Target: freelance designers managing multiple client accounts simultaneously

### Smart asset search

- Natural language brief → ranked asset recommendations from local library
- AI tags generated and cached per filename — never re-tagged (no repeat API costs)
- Results with thumbnails, tag pills, and rationale for each match

---

## 7. What This Prototype Validates

| Hypothesis | How it's tested | Signal |
|---|---|---|
| Behavioral memory outperforms declared memory | choices_log (tool calls) vs style_signature (stated) — priority ordering tested across sessions | Session re-explanation rate in return sessions |
| Creative intent is gradeable separately from task completion | 3-dimension rubric with creative_intent as distinct axis | Divergence between goal_completion and creative_intent scores |
| Frequency analysis produces smarter injection than recency alone | build_system_prompt() surfaces dominant vs. recent signal | Qualitative session quality with consistent vs. diverging preferences |
| Feed consistency is measurable and actionable | Feed Cohesion Score with dimension breakdown and suggested fix | Score accuracy vs. creator's subjective feed perception |
| Conversational interface works for complex multi-step creative workflows | Full session logs, turn count, re-briefing rate | Session length 4–6 turns; D7 retention > 40% |
| < $0.05/user/day is achievable at product quality | Haiku for all AI tasks; Pillow for all image processing | Actual API cost per session from logs |

---

## 8. Target Creators

### Persona 1 — The Solo Creator (primary)
- Posts 3–5×/week on Instagram and TikTok
- Has a recognisable aesthetic: warm tones, square crops, minimal overlays
- Uses Lightroom for serious edits, Canva for quick social posts
- **Job to be done:** Apply my aesthetic without re-explaining it every time
- **Quote:** *"I've told every AI tool I like warm tones. None of them remember."*
- **Success signal:** *"It just knows what I want now."*

### Persona 2 — The Freelance Brand Designer (secondary)
- Manages 3–5 client brand accounts simultaneously
- Each client has distinct colours, crop ratios, platform export specs
- **Job to be done:** Switch between client contexts without constant re-briefing
- **Success signal:** *"I brief it once per brand and it stays on-brand forever."*

### Persona 3 — The Small Business Owner (tertiary)
- Runs an e-commerce brand or local service business
- Not a designer. Posts on Instagram to drive sales.
- **Job to be done:** My social posts should look like my brand, not generic AI output
- **Success signal:** *"It actually looks like us."*

---

## 9. Success Metrics

### Primary — product quality
- **Creative intent score ≥ 4.0/5.0** — Stil serves what users actually want, not just what they type
- **Style retention rate > 70%** — returning users whose profile updated ≥ once in first week
- **Session re-explanation rate < 10%** — users not re-specifying already-known preferences by session 3

### Secondary — engagement
- D7 retention: > 40%
- Sessions per week per active user: > 3
- Average session length: 4–6 turns

### Harness health metrics
- **choices_log → style_signature agreement rate**: how often do behavioral signals and AI-extracted intent agree? High agreement = the extraction model is working. Persistent divergence = the extraction prompt needs revision.
- **Completion vs. intent gap per session**: sessions where goal_completion ≥ 4 and creative_intent ≤ 2 indicate prompt architecture failures — the agent is technically capable but not creatively aligned
- **Frequency analysis divergence rate**: how often does the most recent session differ from the dominant preference pattern? High rate = creators are experimenting (healthy); low rate = preferences are stable (simpler memory strategy is sufficient)

### Guardrails
- API cost per user per day: < $0.10
- Style extraction failure rate: < 5%
- Tool call accuracy: > 4.0/5.0

---

## 10. Roadmap — From Prototype to FF Agentic

### v0.1 — Concept validator ✓ Shipped
Local Streamlit prototype. Full agentic loop end-to-end. Behavioral memory (choices_log + style_signature). Frequency analysis in prompt injection. Real before/after preview via Pillow. Platform export grid (Instagram, Reels, Twitter, LinkedIn). Feed Cohesion Score. Style Transfer. Brief-to-Edit Translator. Client Brand Switcher. Quality insights with 3-dimension eval rubric and session trend chart. Asset search. EXIF camera profile.

**What it proves:** The core architecture works. Behavioral memory outperforms declared memory in multi-session creative workflows. Creative intent can be graded separately from task completion, and the gap between the two is a meaningful signal.

### v0.2 — Deeper style model and research loop
Deepen the style profile: aesthetic mood tags (editorial, lifestyle, minimalist), platform-specific crop/export defaults surfaced prominently. Export style as a shareable "creative brief" PDF — portability proof before real integrations exist. Begin structured creator research: 10–15 creator interviews using the prototype, capture re-explanation rate and drift patterns in real sessions. Session comparison view.

**Research goal:** Validate that the behavioral memory loop matches what creators say they want vs. what they actually do across sessions. Identify where the 3-dimension eval rubric misses real intent.

### v0.3 — Real tool integrations via MCP
**Canva Apps SDK** is the primary target: 150M MAU, public API, and an app marketplace that solves distribution. A Stil Canva App puts style memory in front of the platform creators already use daily. **Cloudinary** as secondary: accessible REST API, real image transformations. This version answers: does memory-augmented editing drive measurably better feed consistency when measured against actual creator feeds, not prototype test data?

**Harness implication:** v0.3 is where the tool architecture decision (Section 5.4) matters at scale. MCP-based tool execution, shared tool definitions, and result routing between Canva SDK and Cloudinary API need the harness layer to abstract them.

### v0.4 — Video workflows and team memory
**Video:** Extend the same memory loop to video clips — trim points, color grade consistency, caption style. The behavioral log pattern applies identically: `set_color_grade("warm")`, `set_trim_point(3.2)`, `set_caption_style("minimal")` write to choices_log the same way image tools do. The eval rubric gains a video-specific intent dimension: "does the edit preserve the narrative arc?"

**Team memory:** Shared style profiles for brand teams. A shared choices_log where multiple editors contribute behavioral signals — the dominant preference across the team, not just one user, becomes the injected context. This is the enterprise unlock: brand consistency enforced across teams, not just individuals.

**Harness implication:** Multi-user memory requires the harness to define memory ownership (user-level vs. team-level) and conflict resolution (what happens when two editors make opposite choices in the same session?).

### v0.5 — Production harness integration (FF Agentic)
Integrate Stil's memory architecture, prompt injection design, and eval framework as requirements inputs for the FF Agentic harness. Specifically:

- **Memory layer:** choices_log + style_signature design as the reference architecture for Harness memory in FF Agentic
- **Prompt architecture:** token budgets, injection order, and priority rules as a proposed standard for creative agent prompts
- **Evals:** 3-dimension rubric (tool accuracy, goal completion, creative intent) as the baseline eval framework for FF Agentic sessions
- **Telemetry:** JSONL session logging format and CHS requirements derived from what the prototype's eval pipeline needed to function

At this stage, Stil is no longer a standalone product. It becomes the research and validation layer for the FF Agentic experience.

### v0.6 — Web app + multi-platform
Hosted web app. Supabase for storage and auth. Mobile-first UI for editing on the go. Cross-platform style profile: a creator's choices on Firefly inform their Canva session, which informs their Express template — one profile, every tool.

---

## 11. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Style profile too shallow to be useful early | Medium | High | Seed card on first session; 3-field minimum; profile deepens with usage |
| Creators don't trust AI to know their style | Medium | Medium | Full transparency — raw profile always visible; every field editable; before/after confirms edit before saving |
| API costs exceed margins at scale | Low | High | Haiku for all AI tasks; Pillow for all image processing; 6-turn cap; tag cache |
| Completion vs. intent gap persists beyond session 3 | Medium | High | Prompt architecture review; deeper style_signature extraction; creator interview feedback loop |
| Canva ships conversational style memory | Medium | High | Speed to market; multi-tool portability Canva cannot offer within their own ecosystem |
| Adobe ships this inside Creative Cloud | Low–Medium | High | Portability across tools Adobe does not own is the structural differentiator — and this prototype demonstrates the architecture Adobe would need anyway |
| Style extraction hallucination | Low | Medium | Merge-not-overwrite strategy; frequency analysis catches outlier sessions; user can review and correct directly |
| Video workflow complexity underestimated | Low–Medium | Medium | v0.4 uses identical log architecture — the tool call format, not the media type, is what the memory system reads |

---

## 12. Open Questions and Next Steps

**1. Harness ownership of memory priority rules**
Currently, the priority ordering (choices_log > style_signature) is enforced in `build_system_prompt()` — application code. In a production harness, this should be a harness-level contract, not something each agent implements independently. The open question: does the harness enforce priority ordering, or does it expose the raw memory layers and let each agent decide?

**2. Creative intent eval at scale — RAG-based approach with Pinecone**
The current eval uses one Haiku call per turn — effective but slow and expensive at scale. The next iteration uses a RAG eval pipeline:

1. Embed all previously graded turns (session transcript + scores) into Pinecone
2. For each new turn, find the 3 nearest-neighbor graded examples by semantic similarity
3. Use those examples as few-shot context for a much shorter Haiku call — or skip the LLM entirely and use the nearest neighbor's score directly when similarity is high (>0.92)
4. Result: eval latency drops from ~2–3 seconds per turn to <200ms; cost drops by ~70%

The Pinecone index also enables new signals: "this turn is similar to 47 past turns that scored 1/5 on creative intent — this is a known failure pattern." That pattern-level insight is not possible with per-turn LLM grading.

**Immediate next step:** Build `insights_v2.py` using Pinecone for the embedding store. Keep the existing Haiku-based grader as the ground truth for populating the index. The RAG grader replaces it for runtime evals once the index has >100 graded examples.

At production scale, the sampling strategy: sessions where tool_accuracy ≥ 4 and goal_completion ≥ 4 get RAG-only eval; sessions where any score is ≤ 2 trigger a full Haiku re-grade (the anomaly cases are where precision matters most).

**3. Multi-user memory conflict resolution**
When two designers on the same brand account make opposite choices in the same week (one uses warm filter, one uses cool), the choices_log has conflicting behavioral signals. The harness needs a conflict resolution policy: most recent wins, most frequent wins, or expose the conflict to both users for resolution. This decision has product implications beyond the technical architecture.

**4. Video intent rubric**
Video creative intent is harder to grade than image intent. "Does this edit serve the creative goal?" for a 30-second TikTok requires understanding narrative arc, pacing, and platform-specific engagement patterns. The eval model for video will need a different rubric than the image rubric — this is a research question before an engineering one.

**5. Portability across tools before v0.5**
The core value proposition — style that travels across tools — cannot be fully demonstrated until real integrations exist. The near-term bridge: export the style profile as a structured "creative brief" that can be pasted into any tool. Tests portability resonance before building integrations.

**6. Creator research cadence**
The prototype is built. The next phase requires putting it in front of 10–15 creators for structured sessions: observe where they re-explain preferences that should be in the profile, track drift patterns, and measure whether creative intent scores improve session-over-session for real creative goals. This research should happen before v0.2 ships.

---

*This document represents the thinking behind a working prototype and a proposed architecture for the FF Agentic harness. The prototype can be run locally and demonstrated end-to-end. Every design decision documented here is validated in code — not as a specification, but as a shipped and tested system.*
