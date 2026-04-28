# Stil — Product Requirements Document

**Version:** 0.4 (updated post-v0.1 ship)
**Status:** Active
**Last updated:** April 2026

---

## 0. What Stil is — one paragraph

Stil is a conversational AI assistant that remembers your visual style and applies it
automatically. You describe what you want, Stil executes it using real editing tools,
and your choices are saved to a persistent style profile. Every session after that,
Stil already knows your aesthetic — warm filters, square crops, Instagram exports —
without being told again. The profile is fully transparent and editable at all times.
The bet: visual style is portable knowledge that belongs to the creator, not to any
single tool.

---

## 1. The problem

### 1.1 Who this is for

Content creators and brand designers who produce visual content professionally or
semi-professionally. They post 3–5 times per week across Instagram, TikTok, and
LinkedIn. They have a distinct visual aesthetic — specific colour temperatures, crop
ratios, export formats — that they have developed over months or years. This is either
their livelihood or a serious side income.

**207 million content creators globally.** The creator economy is valued at $205–254B
in 2025, growing at ~23% CAGR toward $1.35T by 2035. 87% of creators already use AI
in their workflows (Artlist, 2025, n=6,500).

### 1.2 The specific problem with image editing today

A creator posts 3–5 times a week. That is 200+ pieces of content a year. Here is what
every single editing session looks like, regardless of which tool they open:

1. **Open their tool of choice** (Lightroom, Canva, CapCut, or an AI assistant)
2. **Re-select their warm filter** — the same one they chose last time, and the time before
3. **Re-crop to square** — every portrait needs this for Instagram
4. **Re-enter their export settings** — 1080×1080, JPEG, sRGB, 85% quality
5. **Re-adjust brightness** — they always go +20 for their style
6. **Repeat this for every photo, every session, across every tool**

None of these are creative decisions. They were decided months ago. But every tool
starts from zero because no tool holds the memory.

**This is not an editing speed problem. It is a consistency problem.**

The deeper consequence is visual drift. Post 1 looks exactly like the creator.
Post 47 is close. Post 180 barely is — not because their aesthetic changed, but because
200 micro-decisions made under time pressure, across three different tools, with varying
energy levels, slowly diverge from the original creative intent.

The creator does not notice it happening turn by turn. They notice it six months later
when their feed no longer looks like theirs.

**46% of a creator's working time goes to tasks other than content creation** —
formatting, distribution, and exactly this kind of repetitive technical re-entry.
Re-explaining style to AI tools is a measurable slice of this. The cumulative drift
it produces is the real cost.

### 1.3 Why existing tools do not solve this

**Tools that learn style (Imagen AI, Aftershoot):**
- Require Lightroom — locked to one tool, useless elsewhere
- Need 2,500–5,000 past edited images to train — inaccessible for most creators
- Batch processing only — no conversational interface
- Built for professional photographers, not social media creators

**Tools that hold brand memory (Typeface, Jasper, Adobe Firefly Style Kits):**
- Enterprise pricing: $49–$500+/month
- Require manual setup — you configure them, they do not learn from usage
- Locked inside their own ecosystems
- No image editing capability

**Tools that are conversational (ChatGPT, Claude, Gemini):**
- Stateless by default — forget everything at session end
- Cannot execute editing actions — they advise, they do not do
- General-purpose memory where available, not visual-style-specific
- No before/after preview of any edit

**The gap:** No tool at individual creator pricing ($10–20/month) combines persistent
cross-session visual style memory + conversational execution + real image feedback +
works from day one without a training data library.

### 1.4 Why "skill" and "memory" features don't solve this

Every major AI platform is now shipping memory. ChatGPT Memories, Claude Projects,
Notion AI, Gemini context — they all offer some form of persistent preference storage.
Adobe has Brand Kits and Style Presets. Lightroom has presets. Canva has brand kits.

None of these solve the consistency problem. Here is why.

**Skills and presets are static configuration.**
They store what you tell them. A memory feature that holds "user likes warm filters"
is a sophisticated preset. You still have to declare your preference. You still have to
update it when your preferences change. You still have to remember to apply it.
The editing burden is reduced — the consistency enforcement is not.

**Memory features store what you say. Stil stores what you do.**
There is a fundamental difference between a system that saves "I prefer warm tones"
and a system that reads `apply_filter("warm")` directly from a tool call. The first
is a declaration. The second is evidence of behavior. Declarations drift — you said
warm in January, you've been using cool since March. Evidence updates automatically,
because it is read from actual editing actions, not from what the user remembers
telling the system.

