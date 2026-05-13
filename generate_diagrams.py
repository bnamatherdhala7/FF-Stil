"""
generate_diagrams.py
Run: python3 generate_diagrams.py
Outputs: diagram_style_flow.png, diagram_eval_flow.png
"""

import sys
sys.path.insert(0, "/Users/bharatnamatherdhala/Library/Python/3.9/lib/python/site-packages")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


# ─── Shared helpers ───────────────────────────────────────────────────────────

FONT = "DejaVu Sans"

C_DARK   = "#0F0E1C"   # primary text
C_ACCENT = "#6B4EFF"   # violet
C_GREEN  = "#22C55E"
C_ORANGE = "#F97316"
C_BLUE   = "#1DA1F2"
C_PINK   = "#E1306C"
C_MUTED  = "#9494AE"
C_BG     = "#F8F7FC"
C_WHITE  = "#FFFFFF"
C_BORDER = "#E4E0F5"
C_PURPLE_BG = "#EDE8FF"


def box(ax, x, y, w, h, label, sublabel=None,
        fc=C_WHITE, ec=C_BORDER, tc=C_DARK, radius=0.015,
        fontsize=9, subfontsize=7.5, bold=False):
    rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle=f"round,pad=0.005,rounding_size={radius}",
                          linewidth=1.2, edgecolor=ec, facecolor=fc, zorder=2)
    ax.add_patch(rect)
    dy = 0.008 if sublabel else 0
    ax.text(x, y + dy, label,
            ha="center", va="center", fontsize=fontsize,
            fontfamily=FONT, color=tc, zorder=3,
            fontweight="bold" if bold else "normal", wrap=False)
    if sublabel:
        ax.text(x, y - 0.022, sublabel,
                ha="center", va="center", fontsize=subfontsize,
                fontfamily=FONT, color=C_MUTED, zorder=3)


def arrow(ax, x1, y1, x2, y2, color=C_MUTED, lw=1.4):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->,head_width=0.012,head_length=0.012",
                                color=color, lw=lw),
                zorder=4)


def label_arrow(ax, x, y, text, color=C_MUTED):
    ax.text(x, y, text, ha="center", va="center",
            fontsize=6.5, fontfamily=FONT, color=color,
            bbox=dict(fc=C_BG, ec="none", pad=1), zorder=5)


def section_header(ax, x, y, w, text, color=C_ACCENT):
    ax.text(x, y, text.upper(), ha="center", va="center",
            fontsize=6, fontfamily=FONT, color=color,
            fontweight="bold", letter_spacing=0.06, zorder=3)


# ─── Diagram 1: Style-to-Edit flow ────────────────────────────────────────────

