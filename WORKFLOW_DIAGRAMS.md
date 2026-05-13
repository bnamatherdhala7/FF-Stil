# Stil — Workflow Diagrams

---

## Diagram 1: How style memory edits a new photo

```
┌─────────────────────────────────────────────────────────────────────────┐
│  USER UPLOADS PHOTO + TYPES REQUEST                                      │
│  "Edit my photo"  (session 2+ — profile already exists)                  │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  load_style()                 │
              │  reads style_profile.json     │
              └───────────────┬───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  build_system_prompt()  — strict token budget                            │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Base persona + task instructions          max 200 tokens        │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │  choices_log injection  ← INJECTED FIRST (highest trust)         │   │
│  │  max 60 tokens                                                   │   │
│  │                                                                  │   │
│  │  "filter: warm (8/11 sessions — consistent preference)"          │   │
│  │  "crop: square (last 3 sessions)"                                │   │
│  │  "export: instagram (last session)"                              │   │
│  │  "brightness: +20 avg across 6 sessions"                        │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │  style_signature  ← fills gaps choices_log doesn't cover         │   │
│  │  max 40 tokens                                                   │   │
│  │                                                                  │   │
│  │  "clean editorial warmth; avoids heavy vignettes;                │   │
│  │   portrait-first, Instagram and LinkedIn audience"               │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │  EXIF camera context                       max 20 tokens        │   │
│  │  "Sony A7III · ISO 3200 · f/1.8 · 85mm"                        │   │
│  │  → high ISO: noise-aware suggestions applied automatically       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              TOTAL: ~320 tokens                          │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  Claude reasons               │
              │  style profile = ground truth │
              │  user request = refinement    │
              └───────────────┬───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  AGENTIC TOOL LOOP  (Claude decides, harness executes, result returned)  │
│                                                                          │
│  apply_filter("warm")           → ✓ Applied warm filter                 │
│       ↓ result returned to Claude                                        │
│  adjust_brightness(+20)         → ✓ Brightness +20                      │
│       ↓ result returned to Claude                                        │
│  crop_image("square")           → ✓ Cropped 1:1                         │
│       ↓ result returned to Claude                                        │
│  set_export_preset("instagram") → ✓ Export preset set                   │
│       ↓ result returned to Claude                                        │
│  Claude: task complete → responds                                        │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  PREVIEW RENDERED  (Pillow — no API call)                                │
│                                                                          │
│  Before ──────────────── After                                           │
│  [original photo]        [warm · +20 brightness · square crop]           │
│                                                                          │
│  Platform export grid:                                                   │
│  [Instagram 1:1]  [Reels 9:16]  [Twitter 16:9]  [LinkedIn 4:5]          │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  POST-SESSION  (two things happen in parallel)                           │
│                                                                          │
│  ┌──────────────────────────────┐   ┌──────────────────────────────┐    │
│  │  choices_log updated         │   │  style_signature updated      │    │
│  │  FROM TOOL CALLS DIRECTLY    │   │  Haiku reads transcript       │    │
│  │  (deterministic — no AI)     │   │  extracts aesthetic intent    │    │
│  │                              │   │  (what tool calls can't say)  │    │
│  │  filter:     warm            │   │                               │    │
│  │  crop:       square          │   │  "prefers editorial warmth;   │    │
│  │  export:     instagram       │   │   portrait-first; avoids      │    │
│  │  brightness: +20             │   │   heavy saturation"           │    │
│  │  ts: 2026-05-12              │   │                               │    │
│  │                              │   │  MERGES — never overwrites    │    │
│  │  Most recent entry wins.     │   │  existing signature           │    │
│  │  Change your mind next       │   │                               │    │
│  │  session — log updates.      │   │                               │    │
│  │  No re-briefing.             │   │                               │    │
│  └──────────────────────────────┘   └──────────────────────────────┘    │
│                              │                                           │
│  ┌───────────────────────────▼──────────────────────────────────────┐   │
│  │  style_profile.json saved                                        │   │
│  │  Sidebar updates live                                            │   │
│  │  ✓ Style profile updated banner shown                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  NEXT SESSION                 │
              │  Style already injected       │
              │  before user types a word     │
              │                              │
              │  ✦ Style active              │
              │  warm · square · instagram    │
              └───────────────────────────────┘
```