**No existing memory feature detects drift.**
If a creator switches from warm to cool over 20 sessions, no AI memory system today
gives them a signal that their feed is becoming inconsistent. They find out six months
later when they scroll back through their grid. Stil's Feed Cohesion Score quantifies
consistency across uploaded photos — objectively, before the drift becomes visible.

**No existing memory feature grades creative intent.**
Completing a task and serving a creative goal are different things. A memory-augmented
AI assistant can complete exactly what was typed and still produce output that misses
the creative purpose entirely. Stil tracks this explicitly — creative intent is scored
per session, and the trend line shows whether style injection is actually improving
output or just making it look like a style is being applied.

**The key distinction:**

| Dimension | Skill / preset / memory feature | Stil |
|---|---|---|
| Learns from | What you say ("I like warm") | What you do (`apply_filter("warm")` from tool call) |
| Updates | When you tell it to | After every session, automatically |
| Handles preference changes | You re-brief it | Choices log always reflects most recent action |
| Detects feed inconsistency | No | Yes — Feed Cohesion Score |
| Grades creative intent | No | Yes — per session, with trend chart |
| Source of truth | Stated preference | Demonstrated behavior |

The fundamental problem with skill-based memory is that it is a better preset, not a
better system. Stil is a different architecture: it observes behavior, extracts patterns
from that behavior, and enforces them — without the creator having to declare anything.

### 1.5 Market size

**TAM:** Creator economy $205B (2025) → $1.35T (2035) at 23% CAGR.
AI image editing tools: $5.1–6.3B (2025) → $39.7B by 2030 at ~39% CAGR.

**SAM:** ~45 million professional creators, 87% already using AI tools.
Estimated $750M–$1B of the AI editing market in 2025.

**SOM (Year 1):** 0.1% of 45M professional creators = 45,000 users.
At $15/month = **$8.1M ARR.**

---

## 2. The solution

### 2.1 What Stil looks like for a creator

**First session — building the profile**

> A photographer opens Stil. She uploads a portrait she just shot.
> She types: "Make this warmer, bump brightness a bit, crop square, export for Instagram."
>
> Stil reads the image. Four tools fire in sequence — apply_filter("warm"),
> adjust_brightness(+20), crop_image("square"), set_export_preset("instagram").
> A before/after preview appears. Her edited photo alongside the original.
> A confirmation bar appears: "✓ Style profile updated."

One session. Four choices. The profile now knows her aesthetic.

**Second session — no re-explanation**

> She opens Stil the next day with a new photo.
> A banner at the top: "✦ Style active — warm · square · instagram · built from 4 edits."
>
> She types: "Edit my photo."
>
> That is all. Stil reads the choices log, applies her style, shows the before/after.
> She never said "warm filter." She never said "square crop." The system already knew.

**Ten sessions later — catching drift**

> She opens the Feed tab. Uploads 8 recent photos from her grid.
> Score: 61/100. "Mostly consistent."
> Issues: "Brightness is inconsistent across your feed" · "Saturation varies — some vivid, others muted."
>
> She did not notice this happening. Stil did.

### 2.2 How Stil works — the full loop

```
Creator uploads a photo and describes what they want
                ↓
Stil reads style_profile.json
→ injects choices_log (recent tool calls) + style_signature (AI-extracted preferences)
  into the system prompt as ground truth
                ↓
Claude reasons about which tools to call, using the style profile as context
                ↓
apply_filter("warm") → adjust_brightness(+20) → crop_image("square")
→ set_export_preset("instagram")
                ↓
Pillow applies the actual edits → before/after preview shown inline
                ↓
Session saved to logs/session_TIMESTAMP.jsonl
                ↓
Two things happen in parallel:
  1. choices_log updated from tool calls (deterministic — no AI involved)
  2. style_signature updated by Haiku from conversation (captures intent beyond tool calls)
                ↓
Next session: warm · square · instagram already injected into context
```

### 2.3 Where the intelligence comes from

Stil is not intelligent because of a single AI call. The intelligence is in the
architecture — specifically, in what gets stored, in what priority, and from what source.

**Layer 1 — Behavioral ground truth (choices_log)**

Every tool call writes to the choices log directly:
`apply_filter("warm")` → `{"filter": "warm", "ts": "2026-04-28 14:32"}`

This is deterministic. No AI involved. No inference. It is a factual record of
what the creator actually did. Most recent entry wins. If they switched from warm
to cool across the last 5 sessions, the log reflects cool — not warm, regardless
of what they may have stated earlier.

