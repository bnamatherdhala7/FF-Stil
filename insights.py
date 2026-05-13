"""
insights.py — Stil quality insights
Grades session logs on 3 dimensions: tool_accuracy, goal_completion, creative_intent.
Uses RAG (Pinecone) when index has examples — falls back to Haiku per turn.
RAG path: embed turn → nearest-neighbor lookup → reuse score if similarity ≥ 0.88.
Graded turns are stored back to Pinecone, so the index compounds over time.
"""

import json
import os
import hashlib
import datetime
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5"
LOGS_DIR = "logs"
REPORT_FILE = "insights_report.md"

# Pinecone config
INDEX_NAME = "stil-evals-v1"
RAG_SIMILARITY_THRESHOLD = 0.88
RAG_MIN_INDEX_SIZE = 10  # require at least this many vectors before using RAG


GRADING_PROMPT = """Grade this agent interaction on 3 dimensions.
Return ONLY valid JSON, no other text:
{{"tool_accuracy": <1-5>, "goal_completion": <1-5>, "creative_intent": <1-5>}}

Rubric:
- tool_accuracy: Did the agent call the right tools for the request? (1=wrong tools, 5=perfect choices)
- goal_completion: Did the agent complete what the user literally asked for? (1=failed, 5=fully complete)
- creative_intent: Did the output serve what the user ACTUALLY wanted as a creative? (1=missed intent, 5=nailed it)

User message: {user_message}
Agent response: {agent_response}
Tools called: {tools_called}"""


# ─── Pinecone helpers ─────────────────────────────────────────────────────────

def _get_pinecone():
    """Lazy Pinecone init. Returns (pc, index) or (None, None) if unavailable."""
    try:
        from pinecone import Pinecone, ServerlessSpec
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            return None, None
        pc = Pinecone(api_key=api_key)
        existing = [idx.name for idx in pc.list_indexes().indexes]
        if INDEX_NAME not in existing:
            pc.create_index(
                name=INDEX_NAME,
                dimension=1024,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        index = pc.Index(INDEX_NAME)
        return pc, index
    except Exception as e:
        print(f"[Pinecone] init failed: {e}")
        return None, None


def _turn_text(turn: dict) -> str:
    """Canonical text for embedding a turn."""
    tools = ", ".join(turn.get("tools_called", [])) or "none"
    return (
        f"User: {turn['user_message']}\n"
        f"Agent: {turn['agent_response']}\n"
        f"Tools: {tools}"
    )


def _turn_id(turn: dict) -> str:
    """Deterministic vector ID from turn content hash."""
    return hashlib.sha256(_turn_text(turn).encode()).hexdigest()[:16]


def _embed(pc, text: str, input_type: str = "passage") -> list:
    """Embed text using Pinecone Inference API (multilingual-e5-large, 1024 dims)."""
    result = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[text],
        parameters={"input_type": input_type}
    )
    return result[0].values


def store_graded_turn(pc, index, turn: dict, scores: dict):
    """Upsert a graded turn into Pinecone for future RAG lookups."""
    try:
        text = _turn_text(turn)
        embedding = _embed(pc, text, input_type="passage")
        index.upsert(vectors=[{
            "id": _turn_id(turn),
            "values": embedding,
            "metadata": {
                "user_message": turn["user_message"][:250],
                "agent_response": turn["agent_response"][:250],
                "tools": ", ".join(turn.get("tools_called", [])),
                "tool_accuracy": float(scores.get("tool_accuracy", 3)),
                "goal_completion": float(scores.get("goal_completion", 3)),
                "creative_intent": float(scores.get("creative_intent", 3)),
                "session": turn.get("session", ""),
            }
        }])
    except Exception as e:
        print(f"[Pinecone] store failed: {e}")


def _rag_lookup(pc, index, turn: dict) -> dict | None:
    """
    Query Pinecone for similar graded turns.
    Returns score dict if a match with similarity ≥ threshold found, else None.
    """
    try:
        stats = index.describe_index_stats()
        total = stats.get("total_vector_count", 0)
        if total < RAG_MIN_INDEX_SIZE:
            return None

        text = _turn_text(turn)
        q_vec = _embed(pc, text, input_type="query")
        results = index.query(vector=q_vec, top_k=3, include_metadata=True)

        if not results.matches:
            return None

        best = results.matches[0]
        if best.score < RAG_SIMILARITY_THRESHOLD:
            return None

        meta = best.metadata
        return {
            "tool_accuracy": round(meta["tool_accuracy"]),
            "goal_completion": round(meta["goal_completion"]),
            "creative_intent": round(meta["creative_intent"]),
            "_rag_score": best.score,
            "_rag_n": total,
        }
    except Exception as e:
        print(f"[Pinecone] lookup failed: {e}")
        return None


# ─── Session loading ──────────────────────────────────────────────────────────

def load_all_sessions() -> list:
    """Load all JSONL session files from logs/."""
    sessions = []
    if not os.path.exists(LOGS_DIR):
        return sessions
    for filename in sorted(os.listdir(LOGS_DIR)):
        if not filename.endswith(".jsonl"):
            continue
        session = {"filename": filename, "messages": [], "tool_calls": []}
        with open(os.path.join(LOGS_DIR, filename)) as f:
            for line in f:
                entry = json.loads(line.strip())
                if entry["type"] == "message":
                    session["messages"].append(entry["data"])
                elif entry["type"] == "tool_call":
                    session["tool_calls"].append(entry["data"])
        sessions.append(session)
    return sessions


