"""
app.py — Stil Streamlit UI
Clean light design for creative professionals.
Run: streamlit run app.py
"""

import base64
import json
import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from agent import run_agent_streaming, load_style, extract_and_save_style, write_session_log
from asset_library import list_assets, find_asset

load_dotenv()

st.set_page_config(
    page_title="Stil",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Design tokens ────────────────────────────────────────────────────────────
# bg:       #F5F5FA  warm light gray page bg
# surface:  #FFFFFF  white cards / sidebar
# border:   #E4E4F0  subtle dividers
# text:     #111124  near-black
# muted:    #6B6B88  secondary text
# subtle:   #AAABB8  placeholder / timestamps
# accent:   #6B4EFF  violet
# green:    #16A34A  success / done
# orange:   #EA580C  firing / warning
# ──────────────────────────────────────────────────────────────────────────────

STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Page */
.stApp { background-color: #F5F5FA; }
.main .block-container { padding: 2rem 2.5rem 4rem; max-width: 900px; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E4E4F0 !important;
}
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.25rem; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    gap: 0;
    border-bottom: 1px solid #E4E4F0;
    margin-bottom: 1.5rem;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #AAABB8 !important;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.01em;
    padding: 0.55rem 1.1rem;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px;
}
.stTabs [aria-selected="true"] {
    color: #111124 !important;
    border-bottom-color: #6B4EFF !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }

/* Chat input */
[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    border: 1.5px solid #E4E4F0 !important;
    border-radius: 10px !important;
    color: #111124 !important;
    font-size: 14px !important;
}
[data-testid="stChatInput"]:focus-within textarea {
    border-color: #6B4EFF !important;
    box-shadow: 0 0 0 3px rgba(107,78,255,0.1) !important;
}

/* Buttons — primary */
.stButton > button[kind="primary"],
.stButton > button {
    background: #6B4EFF !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.45rem 1.1rem !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    box-shadow: 0 1px 3px rgba(107,78,255,0.25);
    transition: background 0.15s, box-shadow 0.15s;
}
.stButton > button:hover {
    background: #5A3EEE !important;
    box-shadow: 0 3px 10px rgba(107,78,255,0.3) !important;
}
/* secondary */
.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #6B6B88 !important;
    border: 1.5px solid #E4E4F0 !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #6B4EFF !important;
    color: #111124 !important;
}

/* Sample chip buttons */
.stButton > button.sample-chip {
    background: #FFFFFF !important;
    color: #6B4EFF !important;
    border: 1.5px solid #DDD8FF !important;
    border-radius: 20px !important;
    padding: 0.3rem 0.9rem !important;
    font-size: 12px !important;
    box-shadow: none !important;
}
.stButton > button.sample-chip:hover {
    background: #F0EEFF !important;
    box-shadow: none !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E4E4F0;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
[data-testid="stMetricLabel"] {
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    color: #AAABB8 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 600 !important;
    color: #111124 !important;
    letter-spacing: -0.02em !important;
}

/* Text input */
.stTextInput > div > div > input {
    background: #FFFFFF !important;
    border: 1.5px solid #E4E4F0 !important;
    border-radius: 8px !important;
    color: #111124 !important;
    font-size: 14px !important;
    padding: 0.55rem 0.9rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6B4EFF !important;
    box-shadow: 0 0 0 3px rgba(107,78,255,0.1) !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #FFFFFF !important;
    border: 1.5px solid #E4E4F0 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    color: #6B6B88 !important;
}

/* Expander */
details > summary {
    background: #FFFFFF !important;
    border: 1px solid #E4E4F0 !important;
    border-radius: 8px !important;
    color: #6B6B88 !important;
    font-size: 13px !important;
    padding: 0.6rem 0.9rem !important;
}
details[open] > summary { border-radius: 8px 8px 0 0 !important; }
details > div {
    background: #FAFAFA !important;
    border: 1px solid #E4E4F0 !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}

/* Divider */
hr { border-color: #E4E4F0; margin: 1.25rem 0; }

/* Alerts */
[data-testid="stAlert"] {
    background: #FFFFFF;
    border: 1px solid #E4E4F0;
    border-radius: 10px;
    font-size: 13px;
    color: #6B6B88;
}

/* Spinner */
[data-testid="stSpinner"] > div { border-top-color: #6B4EFF !important; }

/* JSON */
.stJson {
    background: #FAFAFA !important;
    border: 1px solid #E4E4F0 !important;
    border-radius: 8px !important;
    font-size: 12px !important;
}
</style>
"""

st.markdown(STYLES, unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────────────────────

def render_sidebar():
    memory = load_style()
    sig = memory.get("style_signature")

    st.sidebar.markdown(
        '<div style="font-size:20px;font-weight:600;letter-spacing:-0.03em;color:#111124;">'
        'Stil <span style="color:#6B4EFF;">✦</span></div>'
        '<div style="font-size:11px;color:#AAABB8;letter-spacing:0.04em;text-transform:uppercase;'
        'font-weight:500;margin-top:2px;">Your creative style</div>',
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        '<hr style="border-color:#E4E4F0;margin:1rem 0 0.9rem;">',
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        '<div style="font-size:10px;font-weight:600;letter-spacing:0.08em;'
        'text-transform:uppercase;color:#AAABB8;margin-bottom:0.6rem;">Profile</div>',
        unsafe_allow_html=True
    )

    if sig:
        tone = sig.get("tone", "—")
        crop = sig.get("crop_preference", "—")
        targets = sig.get("export_targets", [])
        notes = sig.get("notes", "")

        filter_style = sig.get("filter_style", "")
        tone_display = filter_style.capitalize() if filter_style and filter_style != "none" else (tone.capitalize() if tone != "—" else "—")
        rows = "".join([
            f'<div style="display:flex;justify-content:space-between;padding:0.45rem 0;'
            f'border-bottom:1px solid #F0F0F6;font-size:12px;">'
            f'<span style="color:#AAABB8;font-weight:500;">{k}</span>'
            f'<span style="color:#111124;font-weight:400;">{v}</span></div>'
            for k, v in [
                ("Style", tone_display),
                ("Crop", crop.capitalize() if crop != "—" else "—"),
                ("Export", ", ".join(targets) if targets else "—"),
            ]
        ])
        st.sidebar.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E4E4F0;border-radius:10px;'
            f'padding:0.2rem 0.85rem 0.4rem;">{rows}</div>',
            unsafe_allow_html=True
        )
        if notes:
            st.sidebar.markdown(
                f'<div style="font-size:11px;color:#AAABB8;line-height:1.55;margin-top:0.6rem;">'
                f'{notes}</div>',
                unsafe_allow_html=True
            )
        updated = memory.get("last_updated", "")
        if updated:
            st.sidebar.markdown(
                f'<div style="font-size:10px;color:#CCCCDA;margin-top:0.5rem;">'
                f'Updated {updated[:16]}</div>',
                unsafe_allow_html=True
            )
    else:
        st.sidebar.markdown(
            '<div style="font-size:12px;color:#AAABB8;line-height:1.6;">'
            'No profile yet.<br>Chat to build one automatically.</div>',
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
    st.markdown(
        '<p style="font-size:13px;color:#6B6B88;margin:-0.5rem 0 1.25rem;">'
        'Describe what you want. Stil picks the right tools and remembers your choices.'
        '</p>',
        unsafe_allow_html=True
    )

    # Init session state
    for key, default in [("messages", []), ("session_log", []), ("tool_trace", []),
                         ("pill_cycle", 0), ("img_cycle", 0), ("api_messages", []),
                         ("session_has_image", False)]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Image uploader ──────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:10px;font-weight:600;letter-spacing:0.07em;'
        'text-transform:uppercase;color:#AAABB8;margin-bottom:0.4rem;">Attach a photo</div>',
        unsafe_allow_html=True
    )
    uploaded_file = st.file_uploader(
        "photo",
        type=["jpg", "jpeg", "png", "webp"],
        key=f"img_upload_{st.session_state.img_cycle}",
        label_visibility="collapsed",
    )

    if uploaded_file:
        prev_col, info_col = st.columns([1, 5])
        with prev_col:
            st.image(uploaded_file, use_container_width=True)
        with info_col:
            st.markdown(
                f'<div style="font-size:12px;color:#6B6B88;padding-top:0.3rem;">'
                f'{uploaded_file.name}</div>'
                f'<div style="font-size:11px;color:#AAABB8;">'
                f'{round(uploaded_file.size / 1024)} KB · {uploaded_file.type}</div>',
                unsafe_allow_html=True
            )
    elif st.session_state.session_has_image:
        st.markdown(
            '<div style="font-size:11px;color:#AAABB8;padding:0.35rem 0;">'
            '↑ Using photo from this session — upload a new one to switch</div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ── Sample prompts ───────────────────────────────────────────────────────
    selected_sample = st.pills(
        "Try a prompt",
        SAMPLE_PROMPTS,
        key=f"sample_pills_{st.session_state.pill_cycle}",
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Chat history ─────────────────────────────────────────────────────────
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            img_html = ""
            if msg.get("image_b64"):
                img_html = (
                    f'<img src="data:{msg["image_media_type"]};base64,{msg["image_b64"]}" '
                    f'style="max-width:220px;max-height:160px;border-radius:8px;'
                    f'display:block;margin-bottom:6px;">'
                )
            st.markdown(
                f'<div style="display:flex;justify-content:flex-end;margin-bottom:0.75rem;">'
                f'<div style="background:#EEE9FF;border:1px solid #DDD8FF;border-radius:14px 14px 3px 14px;'
                f'padding:0.6rem 0.95rem;font-size:14px;color:#2A1A88;line-height:1.55;max-width:82%;">'
                f'{img_html}{msg["content"]}</div></div>',
                unsafe_allow_html=True
            )
        else:
            if msg.get("is_error"):
                st.markdown(
                    f'<div style="margin-bottom:0.75rem;">'
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
                        f'background:rgba(22,163,74,0.08);color:#16A34A;border:1px solid rgba(22,163,74,0.18);'
                        f'border-radius:20px;padding:2px 10px 2px 8px;font-size:11px;font-weight:500;">'
                        f'✓ {t["tool"]}</span>'
                        f'<span style="font-size:11px;color:#AAABB8;">→ {t["result"].get("action","done")}</span>'
                        for t in msg["tool_trace"]
                    )
                    tool_pills_html = f'<div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:6px;">{pills}</div>'
                st.markdown(
                    f'<div style="margin-bottom:0.75rem;">{tool_pills_html}'
                    f'<div style="background:#FFFFFF;border:1px solid #E4E4F0;border-radius:3px 14px 14px 14px;'
                    f'padding:0.65rem 1rem;font-size:14px;color:#2A2A3E;line-height:1.65;max-width:88%;'
                    f'box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
                    f'{msg["content"]}</div></div>',
                    unsafe_allow_html=True
                )

    # Chat input
    user_input = st.chat_input("What do you want to do with your photo?")

    # Use selected pill as input (increment cycle to reset pills after use)
    if selected_sample and not user_input:
        user_input = selected_sample
        st.session_state.pill_cycle += 1

    if user_input:
        # Capture image before session state is mutated
        img_bytes = None
        img_media_type = "image/jpeg"
        img_b64 = None
        if uploaded_file:
            uploaded_file.seek(0)
            img_bytes = uploaded_file.read()
            img_media_type = uploaded_file.type or "image/jpeg"
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "image_b64": img_b64,
            "image_media_type": img_media_type,
        })
        st.session_state.session_log.append({"role": "user", "content": user_input})

        # Show user bubble immediately (with thumbnail if image attached)
        img_html = ""
        if img_b64:
            img_html = (
                f'<img src="data:{img_media_type};base64,{img_b64}" '
                f'style="max-width:220px;max-height:160px;border-radius:8px;'
                f'display:block;margin-bottom:6px;">'
            )
        st.markdown(
            f'<div style="display:flex;justify-content:flex-end;margin-bottom:0.75rem;">'
            f'<div style="background:#EEE9FF;border:1px solid #DDD8FF;border-radius:14px 14px 3px 14px;'
            f'padding:0.6rem 0.95rem;font-size:14px;color:#2A1A88;line-height:1.55;max-width:82%;">'
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
            user_input, memory, img_bytes, img_media_type,
            conversation_history=st.session_state.api_messages
        ):
            if event["type"] == "tool_start":
                pill = (
                    f'<span style="display:inline-flex;align-items:center;gap:4px;'
                    f'background:rgba(234,88,12,0.07);color:#EA580C;border:1px solid rgba(234,88,12,0.18);'
                    f'border-radius:20px;padding:2px 10px 2px 8px;font-size:11px;font-weight:500;">'
                    f'⚡ {event["tool"]}</span> '
                )
                current_pills_html += pill
                tool_placeholder.markdown(
                    f'<div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:6px;">'
                    f'{current_pills_html}</div>',
                    unsafe_allow_html=True
                )

            elif event["type"] == "tool_end":
                action = event["result"].get("action", "done")
                current_pills_html = current_pills_html.replace(
                    f'background:rgba(234,88,12,0.07);color:#EA580C;border:1px solid rgba(234,88,12,0.18);'
                    f'border-radius:20px;padding:2px 10px 2px 8px;font-size:11px;font-weight:500;">'
                    f'⚡ {event["tool"]}</span>',
                    f'background:rgba(22,163,74,0.08);color:#16A34A;border:1px solid rgba(22,163,74,0.18);'
                    f'border-radius:20px;padding:2px 10px 2px 8px;font-size:11px;font-weight:500;">'
                    f'✓ {event["tool"]}</span>'
                    f'<span style="font-size:11px;color:#AAABB8;"> → {action}</span>'
                )
                tool_placeholder.markdown(
                    f'<div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:6px;">'
                    f'{current_pills_html}</div>',
                    unsafe_allow_html=True
                )
                session_tool_trace.append({"tool": event["tool"], "result": event["result"]})

            elif event["type"] == "text":
                full_response += event["content"]
                response_placeholder.markdown(
                    f'<div style="background:#FFFFFF;border:1px solid #E4E4F0;'
                    f'border-radius:3px 14px 14px 14px;padding:0.65rem 1rem;font-size:14px;'
                    f'color:#2A2A3E;line-height:1.65;max-width:88%;'
                    f'box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
                    f'{full_response}</div>',
                    unsafe_allow_html=True
                )

            elif event["type"] == "error":
                had_error = True
                full_response = event["content"]
                response_placeholder.markdown(
                    f'<div style="background:#FFF5F5;border:1px solid #FECACA;'
                    f'border-radius:10px;padding:0.75rem 1rem;font-size:13px;'
                    f'color:#991B1B;line-height:1.6;">'
                    f'⚠ {event["content"]}</div>',
                    unsafe_allow_html=True
                )

            elif event["type"] == "done":
                st.session_state.tool_trace.extend(event.get("tool_trace", []))
                new_api_messages = event.get("api_messages", [])

        if not had_error:
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "tool_trace": session_tool_trace
            })
            st.session_state.session_log.append({"role": "assistant", "content": full_response})
            # Persist full Claude API conversation history for next turn
            st.session_state.api_messages = new_api_messages
            if img_bytes:
                st.session_state.session_has_image = True
            extract_and_save_style(st.session_state.session_log, load_style())
            write_session_log(st.session_state.session_log, st.session_state.tool_trace)
            # Reset uploader so a new photo can be attached next turn
            st.session_state.img_cycle += 1
            st.rerun()
        else:
            # Keep user message in history; add error as assistant reply; don't log
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "is_error": True,
                "tool_trace": []
            })
            st.session_state.session_log.pop()  # remove from log only
            st.rerun()


# ─── Style Tab ────────────────────────────────────────────────────────────────

def tab_memory():
    st.markdown(
        '<p style="font-size:13px;color:#6B6B88;margin:-0.5rem 0 1.25rem;">'
        'What Stil remembers about you — injected automatically into every new session.'
        '</p>',
        unsafe_allow_html=True
    )

    memory = load_style()
    sig = memory.get("style_signature")

    if not sig:
        _empty_state("✦", "No style profile yet",
                     "Go to the Edit tab and have a conversation.<br>Stil extracts preferences automatically.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Tone", sig.get("tone", "—").capitalize())
    with c2:
        st.metric("Crop", sig.get("crop_preference", "—").capitalize())
    with c3:
        targets = sig.get("export_targets", [])
        st.metric("Export targets", str(len(targets)))

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    if targets:
        st.markdown(_section_label("Export platforms"), unsafe_allow_html=True)
        pills = " ".join(_tag_pill(t) for t in targets)
        st.markdown(pills, unsafe_allow_html=True)
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    if sig.get("notes"):
        st.markdown(_section_label("Summary"), unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E4E4F0;border-radius:10px;'
            f'padding:0.85rem 1rem;font-size:14px;color:#3A3A5C;line-height:1.7;">'
            f'{sig["notes"]}</div>',
            unsafe_allow_html=True
        )
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    if memory.get("last_updated"):
        st.markdown(
            f'<div style="font-size:11px;color:#CCCCDA;">Last updated: {memory["last_updated"][:16]}</div>',
            unsafe_allow_html=True
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    with st.expander("Raw style_profile.json"):
        st.json(memory)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if st.button("Clear style memory", key="clear_memory"):
        if os.path.exists("style_profile.json"):
            os.remove("style_profile.json")
        st.session_state.api_messages = []
        st.session_state.session_has_image = False
        st.rerun()


# ─── Insights Tab ─────────────────────────────────────────────────────────────

def tab_evals():
    st.markdown(
        '<p style="font-size:13px;color:#6B6B88;margin:-0.5rem 0 1.25rem;">'
        'Grade sessions on tool accuracy, goal completion, and creative intent.'
        '</p>',
        unsafe_allow_html=True
    )

    log_count = len([f for f in os.listdir("logs") if f.endswith(".jsonl")]) \
        if os.path.exists("logs") else 0

    col_btn, col_info = st.columns([1, 4])
    with col_btn:
        run_clicked = st.button("Run evals", type="primary", use_container_width=True)
    with col_info:
        st.markdown(
            f'<div style="font-size:13px;color:#AAABB8;padding-top:0.55rem;">'
            f'{log_count} session log{"s" if log_count != 1 else ""} available</div>',
            unsafe_allow_html=True
        )

    if run_clicked:
        if log_count == 0:
            st.warning("No session logs found. Complete a chat session in the Edit tab first.")
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

    # Score cards with inline bar
    c1, c2, c3 = st.columns(3)
    for col, label, dim in [
        (c1, "Tool accuracy", "tool_accuracy"),
        (c2, "Goal completion", "goal_completion"),
        (c3, "Creative intent", "creative_intent"),
    ]:
        score = scores.get(dim, 0)
        pct = int((score / 5) * 100)
        col.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E4E4F0;border-radius:12px;'
            f'padding:1rem 1.1rem;box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
            f'<div style="font-size:10px;font-weight:600;letter-spacing:0.07em;'
            f'text-transform:uppercase;color:#AAABB8;margin-bottom:0.35rem;">{label}</div>'
            f'<div style="font-size:1.9rem;font-weight:600;color:#111124;letter-spacing:-0.03em;">'
            f'{score}<span style="font-size:1rem;color:#CCCCDA;font-weight:400;"> /5</span></div>'
            f'<div style="background:#F0F0F6;border-radius:4px;height:4px;margin-top:8px;">'
            f'<div style="width:{pct}%;height:100%;border-radius:4px;'
            f'background:linear-gradient(90deg,#6B4EFF,#9B81FF);"></div></div>'
            f'</div>',
            unsafe_allow_html=True
        )

    if graded:
        st.markdown("<div style='height:1.1rem'></div>", unsafe_allow_html=True)
        st.markdown(_section_label("Score by turn"), unsafe_allow_html=True)
        df = pd.DataFrame([{
            "Turn": f"T{t['turn']}",
            "Tool accuracy": t.get("tool_accuracy", 0),
            "Goal completion": t.get("goal_completion", 0),
            "Creative intent": t.get("creative_intent", 0),
        } for t in graded]).set_index("Turn")
        st.bar_chart(df, height=180, color=["#6B4EFF", "#16A34A", "#EA580C"])

    if summary:
        st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
        st.markdown(_section_label("Product health summary"), unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E4E4F0;border-radius:10px;'
            f'padding:1rem 1.1rem;font-size:14px;color:#3A3A5C;line-height:1.8;">'
            f'{summary}</div>',
            unsafe_allow_html=True
        )

    if os.path.exists("insights_report.md"):
        with open("insights_report.md") as f:
            report_md = f.read()
        with st.expander("Full insights_report.md"):
            st.markdown(report_md)


# ─── Assets Tab ───────────────────────────────────────────────────────────────

def tab_assets():
    st.markdown(
        '<p style="font-size:13px;color:#6B6B88;margin:-0.5rem 0 1.25rem;">'
        'Describe what you need. Stil scores your library by keyword match and AI tags.'
        '</p>',
        unsafe_allow_html=True
    )

    assets = list_assets()
    asset_files = assets.get("assets", [])

    if not asset_files:
        _empty_state("◻", "No assets found",
                     'Drop JPG/PNG files with descriptive names into <code>assets/</code>.')
        st.code(
            "portrait_warm_natural_light.jpg\n"
            "dark_high_contrast_abstract_bg.jpg\n"
            "soft_pastel_gradient_bg.jpg"
        )
        return

    st.markdown(
        f'<div style="font-size:12px;color:#AAABB8;margin-bottom:1rem;">'
        f'{len(asset_files)} asset{"s" if len(asset_files) != 1 else ""} in library</div>',
        unsafe_allow_html=True
    )

    query = st.text_input(
        "search",
        placeholder="high contrast background for a social post…",
        label_visibility="collapsed"
    )

    if query:
        with st.spinner("Searching…"):
            result = find_asset(query)

        if result.get("results"):
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            for r in result["results"]:
                filepath = os.path.join("assets", r["filename"])
                c1, c2 = st.columns([1, 4])
                with c1:
                    if os.path.exists(filepath):
                        st.image(filepath, use_container_width=True)
                    else:
                        st.markdown(
                            '<div style="background:#F5F5FA;border:1px solid #E4E4F0;'
                            'border-radius:8px;height:80px;display:flex;align-items:center;'
                            'justify-content:center;color:#CCCCDA;font-size:20px;">◻</div>',
                            unsafe_allow_html=True
                        )
                with c2:
                    tags_html = " ".join(_tag_pill(t) for t in (r.get("tags") or []))
                    st.markdown(
                        f'<div style="background:#FFFFFF;border:1px solid #E4E4F0;border-radius:10px;'
                        f'padding:0.85rem 1rem;box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
                        f'<div style="font-size:10px;font-weight:600;letter-spacing:0.07em;'
                        f'text-transform:uppercase;color:#6B4EFF;margin-bottom:0.25rem;">#{r["rank"]}</div>'
                        f'<div style="font-size:14px;font-weight:500;color:#111124;margin-bottom:0.35rem;">'
                        f'{r["filename"]}</div>'
                        f'<div style="margin-bottom:0.4rem;">{tags_html}</div>'
                        f'<div style="font-size:12px;color:#AAABB8;line-height:1.5;">{r["rationale"]}</div>'
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
                        '<div style="background:#FFFFFF;border:1px solid #E4E4F0;border-radius:8px;'
                        'height:100px;"></div>',
                        unsafe_allow_html=True
                    )
                st.markdown(
                    f'<div style="font-size:10px;color:#AAABB8;text-align:center;margin-top:4px;'
                    f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{label}</div>',
                    unsafe_allow_html=True
                )


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _section_label(text: str) -> str:
    return (
        f'<div style="font-size:10px;font-weight:600;letter-spacing:0.08em;'
        f'text-transform:uppercase;color:#AAABB8;margin-bottom:0.6rem;">{text}</div>'
    )


def _tag_pill(text: str) -> str:
    return (
        f'<span style="display:inline-block;background:rgba(107,78,255,0.07);'
        f'color:#6B4EFF;border:1px solid rgba(107,78,255,0.18);border-radius:20px;'
        f'font-size:10px;font-weight:500;padding:2px 9px;margin:2px 3px 2px 0;">{text}</span>'
    )


def _empty_state(icon: str, title: str, body: str):
    st.markdown(
        f'<div style="text-align:center;padding:3rem 1rem;color:#AAABB8;">'
        f'<div style="font-size:2rem;margin-bottom:0.75rem;">{icon}</div>'
        f'<div style="font-size:15px;font-weight:500;color:#6B6B88;margin-bottom:0.4rem;">{title}</div>'
        f'<div style="font-size:13px;line-height:1.65;">{body}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    render_sidebar()

    st.markdown(
        '<div style="margin-bottom:0.2rem;">'
        '<span style="font-size:24px;font-weight:600;letter-spacing:-0.04em;color:#111124;">Stil</span>'
        '<span style="font-size:24px;font-weight:600;color:#6B4EFF;margin-left:4px;">✦</span>'
        '</div>'
        '<div style="font-size:11px;color:#AAABB8;letter-spacing:0.05em;'
        'text-transform:uppercase;font-weight:500;margin-bottom:1.5rem;">'
        'Creative editing with memory'
        '</div>',
        unsafe_allow_html=True
    )

    tab1, tab2, tab3, tab4 = st.tabs(["Edit", "Style", "Insights", "Assets"])
    with tab1:
        tab_agent()
    with tab2:
        tab_memory()
    with tab3:
        tab_evals()
    with tab4:
        tab_assets()


if __name__ == "__main__":
    main()
