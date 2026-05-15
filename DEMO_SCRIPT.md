# Stil — VP Demo Script
**8 minutes live · 2 minutes Q&A · May 2026**

---

## Setup (before the VP walks in)

- App running at `http://localhost:8501`
- Style profile **cleared** — start fresh so session 1 is genuine
- Two photos staged and ready to upload: a portrait for session 1, a landscape for session 2
- Insights tab: run evals in advance so the chart is ready (evals take ~30s)
- Have the brief open on a second screen or printed

---

## Scene 1 — The problem (60 seconds)

**Say:**
> "207 million creators. Every one of them did this today."

Point to the brief or say aloud:
> "Apply the warm filter — *again.* Crop to square — *again.* Set export to 1080×1080 — *again.* Bump brightness +20 — *again.*"
>
> "None of these are creative decisions. They were made months ago. But every tool resets. Lightroom resets. Canva resets. Every AI tool resets. 83% of users say having to repeat context to AI is their biggest frustration. 43% of brands say they can't maintain visual consistency across platforms.
>
> "Creators don't notice the drift in the moment. They notice it six months later when they scroll their own feed and it no longer looks like theirs. The word that shows up verbatim across Lightroom forums and AI tool reviews: *starting from scratch.*"

**Then:**
> "Let me show you what it looks like when the tool actually holds the memory."

---

## Scene 2 — Session 1: teaching it once (90 seconds)

**Open the Edit tab. Upload the portrait photo.**

**Say:**
> "First session. No setup. No configuration. No training library. Just upload and type."

**Type in chat:**
```
Warm editorial look, square crop, export for Instagram
```

**As tools fire, narrate each pill:**
> "Watch the tool pills. Claude isn't just replying — it's deciding which tools to call, executing them, observing each result, deciding what's next."
>
> ⚡ `apply_filter` fires → ✓ resolved: *"That's the warm filter."*
> ⚡ `adjust_brightness` fires → ✓ resolved: *"Brightness bump."*
> ⚡ `crop_image` fires → ✓ resolved: *"Square crop."*
> ⚡ `set_export_preset` fires → ✓ resolved: *"Instagram preset set."*

**Point at the before/after preview:**
> "Before. After. Warm, square, Instagram-ready."

**Point at the sidebar style profile:**
> "Now look here. The style profile just wrote itself. Not from what she said — from what she *did.* The tool calls are the source of truth. No AI paraphrasing. The literal record of what happened."

---

## Scene 3 — Session 2: the aha moment (60 seconds)

**This is the centrepiece. Slow down here.**

**Clear the chat / start new session. Upload the second photo.**

**Say:**
> "Session 2. Different photo. Watch what I type."

**Type in chat — pause before hitting send:**
```
Edit my photo
```

**Hit send. Let the silence land.**

**As the Style active banner appears:**
> "✦ Style active — warm · square · instagram. She didn't say warm. She didn't say square. She didn't say Instagram. She said: *edit my photo.*"

**As tools fire automatically:**
> "Same four tools. Same aesthetic. Applied from the choices log."

**Show the before/after:**
> "By session 10, the profile knows she prefers warm 8 out of 11 sessions. That the last three sessions were always square. That Instagram is her primary platform. It surfaces that pattern — dominant preference versus recent divergence — at prompt time. Not left to the model to figure out from raw history."

---

## Scene 4 — Style tab: transparency (30 seconds)

**Click ◑ Style.**

**Say:**
> "Two layers. The choices log — deterministic, written directly from tool calls. The style signature — what Haiku extracted from the conversation transcript, the aesthetic intent the tool calls can't capture. The choices log always wins when they conflict."
>
> "Every field is editable. The raw JSON is always visible. Creators can trust it because they can see exactly what's in it."

---

## Scene 5 — Feed tab: the drift problem solved (60 seconds)

**Click ⊡ Feed. Upload 4–5 photos from the assets folder.**

**Run the Feed Cohesion Score.**

**Say:**
> "61 out of 100. Brightness inconsistent. Saturation varies."
>
> "She posted 180 times. None of her tools told her this was happening. Stil is the first tool that can measure feed consistency objectively — not with an AI opinion, but with Pillow variance analysis across color temperature, brightness, contrast, and saturation. Zero API calls. A number, not a feeling."
>
> "This is the compounding problem. 200 micro-decisions made under time pressure, across three tools, at varying energy levels. Stil catches it before the creator has to scroll back six months to notice."

---

## Scene 6 — Insights tab: the eval signal (60 seconds)

**Click ◎ Insights. The eval results should already be loaded.**

**Point at the three score cards:**
> "Three dimensions. Tool accuracy — did it call the right tools? Goal completion — did it finish what was literally asked? Creative intent — did the output serve what the user *actually* wanted?"
>
> "The first two always look good. An agent that never fails to fire tools scores 5/5 on completion forever. That number tells you nothing about whether it served the creator."

