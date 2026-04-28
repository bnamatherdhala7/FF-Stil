"""
app.py — Stil Streamlit UI
Dark sidebar · Split-panel editing · Platform export grid
Run: streamlit run app.py
"""

import base64
import io
import json
import os
import streamlit as st
import pandas as pd
from PIL import Image
from dotenv import load_dotenv
from agent import (run_agent_streaming, load_style, save_style, extract_and_save_style,
                   write_session_log, update_choices_log, extract_color_palette, extract_exif,
                   translate_brief_to_edits, format_edit_plan)
from asset_library import list_assets, find_asset
from creative_tools import preview_edits
from feed_analyzer import analyze_feed, extract_reference_style, apply_style_transfer

load_dotenv()

st.set_page_config(
    page_title="Stil",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Design tokens ────────────────────────────────────────────────────────────
# page-bg:      #F0EDF8   soft violet-tinted canvas
# surface:      #FFFFFF   card surface
# border:       #E4E0F5   subtle divider
# text:         #0F0E1C   primary near-black
# muted:        #5A5A78   secondary text
# subtle:       #9494AE   placeholder / labels
# accent:       #6B4EFF   violet
# accent-light: #EDE8FF   violet fill
# sidebar-bg:   #100F27   dark deep violet
# preview-bg:   #090817   darkest — image canvas
# green:        #22C55E
# orange:       #F97316
# ─────────────────────────────────────────────────────────────────────────────

STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* ── Page background ──────────────────────────────── */
.stApp { background-color: #F0EDF8; }
.main .block-container {
    padding: 1.75rem 2rem 5rem;
    max-width: 1200px;
}

/* ── Dark sidebar ─────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #100F27 0%, #0B0A1E 100%) !important;
    border-right: 1px solid rgba(107,78,255,0.25) !important;
}
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.25rem; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(107,78,255,0.2) !important;
    color: rgba(240,237,248,0.9) !important;
    border: 1px solid rgba(107,78,255,0.35) !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(107,78,255,0.35) !important;
    transform: none !important;
}

/* ── Tabs ─────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    gap: 0;
    border-bottom: 1px solid #E4E0F5;
    margin-bottom: 1.5rem;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #9494AE !important;
    font-size: 13px;
    font-weight: 500;
    padding: 0.6rem 1.25rem;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px;
    transition: color 0.15s;
}
.stTabs [aria-selected="true"] {
    color: #0F0E1C !important;
    border-bottom-color: #6B4EFF !important;
    font-weight: 600 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }

/* ── Chat input ───────────────────────────────────── */
[data-testid="stChatInput"] {
    border-top: 1px solid #E4E0F5 !important;
    background: #F0EDF8 !important;
    padding: 0.75rem 2rem !important;
}
[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    border: 1.5px solid #E4E0F5 !important;
    border-radius: 14px !important;
    color: #0F0E1C !important;
    font-size: 14px !important;
    padding: 0.75rem 1.1rem !important;
    box-shadow: 0 2px 8px rgba(107,78,255,0.06) !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
[data-testid="stChatInput"]:focus-within textarea {
    border-color: #6B4EFF !important;
    box-shadow: 0 0 0 3px rgba(107,78,255,0.12) !important;
}

/* ── Buttons ──────────────────────────────────────── */
.stButton > button {
    background: #6B4EFF !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.25rem !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(107,78,255,0.35) !important;
    transition: background 0.15s, box-shadow 0.15s, transform 0.12s !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: #5A3EEE !important;
    box-shadow: 0 4px 16px rgba(107,78,255,0.45) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #5A5A78 !important;
    border: 1.5px solid #E4E0F5 !important;
    box-shadow: 0 1px 3px rgba(15,14,28,0.06) !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #6B4EFF !important;
    color: #0F0E1C !important;
}

/* ── Metrics ──────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E4E0F5;
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
    box-shadow: 0 1px 4px rgba(15,14,28,0.04), 0 4px 16px rgba(107,78,255,0.06);
}
[data-testid="stMetricLabel"] {
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
    color: #9494AE !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #0F0E1C !important;
    letter-spacing: -0.03em !important;
}

/* ── Text inputs ──────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #FFFFFF !important;
    border: 1.5px solid #E4E0F5 !important;
    border-radius: 10px !important;
    color: #0F0E1C !important;
    font-size: 14px !important;
    padding: 0.6rem 0.95rem !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6B4EFF !important;
    box-shadow: 0 0 0 3px rgba(107,78,255,0.1) !important;
}

/* ── Select ───────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: #FFFFFF !important;
    border: 1.5px solid #E4E0F5 !important;
    border-radius: 10px !important;
    font-size: 13px !important;
}

/* ── Expander ─────────────────────────────────────── */
details > summary {
    background: #FFFFFF !important;
    border: 1.5px solid #E4E0F5 !important;
    border-radius: 10px !important;
    color: #5A5A78 !important;
    font-size: 13px !important;
    padding: 0.65rem 1rem !important;
}
details > summary:hover { border-color: #6B4EFF !important; color: #0F0E1C !important; }
details[open] > summary { border-radius: 10px 10px 0 0 !important; border-color: #6B4EFF !important; }
details > div {
    background: #FAFAFE !important;
    border: 1.5px solid #6B4EFF !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
}

/* ── File uploader ────────────────────────────────── */
[data-testid="stFileUploader"] > section {
    background: #FAFAFE !important;
    border: 2px dashed #CCC6FF !important;
    border-radius: 14px !important;
    transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stFileUploader"] > section:hover {
    border-color: #6B4EFF !important;
    background: #EDE8FF !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] p {
    font-size: 13px !important;
    color: #9494AE !important;
}

/* ── Pills ────────────────────────────────────────── */
[data-testid="stPillsGroup"] button {
    background: #FFFFFF !important;
    color: #6B4EFF !important;
    border: 1.5px solid #D4CCFF !important;
    border-radius: 24px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 0.3rem 1rem !important;
    transition: all 0.15s !important;
    box-shadow: 0 1px 3px rgba(107,78,255,0.08) !important;
}
[data-testid="stPillsGroup"] button:hover {
    background: #EDE8FF !important;
    border-color: #6B4EFF !important;
}
[data-testid="stPillsGroup"] button[aria-pressed="true"] {
    background: #6B4EFF !important;
    color: #FFFFFF !important;
    border-color: #6B4EFF !important;
}

/* ── Form ─────────────────────────────────────────── */
[data-testid="stForm"] {
    background: #FFFFFF;
    border: 1.5px solid #E4E0F5;
    border-radius: 14px;
    padding: 1rem 1.25rem 0.75rem;
    box-shadow: 0 1px 4px rgba(15,14,28,0.04);
}

/* ── Scrollbar ────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D4CCFF; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #A898FF; }

/* ── Divider / hr ─────────────────────────────────── */
hr { border-color: #E4E0F5; margin: 1.5rem 0; }

/* ── Spinner ──────────────────────────────────────── */
[data-testid="stSpinner"] > div { border-top-color: #6B4EFF !important; }

/* ── Alert ────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: #FFFFFF;
    border: 1px solid #E4E0F5;
    border-radius: 12px;
    font-size: 13px;
}

/* ── Dataframe ────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #E4E0F5 !important;
    border-radius: 12px !important;
}

/* ── Preview panel — force visible even when empty ── */
.stil-preview-panel {
    background: #090817;
    border-radius: 16px;
    padding: 1.1rem;
    min-height: 540px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.45), 0 2px 8px rgba(107,78,255,0.12);
    position: sticky;
    top: 1.5rem;
}
</style>
"""

st.markdown(STYLES, unsafe_allow_html=True)


# ─── Platform export crops ────────────────────────────────────────────────────

PLATFORM_SPECS = [
    ("Instagram", 1, 1, "#E1306C", "1:1 · 1080px"),
    ("Reels", 9, 16, "#C13584", "9:16 · 1080px"),
    ("Twitter", 16, 9, "#1DA1F2", "16:9 · 1200px"),
    ("LinkedIn", 4, 5, "#0A66C2", "4:5 · 1080px"),
]


def _get_platform_crops(image_bytes: bytes) -> list:
    """Center-crop an image to 4 platform aspect ratios. Returns list of dicts."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    crops = []
    for name, pw, ph, color, size_label in PLATFORM_SPECS:
        target_ratio = pw / ph
        current_ratio = w / h
        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            cropped = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            cropped = img.crop((0, top, w, top + new_h))
        cw, ch = cropped.size
        cap = 420
        if max(cw, ch) > cap:
            scale = cap / max(cw, ch)
            cropped = cropped.resize((int(cw * scale), int(ch * scale)), Image.LANCZOS)
        buf = io.BytesIO()
        cropped.save(buf, "JPEG", quality=82)
        crops.append({
            "name": name,
            "b64": base64.b64encode(buf.getvalue()).decode(),
            "color": color,
            "size": size_label,
        })
    return crops


# ─── Sidebar ──────────────────────────────────────────────────────────────────

def render_sidebar():
    memory = load_style()
    sig = memory.get("style_signature")

    # Wordmark on dark bg
    st.sidebar.markdown(
        '<div style="display:flex;align-items:center;gap:6px;margin-bottom:1.5rem;">'
        '<span style="font-size:20px;font-weight:800;letter-spacing:-0.05em;'
        'color:#EDE8FF;">Stil</span>'
        '<span style="font-size:20px;font-weight:800;color:#6B4EFF;">✦</span>'
        '</div>',
        unsafe_allow_html=True
    )

    # Section label helper for dark bg
    def _slabel(t):
        return (
            f'<div style="font-size:9px;font-weight:700;letter-spacing:0.1em;'
            f'text-transform:uppercase;color:#3A3860;margin-bottom:0.5rem;">{t}</div>'
        )

    st.sidebar.markdown(_slabel("Style profile"), unsafe_allow_html=True)

    if sig:
        tone = sig.get("tone", "—")
        crop = sig.get("crop_preference", "—")
        targets = sig.get("export_targets", [])
        notes = sig.get("notes", "")
        filter_style = sig.get("filter_style", "")
        tone_display = (
            filter_style.capitalize()
            if filter_style and filter_style not in ("none", "")
            else (tone.capitalize() if tone != "—" else "—")
        )

        rows_html = "".join([
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:0.45rem 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
            f'<span style="font-size:11px;color:#4A4870;font-weight:500;">{k}</span>'
            f'<span style="font-size:12px;color:#C8C4F0;font-weight:600;">{v}</span></div>'
            for k, v in [
                ("Style", tone_display),
                ("Crop", crop.capitalize() if crop not in ("—", "none") else "—"),
                ("Export", ", ".join(targets) if targets else "—"),
            ]
        ])
        st.sidebar.markdown(
            f'<div style="background:rgba(107,78,255,0.08);border:1px solid rgba(107,78,255,0.18);'
            f'border-radius:12px;padding:0.25rem 0.9rem 0.5rem;">'
            f'{rows_html}</div>',
            unsafe_allow_html=True
        )
        if notes:
            st.sidebar.markdown(
                f'<div style="font-size:11px;color:#3A3860;line-height:1.55;'
                f'margin-top:0.55rem;font-style:italic;">{notes}</div>',
                unsafe_allow_html=True
            )
        edit_count = len(memory.get("choices_log", []))
        updated = memory.get("last_updated", "")
        meta_parts = []
        if edit_count:
            meta_parts.append(f"{edit_count} edit{'s' if edit_count != 1 else ''}")
        if updated:
            meta_parts.append(f"updated {updated[:10]}")
        if meta_parts:
            st.sidebar.markdown(
                f'<div style="font-size:10px;color:#252445;margin-top:0.4rem;">'
                f'{" · ".join(meta_parts)}</div>',
                unsafe_allow_html=True
            )
    else:
        st.sidebar.markdown(
            '<div style="background:rgba(107,78,255,0.07);'
            'border:1.5px dashed rgba(107,78,255,0.2);border-radius:12px;'
            'padding:1rem 0.9rem;text-align:center;">'
            '<div style="font-size:1.5rem;margin-bottom:0.35rem;color:#2A2850;">✦</div>'
            '<div style="font-size:12px;color:#3A3860;line-height:1.7;">'
            'Style profile builds<br>automatically as you edit.</div>'
            '</div>',
            unsafe_allow_html=True
        )

    # Color palette
    palette = memory.get("color_palette", [])
    if palette:
        st.sidebar.markdown(
            '<hr style="border-color:rgba(255,255,255,0.05);margin:1rem 0 0.75rem;">'
            + _slabel("Palette"),
            unsafe_allow_html=True
        )
        swatches = "".join(
            f'<span title="{c}" style="display:inline-block;width:22px;height:22px;'
            f'border-radius:6px;background:{c};margin-right:4px;'
            f'border:1px solid rgba(255,255,255,0.12);'
            f'box-shadow:0 2px 6px rgba(0,0,0,0.3);cursor:pointer;"></span>'
            for c in palette
        )
        st.sidebar.markdown(
            f'<div style="display:flex;flex-wrap:wrap;align-items:center;">{swatches}</div>',
            unsafe_allow_html=True
        )

    # Choices log
    choices_log = memory.get("choices_log", [])
    if choices_log:
        st.sidebar.markdown(
            '<hr style="border-color:rgba(255,255,255,0.05);margin:1rem 0 0.75rem;">'
            + _slabel("Recent choices"),
            unsafe_allow_html=True
        )
        ICONS = {"filter": "◑", "crop": "⊡", "export": "↗", "brightness": "☀"}
        for entry in choices_log[:3]:
            ts = entry.get("ts", "")
            pills = "".join(
                f'<span style="display:inline-block;background:rgba(107,78,255,0.18);'
                f'color:#9B81FF;border:1px solid rgba(107,78,255,0.3);border-radius:20px;'
                f'font-size:10px;padding:1px 7px;margin:0 2px 2px 0;">'
                f'{ICONS.get(k, "·")} {v if k != "brightness" else (f"+{v}" if v > 0 else str(v))}'
                f'</span>'
                for k, v in entry.items() if k != "ts"
            )
            st.sidebar.markdown(
                f'<div style="margin-bottom:0.4rem;">'
                f'<div style="font-size:10px;color:#252445;margin-bottom:2px;">{ts}</div>'
                f'{pills}</div>',
                unsafe_allow_html=True
            )


# ─── Preview panel ────────────────────────────────────────────────────────────

def _preview_style_pills(style: dict) -> str:
    log = style.get("choices_log", [])
    recent = log[0] if log else {}
    sig = style.get("style_signature", {})
    pills = []
    if recent.get("filter"):
        pills.append(f'◑ {recent["filter"]}')
    elif sig.get("tone") and sig["tone"] not in ("neutral", "—", ""):
        pills.append(f'◑ {sig["tone"]}')
    if recent.get("crop"):
        pills.append(f'⊡ {recent["crop"]}')
    if recent.get("export"):
        pills.append(f'↗ {recent["export"]}')
    if not pills:
        return ""
    pill_html = "".join(
        f'<span style="display:inline-block;background:rgba(107,78,255,0.18);'
        f'color:#7B6FCC;border:1px solid rgba(107,78,255,0.2);border-radius:16px;'
        f'font-size:9px;font-weight:600;padding:2px 8px;margin:2px 3px 0 0;">{p}</span>'
        for p in pills
    )
    return (
        f'<div style="margin-top:10px;padding-top:10px;'
        f'border-top:1px solid rgba(255,255,255,0.05);">'
        f'<div style="font-size:8px;color:#2A284A;text-transform:uppercase;'
        f'letter-spacing:0.08em;font-weight:700;margin-bottom:5px;">Active style</div>'
        f'{pill_html}</div>'
    )


def _platform_grid_html(after_bytes: bytes) -> str:
    """Build the 2×2 platform export grid HTML from edited image bytes."""
    try:
        crops = _get_platform_crops(after_bytes)
    except Exception:
        return ""

    cards = ""
    for crop in crops:
        cards += (
            f'<div style="background:#0F0D25;border-radius:8px;overflow:hidden;'
            f'border:1px solid rgba(255,255,255,0.05);">'
            f'<img src="data:image/jpeg;base64,{crop["b64"]}" '
            f'style="width:100%;display:block;object-fit:cover;">'
            f'<div style="padding:5px 7px;display:flex;justify-content:space-between;'
            f'align-items:center;">'
            f'<span style="font-size:9px;font-weight:800;letter-spacing:0.04em;'
            f'text-transform:uppercase;color:{crop["color"]};">{crop["name"]}</span>'
            f'<span style="font-size:8px;color:#2A284A;">{crop["size"]}</span>'
            f'</div></div>'
        )

    return (
        f'<div style="margin-top:10px;">'
        f'<div style="font-size:8px;color:#2A284A;text-transform:uppercase;'
        f'letter-spacing:0.08em;font-weight:700;margin-bottom:7px;">Platform exports</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">'
        f'{cards}</div></div>'
    )


def _render_preview_panel():
    """Render the sticky dark preview panel with before/after and platform export grid."""
    style = load_style()
    messages = st.session_state.get("messages", [])
    latest_preview = next(
        (m for m in reversed(messages) if m.get("preview_after_b64")), None
    )
    current_img = st.session_state.get("last_img_bytes")

    # ── Header label ──────────────────────────────────────────────────────────
    header = (
        '<div style="font-size:9px;color:#252445;text-transform:uppercase;'
        'letter-spacing:0.1em;font-weight:700;margin-bottom:10px;">Preview</div>'
    )

    if latest_preview:
        before_b64 = latest_preview["preview_before_b64"]
        after_b64 = latest_preview["preview_after_b64"]
        after_bytes = base64.b64decode(after_b64)

        # Tool pills
        trace = latest_preview.get("tool_trace", [])
        trace_pills = "".join(
            f'<span style="display:inline-block;background:rgba(34,197,94,0.15);'
            f'color:#4ADE80;border:1px solid rgba(34,197,94,0.25);border-radius:16px;'
            f'font-size:9px;font-weight:600;padding:2px 8px;margin:2px 2px 0 0;">✓ {t["tool"]}</span>'
            for t in trace[:5]
        )
        tools_row = (
            f'<div style="margin-top:10px;padding-top:8px;'
            f'border-top:1px solid rgba(255,255,255,0.05);">'
            f'<div style="font-size:8px;color:#2A284A;text-transform:uppercase;'
            f'letter-spacing:0.08em;font-weight:700;margin-bottom:5px;">Applied</div>'
            f'<div style="display:flex;flex-wrap:wrap;">{trace_pills}</div></div>'
        ) if trace else ""

        # Before / After strip
        ba_strip = (
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:4px;">'
            f'<div>'
            f'<div style="font-size:8px;color:#2A284A;text-transform:uppercase;'
            f'letter-spacing:0.07em;font-weight:700;margin-bottom:4px;">Before</div>'
            f'<img src="data:image/jpeg;base64,{before_b64}" '
            f'style="width:100%;border-radius:7px;display:block;'
            f'border:1px solid rgba(255,255,255,0.05);">'
            f'</div>'
            f'<div>'
            f'<div style="font-size:8px;color:#9B81FF;text-transform:uppercase;'
            f'letter-spacing:0.07em;font-weight:700;margin-bottom:4px;">After</div>'
            f'<img src="data:image/jpeg;base64,{after_b64}" '
            f'style="width:100%;border-radius:7px;display:block;'
            f'border:1.5px solid rgba(107,78,255,0.45);">'
            f'</div>'
            f'</div>'
        )

        # Multi-image previews (when multiple files were edited)
        extra_previews = st.session_state.get("all_previews", [])
        extra_html = ""
        if len(extra_previews) > 1:
            extra_html = (
                f'<div style="margin-top:8px;">'
                f'<div style="font-size:8px;color:#2A284A;text-transform:uppercase;'
                f'letter-spacing:0.08em;font-weight:700;margin-bottom:6px;">'
                f'All {len(extra_previews)} images edited</div>'
                f'<div style="display:grid;grid-template-columns:repeat({min(len(extra_previews),3)},1fr);gap:5px;">'
            )
            for p in extra_previews:
                extra_html += (
                    f'<div>'
                    f'<img src="data:image/jpeg;base64,{p["after_b64"]}" '
                    f'style="width:100%;border-radius:6px;display:block;'
                    f'border:1px solid rgba(107,78,255,0.3);">'
                    f'<div style="font-size:7px;color:#3A3860;margin-top:2px;'
                    f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                    f'{p["filename"]}</div></div>'
                )
            extra_html += '</div></div>'

        platform_grid = _platform_grid_html(after_bytes)

        st.markdown(
            f'<div class="stil-preview-panel">'
            f'{header}'
            f'{ba_strip}'
            f'{extra_html}'
            f'{platform_grid}'
            f'{tools_row}'
            f'{_preview_style_pills(style)}'
            f'</div>',
            unsafe_allow_html=True
        )

    elif current_img:
        img_b64 = base64.b64encode(current_img).decode()
        st.markdown(
            f'<div class="stil-preview-panel">'
            f'{header}'
            f'<img src="data:image/jpeg;base64,{img_b64}" '
            f'style="width:100%;border-radius:10px;display:block;">'
            f'{_preview_style_pills(style)}'
            f'</div>',
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            '<div class="stil-preview-panel" style="display:flex;flex-direction:column;'
            'align-items:center;justify-content:center;text-align:center;">'
            '<div style="font-size:3.5rem;color:#161430;margin-bottom:0.9rem;">◑</div>'
            '<div style="font-size:12px;color:#2A284A;line-height:1.75;">'
            'Upload a photo<br>to see platform exports<br>'
            '<span style="font-size:10px;color:#1A1838;margin-top:6px;display:block;">'
            'Instagram · Reels · Twitter · LinkedIn</span></div>'
            '</div>',
            unsafe_allow_html=True
        )


# ─── Edit Tab ─────────────────────────────────────────────────────────────────

SAMPLE_PROMPTS = [
    "Make portrait warmer, crop square, export for Instagram",
    "Apply vintage filter, bump brightness +20",
    "Crop to 16:9 and export for Twitter",
    "Moody dramatic look for a dark editorial",
]


def tab_agent():
    # ── Header ──────────────────────────────────────────────────────────────
    hdr_col, btn_col = st.columns([10, 1])
    with hdr_col:
        st.markdown(
            '<p style="font-size:13px;color:#9494AE;margin:-0.5rem 0 1.25rem;line-height:1.6;">'
            'Describe your edit. Stil picks the right tools, applies them to every image, '
            'and shows platform-ready exports instantly.'
            '</p>',
            unsafe_allow_html=True
        )
    with btn_col:
        if st.button("↺", key="new_session", help="New session"):
            for k in ("messages", "session_log", "tool_trace", "api_messages",
                      "all_previews", "last_img_bytes", "session_has_image"):
                st.session_state[k] = [] if k != "last_img_bytes" else None
            if k == "session_has_image":
                st.session_state[k] = False
            st.session_state.img_cycle = st.session_state.get("img_cycle", 0) + 1
            st.rerun()

    # ── Session state ────────────────────────────────────────────────────────
    for key, default in [
        ("messages", []), ("session_log", []), ("tool_trace", []),
        ("pill_cycle", 0), ("img_cycle", 0), ("api_messages", []),
        ("session_has_image", False), ("last_img_bytes", None),
        ("all_previews", []), ("style_just_saved", False),
        ("brief_prompt", ""), ("brief_plan", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Style saved flash ────────────────────────────────────────────────────
    if st.session_state.style_just_saved:
        st.session_state.style_just_saved = False
        st.markdown(
            '<div style="background:linear-gradient(135deg,#F0FFF4,#ECFDF5);'
            'border:1px solid #BBF7D0;border-radius:10px;padding:0.55rem 1rem;'
            'margin-bottom:0.75rem;font-size:12px;color:#166534;'
            'display:flex;align-items:center;gap:6px;">'
            '<span>✓</span><span>Style profile updated — choices saved.</span>'
            '</div>',
            unsafe_allow_html=True
        )

    # ── Style active banner ──────────────────────────────────────────────────
    _style = load_style()
    _log = _style.get("choices_log", [])
    _sig = _style.get("style_signature", {})
    if _log or _sig:
        _recent = _log[0] if _log else {}
        _prefs = []
        if _recent.get("filter"):
            _prefs.append(_recent["filter"])
        elif _sig.get("tone") and _sig["tone"] not in ("neutral", "—"):
            _prefs.append(_sig["tone"])
        if _recent.get("crop"):
            _prefs.append(_recent["crop"])
        if _recent.get("export"):
            _prefs.append(_recent["export"])
        elif _sig.get("export_targets"):
            _prefs += _sig["export_targets"][:1]
        _prefs_text = " · ".join(_prefs[:3]) if _prefs else "your aesthetic"
        _count = f"{len(_log)} edit{'s' if len(_log) != 1 else ''}" if _log else ""
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#EDE8FF,#EAF1FF);'
            f'border:1px solid #D4CCFF;border-radius:10px;padding:0.55rem 1rem;'
            f'margin-bottom:0.85rem;display:flex;align-items:center;justify-content:space-between;">'
            f'<div style="display:flex;align-items:center;gap:7px;">'
            f'<span style="color:#6B4EFF;font-weight:800;">✦</span>'
            f'<span style="font-size:12px;font-weight:700;color:#2A1A88;">Style active</span>'
            f'<span style="font-size:12px;color:#6B6B88;"> — {_prefs_text}</span>'
            f'</div>'
            f'<span style="font-size:10px;color:#AAABB8;">{_count}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    # ── Onboarding (first-time) ──────────────────────────────────────────────
    if not load_style():
        st.markdown(
            '<div style="background:linear-gradient(135deg,#EDE8FF,#EAF1FF);'
            'border:1.5px solid #D4CCFF;border-radius:14px;'
            'padding:1rem 1.25rem 0.75rem;margin-bottom:1rem;">'
            '<div style="font-size:13px;font-weight:700;color:#2A1A88;margin-bottom:0.2rem;">'
            'Seed your style profile</div>'
            '<div style="font-size:12px;color:#6B6B88;">'
            'Answer 3 quick questions — Stil knows your aesthetic from session one.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        ob1, ob2, ob3, ob4 = st.columns([2, 2, 3, 1])
        with ob1:
            ob_tone = st.selectbox("Tone", ["warm", "cool", "neutral"],
                                   key="ob_tone", label_visibility="collapsed")
        with ob2:
            ob_platform = st.selectbox("Platform", ["instagram", "tiktok", "both"],
                                       key="ob_platform", label_visibility="collapsed")
        with ob3:
            ob_aesthetic = st.text_input("Aesthetic", placeholder="moody, minimal, vibrant…",
                                         key="ob_aesthetic", label_visibility="collapsed")
        with ob4:
            if st.button("Start →", key="ob_submit"):
                targets = ["instagram", "tiktok"] if ob_platform == "both" else [ob_platform]
                save_style({
                    "style_signature": {
                        "tone": ob_tone,
                        "filter_style": ob_tone if ob_tone != "neutral" else "none",
                        "crop_preference": "story" if ob_platform == "tiktok" else "square",
                        "export_targets": targets,
                        "notes": ob_aesthetic or f"{ob_tone} aesthetic for {ob_platform}",
                    }
                })
                st.rerun()
        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

    # ── 2-column layout ──────────────────────────────────────────────────────
    chat_col, preview_col = st.columns([13, 11], gap="large")

    with chat_col:
        # Upload — multiple files
        st.markdown(
            '<div style="font-size:10px;font-weight:700;letter-spacing:0.08em;'
            'text-transform:uppercase;color:#9494AE;margin-bottom:0.4rem;">Attach photos</div>',
            unsafe_allow_html=True
        )
        uploaded_files = st.file_uploader(
            "photo",
            type=["jpg", "jpeg", "png", "webp"],
            key=f"img_upload_{st.session_state.img_cycle}",
            label_visibility="collapsed",
            accept_multiple_files=True,
        )

        if uploaded_files:
            n = len(uploaded_files)
            if n == 1:
                fi1, fi2 = st.columns([1, 5])
                with fi1:
                    st.image(uploaded_files[0], use_container_width=True)
                with fi2:
                    st.markdown(
                        f'<div style="font-size:12px;color:#5A5A78;padding-top:0.2rem;'
                        f'font-weight:500;">{uploaded_files[0].name}</div>'
                        f'<div style="font-size:11px;color:#9494AE;">'
                        f'{round(uploaded_files[0].size / 1024)} KB</div>',
                        unsafe_allow_html=True
                    )
            else:
                thumb_cols = st.columns(min(n, 5))
                for i, f in enumerate(uploaded_files[:5]):
                    with thumb_cols[i]:
                        st.image(f, use_container_width=True)
                st.markdown(
                    f'<div style="font-size:11px;color:#9494AE;margin-top:4px;">'
                    f'{n} photos ready{" (+more)" if n > 5 else ""}</div>',
                    unsafe_allow_html=True
                )
        elif st.session_state.session_has_image:
            st.markdown(
                '<div style="font-size:11px;color:#9494AE;padding:0.3rem 0 0.15rem;">'
                '↑ Using photo from this session</div>',
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:0.55rem'></div>", unsafe_allow_html=True)

        # Sample prompts
        selected_sample = st.pills(
            "Try",
            SAMPLE_PROMPTS,
            key=f"sample_pills_{st.session_state.pill_cycle}",
            label_visibility="collapsed",
        )
        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

        # Brief-to-Edit
        with st.expander("✦ Generate from brief", expanded=False):
            st.markdown(
                '<div style="font-size:12px;color:#5A5A78;margin-bottom:0.55rem;padding:0.4rem 0 0;">'
                'Paste a creative brief — Stil translates it into an edit command.</div>',
                unsafe_allow_html=True
            )
            brief_text = st.text_area(
                "brief", height=68, label_visibility="collapsed",
                placeholder="Moody editorial — cool tones, high contrast, portrait for instagram…",
                key="brief_input"
            )
            bbc1, bbc2 = st.columns([2, 6])
            with bbc1:
                gen_clicked = st.button("Generate", key="gen_brief")
            if gen_clicked and brief_text.strip():
                with st.spinner("Translating…"):
                    plan = translate_brief_to_edits(brief_text.strip())
                st.session_state.brief_plan = plan

            plan = st.session_state.brief_plan
            if plan:
                if plan.get("rationale"):
                    st.markdown(
                        f'<div style="font-size:12px;color:#6B4EFF;font-style:italic;'
                        f'margin:0.5rem 0 0.4rem;">"{plan["rationale"]}"</div>',
                        unsafe_allow_html=True
                    )
                pills_html = "".join([
                    f'<span style="display:inline-block;background:rgba(107,78,255,0.07);'
                    f'color:#6B4EFF;border:1px solid rgba(107,78,255,0.18);border-radius:20px;'
                    f'font-size:11px;font-weight:500;padding:3px 10px;margin:2px 3px 2px 0;">'
                    f'{k}: {v}</span>'
                    for k, v in {
                        "Filter": plan.get("filter", ""),
                        "Brightness": f"{plan.get('brightness', 0):+d}" if plan.get("brightness") else "",
                        "Contrast": f"{plan.get('contrast', 0):+d}" if plan.get("contrast") else "",
                        "Crop": plan.get("crop", ""),
                        "Platform": plan.get("platform", ""),
                    }.items() if v and v not in ("none", "")
                ])
                st.markdown(f'<div style="margin-bottom:0.4rem;">{pills_html}</div>', unsafe_allow_html=True)
                with bbc2:
                    if st.button("Send to editor →", key="send_brief"):
                        st.session_state.brief_prompt = format_edit_plan(plan)
                        st.session_state.brief_plan = None
                        st.rerun()

        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

        # Prompt resolution
        user_input_override = None
        if selected_sample:
            user_input_override = selected_sample
            st.session_state.pill_cycle += 1
        if not user_input_override and st.session_state.get("brief_prompt"):
            user_input_override = st.session_state.brief_prompt
            st.session_state.brief_prompt = ""

        # Chat history
        if not st.session_state.messages:
            st.markdown(
                '<div style="text-align:center;padding:3rem 1rem;">'
                '<div style="font-size:1.75rem;color:#D4CCFF;margin-bottom:0.5rem;">✦</div>'
                '<div style="font-size:13px;color:#AAABB8;">Your conversation appears here.</div>'
                '</div>',
                unsafe_allow_html=True
            )

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                img_html = ""
                if msg.get("image_b64"):
                    img_html = (
                        f'<img src="data:{msg["image_media_type"]};base64,{msg["image_b64"]}" '
                        f'style="max-width:160px;max-height:120px;border-radius:7px;'
                        f'display:block;margin-bottom:5px;border:1px solid rgba(255,255,255,0.15);">'
                    )
                if msg.get("extra_images"):
                    grid_imgs = "".join(
                        f'<img src="data:image/jpeg;base64,{b64}" '
                        f'style="width:60px;height:60px;object-fit:cover;border-radius:5px;'
                        f'border:1px solid rgba(255,255,255,0.1);">'
                        for b64 in msg["extra_images"][:4]
                    )
                    img_html += f'<div style="display:flex;gap:3px;flex-wrap:wrap;margin-bottom:5px;">{grid_imgs}</div>'
                st.markdown(
                    f'<div style="display:flex;justify-content:flex-end;margin-bottom:0.85rem;">'
                    f'<div style="background:linear-gradient(135deg,#7B62FF,#5A3EEE);'
                    f'border-radius:18px 18px 4px 18px;padding:0.65rem 1rem;font-size:14px;'
                    f'color:#FFFFFF;line-height:1.55;max-width:82%;'
                    f'box-shadow:0 3px 12px rgba(107,78,255,0.35);">'
                    f'{img_html}{msg["content"]}</div></div>',
                    unsafe_allow_html=True
                )
            else:
                if msg.get("is_error"):
                    st.markdown(
                        f'<div style="margin-bottom:0.85rem;">'
                        f'<div style="background:#FFF5F5;border:1px solid #FECACA;border-radius:10px;'
                        f'padding:0.65rem 1rem;font-size:13px;color:#991B1B;line-height:1.6;max-width:88%;">'
                        f'⚠ {msg["content"]}</div></div>',
                        unsafe_allow_html=True
                    )
                else:
                    tool_pills_html = ""
                    if msg.get("tool_trace"):
                        pills = " ".join(
                            f'<span style="display:inline-flex;align-items:center;gap:4px;'
                            f'background:rgba(34,197,94,0.08);color:#22C55E;'
                            f'border:1px solid rgba(34,197,94,0.2);border-radius:20px;'
                            f'padding:2px 10px 2px 8px;font-size:11px;font-weight:600;">'
                            f'✓ {t["tool"]}</span>'
                            f'<span style="font-size:11px;color:#9494AE;">→ {t["result"].get("action","done")}</span>'
                            for t in msg["tool_trace"]
                        )
                        tool_pills_html = (
                            f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:7px;">{pills}</div>'
                        )
                    st.markdown(
                        f'<div style="margin-bottom:0.85rem;">{tool_pills_html}'
                        f'<div style="background:#FFFFFF;border:1px solid #E4E0F5;'
                        f'border-radius:4px 18px 18px 18px;padding:0.7rem 1.1rem;'
                        f'font-size:14px;color:#0F0E1C;line-height:1.65;max-width:90%;'
                        f'box-shadow:0 1px 4px rgba(15,14,28,0.04),'
                        f'0 4px 14px rgba(107,78,255,0.06);">'
                        f'{msg["content"]}</div></div>',
                        unsafe_allow_html=True
                    )

    with preview_col:
        _render_preview_panel()

    # ── Chat input ───────────────────────────────────────────────────────────
    user_input = st.chat_input("What do you want to do with your photos?")
    if user_input_override and not user_input:
        user_input = user_input_override

    if user_input:
        # Collect all uploaded files
        files = uploaded_files or []
        primary_bytes = None
        primary_media = "image/jpeg"
        primary_b64 = None
        extra_b64s = []

        if files:
            files[0].seek(0)
            primary_bytes = files[0].read()
            primary_media = files[0].type or "image/jpeg"
            primary_b64 = base64.b64encode(primary_bytes).decode()
            st.session_state.last_img_bytes = primary_bytes
            for f in files[1:]:
                f.seek(0)
                b = f.read()
                extra_b64s.append(base64.b64encode(b).decode())

        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "image_b64": primary_b64,
            "image_media_type": primary_media,
            "extra_images": extra_b64s,
        })
        st.session_state.session_log.append({"role": "user", "content": user_input})

        # Render user bubble immediately
        img_html = ""
        if primary_b64:
            img_html = (
                f'<img src="data:{primary_media};base64,{primary_b64}" '
                f'style="max-width:160px;max-height:120px;border-radius:7px;'
                f'display:block;margin-bottom:5px;">'
            )
        if extra_b64s:
            grid = "".join(
                f'<img src="data:image/jpeg;base64,{b}" '
                f'style="width:60px;height:60px;object-fit:cover;border-radius:5px;">'
                for b in extra_b64s[:4]
            )
            img_html += f'<div style="display:flex;gap:3px;flex-wrap:wrap;margin-bottom:5px;">{grid}</div>'
        st.markdown(
            f'<div style="display:flex;justify-content:flex-end;margin-bottom:0.85rem;">'
            f'<div style="background:linear-gradient(135deg,#7B62FF,#5A3EEE);'
            f'border-radius:18px 18px 4px 18px;padding:0.65rem 1rem;font-size:14px;'
            f'color:#FFFFFF;line-height:1.55;max-width:82%;'
            f'box-shadow:0 3px 12px rgba(107,78,255,0.35);">'
            f'{img_html}{user_input}</div></div>',
            unsafe_allow_html=True
        )

        tool_placeholder = st.empty()
        response_placeholder = st.empty()

        memory = load_style()
        full_response = ""
        current_pills_html = ""
        session_tool_trace = []
        had_error = False
        new_api_messages = []

        for event in run_agent_streaming(
            user_input, memory, primary_bytes, primary_media,
            conversation_history=st.session_state.api_messages
        ):
            if event["type"] == "tool_start":
                current_pills_html += (
                    f'<span style="display:inline-flex;align-items:center;gap:4px;'
                    f'background:rgba(249,115,22,0.1);color:#F97316;'
                    f'border:1px solid rgba(249,115,22,0.25);border-radius:20px;'
                    f'padding:2px 10px 2px 8px;font-size:11px;font-weight:600;">'
                    f'⚡ {event["tool"]}</span> '
                )
                tool_placeholder.markdown(
                    f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:6px;">'
                    f'{current_pills_html}</div>',
                    unsafe_allow_html=True
                )
            elif event["type"] == "tool_end":
                action = event["result"].get("action", "done")
                current_pills_html = current_pills_html.replace(
                    f'background:rgba(249,115,22,0.1);color:#F97316;'
                    f'border:1px solid rgba(249,115,22,0.25);border-radius:20px;'
                    f'padding:2px 10px 2px 8px;font-size:11px;font-weight:600;">'
                    f'⚡ {event["tool"]}</span>',
                    f'background:rgba(34,197,94,0.08);color:#22C55E;'
                    f'border:1px solid rgba(34,197,94,0.2);border-radius:20px;'
                    f'padding:2px 10px 2px 8px;font-size:11px;font-weight:600;">'
                    f'✓ {event["tool"]}</span>'
                    f'<span style="font-size:11px;color:#9494AE;"> → {action}</span>'
                )
                tool_placeholder.markdown(
                    f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:6px;">'
                    f'{current_pills_html}</div>',
                    unsafe_allow_html=True
                )
                session_tool_trace.append({
                    "tool": event["tool"],
                    "input": event.get("input", {}),
                    "result": event["result"],
                })
            elif event["type"] == "text":
                full_response += event["content"]
                response_placeholder.markdown(
                    f'<div style="background:#FFFFFF;border:1px solid #E4E0F5;'
                    f'border-radius:4px 18px 18px 18px;padding:0.7rem 1.1rem;'
                    f'font-size:14px;color:#0F0E1C;line-height:1.65;max-width:90%;'
                    f'box-shadow:0 1px 4px rgba(15,14,28,0.04),'
                    f'0 4px 14px rgba(107,78,255,0.06);">'
                    f'{full_response}</div>',
                    unsafe_allow_html=True
                )
            elif event["type"] == "error":
                had_error = True
                full_response = event["content"]
                response_placeholder.markdown(
                    f'<div style="background:#FFF5F5;border:1px solid #FECACA;'
                    f'border-radius:10px;padding:0.75rem 1rem;font-size:13px;'
                    f'color:#991B1B;line-height:1.6;">⚠ {event["content"]}</div>',
                    unsafe_allow_html=True
                )
            elif event["type"] == "done":
                st.session_state.tool_trace.extend(event.get("tool_trace", []))
                new_api_messages = event.get("api_messages", [])

        if not had_error:
            assistant_msg = {
                "role": "assistant",
                "content": full_response,
                "tool_trace": session_tool_trace,
            }

            # Generate platform-ready previews for ALL uploaded images
            all_previews = []
            if files:
                for f in files:
                    f.seek(0)
                    fb = f.read()
                    try:
                        edited = preview_edits(fb, session_tool_trace)
                        if edited:
                            all_previews.append({
                                "filename": f.name,
                                "before_b64": base64.b64encode(fb).decode(),
                                "after_b64": base64.b64encode(edited).decode(),
                            })
                    except Exception:
                        pass

            if all_previews:
                # Primary preview from first image
                assistant_msg["preview_before_b64"] = all_previews[0]["before_b64"]
                assistant_msg["preview_after_b64"] = all_previews[0]["after_b64"]
                assistant_msg["tool_trace"] = session_tool_trace
                st.session_state.all_previews = all_previews
            elif st.session_state.get("last_img_bytes"):
                try:
                    edited = preview_edits(st.session_state.last_img_bytes, session_tool_trace)
                    if edited:
                        assistant_msg["preview_before_b64"] = base64.b64encode(
                            st.session_state.last_img_bytes).decode()
                        assistant_msg["preview_after_b64"] = base64.b64encode(edited).decode()
                        assistant_msg["tool_trace"] = session_tool_trace
                except Exception:
                    pass

            st.session_state.messages.append(assistant_msg)
            st.session_state.session_log.append({"role": "assistant", "content": full_response})
            st.session_state.api_messages = new_api_messages

            if primary_bytes:
                st.session_state.session_has_image = True
                current_style = load_style()
                try:
                    palette = extract_color_palette(primary_bytes)
                    if palette:
                        current_style["color_palette"] = palette
                except Exception:
                    pass
                try:
                    exif = extract_exif(primary_bytes)
                    if exif:
                        current_style["camera_profile"] = exif
                except Exception:
                    pass
                save_style(current_style)

            updated = extract_and_save_style(st.session_state.session_log, load_style())
            update_choices_log(session_tool_trace, updated)
            write_session_log(st.session_state.session_log, st.session_state.tool_trace)
            st.session_state.style_just_saved = True
            st.session_state.img_cycle += 1
            st.rerun()
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "is_error": True,
                "tool_trace": [],
            })
            st.session_state.session_log.pop()
            st.rerun()


# ─── Style Tab ────────────────────────────────────────────────────────────────

def tab_memory():
    st.markdown(
        '<p style="font-size:13px;color:#9494AE;margin:-0.5rem 0 1.25rem;">'
        'What Stil remembers about you — injected into every new session automatically.'
        '</p>',
        unsafe_allow_html=True
    )

    memory = load_style()
    sig = memory.get("style_signature")

    if not sig:
        _empty_state("✦", "No style profile yet",
                     "Have a conversation in the Edit tab.<br>Stil extracts your preferences automatically.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Tone", sig.get("tone", "—").capitalize())
    with c2:
        st.metric("Crop", sig.get("crop_preference", "—").capitalize())
    with c3:
        targets = sig.get("export_targets", [])
        st.metric("Platforms", str(len(targets)) if targets else "—")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    if targets:
        st.markdown(_section_label("Export platforms"), unsafe_allow_html=True)
        st.markdown(" ".join(_tag_pill(t) for t in targets), unsafe_allow_html=True)
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    if memory.get("color_palette"):
        st.markdown(_section_label("Color palette"), unsafe_allow_html=True)
        swatches = "".join(
            f'<span style="display:inline-block;width:36px;height:36px;border-radius:10px;'
            f'background:{c};margin-right:8px;border:1px solid rgba(0,0,0,0.07);'
            f'box-shadow:0 2px 6px rgba(0,0,0,0.1);"></span>'
            for c in memory["color_palette"]
        )
        st.markdown(f'<div style="display:flex;flex-wrap:wrap;">{swatches}</div>',
                    unsafe_allow_html=True)
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    camera = memory.get("camera_profile", {})
    if camera:
        st.markdown(_section_label("Camera profile"), unsafe_allow_html=True)
        cam_rows = "".join([
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:0.4rem 0;border-bottom:1px solid #F2F2F8;font-size:12px;">'
            f'<span style="color:#9494AE;font-weight:500;">{k.replace("_"," ").capitalize()}</span>'
            f'<span style="color:#0F0E1C;font-weight:600;">{v}</span></div>'
            for k, v in camera.items()
        ])
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E4E0F5;border-radius:12px;'
            f'padding:0.25rem 0.9rem 0.5rem;">{cam_rows}</div>',
            unsafe_allow_html=True
        )
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    if sig.get("notes"):
        st.markdown(_section_label("Aesthetic summary"), unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E4E0F5;border-radius:12px;'
            f'padding:0.9rem 1.1rem;font-size:14px;color:#3A3A5C;line-height:1.7;">'
            f'{sig["notes"]}</div>',
            unsafe_allow_html=True
        )
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    if memory.get("last_updated"):
        st.markdown(
            f'<div style="font-size:11px;color:#C8C8DA;">Last updated {memory["last_updated"][:16]}</div>',
            unsafe_allow_html=True
        )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(_section_label("Edit profile"), unsafe_allow_html=True)
    tone_options = ["warm", "cool", "neutral"]
    crop_options = ["square", "portrait", "landscape", "story", "none"]
    platform_options = ["instagram", "tiktok", "twitter", "linkedin", "web", "print"]
    tone_val = sig.get("tone", "neutral")
    crop_val = sig.get("crop_preference", "none")
    targets_val = sig.get("export_targets", [])
    notes_val = sig.get("notes", "")

    with st.form("edit_profile_form"):
        ed1, ed2 = st.columns(2)
        with ed1:
            new_tone = st.selectbox("Tone", tone_options,
                index=tone_options.index(tone_val) if tone_val in tone_options else 2)
            new_crop = st.selectbox("Crop", crop_options,
                index=crop_options.index(crop_val) if crop_val in crop_options else 4)
        with ed2:
            new_targets = st.multiselect("Export targets", platform_options,
                default=[t for t in targets_val if t in platform_options])
            new_notes = st.text_area("Aesthetic notes", value=notes_val, height=88)
        if st.form_submit_button("Save changes"):
            memory["style_signature"] = {
                **(memory.get("style_signature") or {}),
                "tone": new_tone,
                "crop_preference": new_crop,
                "export_targets": new_targets,
                "notes": new_notes,
            }
            save_style(memory)
            st.success("Profile updated.")
            st.rerun()

    with st.expander("Raw style_profile.json"):
        st.json(memory)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(_section_label("Saved brands"), unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:12px;color:#9494AE;margin-bottom:0.75rem;">'
        'Save named style profiles — switch between clients or campaigns in one click.</div>',
        unsafe_allow_html=True
    )
    brands = memory.get("brands", {})
    if brands:
        for brand_name, brand_data in list(brands.items()):
            b1, b2, b3 = st.columns([5, 1, 1])
            with b1:
                b_sig = brand_data.get("style_signature", {})
                b_tone = b_sig.get("tone", "—")
                b_targets = ", ".join(b_sig.get("export_targets", [])) or "—"
                st.markdown(
                    f'<div style="background:#FFFFFF;border:1px solid #E4E0F5;border-radius:10px;'
                    f'padding:0.5rem 0.9rem;font-size:12px;">'
                    f'<span style="font-weight:700;color:#0F0E1C;">{brand_name}</span>'
                    f'<span style="color:#9494AE;margin-left:8px;">{b_tone} · {b_targets}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with b2:
                if st.button("Load", key=f"load_brand_{brand_name}"):
                    memory["style_signature"] = brand_data.get("style_signature", {})
                    if brand_data.get("choices_log"):
                        memory["choices_log"] = brand_data["choices_log"]
                    save_style(memory)
                    st.success(f"Loaded {brand_name}")
                    st.rerun()
            with b3:
                if st.button("×", key=f"del_brand_{brand_name}"):
                    del memory["brands"][brand_name]
                    save_style(memory)
                    st.rerun()
    else:
        st.markdown(
            '<div style="font-size:12px;color:#C8C8DA;margin-bottom:0.4rem;">No saved brands yet.</div>',
            unsafe_allow_html=True
        )

    with st.form("save_brand_form"):
        br1, br2 = st.columns([4, 1])
        with br1:
            brand_input = st.text_input("Brand name",
                placeholder="Summer campaign, Brand B…", label_visibility="collapsed")
        with br2:
            if st.form_submit_button("Save"):
                if brand_input.strip():
                    if "brands" not in memory:
                        memory["brands"] = {}
                    memory["brands"][brand_input.strip()] = {
                        "style_signature": memory.get("style_signature", {}),
                        "choices_log": memory.get("choices_log", []),
                    }
                    save_style(memory)
                    st.success(f'Saved as "{brand_input.strip()}"')
                    st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if st.button("Clear style memory", key="clear_memory"):
        if os.path.exists("style_profile.json"):
            os.remove("style_profile.json")
        for k in ("api_messages", "all_previews"):
            st.session_state[k] = []
        st.session_state.session_has_image = False
        st.session_state.last_img_bytes = None
        st.rerun()


# ─── Insights Tab ─────────────────────────────────────────────────────────────

def tab_evals():
    st.markdown(
        '<p style="font-size:13px;color:#9494AE;margin:-0.5rem 0 1.25rem;">'
        'Grade sessions on tool accuracy, goal completion, and creative intent.'
        '</p>',
        unsafe_allow_html=True
    )

    log_count = len([f for f in os.listdir("logs") if f.endswith(".jsonl")]) \
        if os.path.exists("logs") else 0

    col_btn, col_info = st.columns([1, 5])
    with col_btn:
        run_clicked = st.button("Run evals", type="primary", use_container_width=True)
    with col_info:
        st.markdown(
            f'<div style="font-size:13px;color:#9494AE;padding-top:0.5rem;">'
            f'{log_count} session log{"s" if log_count != 1 else ""} available</div>',
            unsafe_allow_html=True
        )

    if run_clicked:
        if log_count == 0:
            st.warning("No session logs yet. Complete a chat session in the Edit tab first.")
        else:
            with st.spinner("Grading with Haiku…"):
                from insights import run_insights
                result = run_insights()
                st.session_state.eval_result = result
            st.rerun()

    result = st.session_state.get("eval_result")
    if not result:
        _empty_state("◎", "No eval data yet",
                     "Run evals after a few sessions to see<br>how well Stil serves your creative intent.")
        return

    scores = result.get("scores", {})
    graded = result.get("graded_turns", [])
    summary = result.get("summary", "")

    c1, c2, c3 = st.columns(3)
    for col, label, dim, desc in [
        (c1, "Tool accuracy", "tool_accuracy", "Right tools for the request?"),
        (c2, "Goal completion", "goal_completion", "Task completed as asked?"),
        (c3, "Creative intent", "creative_intent", "Output served the creative goal?"),
    ]:
        score = scores.get(dim, 0)
        pct = int((score / 5) * 100)
        bar_color = "#22C55E" if score >= 4 else ("#F97316" if score >= 3 else "#EF4444")
        col.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E4E0F5;border-radius:14px;'
            f'padding:1.1rem 1.25rem;box-shadow:0 1px 4px rgba(15,14,28,0.04),'
            f'0 4px 16px rgba(107,78,255,0.06);">'
            f'<div style="font-size:10px;font-weight:700;letter-spacing:0.08em;'
            f'text-transform:uppercase;color:#9494AE;margin-bottom:0.3rem;">{label}</div>'
            f'<div style="font-size:2rem;font-weight:700;color:#0F0E1C;letter-spacing:-0.03em;">'
            f'{score}<span style="font-size:1rem;color:#C8C8DA;font-weight:400;"> /5</span></div>'
            f'<div style="font-size:11px;color:#9494AE;margin-top:2px;margin-bottom:8px;">{desc}</div>'
            f'<div style="background:#F0EDF8;border-radius:4px;height:4px;">'
            f'<div style="width:{pct}%;height:100%;border-radius:4px;background:{bar_color};"></div></div>'
            f'</div>',
            unsafe_allow_html=True
        )

    if graded:
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown(_section_label("Score by turn"), unsafe_allow_html=True)
        df = pd.DataFrame([{
            "Turn": f"T{t['turn']}",
            "Tool accuracy": t.get("tool_accuracy", 0),
            "Goal completion": t.get("goal_completion", 0),
            "Creative intent": t.get("creative_intent", 0),
        } for t in graded]).set_index("Turn")
        st.bar_chart(df, height=180, color=["#6B4EFF", "#22C55E", "#F97316"])

        unique_sessions = list(dict.fromkeys(t["session"] for t in graded))
        if len(unique_sessions) > 1:
            from collections import defaultdict
            session_ci: dict = defaultdict(list)
            for t in graded:
                session_ci[t["session"]].append(t.get("creative_intent", 3))
            trend_df = pd.DataFrame([
                {"Session": f"S{i+1}",
                 "Creative intent": round(sum(session_ci[s]) / len(session_ci[s]), 1)}
                for i, s in enumerate(unique_sessions)
            ]).set_index("Session")
            st.markdown(_section_label("Creative intent over sessions"), unsafe_allow_html=True)
            st.line_chart(trend_df, height=160, color=["#6B4EFF"])

    if summary:
        st.markdown(_section_label("Product health summary"), unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E4E0F5;border-radius:12px;'
            f'padding:1rem 1.1rem;font-size:14px;color:#3A3A5C;line-height:1.8;">'
            f'{summary}</div>',
            unsafe_allow_html=True
        )


# ─── Assets Tab ───────────────────────────────────────────────────────────────

def tab_assets():
    st.markdown(
        '<p style="font-size:13px;color:#9494AE;margin:-0.5rem 0 1.25rem;">'
        'Describe what you need. Stil scores your library by keyword match and AI tags.'
        '</p>',
        unsafe_allow_html=True
    )

    assets = list_assets()
    asset_files = assets.get("assets", [])

    if not asset_files:
        _empty_state("◻", "No assets found",
                     'Drop JPG/PNG files with descriptive names into <code>assets/</code>.')
        st.code("portrait_warm_natural_light.jpg\ndark_high_contrast_abstract_bg.jpg")
        return

    st.markdown(
        f'<div style="font-size:12px;color:#9494AE;margin-bottom:1rem;">'
        f'{len(asset_files)} asset{"s" if len(asset_files) != 1 else ""} in library</div>',
        unsafe_allow_html=True
    )

    query = st.text_input(
        "search", placeholder="high contrast background for a social post…",
        label_visibility="collapsed"
    )

    if query:
        with st.spinner("Searching…"):
            result = find_asset(query)
        if result.get("results"):
            for r in result["results"]:
                filepath = os.path.join("assets", r["filename"])
                c1, c2 = st.columns([1, 4])
                with c1:
                    if os.path.exists(filepath):
                        st.image(filepath, use_container_width=True)
                    else:
                        st.markdown(
                            '<div style="background:#F0EDF8;border:1px solid #E4E0F5;'
                            'border-radius:10px;height:80px;"></div>',
                            unsafe_allow_html=True
                        )
                with c2:
                    tags_html = " ".join(_tag_pill(t) for t in (r.get("tags") or []))
                    st.markdown(
                        f'<div style="background:#FFFFFF;border:1px solid #E4E0F5;border-radius:12px;'
                        f'padding:0.85rem 1rem;">'
                        f'<div style="font-size:10px;font-weight:700;letter-spacing:0.07em;'
                        f'text-transform:uppercase;color:#6B4EFF;margin-bottom:0.25rem;">#{r["rank"]}</div>'
                        f'<div style="font-size:14px;font-weight:600;color:#0F0E1C;margin-bottom:0.35rem;">'
                        f'{r["filename"]}</div>'
                        f'<div style="margin-bottom:0.4rem;">{tags_html}</div>'
                        f'<div style="font-size:12px;color:#9494AE;line-height:1.55;">{r["rationale"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    else:
        cols = st.columns(4)
        for i, fname in enumerate(asset_files[:12]):
            with cols[i % 4]:
                filepath = os.path.join("assets", fname)
                label = fname.rsplit(".", 1)[0].replace("_", " ")
                if os.path.exists(filepath):
                    st.image(filepath, use_container_width=True)
                else:
                    st.markdown(
                        '<div style="background:#FFFFFF;border:1px solid #E4E0F5;'
                        'border-radius:10px;height:100px;"></div>',
                        unsafe_allow_html=True
                    )
                st.markdown(
                    f'<div style="font-size:10px;color:#9494AE;text-align:center;'
                    f'margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                    f'{label}</div>',
                    unsafe_allow_html=True
                )


# ─── Feed Tab ─────────────────────────────────────────────────────────────────

def tab_feed():
    st.markdown(
        '<p style="font-size:13px;color:#9494AE;margin:-0.5rem 0 1.25rem;">'
        'Analyze feed consistency and transfer visual style from any reference photo.'
        '</p>',
        unsafe_allow_html=True
    )

    feed_sub1, feed_sub2 = st.tabs(["Cohesion Score", "Style Transfer"])

    with feed_sub1:
        st.markdown(
            '<div style="font-size:12px;color:#9494AE;margin-bottom:1rem;line-height:1.6;">'
            'Upload 3–10 photos from your feed. Stil measures consistency across '
            'color temperature, brightness, contrast, and saturation.</div>',
            unsafe_allow_html=True
        )
        feed_files = st.file_uploader(
            "Upload feed photos", type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True, key="feed_upload", label_visibility="collapsed",
        )
        if feed_files:
            n = len(feed_files)
            st.markdown(
                f'<div style="font-size:11px;color:#9494AE;margin:0.4rem 0 0.75rem;">'
                f'{n} photo{"s" if n != 1 else ""} ready</div>',
                unsafe_allow_html=True
            )
            thumb_cols = st.columns(min(n, 6))
            for i, f in enumerate(feed_files[:6]):
                with thumb_cols[i]:
                    st.image(f, use_container_width=True)
                    st.markdown(
                        f'<div style="font-size:9px;color:#9494AE;text-align:center;'
                        f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                        f'{f.name[:18]}</div>',
                        unsafe_allow_html=True
                    )

        if feed_files and st.button("Analyze feed", type="primary", key="analyze_feed"):
            with st.spinner("Measuring cohesion…"):
                image_bytes_list, filenames = [], []
                for f in feed_files:
                    f.seek(0)
                    image_bytes_list.append(f.read())
                    filenames.append(f.name)
                st.session_state.cohesion_result = analyze_feed(image_bytes_list, filenames)

        result = st.session_state.get("cohesion_result")
        if result and not result.get("error"):
            score = result["score"]
            if score >= 80:
                label, color, bg = "Highly cohesive", "#22C55E", "#F0FFF4"
            elif score >= 60:
                label, color, bg = "Mostly consistent", "#F97316", "#FFF9F0"
            elif score >= 40:
                label, color, bg = "Mixed feed", "#EF4444", "#FFF5F5"
            else:
                label, color, bg = "Inconsistent", "#EF4444", "#FFF5F5"

            st.markdown(
                f'<div style="background:#FFFFFF;border:1px solid #E4E0F5;border-radius:16px;'
                f'padding:1.5rem 1.75rem;margin-bottom:1rem;display:flex;align-items:center;'
                f'justify-content:space-between;box-shadow:0 2px 8px rgba(15,14,28,0.06),'
                f'0 8px 24px rgba(107,78,255,0.07);">'
                f'<div>'
                f'<div style="font-size:10px;font-weight:700;letter-spacing:0.09em;'
                f'text-transform:uppercase;color:#9494AE;margin-bottom:0.35rem;">Cohesion score</div>'
                f'<div style="font-size:3.5rem;font-weight:800;color:#0F0E1C;letter-spacing:-0.05em;">'
                f'{score}<span style="font-size:1.25rem;color:#C8C8DA;font-weight:400;"> /100</span></div>'
                f'</div>'
                f'<div style="background:{bg};border:1px solid rgba(0,0,0,0.05);border-radius:12px;'
                f'padding:0.5rem 1rem;text-align:right;">'
                f'<div style="font-size:15px;font-weight:700;color:{color};">{label}</div>'
                f'<div style="font-size:11px;color:#9494AE;margin-top:3px;">'
                f'{len(result.get("per_image_metrics",[]))} photos</div>'
                f'</div></div>',
                unsafe_allow_html=True
            )

            if result.get("dimension_scores"):
                st.markdown(_section_label("Consistency by dimension"), unsafe_allow_html=True)
                dim_cols = st.columns(4)
                for i, (dim, ds) in enumerate(result["dimension_scores"].items()):
                    bc = "#22C55E" if ds >= 80 else ("#F97316" if ds >= 60 else "#EF4444")
                    dim_cols[i].markdown(
                        f'<div style="background:#FFFFFF;border:1px solid #E4E0F5;border-radius:12px;'
                        f'padding:0.85rem 0.95rem;text-align:center;">'
                        f'<div style="font-size:10px;font-weight:700;letter-spacing:0.06em;'
                        f'text-transform:uppercase;color:#9494AE;margin-bottom:0.5rem;">{dim}</div>'
                        f'<div style="font-size:1.6rem;font-weight:700;color:#0F0E1C;">{ds}</div>'
                        f'<div style="background:#F0EDF8;border-radius:4px;height:4px;margin-top:7px;">'
                        f'<div style="width:{ds}%;height:100%;border-radius:4px;background:{bc};"></div>'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )

            issues = result.get("issues", [])
            if issues:
                st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
                st.markdown(_section_label("What's breaking consistency"), unsafe_allow_html=True)
                for issue in issues:
                    st.markdown(
                        f'<div style="background:#FFF9F0;border:1px solid #FED7AA;border-radius:10px;'
                        f'padding:0.55rem 0.95rem;margin-bottom:0.4rem;font-size:12px;color:#92400E;">'
                        f'⚠ {issue}</div>',
                        unsafe_allow_html=True
                    )

            if result.get("suggested_fix"):
                st.markdown(
                    f'<div style="background:#F0FFF4;border:1px solid #BBF7D0;border-radius:10px;'
                    f'padding:0.6rem 1rem;margin-top:0.5rem;font-size:12px;color:#166534;">'
                    f'→ <strong>Suggested fix:</strong> {result["suggested_fix"]}</div>',
                    unsafe_allow_html=True
                )

            if result.get("per_image_metrics"):
                with st.expander("Per-photo breakdown"):
                    df = pd.DataFrame(result["per_image_metrics"])
                    df.columns = [c.replace("_", " ").capitalize() for c in df.columns]
                    st.dataframe(df, use_container_width=True, hide_index=True)

        elif not feed_files:
            _empty_state("◎", "No photos uploaded",
                         "Upload 3 or more photos from your feed to measure consistency.")

    with feed_sub2:
        st.markdown(
            '<div style="font-size:12px;color:#9494AE;margin-bottom:1rem;line-height:1.6;">'
            'Upload a reference photo — competitor shot, mood board, or editorial. '
            'Stil reads its visual style and applies it to your photo.</div>',
            unsafe_allow_html=True
        )
        ref_col, target_col = st.columns(2, gap="large")

        with ref_col:
            st.markdown(_section_label("Reference"), unsafe_allow_html=True)
            ref_file = st.file_uploader("Reference", type=["jpg", "jpeg", "png", "webp"],
                                        key="ref_upload", label_visibility="collapsed")
            if ref_file:
                st.image(ref_file, use_container_width=True)
                ref_file.seek(0)
                ref_bytes_preview = ref_file.read()
                ref_style = extract_reference_style(ref_bytes_preview)
                st.markdown(
                    f'<div style="background:#FFFFFF;border:1px solid #E4E0F5;border-radius:10px;'
                    f'padding:0.65rem 0.85rem;margin-top:0.55rem;">'
                    f'<div style="font-size:9px;font-weight:700;text-transform:uppercase;'
                    f'letter-spacing:0.07em;color:#9494AE;margin-bottom:5px;">Style detected</div>'
                    f'<div style="font-size:13px;font-weight:700;color:#6B4EFF;margin-bottom:3px;">'
                    f'{ref_style["filter_type"].upper()}</div>'
                    f'<div style="font-size:11px;color:#5A5A78;margin-bottom:5px;">'
                    f'{ref_style["description"]}</div>'
                    f'<div style="font-size:10px;color:#9494AE;">'
                    f'Brightness {ref_style["brightness_delta"]:+d} · '
                    f'Contrast {ref_style["contrast_delta"]:+d} · {ref_style["tone"]} tone</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        with target_col:
            st.markdown(_section_label("Your photo"), unsafe_allow_html=True)
            target_file = st.file_uploader("Your photo", type=["jpg", "jpeg", "png", "webp"],
                                           key="target_upload", label_visibility="collapsed")
            if target_file:
                st.image(target_file, use_container_width=True)

        if ref_file and target_file:
            if st.button("Transfer style →", type="primary", key="transfer_style"):
                with st.spinner("Applying style…"):
                    ref_file.seek(0)
                    target_file.seek(0)
                    ref_b = ref_file.read()
                    target_b = target_file.read()
                    result_bytes = apply_style_transfer(target_b, ref_b)
                    si = extract_reference_style(ref_b)
                st.session_state.transfer_result = {
                    "before_b64": base64.b64encode(target_b).decode(),
                    "after_b64": base64.b64encode(result_bytes).decode(),
                    "style_info": si,
                }

        xfer = st.session_state.get("transfer_result")
        if xfer:
            st.markdown(_section_label("Result"), unsafe_allow_html=True)
            bc, ac = st.columns(2)
            with bc:
                st.markdown(
                    '<div style="font-size:10px;font-weight:700;letter-spacing:0.06em;'
                    'text-transform:uppercase;color:#9494AE;margin-bottom:5px;">Before</div>',
                    unsafe_allow_html=True
                )
                st.image(base64.b64decode(xfer["before_b64"]), use_container_width=True)
            with ac:
                st.markdown(
                    '<div style="font-size:10px;font-weight:700;letter-spacing:0.06em;'
                    'text-transform:uppercase;color:#6B4EFF;margin-bottom:5px;">After</div>',
                    unsafe_allow_html=True
                )
                st.image(base64.b64decode(xfer["after_b64"]), use_container_width=True)
            si = xfer.get("style_info", {})
            st.markdown(
                f'<div style="background:#F0FFF4;border:1px solid #BBF7D0;border-radius:10px;'
                f'padding:0.55rem 1rem;margin-top:0.55rem;font-size:12px;color:#166534;">'
                f'✓ Applied: <strong>{si.get("filter_type","").upper()}</strong> · '
                f'brightness {si.get("brightness_delta",0):+d} · '
                f'contrast {si.get("contrast_delta",0):+d}</div>',
                unsafe_allow_html=True
            )
        elif not (ref_file and target_file):
            _empty_state("◑", "Upload both photos to begin",
                         "Reference sets the style. Your photo receives it.")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _section_label(text: str) -> str:
    return (
        f'<div style="font-size:10px;font-weight:700;letter-spacing:0.09em;'
        f'text-transform:uppercase;color:#9494AE;margin-bottom:0.55rem;">{text}</div>'
    )


def _tag_pill(text: str) -> str:
    return (
        f'<span style="display:inline-block;background:rgba(107,78,255,0.07);'
        f'color:#6B4EFF;border:1px solid rgba(107,78,255,0.18);border-radius:20px;'
        f'font-size:10px;font-weight:600;padding:2px 9px;margin:2px 3px 2px 0;">{text}</span>'
    )


def _empty_state(icon: str, title: str, body: str):
    st.markdown(
        f'<div style="text-align:center;padding:3.5rem 1rem;">'
        f'<div style="font-size:2.25rem;color:#D4CCFF;margin-bottom:0.7rem;">{icon}</div>'
        f'<div style="font-size:15px;font-weight:600;color:#5A5A78;margin-bottom:0.4rem;">{title}</div>'
        f'<div style="font-size:13px;color:#9494AE;line-height:1.65;">{body}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    render_sidebar()

    st.markdown(
        '<div style="margin-bottom:0.15rem;display:flex;align-items:baseline;gap:7px;">'
        '<span style="font-size:28px;font-weight:800;letter-spacing:-0.05em;color:#0F0E1C;">Stil</span>'
        '<span style="font-size:28px;font-weight:800;color:#6B4EFF;">✦</span>'
        '</div>'
        '<div style="font-size:11px;color:#9494AE;letter-spacing:0.06em;'
        'text-transform:uppercase;font-weight:600;margin-bottom:1.4rem;">'
        'Creative editing with memory'
        '</div>',
        unsafe_allow_html=True
    )

    for key, default in [("cohesion_result", None), ("transfer_result", None),
                          ("eval_result", None), ("all_previews", [])]:
        if key not in st.session_state:
            st.session_state[key] = default

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Edit", "Style", "Insights", "Assets", "Feed"])
    with tab1:
        tab_agent()
    with tab2:
        tab_memory()
    with tab3:
        tab_evals()
    with tab4:
        tab_assets()
    with tab5:
        tab_feed()


if __name__ == "__main__":
    main()
