# Stil — Executive Brief
**May 2026 · Prototype shipped · VP review · Built for Adobe**

---

## 1. The problem

**Every creative editing tool starts from zero every session.**

A creator posts 3–5 times a week — 200+ pieces of content a year. Here is what every session looks like regardless of which tool they open:

1. Apply the warm filter — *again*
2. Crop to square for Instagram — *again*
3. Set export to 1080×1080, JPEG, sRGB — *again*
4. Bump brightness +20 — *again*

None of these are creative decisions. They were made months ago. But every tool resets because **no tool holds the memory**.

This creates a compounding second problem: **visual drift**. Post 1 looks exactly like the creator. Post 180 barely does — not because the aesthetic changed, but because 200 micro-decisions made under time pressure, across three tools, slowly diverged from the original intent. Creators don't notice turn by turn. They notice six months later when they scroll their own feed and it no longer looks like theirs.

**This is not a speed problem. It is a consistency problem.**

---

## 2. How big is this problem

| Signal | Data |
|---|---|
| Content creators globally | 207 million |
| Already using AI in their workflow | 87% (Artlist, 2025, n=6,500) |
| Creator time on non-creative tasks | 46% — formatting, re-entry, repetitive editing |
| Creator economy | $205–254B (2025) → $1.35T by 2035 at 23% CAGR |
| AI image editing market | $5.1B (2025) → $39.7B (2030) at 39% CAGR |
| Editing time for photographers | >50% of working hours — not shooting, editing |

**The gap no tool has closed:** persistent cross-session style memory + conversational execution + real image feedback, at individual creator pricing, working from session one without a training library.

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
— Teresa Torres, ProductTalk.org

> *"Your Instagram feed looks like it belongs to three different companies."*
— InvokeMedia *(invokemedia.co.uk)*

**83%** of users report having to repeat context to AI agents across sessions. **33%** name it their single most frustrating AI experience. *(MemMachine AI, 2025)*

**43% of brands** say it is "incredibly difficult" to maintain visual consistency across platforms — and most don't notice drift until they scroll back six months. *(Jennifer Zmuda, 2025)*

The word that appears verbatim across Lightroom forums, AI tool reviews, and creator communities: **"starting from scratch."** Not slow. Not expensive. Starting from scratch — every single time.

---

## 4. What exists — and the gap Adobe has not closed

| | Lightroom presets | Imagen AI / Aftershoot | ChatGPT / Claude Memory | Adobe Express Brand Kit | Canva Brand Kit | **Stil** |
|---|---|---|---|---|---|---|
| **Learns from** | Nothing | 2,500–5,000 past photos | What you *say* | What you *upload* | What you *upload* | What you ***do*** (tool calls) |
| **Works from session 1** | No — manual preset | No — needs training library | Yes — but text only | No — manual setup | No — manual setup | **Yes** |
| **Updates when behavior changes** | No | No — retrain quarterly | No — you re-brief | No — you reconfigure | No — you reconfigure | **Yes — every session** |
| **Conversational** | No | No | Yes — no editing tools | No | No | **Yes** |
| **Detects feed drift** | No | No | No | No | No | **Feed Cohesion Score** |
| **Grades creative intent** | No | No | No | No | No | **Per session, trend chart** |
| **Pricing (individual)** | $19.99/mo | $0.05/photo or $59–199/mo | $20/mo (no editing) | $9.99/mo (no learning) | $15/mo (no learning) | **$15/mo target** |
| **Portable across tools** | Adobe only | Lightroom only | No editing tools | Adobe only | Canva only | **Cross-tool** |

**Lightroom:** 74% of pro photographers depend on it, yet every session resets. Adobe's own answer to style memory is a manual preset.

**Imagen AI / Aftershoot:** Deepest style learning on the market — but gated behind 2,000–5,000 training photos. Not conversational. Wrong audience for social-first creators.

**ChatGPT / Claude Memory:** Store what you *say*, not what you *do*. 1,200-word cap. No editing tools. Can describe how to edit a photo. Cannot perform the edit.

**Adobe Express / Canva:** Manual declaration systems. 265 million Canva MAU. None of them have behavioral style memory. A creator who edits the same way 200 times has trained neither system at all.

**The declaration trap:** Every major AI platform ships memory now. But declarations freeze. When a creator has been using cool tones for 20 sessions for a winter campaign, the memory still says warm. Nothing fired. Managing that gap becomes the creator's second job — invisible in usage metrics, corrosive to trust.

