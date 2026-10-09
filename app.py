import html
import os

import requests
import streamlit as st


API_URL = os.getenv(
    "ORACLE_X_API_URL",
    "https://oracle-x.fastapicloud.dev",
).rstrip("/")


st.set_page_config(
    page_title="ORACLE-X | Decision Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def esc(value):
    """Escape any API-provided value before putting it inside HTML."""
    if value is None:
        return ""
    return html.escape(str(value))


def md(markup):
    """
    Render an HTML snippet.

    Streamlit's markdown turns any line indented by 4+ spaces into a code
    block, which is what printed the stray "</div>" boxes before. Stripping
    every line's indentation makes that impossible.
    """
    flat = "".join(line.strip() for line in markup.splitlines())
    st.markdown(flat, unsafe_allow_html=True)


def pretty(value):
    """Turn API codes like INSUFFICIENT_EVIDENCE into readable text."""
    friendly = {
        "ACTIONABLE": "Action recommended",
        "VALID": "Verified",
        "INVALID": "Failed verification",
        "HIGH": "High",
        "MEDIUM": "Medium",
        "LOW": "Low",
        "CRITICAL": "Critical",
        "MODERATE": "Moderate",
        "SIMULATED": "Simulated",
        "INTERPRETATION_AVAILABLE": "Available",
        "OBSERVED_HISTORICAL": "Real historical data",
        "MODEL_DERIVED": "Calculated by a model",
        "DETERMINISTIC_RCA": "Rule-based analysis",
        "DETERMINISTIC_OBSERVED_OUTCOMES": "Rule-based, from real outcomes",
        "DETERMINISTIC_READ_ONLY": "Rule-based, read only",
        "LLM_EVIDENCE_INTERPRETATION": "AI-written explanation",
    }
    text = str(value).strip()
    return friendly.get(text.upper(), text.replace("_", " ").capitalize())


def tone_for(value):
    """Pick a colour tone for a status value."""
    v = str(value).strip().upper()
    if v in {"VALID", "PASS", "COMPLETED", "TRUE", "AVAILABLE",
             "STRUCTURALLY_STRONG", "LOW", "OBSERVED_HISTORICAL",
             "INTERPRETATION_AVAILABLE"}:
        return "good"
    if v in {"ACTIONABLE"}:
        return "info"
    if v in {"MEDIUM", "MODERATE", "WARNING", "PENDING", "SIMULATED",
             "INSUFFICIENT_LEARNING_DATA", "INSUFFICIENT-EVIDENCE"}:
        return "warn"
    if v in {"HIGH", "CRITICAL", "INVALID", "FAILED", "REJECTED",
             "FALSE", "ERROR"}:
        return "bad"
    if v in {"MODEL_DERIVED"}:
        return "info"
    return "neutral"


def chip(text, tone="neutral", prefix=""):
    label = f"<span class='ox-chip-prefix'>{esc(prefix)}</span>" if prefix else ""
    return f"<span class='ox-chip ox-{tone}'><i></i>{label}{esc(text)}</span>"


def num(source, key, default=0.0):
    try:
        return float(source.get(key, default))
    except (TypeError, ValueError, AttributeError):
        return default


def items_html(items, empty_text):
    if not items:
        return f"<div class='ox-empty-line'>{esc(empty_text)}</div>"
    rows = "".join(f"<li>{esc(i)}</li>" for i in items)
    return f"<ul class='ox-list'>{rows}</ul>"


def metric_card(label, value, delta_text, delta_value, source_text, source_tone):
    if delta_value > 0:
        d_tone, arrow = "good", "▲"
    elif delta_value < 0:
        d_tone, arrow = "bad", "▼"
    else:
        d_tone, arrow = "neutral", "–"
    return f"""
    <div class="ox-metric">
        <div class="ox-metric-label">{esc(label)}</div>
        <div class="ox-metric-value">{esc(value)}</div>
        <div class="ox-metric-foot">
            <span class="ox-delta ox-{d_tone}">{arrow} {esc(delta_text)}</span>
            {chip(source_text, source_tone)}
        </div>
    </div>
    """


def confidence_meter(level):
    v = str(level).strip().upper()
    filled = {"LOW": 1, "MEDIUM": 2, "MODERATE": 2, "HIGH": 3}.get(v, 0)
    tone = {1: "bad", 2: "warn", 3: "good"}.get(filled, "neutral")
    bars = "".join(
        f"<b class='{'ox-on ox-' + tone if i < filled else ''}'></b>"
        for i in range(3)
    )
    return f"""
    <div class="ox-confidence">
        <div class="ox-meter">{bars}</div>
        <span>{esc(pretty(level))} confidence</span>
    </div>
    """


def section(title, subtitle=""):
    sub = f"<p>{esc(subtitle)}</p>" if subtitle else ""
    md(f"<div class='ox-section'><h3>{esc(title)}</h3>{sub}</div>")


# ---------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --ink: #12141c;
    --ink-2: #454a58;
    --muted: #7a8090;
    --line: #e8eaf0;
    --line-2: #d9dce5;
    --bg: #ffffff;
    --soft: #f6f7fa;
    --accent: #3555f0;
    --accent-soft: #eef1ff;
    --good: #12805c;   --good-bg: #e8f6f0;
    --warn: #a8620a;   --warn-bg: #fdf3e2;
    --bad: #c23b3b;    --bad-bg: #fdecec;
    --info: #3555f0;   --info-bg: #eef1ff;
    --neutral: #5b6070; --neutral-bg: #f1f2f6;
    --r-sm: 10px;
    --r-lg: 20px;
}

