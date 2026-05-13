# Stil — Executive Brief
**May 2026 · Prototype shipped · VP review**

---

## 1. The problem

**Every creative editing tool starts from zero every session.**

A creator posts 3–5 times a week. That is 200+ pieces of content a year. Here is what every session looks like regardless of which tool they open:

1. Apply the warm filter — *again*
2. Crop to square for Instagram — *again*
3. Set export to 1080×1080, JPEG, sRGB — *again*
4. Bump brightness +20 — *again*

None of these are creative decisions. They were made months ago. But every tool resets because **no tool holds the memory**.

This compounds into a deeper problem: **visual drift**. Post 1 looks exactly like the creator. Post 180 barely does — not because their aesthetic changed, but because 200 micro-decisions made under time pressure, across three tools, at varying energy levels, slowly diverged from the original intent. Creators notice it six months later when they scroll their own feed and it no longer looks like theirs.

---

## 2. How big is this problem today

| Signal | Data |
|---|---|
| Content creators globally | 207 million |
| Already using AI in their workflow | 87% (Artlist, 2025, n=6,500) |
| Creator working time on non-creative tasks | 46% — formatting, re-entry, repetitive editing |
| Creator economy today | $205–254B (2025) → $1.35T by 2035 at 23% CAGR |
| AI image editing market | $5.1B (2025) → $39.7B (2030) at 39% CAGR |
| Editing hours per photographer | >50% of working time spent editing, not shooting |

**The gap:** No tool at individual creator pricing ($10–20/month) combines persistent cross-session style memory + conversational execution + real image feedback from day one.

---

## 3. What creators are actually saying

> *"I've told every AI tool I like warm tones. None of them remember."*
— Creator interview, recurring verbatim

> *"Every time you start a new conversation with AI, it forgets everything from the last conversation. You're constantly re-explaining your brand, re-correcting the same mistakes, and getting inconsistent output."*
— Creator productivity research, 2025

> *"We spend more time editing AI content to match our voice than it would take to write from scratch. We keep making the same edits over and over because the AI doesn't learn."*
— Creator brand consistency research, 2025

> *"I only notice my feed is inconsistent six months later, when I scroll back."*
— Creator interview

> *"That preset you bought makes your indoor portrait look orange. You end up spending more time tweaking sliders than if you'd just started from scratch."*
— Lightroom community, signatureedits.com

**Common vocabulary across all sources:** "Starting from scratch." It appears verbatim across AI tool reviews, Lightroom forums, and creator strategy content. This is the named experience.

---

## 4. The solution

**Stil is a conversational AI assistant that learns your visual style from what you do — not what you say — and applies it automatically in every session.**

**First session:**
> Creator uploads a portrait. Types: *"Make this warmer, crop square, export for Instagram."*
> Stil fires four tools: `apply_filter("warm")` → `adjust_brightness(+20)` → `crop_image("square")` → `set_export_preset("instagram")`
> Before/after preview appears. Platform exports shown: Instagram 1:1, Reels 9:16, Twitter 16:9, LinkedIn 4:5.
> Style profile saved. Memory loop visible to the creator.

**Second session — no re-explanation:**
> Creator uploads a new photo. Banner at top: *"✦ Style active — warm · square · instagram · built from 4 edits."*
> Types: *"Edit my photo."* That is all.
> Stil reads the choices log and applies the full aesthetic without being asked.

**Ten sessions later:**
> Creator opens the Feed tab. Uploads 8 recent grid photos.
> Score: 61/100. Issues: *"Brightness inconsistent across your feed · Saturation varies."*
> She did not notice this happening. Stil did.

---

## 5. Has anyone already built this?

**No. Here is the precise gap:**

| | Lightroom presets | Imagen AI / Aftershoot | ChatGPT / Claude Memory | Adobe Brand Kits | **Stil** |
|---|---|---|---|---|---|
| Learns from | Nothing | Past edited images | What you *say* | What you configure | What you *do* (tool calls) |
| Works from session 1 | No — needs 2,500–5,000 photos | No — needs training library | Yes but stateless | Yes but manual setup | **Yes** |
| Updates when behavior changes | No | No | No — you re-brief | No — you re-brief | **Yes — automatically** |
| Detects feed drift | No | No | No | No | **Feed Cohesion Score** |
| Grades creative intent | No | No | No | No | **Per session, trend chart** |
| Conversational interface | No | No | Yes | No | **Yes** |
| Individual creator pricing | Yes | $9–19/mo (Lightroom only) | $20/mo (general) | Enterprise | **Target: $10–20/mo** |

**The closest competitors — and why they don't close the gap:**
- **Imagen AI / Aftershoot** — requires 2,500–5,000 past edited images to train, Lightroom-only, batch processing, built for wedding photographers not social creators
- **ChatGPT/Claude with memory** — stores declarations ("I like warm filters"), cannot execute editing actions, no before/after preview, no feed consistency measurement
- **Adobe Brand Kits / Style Presets** — manual configuration, no behavioral learning, no drift detection, enterprise pricing

---

## 6. Why Stil is different — the intelligence we added