**The structural gap Adobe has not closed:** no Adobe product learns a creator's visual style from observed behavior, updates it automatically, and applies it conversationally — from session one, at individual creator pricing, across the Adobe suite.

---

## 5. What we built — v0.1

Prototype is live. Every claim below runs in code.

### The core loop

```
Creator types: "Make this warmer, crop square, export for Instagram"
       ↓
Stil reads style profile (choices_log injected first, highest trust)
       ↓
Claude reasons → fires tools → observes results → loops until done
       ↓
Before/after preview + platform export grid rendered
       ↓
Style profile updated from tool calls — no re-briefing ever
```

### What shipped

| Capability | What it does | How it works |
|---|---|---|
| **Agentic editing loop** | Claude fires 5 editing tools in real time, observes each result, decides next step | Anthropic tool use API, streaming |
| **Behavioral memory** | Stores tool-call choices across sessions, not declarations | Two layers: `choices_log` (deterministic) + `style_signature` (AI-extracted) |
| **Frequency analysis** | "warm (last session) — usual is warm 8/11 sessions" injected at prompt time | Built into `build_system_prompt()` — not left to model to infer |
| **Feed Cohesion Score** | 0–100 visual consistency score across uploaded feed photos | Pillow variance analysis — zero API calls |
| **Style Transfer** | Extract fingerprint from any reference photo, apply to yours | Deterministic Pillow pipeline |
| **Platform export grid** | Smart per-platform crops (Instagram 1:1, Reels 9:16, Twitter 16:9, LinkedIn 4:5) | Filtered to requested platform via tool trace + style profile fallback |
| **Brief Translator** | Brand brief in plain language → structured edit plan | Haiku single-pass extraction |
| **FastMCP asset search** | Describe a creative need → ranked asset recommendations | Keyword + AI tag scoring, cached |
| **Pinecone RAG eval pipeline** | Grade session quality at scale without an LLM call every turn | Embed → nearest-neighbor → reuse if similarity ≥ 0.88 |
| **Creative intent grading** | 3-dimension rubric: tool accuracy, goal completion, creative intent | Haiku fallback when RAG misses; results stored to compound index |

### The experience at three moments

**Session 1** — Upload photo. Type: *"Make this warmer, crop square, export for Instagram."* Four tools fire in real time. Before/after preview appears. Platform exports render. Style profile saved automatically.

**Session 2** — Upload new photo. Banner: *"✦ Style active — warm · square · instagram."* Type: *"Edit my photo."* That is all. Stil applies the full aesthetic from the choices log.

**Session 10** — Open Feed tab. Upload 8 recent grid photos. Score: 61/100. *"Brightness inconsistent · Saturation varies."* The creator did not notice this happening. Stil did.

---

## 6. Under the hood — what makes this work

**Why this is an agent, not a chatbot:** if you replaced Claude with hardcoded if/else logic, would Stil still work? A chatbot: yes. Stil: no — Claude reasons about which tools to call, executes them, observes each result, decides the next action, loops until complete, then extracts the style update. Remove the reasoning and the system breaks. This matters more in creative workflows than anywhere else: a writing agent that forgets context produces a worse paragraph. A creative agent that forgets context produces a feed that no longer looks like the creator's brand. The stakes are cumulative and visible.

**Two memory layers, explicit priority:**

| Layer | Source | Wins when |
|---|---|---|
| `choices_log` | Written directly from tool call parameters — no AI paraphrasing | Always — highest trust, injected first |
| `style_signature` | Haiku reads the session transcript, extracts aesthetic intent | Fills dimensions tool calls don't cover (mood, context, creative purpose) |

**Frequency analysis — not just recency.** The system doesn't blindly follow the last click. It surfaces the pattern: *"cool (last session) — usual style is warm 8/11 sessions; apply cool unless user says otherwise."* Warm 8/11 is a preference. Cool last session is a divergence worth noting — not overriding.

**Feed Cohesion Score.** Pillow variance analysis across color temperature, brightness, contrast, and saturation. 0–100 score with a specific diagnosis. Zero API calls. The first objective measurement of feed consistency at the individual creator level.

**Creative intent grading.** A session can score 5/5 on goal completion and 1/5 on creative intent — the agent did exactly what was typed and completely missed the creative purpose. That gap is the signal no rule-based system can generate. It is also the diagnostic: if it persists, the prompt architecture needs revision, not the model.

---