/* ---------- base ---------- */
html, body, .stApp, .stMarkdown, button, input, textarea,
[data-baseweb="tab"], [data-testid="stNumberInput"] {
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
.stApp { background: var(--bg); color: var(--ink); }
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container {
    max-width: 1080px;
    padding: 2.2rem 1.6rem 5rem 1.6rem;
}
[data-testid="stVerticalBlock"] { gap: 0.9rem; }

/* ---------- top bar ---------- */
.ox-top {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 1.1rem;
}
.ox-brand { display: flex; align-items: center; gap: 0.7rem; }
.ox-logo {
    width: 38px; height: 38px; border-radius: 11px;
    background: var(--ink); color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.ox-brand-name { font-weight: 800; font-size: 1.15rem; letter-spacing: -0.02em; color: var(--ink); }
.ox-brand-tag { font-size: 0.78rem; color: var(--muted); margin-top: 1px; }
.ox-live {
    display: inline-flex; align-items: center; gap: 0.45rem;
    font-size: 0.78rem; font-weight: 600; color: var(--ink-2);
    border: 1px solid var(--line); border-radius: 999px; padding: 0.4rem 0.8rem;
}
.ox-live i { width: 7px; height: 7px; border-radius: 50%; background: var(--good); }

/* ---------- intro ---------- */
.ox-intro { padding: 1.6rem 0 0.4rem 0; }
.ox-intro h1 {
    font-size: 2.7rem; line-height: 1.1; font-weight: 800;
    letter-spacing: -0.04em; color: var(--ink); margin: 0; padding: 0;
}
.ox-intro p {
    max-width: 640px; margin: 0.9rem 0 0 0;
    font-size: 1.02rem; line-height: 1.65; color: var(--ink-2);
}

/* ---------- run panel ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--line) !important;
    border-radius: var(--r-lg) !important;
    background: var(--soft);
    padding: 0.4rem 0.5rem;
}
[data-testid="stNumberInput"] label p {
    font-size: 0.85rem; font-weight: 600; color: var(--ink);
}
[data-testid="stNumberInput"] input {
    background: #fff; color: var(--ink); font-weight: 600;
    border-radius: var(--r-sm);
}
[data-testid="stNumberInput"] div[data-baseweb="input"] {
    border-radius: var(--r-sm); border: 1px solid var(--line-2); background: #fff;
}
[data-testid="stNumberInput"] button { background: #fff; color: var(--ink-2); }
.stButton > button {
    min-height: 46px; border-radius: var(--r-sm);
    background: var(--accent); border: 1px solid var(--accent);
    color: #fff; font-weight: 700; font-size: 0.95rem;
    transition: background 0.15s ease;
}
.stButton > button p { color: #fff !important; font-weight: 700; }
.stButton > button:hover { background: #2a45d1; border-color: #2a45d1; color: #fff; }
.stButton > button:focus-visible { outline: 3px solid #b9c5ff; outline-offset: 2px; }
.ox-hint { font-size: 0.82rem; color: var(--muted); padding: 0 0.2rem; }

/* ---------- how it works ---------- */
.ox-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.9rem; margin-top: 0.4rem; }
.ox-step { border: 1px solid var(--line); border-radius: var(--r-lg); padding: 1.2rem 1.3rem; }
.ox-step b { display: block; font-size: 0.98rem; color: var(--ink); margin-bottom: 0.3rem; }
.ox-step span { font-size: 0.88rem; line-height: 1.55; color: var(--ink-2); }

/* ---------- section titles ---------- */
.ox-section { margin: 1.9rem 0 0.2rem 0; }
.ox-section h3 {
    font-size: 1.35rem; font-weight: 750; letter-spacing: -0.025em;
    color: var(--ink); margin: 0; padding: 0;
}
.ox-section p { margin: 0.35rem 0 0 0; font-size: 0.92rem; line-height: 1.55; color: var(--muted); max-width: 680px; }

/* ---------- chips ---------- */
.ox-chip {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.3rem 0.65rem; border-radius: 999px;
    font-size: 0.78rem; font-weight: 650; white-space: nowrap;
}
.ox-chip i { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.ox-chip-prefix { font-weight: 500; opacity: 0.75; }
.ox-chip.ox-good, .ox-delta.ox-good { background: var(--good-bg); color: var(--good); }
.ox-chip.ox-warn, .ox-delta.ox-warn { background: var(--warn-bg); color: var(--warn); }
.ox-chip.ox-bad,  .ox-delta.ox-bad  { background: var(--bad-bg);  color: var(--bad); }
.ox-chip.ox-info, .ox-delta.ox-info { background: var(--info-bg); color: var(--info); }
.ox-chip.ox-neutral, .ox-delta.ox-neutral { background: var(--neutral-bg); color: var(--neutral); }

/* ---------- verdict (the one standout element) ---------- */
.ox-verdict {
    border: 1px solid var(--line); border-radius: 24px;
    padding: 2rem 2.1rem; background: #fff;
    box-shadow: 0 1px 0 rgba(18, 20, 28, 0.02), 0 18px 40px -24px rgba(18, 20, 28, 0.18);
}
.ox-incident-id { font-size: 0.85rem; font-weight: 600; color: var(--muted); }
.ox-verdict-title {
    font-size: 1.9rem; line-height: 1.2; font-weight: 800;
    letter-spacing: -0.035em; color: var(--ink); margin: 0.5rem 0 0 0;
}
.ox-verdict-sub {
    font-size: 1rem; line-height: 1.65; color: var(--ink-2);
    margin: 0.7rem 0 0 0; max-width: 720px;
}
.ox-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1.3rem; }

.ox-action {
    margin-top: 1.4rem; padding: 1.4rem 1.6rem;
    border-radius: var(--r-lg); background: var(--accent-soft);
}
.ox-action-label { font-size: 0.85rem; font-weight: 700; color: var(--accent); }
.ox-action-text { font-size: 1.3rem; line-height: 1.4; font-weight: 700; color: var(--ink); margin-top: 0.35rem; letter-spacing: -0.02em; }
.ox-action-why { font-size: 0.92rem; line-height: 1.65; color: var(--ink-2); margin-top: 0.7rem; }

/* ---------- metrics ---------- */
.ox-metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.9rem; }
.ox-metric { border: 1px solid var(--line); border-radius: var(--r-lg); padding: 1.2rem 1.25rem; background: #fff; }
.ox-metric-label { font-size: 0.88rem; font-weight: 600; color: var(--ink-2); }
.ox-metric-value { font-size: 1.9rem; font-weight: 800; letter-spacing: -0.04em; color: var(--ink); margin-top: 0.5rem; }
.ox-metric-foot { display: flex; flex-wrap: wrap; align-items: center; gap: 0.45rem; margin-top: 0.8rem; }
.ox-delta { display: inline-flex; padding: 0.3rem 0.6rem; border-radius: 999px; font-size: 0.78rem; font-weight: 700; }
.ox-note { font-size: 0.82rem; color: var(--muted); margin-top: 0.7rem; line-height: 1.55; }

/* ---------- causes ---------- */
.ox-causes { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.9rem; }
.ox-cause { border: 1px solid var(--line); border-radius: var(--r-lg); padding: 1.3rem 1.4rem; background: #fff; }
.ox-cause-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }
.ox-cause-title { font-size: 1.05rem; font-weight: 750; color: var(--ink); letter-spacing: -0.015em; }
.ox-confidence { display: flex; flex-direction: column; align-items: flex-end; gap: 0.3rem; font-size: 0.75rem; color: var(--muted); font-weight: 600; white-space: nowrap; }
.ox-meter { display: flex; gap: 3px; }
.ox-meter b { width: 20px; height: 6px; border-radius: 3px; background: var(--line); display: block; }
.ox-meter b.ox-on.ox-good { background: var(--good); }
.ox-meter b.ox-on.ox-warn { background: #e0a23b; }
.ox-meter b.ox-on.ox-bad  { background: var(--bad); }
.ox-cause-block { margin-top: 1rem; }
.ox-cause-block b { display: block; font-size: 0.8rem; font-weight: 700; color: var(--ink); margin-bottom: 0.2rem; }
.ox-cause-block span { font-size: 0.88rem; line-height: 1.55; color: var(--ink-2); }
.ox-cause-type { margin-top: 1rem; }

/* ---------- plain-words card ---------- */
.ox-plain { border: 1px solid var(--line); border-radius: var(--r-lg); padding: 1.5rem 1.7rem; background: var(--soft); }
.ox-plain p { font-size: 1.02rem; line-height: 1.8; color: var(--ink); margin: 0; }
.ox-plain small { display: block; margin-top: 1rem; font-size: 0.8rem; color: var(--muted); }

/* ---------- tabs ---------- */
[data-baseweb="tab-list"] { gap: 0.4rem; border-bottom: 1px solid var(--line); }
[data-baseweb="tab"] { height: 44px; padding: 0 0.9rem; font-weight: 600; color: var(--muted); background: transparent; }
[data-baseweb="tab"][aria-selected="true"] { color: var(--ink); }
[data-baseweb="tab-highlight"] { background: var(--ink); height: 2px; }
[data-baseweb="tab-border"] { display: none; }

.ox-list { margin: 0.6rem 0 0 0; padding: 0; list-style: none; }
.ox-list li {
    position: relative; padding: 0.7rem 0 0.7rem 1.4rem;
    border-bottom: 1px solid var(--line);
    font-size: 0.95rem; line-height: 1.6; color: var(--ink-2);
}
.ox-list li:last-child { border-bottom: none; }
.ox-list li::before {
    content: ""; position: absolute; left: 0.2rem; top: 1.2rem;
    width: 6px; height: 6px; border-radius: 50%; background: var(--accent);
}
.ox-empty-line { padding: 1rem 0; font-size: 0.92rem; color: var(--muted); }

.ox-sources { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.7rem; margin-top: 0.8rem; }
.ox-source {
    display: flex; align-items: center; justify-content: space-between; gap: 1rem;
    border: 1px solid var(--line); border-radius: var(--r-sm); padding: 0.8rem 1rem;
}
.ox-source span { font-size: 0.9rem; font-weight: 600; color: var(--ink); }

.ox-tech { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.9rem; margin-top: 0.8rem; }
.ox-tech div { border: 1px solid var(--line); border-radius: var(--r-sm); padding: 0.9rem 1rem; }
.ox-tech small { display: block; font-size: 0.78rem; color: var(--muted); font-weight: 600; }
.ox-tech b { display: block; font-size: 0.95rem; color: var(--ink); margin-top: 0.25rem; word-break: break-word; }
.ox-callout { margin-top: 0.9rem; padding: 1rem 1.2rem; border-radius: var(--r-sm); background: var(--accent-soft); color: var(--ink-2); font-size: 0.9rem; line-height: 1.6; }

/* ---------- footer ---------- */
.ox-footer {
    margin-top: 2.5rem; padding-top: 1.4rem; border-top: 1px solid var(--line);
    font-size: 0.82rem; line-height: 1.65; color: var(--muted); max-width: 760px;
}

/* ---------- alerts ---------- */
[data-testid="stAlert"] { border-radius: var(--r-sm); }

/* ---------- mobile ---------- */
@media (max-width: 900px) {
    .block-container { padding: 1.2rem 1rem 4rem 1rem; }
    .ox-intro h1 { font-size: 2rem; }
    .ox-metrics { grid-template-columns: repeat(2, 1fr); }
    .ox-causes, .ox-sources, .ox-tech, .ox-steps { grid-template-columns: 1fr; }
    .ox-verdict { padding: 1.4rem 1.3rem; }
    .ox-verdict-title { font-size: 1.5rem; }
    .ox-live { display: none; }
}
@media (max-width: 520px) {
    .ox-metrics { grid-template-columns: 1fr; }
}
</style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Top bar and introduction
# ---------------------------------------------------------------------

md(
    """
    <div class="ox-top">
        <div class="ox-brand">
            <div class="ox-logo">◈</div>
            <div>
                <div class="ox-brand-name">ORACLE-X</div>
                <div class="ox-brand-tag">Decision intelligence</div>
            </div>
        </div>
        <div class="ox-live"><i></i>Rule-based and auditable</div>
    </div>
    """
)

md(
    """
    <div class="ox-intro">
        <h1>See what happened, why it happened, and what to do next.</h1>
        <p>
            Pick a business incident and ORACLE-X will investigate it,
            check the evidence, and give you a clear recommendation you
            can verify.
        </p>
    </div>
    """
)


# ---------------------------------------------------------------------
# Run panel
# ---------------------------------------------------------------------

with st.container(border=True):
    col_input, col_button = st.columns([1.2, 1], vertical_alignment="bottom")

    with col_input:
        incident_id = st.number_input(
            "Incident number",
            min_value=2,
            value=2,
            step=1,
            help="Each incident is a detected business problem. Start with 2 to see an example.",
        )

    with col_button:
        run_investigation = st.button(
            "Investigate this incident",
            type="primary",
            use_container_width=True,
        )


# ---------------------------------------------------------------------
# Fetch (kept in session so the page does not reset on interaction)
# ---------------------------------------------------------------------

REQUIRED_SECTIONS = {
    "incident",
    "decision",
    "validation",
    "scenario_metrics",
    "llm_interpretation",
    "provenance",
}


def fetch_investigation(incident_number):
    """Call the API. Returns (data, error_message)."""
    try:
        with st.spinner("Investigating. This can take up to a minute..."):
            response = requests.get(
                f"{API_URL}/investigate/{incident_number}/summary",
                timeout=120,
            )
    except requests.Timeout:
        return None, "The request took too long. The investigation may still be running, so please try again in a moment."
    except requests.ConnectionError:
        return None, "We couldn't reach the ORACLE-X service. Check your connection, or make sure the API is running."
    except requests.RequestException as exc:
        return None, f"The request failed: {exc}"

    if response.status_code == 404:
        return None, f"Incident #{incident_number} doesn't exist. Try another number."
    if response.status_code != 200:
        return None, f"The service returned an error (HTTP {response.status_code}). Please try again."

    try:
        data = response.json()
    except ValueError:
        return None, "The service sent back an unreadable response."

    missing = REQUIRED_SECTIONS - set(data.keys())
    if missing:
        return None, "The response is incomplete. Missing: " + ", ".join(sorted(missing))

    return data, None


if run_investigation:
    data, error = fetch_investigation(int(incident_id))
    if error:
        st.session_state.pop("result", None)
        st.error(error)
    else:
        st.session_state["result"] = {"id": int(incident_id), "data": data}


# ---------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------

result = st.session_state.get("result")

if not result:
    section("How it works")
    md(
        """
        <div class="ox-steps">
            <div class="ox-step">
                <b>1. Choose an incident</b>
                <span>Enter the number of a detected business problem. Incident 2 is a good place to start.</span>
            </div>
            <div class="ox-step">
                <b>2. We investigate</b>
                <span>Clear business rules look at demand, stock, revenue and customer reviews, then rank the likely causes.</span>
            </div>
            <div class="ox-step">
                <b>3. You get an answer</b>
                <span>A recommended action, the evidence behind it, and an honest list of what we're still unsure about.</span>
            </div>
        </div>
        """
    )
    st.stop()


# ---------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------

data = result["data"]

try:
    incident = data["incident"]
    decision = data["decision"]
    validation = data["validation"]
    metrics = data["scenario_metrics"]
    root_cause = data.get("root_cause_analysis", {}) or {}
    llm = data["llm_interpretation"]
    provenance = data["provenance"]

    # ---- Verdict -----------------------------------------------------

    chips = (
        chip(pretty(incident.get("severity")), tone_for(incident.get("severity")), "Severity: ")
        + chip(pretty(decision.get("status")), tone_for(decision.get("status")), "Decision: ")
        + chip(pretty(validation.get("status")), tone_for(validation.get("status")), "Checks: ")
        + chip(pretty(incident.get("source_type")), tone_for(incident.get("source_type")), "Data: ")
    )

    section("Result", f"Investigation finished for incident #{result['id']}.")

    md(
        f"""
        <div class="ox-verdict">
            <div class="ox-incident-id">Incident #{esc(incident.get("incident_id"))}</div>
            <div class="ox-verdict-title">{esc(incident.get("title"))}</div>
            <div class="ox-verdict-sub">{esc(incident.get("summary"))}</div>
            <div class="ox-chips">{chips}</div>
            <div class="ox-action">
                <div class="ox-action-label">What to do</div>
                <div class="ox-action-text">{esc(decision.get("recommended_action"))}</div>
                <div class="ox-action-why">
                    <strong>Why:</strong> {esc(decision.get("rationale"))}
                </div>
            </div>
        </div>
        """
    )

    # ---- Numbers -----------------------------------------------------

    demand = metrics.get("demand", {})
    inventory = metrics.get("inventory", {})
    financial = metrics.get("financial", {})
    customer = metrics.get("customer", {})

    section(
        "The numbers",
        "A snapshot of the situation. Arrows show the change compared with normal.",
    )

    md(
        '<div class="ox-metrics">'
        + metric_card(
            "Orders per day",
            f"{num(demand, 'simulated_daily_orders'):,.0f}",
            f"{num(demand, 'change_pct'):+.1f}%",
            num(demand, "change_pct"),
            "Scenario",
            "warn",
        )
        + metric_card(
            "Stock lasts",
            f"{num(inventory, 'simulated_cover_days'):.1f} days",
            f"{-num(inventory, 'decline_pct'):+.1f}%",
            -num(inventory, "decline_pct"),
            "Estimated",
            "info",
        )
        + metric_card(
            "Revenue per day",
            f"${num(financial, 'current_daily_revenue'):,.0f}",
            f"{num(financial, 'change_pct'):+.1f}%",
            num(financial, "change_pct"),
            "Scenario",
            "warn",
        )
        + metric_card(
            "Review score",
            f"{num(customer, 'current_review_score'):.2f} / 5",
            f"{num(customer, 'change'):+.2f}",
            num(customer, "change"),
            "Scenario",
            "warn",
        )
        + "</div>"
    )

    md(
        """
        <div class="ox-note">
            Orders, revenue and reviews come from a simulated scenario.
            Stock levels are estimated by a model, not counted in a warehouse.
        </div>
        """
    )

    # ---- Likely causes ----------------------------------------------

    candidates = root_cause.get("candidate_causes", []) or []

    if candidates:
        section(
            "Likely causes",
            "These are possible explanations, ranked by how well the evidence supports them. "
            "None of them is proven.",
        )

        cards = ""
        for c in candidates:
            cards += f"""
            <div class="ox-cause">
                <div class="ox-cause-head">
                    <div class="ox-cause-title">{esc(c.get("candidate_cause"))}</div>
                    {confidence_meter(c.get("confidence"))}
                </div>
                <div class="ox-cause-block">
                    <b>What supports it</b>
                    <span>{esc(c.get("evidence_for"))}</span>
                </div>
                <div class="ox-cause-block">
                    <b>What holds it back</b>
                    <span>{esc(c.get("evidence_against"))}</span>
                </div>
                <div class="ox-cause-type">
                    {chip(pretty(c.get("evidence_type")), "neutral", "Evidence: ")}
                </div>
            </div>
            """
        md(f'<div class="ox-causes">{cards}</div>')

    # ---- Plain-words summary ----------------------------------------

    section("In plain words")
    md(
        f"""
        <div class="ox-plain">
            <p>{esc(llm.get("executive_summary"))}</p>
            <small>
                Written by an AI assistant to explain the findings.
                It cannot change the decision or the numbers.
            </small>
        </div>
        """
    )

    # ---- Details -----------------------------------------------------

    section("Details", "Everything behind the recommendation, for anyone who wants to check.")

    tab_seen, tab_unsure, tab_open, tab_sources, tab_tech = st.tabs(
        [
            "What we found",
            "What we're unsure about",
            "Open questions",
            "Where data comes from",
            "Technical",
        ]
    )

    with tab_seen:
        md(items_html(llm.get("key_observations", []), "No observations were reported."))

    with tab_unsure:
        md(items_html(llm.get("uncertainty", []), "No uncertainties were reported."))

    with tab_open:
        md(items_html(llm.get("unresolved_questions", []), "No open questions were reported."))

    with tab_sources:
        if provenance:
            rows = ""
            for source, label in provenance.items():
                rows += f"""
                <div class="ox-source">
                    <span>{esc(pretty(source))}</span>
                    {chip(pretty(label), tone_for(label))}
                </div>
                """
            md(
                "<div class='ox-note' style='margin-top:0.8rem'>"
                "Each piece of information is labelled so you can tell real data "
                "from simulated, estimated or AI-written content.</div>"
                f"<div class='ox-sources'>{rows}</div>"
            )
        else:
            md("<div class='ox-empty-line'>No data sources were returned.</div>")

    with tab_tech:
        rca_check = root_cause.get("validation", {}) or {}
        md(
            f"""
            <div class="ox-tech">
                <div><small>AI status</small><b>{esc(pretty(llm.get("status")))}</b></div>
                <div><small>AI model</small><b>{esc(llm.get("model"))}</b></div>
                <div><small>AI permission</small><b>Read only</b></div>
                <div><small>Rule-based analysis</small><b>{esc(rca_check.get("deterministic", "n/a"))}</b></div>
                <div><small>Claims certain cause</small><b>{esc(rca_check.get("causal_certainty_claimed", "n/a"))}</b></div>
                <div><small>Historical data used</small><b>{esc(rca_check.get("historical_context_available", "n/a"))}</b></div>
            </div>
            <div class="ox-callout">
                The AI only explains results that were already produced.
                Business rules decide the facts, the recommendation and its verification.
            </div>
            """
        )

    # ---- Footer ------------------------------------------------------

    md(
        """
        <div class="ox-footer">
            Decisions are produced and verified by fixed business rules.
            Simulated inputs are always labelled, estimated values stay traceable,
            and the cause analysis never claims more certainty than the evidence allows.
            The AI assistant only explains the results.
        </div>
        """
    )

except KeyError as exc:
    st.error(f"The response is missing an expected field: {exc}")
except Exception as exc:
    st.error(f"Something unexpected went wrong: {exc}")
