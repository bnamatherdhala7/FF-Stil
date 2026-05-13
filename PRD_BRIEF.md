# Stil — Executive Brief
**May 2026 · Prototype shipped · VP review**

---

## 1. The problem

**Every creative editing tool starts from zero every session.**

A creator posts 3–5 times a week — 200+ pieces of content a year. Here is what every session looks like regardless of which tool they open:

1. Apply the warm filter — *again*
2. Crop to square for Instagram — *again*
3. Set export to 1080×1080, JPEG, sRGB — *again*
4. Bump brightness +20 — *again*

None of these are creative decisions. They were made months ago. But every tool resets because **no tool holds the memory**.

This creates a compounding second problem: **visual drift**. Post 1 looks exactly like the creator. Post 180 barely does — not because the aesthetic changed, but because 200 micro-decisions made under time pressure, across three tools, at varying energy levels, slowly diverged from the original intent. Creators do not notice it turn by turn. They notice it six months later when they scroll their own feed and it no longer looks like theirs.

**This is not a speed problem. It is a consistency problem.**

---

## 2. How big is this problem today

| Signal | Data |
|---|---|
| Content creators globally | 207 million |
| Already using AI in their workflow | 87% (Artlist, 2025, n=6,500) |
| Creator working time on non-creative tasks | 46% — formatting, re-entry, repetitive editing |
| Creator economy | $205–254B (2025) → $1.35T by 2035 at 23% CAGR |
| AI image editing market | $5.1B (2025) → $39.7B (2030) at 39% CAGR |
| Editing time for photographers | >50% of working hours — not shooting, editing |

**The gap no tool has closed:** persistent cross-session style memory + conversational execution + real image feedback, at individual creator pricing ($10–20/mo), working from session one without a training library.

---

## 3. What creators are actually saying

> *"I've told every AI tool I like warm tones. None of them remember."*
— Creator interview, recurring verbatim

> *"Every time you start a new conversation with AI, it forgets everything. You're constantly re-explaining your brand, re-correcting the same mistakes, getting inconsistent output."*
— Creator productivity research, 2025

> *"We spend more time editing AI content to match our voice than it would take to write from scratch. We keep making the same edits over and over because the AI doesn't learn."*
— Creator brand consistency research, 2025

> *"I only notice my feed is inconsistent six months later, when I scroll back."*
— Creator interview

> *"That preset makes your indoor portrait look orange. You end up spending more time tweaking sliders than if you'd just started from scratch."*
— Lightroom community

The phrase **"starting from scratch"** appears verbatim across AI tool reviews, Lightroom forums, and social media strategy content. It is the single word creators use to describe this experience. "Stateless" has entered mainstream creator discourse as the named cause.

---

## 4. Current solutions — and why they fail

| | Lightroom presets | Imagen AI / Aftershoot | ChatGPT / Claude Memory | Adobe Brand Kits | **Stil** |
|---|---|---|---|---|---|
| Learns from | Nothing | 2,500–5,000 past photos | What you *say* | What you configure | What you *do* (tool calls) |
| Works from session 1 | No | No — needs training | Yes but stateless | Yes but manual | **Yes** |
| Updates when behavior changes | No | No | No — you re-brief | No — you re-brief | **Yes — automatically** |
| Detects feed drift | No | No | No | No | **Feed Cohesion Score** |
| Grades creative intent | No | No | No | No | **Per session, trend chart** |
| Conversational | No | No | Yes | No | **Yes** |

**Why memory features don't close this gap:**

Every major AI platform ships memory now — ChatGPT Memories, Claude Projects, Notion AI. These are real features. But they store *declarations*: "user likes warm filters." Declarations freeze. When you've been using cool tones for 20 sessions because of a winter campaign, the memory still confidently says warm. Nothing fired. The drift happened invisibly.

The deeper problem: **every memory system built on declarations requires the creator to manage the memory as a second job** — tracking what changed, updating preferences manually, catching the moments when stated preference and actual behavior diverged. That overhead is invisible in any usage metric, but it erodes exactly the trust you are trying to build.

---

## 5. The solution

**Stil stores what you do, not what you say.**

```
You type: "Make this warmer, crop square, export for Instagram"
              ↓
Stil executes:  apply_filter("warm")          → logs: filter: warm
                crop_image("square")          → logs: crop: square
                set_export_preset("instagram") → logs: export: instagram
```

The choices log is written directly from the API response — no AI guessing, no paraphrasing. It is the literal record of what happened. The most recent action always wins. If you switch to cool tones next session, the log updates immediately. You never re-briefed anything.

**Two intelligence layers, explicit priority:**

| Layer | Source | Update | Priority |
|---|---|---|---|
| `choices_log` | Actual tool call parameters | After every session, deterministic | Injected first — highest trust |
| `style_signature` | Haiku reads conversation transcript | Merges after every session | Fills gaps choices_log doesn't cover |

**Frequency intelligence — not just recency:**

Stil does not follow the last click. It analyzes the full behavioral history:

> *"cool (last session) — usual style is warm (8/11 sessions); apply cool unless user says otherwise"*

This distinction is the difference between a system that follows what you just did and one that understands your underlying pattern. Warm 8/11 times is a consistent preference. Cool last session is a divergence worth noting, not blindly overriding.

**What the experience looks like:**

*First session:* Upload photo. Type: *"Make this warmer, crop square, export for Instagram."* Four tools fire. Before/after preview. Platform exports appear (Instagram 1:1, Reels 9:16, Twitter 16:9, LinkedIn 4:5). Style profile saved.

*Second session:* Upload new photo. Banner: *"✦ Style active — warm · square · instagram."* Type: *"Edit my photo."* That is all. Stil reads the choices log and applies the full aesthetic.