## 8. How we grade it — evals

**The insight:** task completion metrics always look good. An agent that never fails to fire tools scores 5/5 on completion forever. That number tells you nothing about whether it served the creator.

**Three dimensions graded per session:**

| Dimension | What it measures |
|---|---|
| Tool accuracy | Did the agent call the right tools? |
| Goal completion | Did it finish what was literally asked? |
| **Creative intent** | Did the output serve what the user *actually* wanted? ← the signal that matters |

**The trend line on creative intent** is the diagnostic for whether memory is working. Improving = behavioral memory is doing its job. Flat or dropping = the prompt architecture needs revision.

**Pinecone RAG pipeline** solves the scale problem. Per-turn LLM grading costs $0.003/call and takes 2–3s. The RAG path: embed the turn → query the `stil-evals-v1` index → reuse the nearest neighbor's score if similarity ≥ 0.88 (<200ms, $0). Every Haiku-graded turn is stored back to Pinecone. The index compounds. Target: ~70% of eval calls skip Haiku at production volume.

---

## 9. KPIs — how we know it's working

### Activation
| Metric | Target | What it signals |
|---|---|---|
| % new users who fire ≥1 tool call in session 1 | >70% | Creator reached the core loop |
| Time to "Style active" banner | <3 min | Aha moment speed |
| % with style profile after session 1 | >80% | Memory loop initiated |

### Retention (the memory working signal)
| Metric | Target | What it signals |
|---|---|---|
| Session 2 return rate (7-day) | >50% | Saw enough value to come back |
| Session 5 return rate (30-day) | >30% | Profile has enough data to feel meaningfully personal |
| % of sessions where style auto-applied | Trending up over time | Creator stopped re-specifying preferences |
| % sessions where user accepted edits without overrides | >60% at session 5+ | Memory is accurate |

### Quality
| Metric | Target | What it signals |
|---|---|---|
| Creative intent score trend | Improving across sessions | Behavioral memory is serving creative goals |
| Feed Cohesion Score improvement | +15 pts avg by session 10 | Drift is being caught and corrected |
| RAG hit rate in eval pipeline | >40% by session 30, >70% at scale | Eval infrastructure is compounding |

### Growth (PLG)
| Metric | Target | What it signals |
|---|---|---|
| Organic referral rate | >15% of new signups | Feed Cohesion Score / style brief sharing driving word-of-mouth |
| Style Brief PDF shares (v0.2) | >20% of active users | Shareable artifact is a growth hook |
| Canva Apps SDK installs (v0.3) | — | Distribution unlock metric |

### For Adobe
| Metric | What it signals |
|---|---|
| CC plan retention: Stil users vs. control | Does behavioral memory reduce churn? |
| Cross-product activation: % of Stil users also using Firefly or Express | Is Stil driving Adobe ecosystem depth? |
| CC upgrade rate from free-tier Stil users | Is the style profile a conversion lever? |

---

## 10. PLG — how this grows

Stil is designed to grow through usage, not sales. Four loops:

**Loop 1 — Zero-friction activation.** No training data. No setup form. No configuration. Upload a photo, type a request, get a style profile. Every competitor that learns style (Imagen, Aftershoot) asks for 2,000+ photos before the product is useful. Stil delivers value in the first session. That is the activation wedge.

**Loop 2 — Compounding retention.** The profile gets smarter every session. A creator at session 10 has a meaningfully better experience than session 1. This creates organic retention: the behavioral data in Stil's profile is the creator's property — and it's only in Stil. Switching cost grows without a lock-in mechanism.

**Loop 3 — Shareable artifacts as growth hooks.**
- **Feed Cohesion Score** — a creator who goes from 61 to 84 screenshotting it is product marketing. "How did you get so consistent?" → Stil.
- **Style Brief PDF** (v0.2) — creators share aesthetic briefs with clients, agencies, social managers → passive distribution in professional networks.
- **Platform export grid** — beautiful side-by-side crops for every platform → shareable before/after content.

**Loop 4 — Distribution through Canva (v0.3).** Canva Apps SDK is a public API with 265 million MAU. A Stil plugin inside Canva means: every time a creator opens Canva, their style profile is already there. This is not a head-on fight with Canva — it is a distribution strategy. Stil's behavioral memory travels into an ecosystem Adobe does not own.

**For Adobe specifically:** a creator whose style profile compounds inside the Adobe suite (Lightroom sessions → Firefly generations → Express designs, all informed by the same behavioral profile) has a structural reason to stay on Creative Cloud. Stil is a retention mechanism dressed as a creativity tool.

