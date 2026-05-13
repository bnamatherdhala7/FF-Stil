# Stil — Product Brief
### Conversational agentic editing with persistent visual memory
**For:** VP review · **Status:** Prototype shipped · **May 2026**

---

## The problem in one sentence

Every creative editing tool starts from zero every session — no tool holds the memory of what you chose last time, so creators repeat the same decisions hundreds of times a year and slowly drift from their own aesthetic without noticing.

---

## Who it's for

**207M content creators globally.** 87% already use AI. The pain is not adoption — it's that every tool is stateless. Creators post 3–5×/week, make 200+ editing decisions/year that are not creative choices — they are re-execution of already-decided preferences. 46% of creator working time goes to non-creative tasks.

Three archetypes:
| | Solo Creator | Freelance Designer | Small Business |
|---|---|---|---|
| Volume | 3–5 posts/week | 3–5 client accounts | 1–3 posts/week |
| Pain | Re-explains style every session | Context-switches between brands | Consistency without design skills |

---

## Why existing tools miss

| | Lightroom presets | ChatGPT / Claude Memory | Adobe Brand Kits | **Stil** |
|---|---|---|---|---|
| Learns from | Nothing | What you *say* | What you configure | What you *do* (tool calls) |
| Updates automatically | No | No — you re-brief it | No | Yes — after every session |
| Handles preference change | — | You manually edit it | You manually edit it | Choices log updates immediately |
| Detects feed drift | No | No | No | Feed Cohesion Score (0–100) |
| Grades creative intent | No | No | No | Per session, trend over time |

**The declaration trap:** Memory features store "user likes warm filters." When you've been using cool for 20 sessions, the memory still says warm. Nothing detected the shift. Stil reads `apply_filter("warm")` directly from the tool call — behavioral ground truth, not a declaration.

---

## What we built (v0.1 — shipped)

**Core loop:** Upload photo → describe edit in natural language → Claude picks and fires tools → before/after preview → platform export grid (Instagram, Reels, Twitter, LinkedIn) → style profile auto-updated

**Memory:** Two layers, explicit priority:
1. `choices_log` — written directly from tool call parameters after every session. Deterministic. No AI involved.
2. `style_signature` — Haiku reads transcript, extracts aesthetic intent (what tool calls can't capture). Fills gaps.

Frequency analysis in prompt injection: *"cool (last session) — usual style is warm (8/11 sessions); apply cool unless user says otherwise"* — not just recency, behavioral pattern.

**Evals:** Sessions graded on 3 dimensions (1–5 each):
- Tool accuracy — right tools for the request?
- Goal completion — task finished as asked?
- **Creative intent** — did the output serve what the user *actually* wanted? ← the one that matters

Now accelerated by **Pinecone RAG**: embed graded turns → reuse scores when similarity ≥ 0.88 — skips the Haiku call entirely. Index compounds over time. ~70% API cost reduction at scale.

**Feed Cohesion Score:** Upload 3–10 photos → get 0–100 consistency score across color temperature, brightness, contrast, saturation. Pure Pillow math. Zero API calls.

**Also ships:** Style Transfer (apply any reference photo's visual fingerprint), Brief-to-Edit Translator (paste creative direction → structured edit plan), Client Brand Switcher (named profiles for multiple clients), EXIF camera profile injection.

---

## Architecture decisions that matter for the harness

| Decision | What it proves | Harness implication |
|---|---|---|
| choices_log > style_signature priority | Behavioral memory beats declared memory | Harness needs defined priority rules, not agent-by-agent |
| Token budget: base 200 + choices 60 + sig 40 + camera 20 | Injection order = priority encoding | Harness owns prompt architecture contract |
| creative_intent as separate eval dimension | Completion always looks good; intent diverges | Eval pipeline needs intent signal as first-class metric |
| JSONL session log as eval source | No log = no feedback loop | CHS must log at tool-call level, not just message level |
| Pinecone RAG for evals | Scales without per-call LLM inference | Harness eval infra needs embedding store from day one |

---

## Key metrics

| Metric | Target |
|---|---|
| Creative intent score | ≥ 4.0 / 5.0 |
| Style retention (profile updated in week 1) | > 70% |
| Re-explanation rate by session 3 | < 10% |
| API cost per user per day | < $0.05 |
| D7 retention | > 40% |

---

## Roadmap

| Version | Focus | Status |
|---|---|---|
| v0.1 | Full prototype: memory, evals, feed score, style transfer, brief translator, brand switcher | ✓ Shipped |
| v0.2 | Mood tags, session comparison, style brief PDF export, 10–15 creator research interviews | Next |
| v0.3 | Real integrations: Canva Apps SDK (150M MAU), Cloudinary API | Planned |
| v0.4 | Video workflows + team/shared memory (enterprise unlock) | Planned |
| v0.5 | FF Agentic harness integration — Stil memory/eval architecture as the reference design | Strategic |
| v0.6 | Web app, Supabase, mobile-first, cross-platform style profile | Scale |

---

## Open questions for VP discussion

1. **Who owns memory priority rules?** Currently in application code — should be a harness contract.
2. **Pinecone RAG evals are the path to scale** — ready to integrate into FF Agentic eval infrastructure.
3. **Creator research before v0.2** — need 10–15 sessions to validate whether behavioral memory matches real session re-explanation rates.
4. **Canva SDK vs. internal first?** v0.3 distribution question: external (Canva, 150M MAU) or internal (Express, Firefly) integration first?

---

*Full architecture detail, research foundation, and feature spec: [PRD.md](PRD.md)*
*Running prototype: `streamlit run app.py` from `stil/`*