### The declaration trap (why existing memory fails)

When ChatGPT or Claude Projects saves "user likes warm filters," it stores a declaration — something you said once. That declaration stays frozen. If you've been using cool tones for 20 sessions because of a winter campaign, the memory still says warm. Nothing detected the shift. You re-brief manually. Declarations drift; behavior is the ground truth.

### Two-layer behavioral memory

```
Layer 1 — choices_log (behavioral ground truth)
  Source:   actual tool call parameters written directly from API response
  Example:  apply_filter("warm") → logs filter: warm
  Update:   after every session, deterministic, no AI involved
  Priority: injected first into the system prompt

Layer 2 — style_signature (AI-extracted intent)
  Source:   Haiku reads conversation transcript after session ends
  Example:  "prefers clean editorial warmth; avoids heavy vignettes"
  Update:   merges with existing — never overwrites
  Priority: fills gaps where choices_log has no entry
```

**Behavior beats declaration.** The choices log updates the moment you change. No re-briefing. No drift.

### Frequency intelligence — not just recency

Stil does not blindly follow the most recent click. It analyzes the full history:

> *"cool (last session) — usual style is warm (8/11 sessions); apply cool unless user says otherwise"*

This is the difference between a system that follows the last click and one that understands the underlying preference pattern. Warm 8/11 times is a consistent preference. Cool last session is a divergence worth noting, not blindly overriding.

### Feed Cohesion Score

Upload 3–10 photos from your grid. Stil computes variance across color temperature, brightness, contrast, and saturation using Pillow image processing. Returns a 0–100 consistency score, identifies which dimension is breaking cohesion, and suggests a specific fix. **Zero API calls. Zero cost.** This is the first time feed consistency has been made objectively measurable for individual creators.

---

## 7. How we're doing evals

**The core insight:** Task completion metrics always look good. An agent that never fails to fire tools scores 5/5 on completion forever. We need a signal that tells us whether the agent is actually serving the creator — not just executing instructions.

### Three dimensions graded per session (1–5 each)

| Dimension | What it measures | Why it matters |
|---|---|---|
| Tool accuracy | Did the agent call the right editing tools? | Validates the agentic decision loop |
| Goal completion | Did it finish what was literally asked? | Baseline task success |
| **Creative intent** | Did the output serve what the user *actually* wanted? | **The one that matters** |

A session can score 5/5 on completion and 1/5 on creative intent — Stil did exactly what was typed and missed the creative purpose entirely. That gap is the signal that no rule-based or preset-based eval system can generate. It tells you whether the style profile is actually working.

### How evals run — Pinecone RAG pipeline

**The problem with per-turn LLM grading:** slow, expensive, doesn't scale. Each Haiku call takes 2–3 seconds and costs ~$0.003. At production scale (millions of sessions), this is untenable.

**The solution — RAG-accelerated evals:**

```
New session turn arrives
        ↓
Embed turn text (Pinecone multilingual-e5-large, 1024 dimensions)
        ↓
Query index for nearest-neighbor graded examples
        ↓
Similarity ≥ 0.88?  →  YES: reuse neighbor's scores  (< 200ms, $0)
                    →  NO:  Haiku grades it           (2–3s, $0.003)
                                ↓
                        Store graded turn to Pinecone
                        (index compounds over time)
```

Index: `stil-evals-v1` (serverless, AWS us-east-1). As the index grows, the % of turns resolved by RAG increases. With >100 graded examples, target ~70% of future eval calls skipping Haiku entirely.

### The trend signal

The session trend chart — creative intent score over sessions — is the primary feedback signal for whether the memory system is working. If creative intent improves as the profile matures, the behavioral memory is doing its job. If it plateaus or drops, the prompt architecture needs revision.

---

## 8. What this prototype proves for FF Agentic

Every design decision in Stil maps to a requirement the FF Agentic harness will need to resolve:

| Stil decision | What it proves | Harness requirement |
|---|---|---|
| choices_log priority over style_signature | Behavioral memory outperforms declared memory | Harness must define memory priority rules — not leave it to each agent |
| Frequency analysis in prompt injection | Recency alone produces worse decisions than pattern analysis | Memory layer needs frequency analysis at infrastructure level |
| Creative intent as separate eval dimension | Completion and intent diverge in practice | Eval pipeline needs intent as first-class signal, not just task completion |
| JSONL session logging at tool-call level | No log = no eval = no feedback loop | CHS must log tool calls, not just messages |
| Pinecone RAG for evals | Per-call LLM grading doesn't scale | Eval infra needs embedding store from day one |

---

## Next steps

1. **Creator research (before v0.2):** 10–15 structured sessions with real creators — observe where they re-explain preferences that should be in the profile, measure re-explanation rate, validate behavioral memory loop
2. **v0.2:** Mood tags, session comparison, style brief PDF export
3. **v0.3:** Canva Apps SDK integration (150M MAU, public API) — the distribution unlock
4. **v0.5:** Stil memory/eval architecture as reference design for FF Agentic harness

---

*Prototype running locally. Full spec: [PRD.md](PRD.md)*