def build_turns(session: dict) -> list:
    """Pair user/agent messages into gradeable turns."""
    turns = []
    messages = session["messages"]
    tool_calls = session["tool_calls"]
    for i in range(0, len(messages) - 1, 2):
        if i + 1 < len(messages):
            user_msg = messages[i].get("content", "")
            agent_msg = messages[i + 1].get("content", "")
            if isinstance(user_msg, str) and isinstance(agent_msg, str):
                tools = [t["tool"] for t in tool_calls]
                turns.append({
                    "session": session["filename"],
                    "turn": i // 2 + 1,
                    "user_message": user_msg[:300],
                    "agent_response": agent_msg[:300],
                    "tools_called": tools,
                })
    return turns


# ─── Grading ──────────────────────────────────────────────────────────────────

def _grade_haiku(turn: dict) -> dict:
    """Grade one turn with Haiku. Returns score dict."""
    prompt = GRADING_PROMPT.format(
        user_message=turn["user_message"],
        agent_response=turn["agent_response"],
        tools_called=", ".join(turn["tools_called"]) or "none"
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        raw = response.content[0].text.strip()
        return json.loads(raw)
    except Exception:
        return {"tool_accuracy": 3, "goal_completion": 3, "creative_intent": 3}


def grade_turns_sync(turns: list) -> list:
    """
    Grade all turns. Uses RAG (Pinecone) when available; Haiku as fallback.
    Stores every Haiku-graded turn back to Pinecone so the index compounds.
    """
    pc, index = _get_pinecone()
    results = []
    rag_hits = 0
    haiku_calls = 0

    for turn in turns:
        rag_result = None
        if pc is not None:
            rag_result = _rag_lookup(pc, index, turn)

        if rag_result:
            scores = {k: v for k, v in rag_result.items() if not k.startswith("_")}
            rag_hits += 1
            print(f"  ↑ RAG hit (similarity={rag_result['_rag_score']:.2f}, "
                  f"n={rag_result['_rag_n']}) — skipped Haiku call")
        else:
            scores = _grade_haiku(turn)
            haiku_calls += 1
            if pc is not None:
                store_graded_turn(pc, index, turn, scores)

        results.append({**turn, **scores})

    if rag_hits or haiku_calls:
        total = rag_hits + haiku_calls
        saved = rag_hits / total * 100 if total else 0
        print(f"\n[Evals] {total} turns — RAG: {rag_hits}, Haiku: {haiku_calls} "
              f"({saved:.0f}% API calls saved)")

    return results


# ─── Aggregation and reporting ────────────────────────────────────────────────

def aggregate_scores(graded_turns: list) -> dict:
    if not graded_turns:
        return {}
    dims = ["tool_accuracy", "goal_completion", "creative_intent"]
    totals = {d: 0 for d in dims}
    for t in graded_turns:
        for d in dims:
            totals[d] += t.get(d, 3)
    n = len(graded_turns)
    return {d: round(totals[d] / n, 1) for d in dims}


def generate_health_summary(scores: dict, turn_count: int) -> str:
    prompt = f"""Write a 3-paragraph Product Health Report for an AI creative assistant agent.
Use these eval scores (out of 5): {json.dumps(scores)}
Total interactions graded: {turn_count}

Paragraph 1: Overall health assessment
Paragraph 2: Biggest strength and biggest gap
Paragraph 3: Top 2 recommendations for improvement

Write in a PM voice. Be specific and actionable. No bullet points."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def write_report(graded_turns: list, scores: dict, summary: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Stil — Quality Insights Report",
        f"Generated: {timestamp}",
        "",
        "## Aggregate Scores",
        "",
        "| Dimension | Score |",
        "|-----------|-------|",
        f"| Tool accuracy | {scores.get('tool_accuracy', 0)} / 5 |",
        f"| Goal completion | {scores.get('goal_completion', 0)} / 5 |",
        f"| Creative intent | {scores.get('creative_intent', 0)} / 5 |",
        "",
        "## Health Summary",
        "",
        summary,
        "",
        "## Turn-by-Turn Scores",
        "",
        "| Session | Turn | Tool acc. | Goal comp. | Creative intent |",
        "|---------|------|-----------|------------|-----------------|",
    ]
    for t in graded_turns:
        lines.append(
            f"| {t['session']} | {t['turn']} | "
            f"{t.get('tool_accuracy', '-')} | "
            f"{t.get('goal_completion', '-')} | "
            f"{t.get('creative_intent', '-')} |"
        )
    with open(REPORT_FILE, "w") as f:
        f.write("\n".join(lines))


def run_insights() -> dict:
    """Main entry point. Returns dict for Streamlit."""
    sessions = load_all_sessions()
    if not sessions:
        print("No session logs found in logs/. Run agent.py first.")
        return {}

    all_turns = []
    for session in sessions:
        all_turns.extend(build_turns(session))

    if not all_turns:
        print("No scoreable turns found.")
        return {}

    print(f"Grading {len(all_turns)} turns across {len(sessions)} sessions...")
    graded = grade_turns_sync(all_turns)
    scores = aggregate_scores(graded)
    summary = generate_health_summary(scores, len(graded))
    write_report(graded, scores, summary)

    print("\n--- Stil Quality Insights ---")
    print(f"Tool accuracy:    {scores.get('tool_accuracy')} / 5")
    print(f"Goal completion:  {scores.get('goal_completion')} / 5")
    print(f"Creative intent:  {scores.get('creative_intent')} / 5")
    print(f"\n{summary}")
    print(f"\nFull report saved to {REPORT_FILE}")

    return {"scores": scores, "graded_turns": graded, "summary": summary}


if __name__ == "__main__":
    run_insights()