def make_style_flow():
    fig, ax = plt.subplots(figsize=(8, 14))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Title
    ax.text(0.5, 0.975, "Style Memory → Edit Flow",
            ha="center", va="top", fontsize=13, fontfamily=FONT,
            color=C_DARK, fontweight="bold")
    ax.text(0.5, 0.958, "How Stil injects your style profile and applies it to a new photo",
            ha="center", va="top", fontsize=8, fontfamily=FONT, color=C_MUTED)

    # 1. User input
    box(ax, 0.5, 0.91, 0.72, 0.038,
        "User uploads photo + types request",
        sublabel='"Edit my photo"  ·  session 2+ (profile exists)',
        fc=C_PURPLE_BG, ec=C_ACCENT, tc=C_DARK, bold=True)

    arrow(ax, 0.5, 0.891, 0.5, 0.873)

    # 2. load_style
    box(ax, 0.5, 0.858, 0.48, 0.028,
        "load_style()", sublabel="reads style_profile.json",
        fc=C_WHITE, ec=C_BORDER)

    arrow(ax, 0.5, 0.844, 0.5, 0.826)

    # 3. System prompt box — big
    prompt_y = 0.77
    rect = FancyBboxPatch((0.08, 0.708), 0.84, 0.118,
                          boxstyle="round,pad=0.005,rounding_size=0.012",
                          linewidth=1.5, edgecolor=C_ACCENT, facecolor="#F5F2FF", zorder=2)
    ax.add_patch(rect)
    ax.text(0.5, 0.822, "build_system_prompt()  —  strict token budget",
            ha="center", va="center", fontsize=8.5, fontfamily=FONT,
            color=C_ACCENT, fontweight="bold", zorder=3)

    rows = [
        (C_MUTED,  "#FAFAFE", "Base persona + task instructions",   "max 200 tokens"),
        ("#166534","#F0FFF4", "choices_log  ← injected first (highest trust)",
                              "filter: warm (8/11 sessions) · crop: square · export: instagram · brightness: +20 avg   |   max 60 tokens"),
        ("#92400E","#FFF9F0", "style_signature  ← fills gaps choices_log doesn't cover",
                              '"clean editorial warmth; portrait-first; avoids heavy vignettes"   |   max 40 tokens'),
        (C_MUTED,  "#F8F7FC", "EXIF camera context",
                              "Sony A7III · ISO 3200 · f/1.8 → noise-aware suggestions   |   max 20 tokens"),
    ]
    row_h = 0.022
    top = 0.807
    for tc2, fc2, label2, sub2 in rows:
        y2 = top - row_h / 2
        rx = FancyBboxPatch((0.11, y2 - row_h/2 + 0.001), 0.78, row_h - 0.002,
                            boxstyle="round,pad=0.003,rounding_size=0.006",
                            linewidth=0.6, edgecolor=C_BORDER, facecolor=fc2, zorder=3)
        ax.add_patch(rx)
        ax.text(0.15, y2 + 0.004, label2, ha="left", va="center",
                fontsize=7, fontfamily=FONT, color=tc2, fontweight="bold", zorder=4)
        ax.text(0.15, y2 - 0.006, sub2, ha="left", va="center",
                fontsize=6, fontfamily=FONT, color=C_MUTED, zorder=4)
        top -= row_h

    ax.text(0.5, 0.712, "TOTAL: ~320 tokens",
            ha="center", va="center", fontsize=7, fontfamily=FONT,
            color=C_MUTED, fontstyle="italic", zorder=3)

    arrow(ax, 0.5, 0.708, 0.5, 0.688)

    # 4. Claude reasons
    box(ax, 0.5, 0.674, 0.52, 0.028,
        "Claude reasons", sublabel="style profile = ground truth  ·  request = refinement",
        fc=C_WHITE, ec=C_BORDER)

    arrow(ax, 0.5, 0.660, 0.5, 0.641)

    # 5. Tool loop
    tl_y = 0.596
    rect2 = FancyBboxPatch((0.08, 0.548), 0.84, 0.093,
                           boxstyle="round,pad=0.005,rounding_size=0.012",
                           linewidth=1.5, edgecolor=C_GREEN, facecolor="#F0FFF4", zorder=2)
    ax.add_patch(rect2)
    ax.text(0.5, 0.638, "Agentic Tool Loop  —  Claude decides, harness executes",
            ha="center", va="center", fontsize=8, fontfamily=FONT,
            color="#166534", fontweight="bold", zorder=3)

    tools = [
        ('apply_filter("warm")',           "✓  warm filter applied"),
        ('adjust_brightness(+20)',         "✓  brightness +20"),
        ('crop_image("square")',           "✓  1:1 crop"),
        ('set_export_preset("instagram")', "✓  export preset set"),
    ]
    t_top = 0.623
    for call, result in tools:
        ax.text(0.18, t_top, call, ha="left", va="center",
                fontsize=6.8, family="monospace", color="#0F6645", zorder=3)
        ax.text(0.75, t_top, result, ha="left", va="center",
                fontsize=6.5, fontfamily=FONT, color=C_GREEN, zorder=3)
        ax.plot([0.16, 0.86], [t_top - 0.005, t_top - 0.005],
                color=C_BORDER, lw=0.4, zorder=2)
        t_top -= 0.017

    arrow(ax, 0.5, 0.548, 0.5, 0.528)

    # 6. Preview
    box(ax, 0.5, 0.513, 0.72, 0.030,
        "Pillow renders preview  (no API call)",
        sublabel="Before / After  ·  Platform exports: Instagram 1:1  Reels 9:16  Twitter 16:9  LinkedIn 4:5",
        fc="#EFF6FF", ec=C_BLUE)

    arrow(ax, 0.5, 0.498, 0.5, 0.478)

    # 7. Two parallel branches
    ax.text(0.5, 0.472, "Post-session — two things happen in parallel",
            ha="center", va="center", fontsize=7.5, fontfamily=FONT,
            color=C_DARK, fontweight="bold")

    # Branch arrows
    arrow(ax, 0.34, 0.462, 0.27, 0.445)
    arrow(ax, 0.66, 0.462, 0.73, 0.445)

    box(ax, 0.27, 0.415, 0.38, 0.056,
        "choices_log updated",
        sublabel="FROM TOOL CALLS DIRECTLY\nDeterministic · no AI\nMost recent action wins\nChange mind → auto-updates",
        fc="#F0FFF4", ec=C_GREEN, tc="#166534", fontsize=7.5, subfontsize=6.5)

    box(ax, 0.73, 0.415, 0.38, 0.056,
        "style_signature updated",
        sublabel="Haiku reads transcript\nExtracts aesthetic intent\n(what tool calls can't say)\nMerges — never overwrites",
        fc="#FFF9F0", ec=C_ORANGE, tc="#92400E", fontsize=7.5, subfontsize=6.5)

    # Merge arrows
    arrow(ax, 0.27, 0.387, 0.27, 0.368)
    arrow(ax, 0.73, 0.387, 0.73, 0.368)
    arrow(ax, 0.27, 0.358, 0.47, 0.340)
    arrow(ax, 0.73, 0.358, 0.53, 0.340)

    # 8. Save
    box(ax, 0.5, 0.326, 0.52, 0.028,
        "style_profile.json saved",
        sublabel="Sidebar updates live  ·  ✓ Style profile updated",
        fc=C_WHITE, ec=C_BORDER)

    arrow(ax, 0.5, 0.312, 0.5, 0.292)

    # 9. Next session
    box(ax, 0.5, 0.276, 0.56, 0.030,
        "✦  Next session — style already injected before user types",
        sublabel="warm  ·  square  ·  instagram  ·  built from N edits",
        fc=C_PURPLE_BG, ec=C_ACCENT, tc=C_ACCENT, bold=True)

    # Next steps box
    ns_y = 0.21
    rect3 = FancyBboxPatch((0.08, 0.155), 0.84, 0.082,
                           boxstyle="round,pad=0.005,rounding_size=0.012",
                           linewidth=1.2, edgecolor=C_BORDER, facecolor=C_WHITE, zorder=2)
    ax.add_patch(rect3)
    ax.text(0.5, 0.234, "Next Steps",
            ha="center", va="center", fontsize=8.5, fontfamily=FONT,
            color=C_DARK, fontweight="bold", zorder=3)
    next_steps = [
        "v0.2  →  Mood tags + session comparison + style brief PDF export",
        "v0.3  →  Canva Apps SDK integration (150M MAU) — real tool execution",
        "v0.4  →  Video workflows + shared team memory (enterprise unlock)",
        "v0.5  →  Stil memory/prompt architecture as FF Agentic harness reference design",
    ]
    ns_top = 0.222
    for step in next_steps:
        ax.text(0.16, ns_top, "→", ha="center", va="center",
                fontsize=7, fontfamily=FONT, color=C_ACCENT, zorder=3)
        ax.text(0.19, ns_top, step, ha="left", va="center",
                fontsize=7, fontfamily=FONT, color=C_DARK, zorder=3)
        ns_top -= 0.016

    # Footer
    ax.text(0.5, 0.04, "Stil  ✦  prototype shipped May 2026  ·  github.com/bnamatherdhala7/FF-Stil",
            ha="center", va="center", fontsize=6.5, fontfamily=FONT, color=C_MUTED)

    plt.tight_layout(pad=0.3)
    plt.savefig("diagram_style_flow.png", dpi=180, bbox_inches="tight",
                facecolor=C_BG)
    plt.close()
    print("Saved diagram_style_flow.png")


