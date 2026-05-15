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

These are not synthesized themes. These are verbatim.

> *"With presets, you almost always have to make adjustments to each individual image. It's like trying to bake a cake with a muffin recipe."*
— Samanta Katz, photographer and educator *(samantakatz.com)*

> *"Presets are consistent. Your photos are not."*
— Lou Marks Presets *(loumarkspresets.com)*

> *"8–10 hours staring at a screen, culling every single wedding. 15+ hours slowly editing each gallery. It was sucking the joy right out of my passion. Last year, I came very close to quitting wedding photography."*
— Ignatios Kourouvasilis, wedding photographer *(ignatioskourouvasilis.com)*

> *"I was paying $300 a month to get my photos 70% edited."*
— Looyenga Photography, on Imagen AI *(looyengaphotography.com)*

> *"The LLM only knows what you tell it — in that specific conversation."*
— Teresa Torres, ProductTalk.org, on stateless AI

> *"Your Instagram feed looks like it belongs to three different companies."*
— InvokeMedia *(invokemedia.co.uk)*

**The number behind the frustration:** 83% of users report having to repeat context to AI agents across sessions. 33% name it their single most frustrating AI experience. *(MemMachine AI, industry survey 2025)*

**43% of brands** say it is "incredibly difficult" to maintain visual consistency across platforms — and most don't notice the drift until they scroll back six months. *(Jennifer Zmuda, visual content research 2025)*

The word that appears verbatim across Lightroom forums, AI tool reviews, and creator communities: **"starting from scratch."** Not slow. Not expensive. Starting from scratch — every single time.

---

## 4. What exists today — and the gap Adobe has not closed

### The competitive landscape

| | Lightroom presets | Imagen AI / Aftershoot | ChatGPT / Claude Memory | Adobe Express Brand Kit | Canva Brand Kit | **Stil** |
|---|---|---|---|---|---|---|
| **Learns from** | Nothing | 2,500–5,000 past photos | What you *say* | What you *upload* | What you *upload* | What you ***do*** (tool calls) |
| **Works from session 1** | No — manual preset | No — needs training library | Yes — but stateless text | No — manual setup | No — manual setup | **Yes — automatically** |
| **Updates when behavior changes** | No | No — retrain quarterly | No — you re-brief | No — you reconfigure | No — you reconfigure | **Yes — after every session** |
| **Conversational interface** | No | No | Yes — no editing tools | No | No | **Yes** |
| **Detects feed drift** | No | No | No | No | No | **Feed Cohesion Score** |
| **Grades creative intent** | No | No | No | No | No | **Per session, trend chart** |
| **Individual creator pricing** | $19.99/mo | $0.05/photo or $59–199/mo | $20/mo (no editing) | $9.99/mo (no learning) | $15/mo (no learning) | **$15/mo target** |
| **Platform portability** | Adobe only | Lightroom only | No editing tools | Adobe only | Canva only | **Cross-tool** |

### Why each existing solution fails

**Lightroom presets** are static parameter files — saved slider values, not behavioral intelligence. They do not adapt, do not update, and do not travel. 74% of professional photographers depend on Lightroom, yet every session still starts from zero unless they manually select a preset. Adobe's own answer to style memory is a manual step.

**Imagen AI and Aftershoot** have the deepest style learning in the market. But they require 2,000–5,000 previously edited photos before the AI is useful. Looyenga Photography was paying $300/month for 70% accuracy. The onboarding cost alone is the product's biggest user complaint — and neither system is conversational.

**ChatGPT Memory and Claude Projects** store what you *say*, not what you *do*. If a creator edits warm and crops square in every session without mentioning it, those patterns are never captured. Memory cap: ~1,200 words. No editing tools. No execution. They can describe how to edit a photo — they cannot perform the edit.

**Adobe Express Brand Kit and Canva Brand Kit** are manual declaration systems. The creator uploads a logo, selects brand colors, chooses a font. Nothing is observed. A creator who edits the same way in 200 sessions has not trained either system at all. Canva has 265 million MAU. None of them have behavioral style memory.

### The declaration trap — why "memory features" don't close this gap

Every major AI platform ships memory now. These are real features. But they store *declarations*: "user likes warm filters." Declarations freeze. When a creator has been using cool tones for 20 sessions for a winter campaign, the memory still confidently says warm. Nothing fired. The drift happened invisibly.

**The deeper problem:** every memory system built on declarations requires the creator to manage their memory as a second job — tracking what changed, updating preferences manually, catching the moments when stated preference and actual behavior diverged. That overhead is invisible in any usage metric, and it erodes exactly the trust the system was supposed to build.

**The structural gap Adobe has not closed:** no Adobe product today learns a creator's visual style from observed behavior, updates it automatically, and applies it conversationally — starting from session one, at individual creator pricing, across the Adobe suite.

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

*Full architecture and feature spec: [PRD.md](PRD.md)*
*Workflow diagrams (eval pipeline + style injection): [WORKFLOW_DIAGRAMS.md](WORKFLOW_DIAGRAMS.md)*
*Prototype: `cd stil && streamlit run app.py`*