This is what separates Stil from skill/preset/memory features. Those systems record
what you say. Stil records what you do. The difference matters when preferences change.

**Layer 2 — AI-extracted intent (style_signature)**

After each session, one Haiku call reads the conversation transcript and extracts
higher-order preferences: tone direction, aesthetic mood, editorial notes that do
not surface from tool calls alone. A creator who says "I want it to feel like
film from the 80s" is expressing an intent that no filter name captures — the
style_signature stores it.

**The priority rule — behavior always beats declaration**

In the next session's system prompt:
```
choices_log entry  →  first priority (what you did)
style_signature    →  fills the gaps (what Stil inferred from what you said)
```

If a creator said "I like warm" in January but has applied cool filters every
session since February, the system prompt reflects cool. The behavioral record
wins — without the creator having to update anything.

**Layer 3 — Objective consistency measurement (Feed Cohesion Score)**

Color temperature variance, brightness variance, contrast variance, saturation
variance — measured across the feed using Pillow math. The score gives creators
a number (0–100) for something they previously had no way to measure:
"Is my feed actually consistent, or does it just feel like it should be?"

**Layer 4 — Creative intent grading**

Sessions are graded on three dimensions: tool accuracy, goal completion, and
creative intent. Creative intent is the one that matters. A session can score
5/5 on completion and 1/5 on intent — Stil did exactly what was typed but
missed the creative goal. This dimension is the feedback signal for whether the
style profile is actually working.

**The combined result:** A system that does not need the creator to maintain their
own preferences. They edit. The system observes. The next session is already aligned.

### 2.3 Why conversational is the right interface

The alternative — a form, a preset selector, a brand kit configuration screen —
puts the burden of articulation on the user upfront. Most creators cannot fully
describe their aesthetic in a questionnaire. They know it when they see it.

Conversational interfaces solve this in two ways:
- **Reactive learning:** Stil extracts preferences from what users do naturally,
  without asking them to describe their aesthetic in abstract terms
- **Low friction:** "Make this warmer and crop it square" is how creators already
  think. Translating that into a menu is the friction Stil removes.

### 2.4 How Stil differs from traditional AI chat

| Dimension | Traditional AI chat | Stil |
|---|---|---|
| **Context** | Forgotten after the session | Persists across sessions — style profile updates after every edit |
| **Input** | Manual prompting every time | Automatic style extraction from conversation + EXIF metadata from image |
| **Execution** | "Here is advice on how to edit" | "I've applied your style — here is the before/after" |
| **Consistency** | Visual drift across 200 posts | Deterministic style alignment — choices log is ground truth, not AI inference |
| **Feedback** | No signal on whether it served the creative goal | Creative intent scored every session; trend chart shows improvement over time |

The consistency row is the one that matters most for the creator problem. The other rows
are table stakes for a good AI tool. Deterministic brand alignment across hundreds of
posts — enforced by a choices log that never drifts — is what Stil uniquely provides.

### 2.5 Transparency as a trust mechanism

The style profile is always visible in the sidebar and Style tab. Users see exactly
what Stil thinks they like. They can edit any field directly — tone, crop preference,
export targets, aesthetic notes. They can clear it entirely. Nothing is hidden.

This is deliberate. Creators will not trust a system that makes assumptions they
cannot inspect or correct. Transparency is how Stil earns trust, not magic.

---

## 3. Target personas

### Persona 1 — The Solo Creator (primary)
- Posts 3–5x/week on Instagram and TikTok
- Has a recognisable aesthetic: warm tones, square crops, minimal overlays
- Uses Lightroom for serious edits, Canva for quick social posts
- **Job to be done:** Apply my aesthetic without re-explaining it every time
- **Quote:** "I've told every AI tool I like warm tones. None of them remember."
- **Success signal:** "It just knows what I want now."

### Persona 2 — The Freelance Brand Designer (secondary)
- Manages 3–5 client brand accounts simultaneously
- Each client has distinct colours, crop ratios, platform export specs
- **Job to be done:** Switch between client contexts without constant re-briefing
- **Success signal:** "I brief it once per brand and it stays on-brand forever."

### Persona 3 — The Small Business Owner (tertiary)
- Runs an e-commerce brand or local service business
- Not a designer. Posts on Instagram to drive sales.
- **Job to be done:** My social posts should look like my brand, not generic AI output
- **Success signal:** "It actually looks like us."

---

## 4. What is built — v0.1

### Core editing loop