*Ten sessions:* Open Feed tab. Upload 8 recent grid photos. Score: 61/100. *"Brightness inconsistent · Saturation varies."* She did not notice this happening. Stil did.

---

## 6. What makes this agentic — not just a chatbot

**The test:** If you replaced Claude with hardcoded if/else logic, would it still work?

A chatbot: yes — user types, AI replies, done.
Stil: no — Claude reasons about which tools to call, executes them, observes the result, decides the next action, loops until complete, saves the session, extracts the style update. Remove the reasoning and the system breaks. That is the line between a chatbot and an agent.

This matters for Adobe because agentic experiences in creative workflows face a problem text-based agents do not: **visual consistency**. A writing agent that forgets context produces a slightly worse paragraph. A creative agent that forgets context produces a feed that no longer looks like the creator's brand. The stakes are cumulative and visible.

---

## 7. The AI and intelligence we added

**1. Behavioral memory** — reads tool calls, not user statements. The first system that stores demonstrated editing behavior as the source of truth, not declared preferences.

**2. Frequency analysis** — surfaces dominant preference vs. recent divergence at prompt injection time. Built into `build_system_prompt()` — not left to the model to figure out from raw history.

**3. Feed Cohesion Score** — computes variance across color temperature, brightness, contrast, and saturation across a creator's uploaded photos using Pillow image processing. Returns a 0–100 consistency score with a specific fix. Zero API calls. The first objective measurement of feed consistency at the individual creator level.

**4. Creative intent grading** — sessions scored on whether the output served what the user *actually* wanted, not just whether the task was completed. A session can score 5/5 on completion and 1/5 on intent. That gap is the signal no rule-based system can generate.

**5. Style Transfer** — extract the visual fingerprint of any reference photo (competitor, mood board, editorial) and apply it to your photo in seconds. Deterministic Pillow pipeline, no extra API calls.

**Research-driven design decisions:**

| Finding | Design decision |
|---|---|
| Creators can't articulate style upfront | Reactive learning from tool calls, not a configuration form |
| Drift is invisible in the moment | Objective Feed Cohesion Score — measurable before drift is visible |
| Task completion ≠ creative intent | Separate eval dimension for creative goal |
| No tool survives a context switch | Behavioral memory (choices_log) beats declared memory (style_signature) |
| Creators need to trust the system | Full profile transparency — every field editable, raw JSON always visible |

---

## 8. How we are doing evals

**The insight that drives the design:** Task completion metrics always look good. An agent that never fails to fire tools scores 5/5 on completion forever. That metric tells you nothing about whether the agent is serving the creator.

**Three dimensions graded per session:**

| Dimension | What it measures |
|---|---|
| Tool accuracy | Did the agent call the right tools? |
| Goal completion | Did it finish what was literally asked? |
| **Creative intent** | Did the output serve what the user actually wanted? ← the one that matters |

**The trend chart** — creative intent score over sessions — is the feedback signal for whether memory is working. If intent improves as the profile matures, the behavioral memory is doing its job. If it plateaus or drops, the prompt architecture needs revision. Without this, there is no way to know if memory is actually helping.

**Pinecone RAG eval pipeline — solving the scale problem:**

Per-turn LLM grading is slow (2–3s) and expensive ($0.003/call) at production scale. The solution:

```
New turn arrives
       ↓
Embed with Pinecone (multilingual-e5-large, 1024d)
       ↓
Query nearest-neighbor graded examples
       ↓
Similarity ≥ 0.88  →  reuse score  (<200ms, $0)
Similarity < 0.88  →  Haiku grades it  (2–3s, $0.003)
                              ↓
                   Store to Pinecone index (compounds over time)
```

Index: `stil-evals-v1` (live, serverless AWS). As the index grows, the % of turns resolved by RAG increases. Target: ~70% of eval calls skipping Haiku at production volume.

---

## 9. Where this leads — the FF Agentic opportunity

Stil was built to answer three specific questions:
1. Can behavioral memory outperform declared memory in multi-session creative workflows?
2. Can creative intent be graded separately from task completion — and does the distinction matter?
3. Can a conversational interface handle complex multi-step creative workflows without re-briefing?

All three: **yes.** And every design decision maps to a requirement the FF Agentic harness needs to resolve.

| Decision in Stil | Harness requirement it surfaces |
|---|---|
| choices_log priority over style_signature | Harness must own memory priority rules — not each agent independently |
| Frequency analysis at injection time | Memory infrastructure needs behavioral pattern analysis, not just recency |
| Creative intent as eval dimension | Eval pipeline needs intent as first-class signal |
| JSONL tool-call-level session logging | CHS must log at tool call level, not just message level |
| Pinecone RAG for evals | Eval infra needs embedding store from day one |

**The Adobe-specific opportunity:** A creator's visual style as a persistent, portable asset — one that travels across Firefly, Express, Lightroom, and Canva, and compounds with every editing session. Portability across tools Adobe does not fully own is the structural differentiator — and this prototype demonstrates the architecture Adobe would need to build it.

**Built in weeks, not months.** Prototype-first. Every claim in this brief is validated in running code.

---

## Roadmap

| Version | What ships | Status |
|---|---|---|
| v0.1 | Full prototype: memory, evals, feed score, style transfer, brief translator, brand switcher, platform exports | ✓ Shipped |
| v0.2 | Mood tags, session comparison, style brief PDF export + 10–15 creator research sessions | Next |
| v0.3 | Canva Apps SDK (150M MAU, public API) — the distribution unlock | Planned |
| v0.4 | Video workflows + shared team memory | Planned |
| v0.5 | Stil memory/eval architecture as reference design for FF Agentic harness | Strategic |

---

*Full architecture, research foundation, feature spec: [PRD.md](PRD.md)*
*Prototype: `cd stil && streamlit run app.py`*