---

## Diagram 2: How evals work (Pinecone RAG pipeline)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SESSION ENDS                                                            │
│  write_session_log() → logs/session_2026-05-12T14:32.jsonl              │
│                                                                          │
│  {"type": "message",   "data": {"role": "user", "content": "..."}}      │
│  {"type": "tool_call", "data": {"tool": "apply_filter", ...}}           │
│  {"type": "message",   "data": {"role": "assistant", "content": "..."}} │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼  (triggered manually or post-session)
              ┌───────────────────────────────┐
              │  load_all_sessions()           │
              │  reads all logs/*.jsonl        │
              └───────────────┬───────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  build_turns()                 │
              │  pairs user ↔ agent messages   │
              │  into gradeable turns          │
              └───────────────┬───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  FOR EACH TURN                                                           │
│                                                                          │
│  Turn text =                                                             │
│    "User: Make this warmer, crop square, export for Instagram            │
│     Agent: Applied warm filter, +20 brightness, square crop…            │
│     Tools: apply_filter, adjust_brightness, crop_image, set_export"     │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  Embed turn text              │
              │  Pinecone Inference API       │
              │  multilingual-e5-large        │
              │  → 1024-dimension vector      │
              └───────────────┬───────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  Query stil-evals-v1 index    │
              │  top_k = 3 nearest neighbors  │
              └───────────────┬───────────────┘
                              │
               ┌──────────────┴──────────────┐
               │                             │
               ▼                             ▼
   Index ≥ 10 vectors               Index < 10 vectors
   AND similarity ≥ 0.88            OR similarity < 0.88
               │                             │
               ▼                             ▼
   ┌───────────────────────┐   ┌───────────────────────────────┐
   │  RAG PATH             │   │  HAIKU PATH                   │
   │                       │   │                               │
   │  Reuse nearest        │   │  Grade with claude-haiku-4-5  │
   │  neighbor's scores    │   │                               │
   │  directly             │   │  Rubric:                      │
   │                       │   │  tool_accuracy    1–5         │
   │  tool_accuracy:  4    │   │  goal_completion  1–5         │
   │  goal_completion: 5   │   │  creative_intent  1–5         │
   │  creative_intent: 3   │   │                               │
   │                       │   │  ~2–3s per turn · $0.003      │
   │  <200ms · $0          │   │                               │
   └──────────┬────────────┘   └──────────────┬────────────────┘
              │                               │
              │                               ▼
              │               ┌───────────────────────────────┐
              │               │  Store graded turn            │
              │               │  to Pinecone index            │
              │               │  (index compounds over time)  │
              │               └──────────────┬────────────────┘
              │                              │
              └──────────────┬───────────────┘
                             │
                             ▼
             ┌───────────────────────────────────┐
             │  As index grows:                  │
             │  session 1–10:   100% Haiku        │
             │  session 11–30:  ~40% RAG          │
             │  session 31+:    ~70%+ RAG         │
             │  (target: 70% API calls saved)     │
             └───────────────┬───────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  AGGREGATE + REPORT                                                      │
│                                                                          │
│  aggregate_scores()           → avg per dimension across all turns       │
│  generate_health_summary()    → Haiku writes 3-para PM report            │
│  write_report()               → insights_report.md                       │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  DISPLAYED IN INSIGHTS TAB                                               │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  Tool accuracy   │  │  Goal completion  │  │  Creative intent │      │
│  │     4.2 / 5      │  │     4.7 / 5       │  │    3.1 / 5  ←   │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│                                                the one that matters      │
│  Bar chart: score per turn                                               │
│  Line chart: creative intent trend over sessions  ← memory working?     │
│  3-paragraph health summary                                              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key: why creative intent is the signal that matters

```
Session scores 5/5 on goal_completion AND 1/5 on creative_intent
                        │
                        ▼
    Stil did exactly what was typed.
    It completely missed the creative purpose.
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
    This is not a          This is a prompt
    model failure.         architecture failure.
                                   │
                                   ▼
                     choices_log → style_signature
                     priority ordering is wrong,
                     OR style extraction is shallow.
                     Fix: review build_system_prompt()
                     before blaming the model.
```

---

*Full spec: [PRD.md](PRD.md) · Quick brief: [PRD_BRIEF.md](PRD_BRIEF.md)*