- Natural language input → agent selects and runs editing tools
- Full multimodal support: upload a photo, Stil sees it and carries it across all turns
- Images automatically compressed to stay within the Anthropic 5MB limit
- Real before/after preview: Pillow applies the actual filter, brightness, contrast,
  and crop to the uploaded image and shows both versions side by side
- Max 6 turns per session (cost guardrail)
- Full Claude API conversation history passed across turns — no context loss

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

- Two-layer profile: choices_log (deterministic) + style_signature (AI-extracted)
- Choices log: newest entry first, capped at 10, written from actual tool calls
- Style signature: extracted by Haiku after every session, merged (never overwritten)
- Priority in system prompt: choices_log > style_signature
- Color palette extraction: Pillow reads dominant colors from uploaded images,
  stored in style profile, shown as swatches in sidebar and Style tab

### Onboarding

- First-time users see a 3-field seed card: tone, primary platform, one aesthetic word
- Seeds the style profile before any conversation so session 1 is already personalised
- Sidebar shows a 3-step explainer on first visit: upload → Stil saves → next session it applies

### Value prop UX — making the memory loop visible

The memory loop only creates trust if users can see it working. Three moments make it visible:

1. **✦ Style active banner** — top of the Edit tab every return session, listing the exact
   preferences that are loaded (warm · square · instagram) and how many edits built the profile.
   Users see their style is ready before they type anything.

2. **✓ Style saved confirmation** — appears once after each completed session, confirming
   that choices were saved. Closes the feedback loop: "I edited → it was saved → next time it applies."

3. **Built from N edits** — shown in the sidebar below the profile. Makes the accumulation
   tangible: a profile built from 12 edits feels more trustworthy than one built from 1.

### Style tab

- Metric cards: tone, crop, export targets
- Color palette swatches (extracted from uploaded images via Pillow)
- **Camera profile** — camera model, focal length, aperture, ISO, exposure read from
  image EXIF metadata automatically. Displayed in the Style tab. Injected into the
  agent system prompt so editing recommendations are informed by shooting conditions
  (e.g. high-ISO shots receive noise-aware suggestions).
- Profile editor: tone, crop, export targets, and aesthetic notes are all directly editable
- Raw style_profile.json always visible
- Clear memory button

### Quality insights

- Sessions graded: tool accuracy, goal completion, creative intent (each 1–5)
- Bar chart per turn, aggregate scores, plain-English health summary
- Session trend chart: creative intent score per session over time
  (the primary validation for the core thesis — does the profile improve output?)
- creative_intent is the dimension that matters most: a session can score 5/5 on
  completion and 1/5 on intent if Stil did exactly what was typed but missed the
  creative purpose

### Smart asset search

- Natural language brief → ranked asset recommendations
- AI tags generated and cached per filename (never re-tagged — no repeat API calls)
- Results with thumbnails, tag pills, and rationale

### Out of scope for v0.1

- Cloud deployment, user accounts, or persistent storage beyond local flat files
- Video editing
- Generative image creation
- Direct social media publishing
- Vector database or semantic image search

---

## 5. What v0.1 needs to validate

| Question | How to measure |
|---|---|
| Does style extraction capture real preferences? | Profile has ≥3 populated fields after 2 sessions |
| Do returning users re-explain less? | Session re-explanation rate < 15% by session 3 |
| Does style injection improve output quality? | Creative intent score improves session 1 → session 3 |
| Is the conversational interface the right UX? | Session length 4–6 turns; D7 retention > 40% |
| Does the before/after preview increase trust? | User edits profile fields after seeing preview < 20% of sessions |
| Is $15/month a sensible price point? | Willingness-to-pay survey + conversion on free trial |

---

## 6. Technical architecture

**Stack:**
- Language: Python 3.11+
- UI: Streamlit (localhost:8501)
- AI runtime: Anthropic API — `claude-haiku-4-5` for all tasks
- Vision: Multimodal messages (base64 image + text), automatic Pillow compression
- Image processing: Pillow (filters, brightness, contrast, crop, palette extraction)
- Asset server: MCP protocol via FastMCP Python SDK
- Storage: Flat files (JSON, JSONL) — no database for v0.1

**Model rules:**

| Task | Model | Why |
|---|---|---|
| Agent loop | claude-haiku-4-5 | Fast, cheap, responsive |
| Style extraction | claude-haiku-4-5 | Tiny structured prompt |
| Insights grading | claude-haiku-4-5 | One call per turn |
| Asset tagging | claude-haiku-4-5 | Cached after first run |
| Color palette | Pillow only | No API call needed |
| Filter preview | Pillow only | No API call needed |