**Point at the creative intent trend line:**
> "This line — creative intent over sessions — is the diagnostic for whether memory is working. Improving means the behavioral profile is doing its job. Flat or dropping means the prompt architecture needs revision. Without this signal, there's no way to know if memory is actually helping."

**Point at the RAG note (if visible in UI) or say:**
> "Graded by Haiku. But not every turn — we use Pinecone RAG. Embed the turn, find the nearest graded example, reuse the score if similarity is above 0.88. That's under 200 milliseconds and costs nothing. Every new grade compounds the index. Target: 70% of eval calls skip Haiku at production volume."

---

## Scene 7 — The close (45 seconds)

**Navigate back to Edit tab. Show the Style active banner.**

**Say:**
> "What Adobe has: Lightroom — 74% of professional photographers. Firefly. Express. 35 million Creative Cloud subscribers.
>
> "What Adobe doesn't have: a behavioral memory layer that sits across all of them.
>
> "A creator who teaches Stil their style — 50 Lightroom sessions, 20 Firefly generations, 30 Express designs — that profile is an asset they built. It lives in Adobe. Moving to a competitor means starting from scratch.
>
> "That's the moat. And this is the prototype that proves it's buildable — in weeks, not months."

**Pause.**

> "Three decisions: ship v0.2 to validate with real creators, fund the Canva SDK integration for distribution, or scope the FF Agentic harness design. Happy to go deeper on any of them."

---

## Anticipated VP questions

**"Why not just use ChatGPT memory for this?"**
> "ChatGPT memory stores what you *say.* If a creator edits warm every session without mentioning it, ChatGPT never knows. Stil knows — because it reads tool calls, not transcripts. ChatGPT also has a 1,200-word memory cap and no editing tools. It can tell you how to edit a photo. It cannot edit it."

**"How is this different from Imagen AI?"**
> "Imagen requires 2,000 to 5,000 training photos before the AI is useful. Zero value on day one. Photographers were paying $300 a month and getting 70% accuracy. Stil starts learning from the first session. And Imagen is not conversational — batch only, locked to Lightroom Classic, wrong audience for social-first creators."

**"What would it take to put this inside Lightroom?"**
> "The behavioral memory architecture is already the right shape. The tool calls Stil executes — filter, brightness, crop, export — map directly to Lightroom operations. The missing piece is MCP, Model Context Protocol, which connects Stil's agent to Lightroom's actual editing engine. That's a v0.3 conversation and a relatively contained engineering scope."

**"What's the business model?"**
> "$15 per month individual creator pricing. PLG path: Feed Cohesion Score is shareable, Style Brief PDF travels into agency workflows, Canva Apps SDK is 265 million MAU with a public API. For Adobe specifically the value is retention, not revenue — a creator whose style profile compounds inside Creative Cloud has a structural reason to stay."

**"How do we know the memory is actually accurate?"**
> "Two ways. One: the creative intent trend line in Insights — if it's improving across sessions, the behavioral memory is serving creative goals. Two: v0.2 includes 10–15 creator research sessions specifically to validate whether the profile feels accurate by session 5. That's the next milestone."

**"What does 'agentic' actually mean here — isn't this just a chatbot?"**
> "The test: if you replaced Claude with hardcoded if/else logic, would Stil still work? A chatbot: yes. Stil: no. Claude decides which tools to call based on what the user said *and* what the previous tools just returned. Remove the reasoning and the system breaks. That's the line."

---

## Timing guide

| Scene | Time | Cumulative |
|---|---|---|
| Scene 1 — The problem | 60s | 1:00 |
| Scene 2 — Session 1, tools fire | 90s | 2:30 |
| Scene 3 — Session 2, aha moment | 60s | 3:30 |
| Scene 4 — Style tab | 30s | 4:00 |
| Scene 5 — Feed Cohesion Score | 60s | 5:00 |
| Scene 6 — Insights / evals | 60s | 6:00 |
| Scene 7 — The close + ask | 45s | 6:45 |
| Buffer | 75s | 8:00 |
| Q&A | 2:00 | 10:00 |

---

## What to have ready

| Item | Where |
|---|---|
| App running | `http://localhost:8501` |
| Style profile cleared | Delete `stil/style_profile.json` before demo |
| Portrait photo for session 1 | `stil/assets/portrait_warm_natural_light.jpg` |
| Landscape photo for session 2 | `stil/assets/warm_golden_hour_outdoor.jpg` |
| 4–5 photos for Feed tab | Any 4–5 from `stil/assets/` |
| Evals pre-run | Click "Run evals" in Insights tab before VP arrives |
| PRD_BRIEF on screen 2 | For the market size numbers in Scene 1 |