# ─── Diagram 2: Eval pipeline ─────────────────────────────────────────────────

def make_eval_flow():
    fig, ax = plt.subplots(figsize=(8, 13))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.5, 0.975, "Eval Pipeline — How Sessions Are Graded",
            ha="center", va="top", fontsize=13, fontfamily=FONT,
            color=C_DARK, fontweight="bold")
    ax.text(0.5, 0.958, "Pinecone RAG accelerated · Haiku fallback · creative intent as the primary signal",
            ha="center", va="top", fontsize=8, fontfamily=FONT, color=C_MUTED)

    # 1. Session ends
    box(ax, 0.5, 0.910, 0.72, 0.038,
        "Session ends",
        sublabel="write_session_log() → logs/session_2026-05-12T14:32.jsonl",
        fc=C_PURPLE_BG, ec=C_ACCENT, tc=C_DARK, bold=True)

    # JSONL example
    ax.text(0.5, 0.870,
            '{"type":"message",   "data":{"role":"user","content":"..."}}   '
            '{"type":"tool_call", "data":{"tool":"apply_filter",...}}',
            ha="center", va="center", fontsize=5.8, fontfamily="monospace",
            color=C_MUTED, zorder=3)

    arrow(ax, 0.5, 0.857, 0.5, 0.838)

    # 2. Load + build turns
    box(ax, 0.5, 0.824, 0.60, 0.028,
        "load_all_sessions()  →  build_turns()",
        sublabel="reads logs/*.jsonl · pairs user ↔ agent messages into gradeable turns",
        fc=C_WHITE, ec=C_BORDER)

    arrow(ax, 0.5, 0.810, 0.5, 0.791)

    # 3. Embed
    box(ax, 0.5, 0.777, 0.52, 0.028,
        "Embed turn text",
        sublabel="Pinecone Inference · multilingual-e5-large · 1024 dimensions",
        fc=C_WHITE, ec=C_BORDER)

    arrow(ax, 0.5, 0.763, 0.5, 0.744)

    # 4. Query
    box(ax, 0.5, 0.730, 0.52, 0.028,
        "Query stil-evals-v1 index",
        sublabel="top_k = 3 nearest neighbors",
        fc=C_WHITE, ec=C_BORDER)

    arrow(ax, 0.5, 0.716, 0.5, 0.697)

    # 5. Decision diamond
    d_x, d_y, d_w, d_h = 0.5, 0.676, 0.16, 0.036
    diamond = plt.Polygon(
        [(d_x, d_y + d_h), (d_x + d_w, d_y), (d_x, d_y - d_h), (d_x - d_w, d_y)],
        closed=True, fc="#FFF9F0", ec=C_ORANGE, lw=1.4, zorder=2)
    ax.add_patch(diamond)
    ax.text(d_x, d_y + 0.005, "similarity", ha="center", va="center",
            fontsize=7, fontfamily=FONT, color=C_DARK, fontweight="bold", zorder=3)
    ax.text(d_x, d_y - 0.010, "≥ 0.88?", ha="center", va="center",
            fontsize=7, fontfamily=FONT, color=C_DARK, zorder=3)

    # YES branch → left
    arrow(ax, d_x - d_w, d_y, 0.22, d_y, color=C_GREEN)
    label_arrow(ax, 0.36, d_y + 0.012, "YES", color=C_GREEN)

    # NO branch → right
    arrow(ax, d_x + d_w, d_y, 0.78, d_y, color=C_ORANGE)
    label_arrow(ax, 0.64, d_y + 0.012, "NO", color=C_ORANGE)

    # RAG path
    box(ax, 0.22, 0.620, 0.34, 0.080,
        "RAG PATH",
        sublabel="Reuse nearest neighbor's\nscores directly\n\ntool_accuracy:   4\ngoal_completion: 5\ncreative_intent: 3\n\n< 200ms  ·  $0",
        fc="#F0FFF4", ec=C_GREEN, tc="#166534", bold=True, fontsize=8, subfontsize=7)

    # Haiku path
    box(ax, 0.78, 0.620, 0.34, 0.080,
        "HAIKU PATH",
        sublabel="claude-haiku-4-5 grades turn\n\ntool_accuracy    1–5\ngoal_completion  1–5\ncreative_intent  1–5\n\n~2–3s  ·  $0.003/turn",
        fc="#FFF9F0", ec=C_ORANGE, tc="#92400E", bold=True, fontsize=8, subfontsize=7)

    # Store back
    arrow(ax, 0.78, 0.580, 0.78, 0.548)
    box(ax, 0.78, 0.533, 0.34, 0.030,
        "Store to Pinecone index",
        sublabel="index compounds — RAG hit rate grows over time",
        fc=C_WHITE, ec=C_BORDER, fontsize=7.5)

    # Index growth note
    ax.text(0.78, 0.495,
            "session 1–10: 100% Haiku\n"
            "session 11–30: ~40% RAG\n"
            "session 31+:  ~70%+ RAG",
            ha="center", va="center", fontsize=6.5, fontfamily=FONT,
            color=C_MUTED, style="italic", zorder=3)

    # Merge arrows down
    arrow(ax, 0.22, 0.580, 0.22, 0.430)
    arrow(ax, 0.78, 0.470, 0.78, 0.430)
    arrow(ax, 0.22, 0.430, 0.47, 0.415)
    arrow(ax, 0.78, 0.430, 0.53, 0.415)

    # 6. Aggregate
    box(ax, 0.5, 0.400, 0.52, 0.030,
        "aggregate_scores()  +  generate_health_summary()",
        sublabel="avg per dimension · Haiku writes 3-para PM health report",
        fc=C_WHITE, ec=C_BORDER)

    arrow(ax, 0.5, 0.385, 0.5, 0.366)

    # 7. Display
    disp_y = 0.310
    rect4 = FancyBboxPatch((0.08, 0.255), 0.84, 0.111,
                           boxstyle="round,pad=0.005,rounding_size=0.012",
                           linewidth=1.5, edgecolor=C_BORDER, facecolor=C_WHITE, zorder=2)
    ax.add_patch(rect4)
    ax.text(0.5, 0.362, "Displayed in Insights tab",
            ha="center", va="center", fontsize=8.5, fontfamily=FONT,
            color=C_DARK, fontweight="bold", zorder=3)

    # Score cards
    cards = [
        (0.24, "Tool accuracy",  "4.2 / 5", C_GREEN,  "#F0FFF4", "Right tools?"),
        (0.50, "Goal completion","4.7 / 5", C_GREEN,  "#F0FFF4", "Task finished?"),
        (0.76, "Creative intent","3.1 / 5", C_ORANGE, "#FFF9F0", "Served creative goal? ←"),
    ]
    for cx, title, score, sc, bg, sub in cards:
        cr = FancyBboxPatch((cx - 0.13, 0.262), 0.26, 0.082,
                            boxstyle="round,pad=0.003,rounding_size=0.008",
                            linewidth=1, edgecolor=sc, facecolor=bg, zorder=3)
        ax.add_patch(cr)
        ax.text(cx, 0.338, title, ha="center", va="center",
                fontsize=6.5, fontfamily=FONT, color=C_MUTED,
                fontweight="bold", zorder=4)
        ax.text(cx, 0.318, score, ha="center", va="center",
                fontsize=11, fontfamily=FONT, color=sc,
                fontweight="bold", zorder=4)
        ax.text(cx, 0.270, sub, ha="center", va="center",
                fontsize=6, fontfamily=FONT, color=C_MUTED, zorder=4)

    ax.text(0.5, 0.258,
            "Bar chart per turn  ·  Creative intent trend over sessions  ·  3-para health summary",
            ha="center", va="center", fontsize=6.5, fontfamily=FONT, color=C_MUTED, zorder=3)

    # 8. Key insight box
    ins_y = 0.195
    rect5 = FancyBboxPatch((0.08, 0.155), 0.84, 0.072,
                           boxstyle="round,pad=0.005,rounding_size=0.012",
                           linewidth=1.2, edgecolor=C_ORANGE, facecolor="#FFF9F0", zorder=2)
    ax.add_patch(rect5)
    ax.text(0.5, 0.223,
            "creative_intent diverges from goal_completion  =  prompt architecture failure, not model failure",
            ha="center", va="center", fontsize=7.5, fontfamily=FONT,
            color="#92400E", fontweight="bold", zorder=3)
    ax.text(0.5, 0.207,
            "Session: 5/5 completion · 1/5 intent  →  Stil did exactly what was typed; missed the creative purpose.",
            ha="center", va="center", fontsize=7, fontfamily=FONT, color=C_DARK, zorder=3)
    ax.text(0.5, 0.165,
            "Fix: review build_system_prompt() priority ordering  ·  "
            "choices_log injected before style_signature?  ·  "
            "style extraction too shallow?",
            ha="center", va="center", fontsize=6.5, fontfamily=FONT, color=C_MUTED, zorder=3)

    # Next steps
    ns_rect = FancyBboxPatch((0.08, 0.068), 0.84, 0.075,
                             boxstyle="round,pad=0.005,rounding_size=0.012",
                             linewidth=1.2, edgecolor=C_BORDER, facecolor=C_WHITE, zorder=2)
    ax.add_patch(ns_rect)
    ax.text(0.5, 0.140, "Next Steps",
            ha="center", va="center", fontsize=8.5, fontfamily=FONT,
            color=C_DARK, fontweight="bold", zorder=3)
    ns_items = [
        "Build insights_v2.py: RAG eval as default path once index reaches 100+ graded turns",
        "Creator research (v0.2): validate behavioral memory vs. re-explanation rate in real sessions",
        "Canva SDK (v0.3): RAG eval pipeline runs against Canva tool calls using same index",
        "FF Agentic (v0.5): Pinecone eval store as harness-level eval infrastructure",
    ]
    ns_top2 = 0.127
    for item in ns_items:
        ax.text(0.14, ns_top2, "→", ha="center", va="center",
                fontsize=7, fontfamily=FONT, color=C_ACCENT, zorder=3)
        ax.text(0.17, ns_top2, item, ha="left", va="center",
                fontsize=6.8, fontfamily=FONT, color=C_DARK, zorder=3)
        ns_top2 -= 0.016

    # Footer
    ax.text(0.5, 0.036, "Stil  ✦  prototype shipped May 2026  ·  github.com/bnamatherdhala7/FF-Stil",
            ha="center", va="center", fontsize=6.5, fontfamily=FONT, color=C_MUTED)

    plt.tight_layout(pad=0.3)
    plt.savefig("diagram_eval_flow.png", dpi=180, bbox_inches="tight",
                facecolor=C_BG)
    plt.close()
    print("Saved diagram_eval_flow.png")


if __name__ == "__main__":
    make_style_flow()
    make_eval_flow()
    print("Done.")