**Cost model:**

| Task | Cost per event |
|---|---|
| Agent loop (per session) | ~$0.01 |
| Style extraction (per session) | ~$0.002 |
| Insights grading (per turn) | ~$0.003 |
| Asset tagging (one-time per image) | ~$0.001 |

**Target: < $0.05 per active user per day.**
At $15/month subscription (~$0.50/day), gross margin is ~$14.50/user/month
before infrastructure.

**Cost guardrails:**
- System prompt: max 200 tokens
- Style injection: max 100 tokens
- Tool descriptions: max 40 tokens each
- Max turns per session: 6
- Tag cache: never re-tag the same filename
- Palette extraction: Pillow only, no API

---

## 7. Success metrics

### Primary (product quality)
- **Creative intent score ≥ 4.0/5.0** — Stil serves what users actually want
- **Style retention rate > 70%** — returning users whose profile updated ≥ once in first week
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
| Style profile too shallow to be useful | Medium | High | Richer extraction prompt; seed card on first session; profile always editable |
| Users do not trust AI to know their style | Medium | Medium | Full transparency — show raw profile; make every field editable; before/after preview |
| API costs exceed margins at scale | Low | High | Haiku model; Pillow for all image processing; 6-turn session cap; tag cache |
| Canva ships conversational style memory | Medium | High | Speed to market; multi-tool portability they structurally cannot offer |
| Adobe ships this inside Creative Cloud | Low–Medium | High | Portability across tools Adobe does not own is the structural differentiator |
| Style extraction hallucination | Low | Medium | Merge-not-overwrite strategy; user can review and correct profile directly |
| v0.1 feels like a toy without real editing | Low (now) | Medium | Real Pillow preview ships with v0.1; before/after shown after every edit |

---

## 9. Roadmap

### v0.1 — Concept validator (shipped)
Local Streamlit prototype. Style memory loop end-to-end. Multimodal vision with real
before/after preview. Color palette extraction. Onboarding seed card. Editable style
profile. Quality insights with session trend chart. Asset search. All core editing tools
including contrast and TikTok/Reels presets.

### v0.2 — Richer style model
Deepen the style profile: aesthetic mood tags (editorial, lifestyle, minimalist),
platform-specific crop/export defaults surfaced more prominently in the UI.
Export style as a shareable "creative brief" PDF — demonstrates portability before
real integrations exist. Session comparison view.

### v0.3 — Real tool integrations
**Canva Apps SDK** is the primary target: 150M MAU, public API, and an app marketplace
that solves the distribution problem. A Stil Canva App puts style memory in front of the
platform creators already use daily.
**Cloudinary** as secondary: accessible REST API, real image transformations.
Lightroom requires Adobe technology partnership — not a v0.3 engineering task.

### v0.4 — Multi-brand support
Multiple style profiles per user. Switch between client brand contexts in one click.
Primary target: freelance designers managing 3–5 client accounts.

### v0.5 — Web app + mobile
Hosted web app. Supabase for storage and auth. Mobile-first UI for editing on the go.

---

## 10. Open questions

**1. Onboarding depth vs. friction**
The seed card asks for tone, platform, and one aesthetic word. Is that enough to produce
a meaningfully personalised session 1? Or does a better first-session output require
more? Current hypothesis: keep it at 3 fields; let the profile deepen from usage.

**2. Multi-tool portability signal**
v0.1 is local-only. The core value proposition — style that travels across tools —
cannot be fully demonstrated until v0.3. How do we communicate this before integrations
exist? One option: export the style profile as a "creative brief" PDF that users can
paste into any tool. Tests whether portability resonates before building the integrations.

**3. Asset library scope**
v0.1 assumes a local folder. Real creators store images in Google Photos, iCloud,
and Lightroom. Cloud storage integrations are a prerequisite for genuine utility at v0.3+.

**4. Pricing model**
$15/month flat subscription vs. usage-based. At < $0.05/day cost, flat subscription
has strong unit economics. Usage-based lowers the barrier for casual users but
complicates messaging. Current lean: flat subscription with a 7-day free trial,
no credit card required.

**5. Platform focus**
Instagram-first vs. platform-agnostic? Instagram is the example in all UX copy.
TikTok is the faster-growing platform for the core persona and now has full tool
support (9:16 crop, 1080×1920 export). Current position: both, with Instagram
as the default in sample prompts and onboarding.