---

## 11. Where this leads — the Adobe agentic opportunity

Stil was built to answer three questions:
1. Can behavioral memory outperform declared memory in multi-session creative workflows?
2. Can creative intent be graded separately from task completion — and does the distinction matter?
3. Can a conversational interface handle complex multi-step creative workflows without re-briefing?

All three: **yes.** And every design decision maps to a requirement the FF Agentic harness needs to resolve.

| Decision in Stil | What it surfaces for Adobe |
|---|---|
| `choices_log` priority over `style_signature` | Harness must own memory priority rules — not each agent independently |
| Frequency analysis at injection time | Memory infra needs behavioral pattern analysis, not just recency |
| Creative intent as eval dimension | Eval pipeline needs intent as first-class signal, not just task completion |
| JSONL tool-call-level session logging | CHS must log at tool call level, not message level |
| Pinecone RAG for evals | Eval infra needs an embedding store from day one |

**The Adobe-specific opportunity:** a creator's visual style as a persistent, portable asset — one that travels across Firefly, Express, Lightroom, and Canva, and compounds with every editing session. The creator who has 50 sessions in Stil has built an asset. Move to a competitor and you start over. That is the moat.

**Built in weeks, not months.** Prototype-first. Every claim in this brief is validated in running code.

---

### The ask

Three decisions to make from this review:

1. **Ship v0.2?** — 10–15 creator research sessions + mood tags + Style Brief PDF. Validates whether behavioral memory feels accurate by session 5 with real professionals. Low cost, high signal.
2. **Fund the Canva SDK integration (v0.3)?** — 265M MAU, public API, zero gatekeeping. The distribution unlock. Requires engineering allocation, no Adobe partnership needed.
3. **Commission the FF Agentic harness reference design (v0.5)?** — Every architectural decision in Stil maps to a harness requirement. This prototype de-risks the harness build. Requires alignment with the FF Agentic team on scope and timeline.

---

## 12. What ships next

### v0.2 — Validate and deepen *(Jun–Jul 2026)*
| What | Why | Success signal |
|---|---|---|
| Mood tags on style profile | Fills the gap between tool calls and aesthetic intent — "editorial," "warm lifestyle," "dark moody" | >60% of users tag within 3 sessions |
| Session comparison view | Makes memory *visible* — side-by-side before/after across sessions builds trust | Opened by >40% of active users |
| Style Brief PDF export | Creator shares aesthetic brief with clients/social team — **PLG hook** | >20% share rate; organic agency distribution |
| Shared team profiles | One creator's profile → team → org-level adoption | First team accounts created |
| 10–15 creator research sessions | Validate memory accuracy with real professionals | Does behavioral memory feel accurate by session 5? |

### v0.3 — Distribution unlock *(Aug–Sep 2026)*
| What | Why | Success signal |
|---|---|---|
| Canva Apps SDK integration | 265M MAU, public API, zero gatekeeping — largest PLG surface available | First 1,000 Canva-sourced activations |
| Style profile portability API | Stil profile readable by Firefly, CapCut, any tool | First third-party integration live |
| Mobile-first session flow | Creators edit on mobile; Streamlit is a demo constraint | Mobile session starts >30% |

### v0.4 — Expand the canvas *(Q1 2027)*
| What | Why | Success signal |
|---|---|---|
| Video workflow memory | Short-form video is the primary format; memory extends to frame rate, caption style, transitions | First video-specific style profiles created |
| Shared team memory | Agency teams need a shared aesthetic layer, not just individual profiles | First agency team onboarded |
| Feed Cohesion Score benchmarks | Creator compares their score to others in their category | Benchmark data published |

### v0.5 — Strategic *(Adobe-dependent, Q2 2027)*
| What | Why |
|---|---|
| Stil architecture as FF Agentic harness reference design | Every decision in Stil maps to a harness requirement — behavioral memory priority rules, intent grading, RAG eval infra. The prototype that de-risks the harness build. |

---

*Full architecture and feature spec: [PRD.md](PRD.md)*
*Workflow diagrams (eval pipeline + style injection): [WORKFLOW_DIAGRAMS.md](WORKFLOW_DIAGRAMS.md)*
*Competitive benchmarking: [COMPETITORS.md](COMPETITORS.md)*
*Prototype: `cd stil && streamlit run app.py`*
