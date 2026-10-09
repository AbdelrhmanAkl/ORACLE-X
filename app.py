import html
import os

import requests
import streamlit as st


API_URL = os.getenv(
    "ORACLE_X_API_URL",
    "https://oracle-x.fastapicloud.dev",
).rstrip("/")

# ---------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="ORACLE-X | Decision Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def safe_text(value):
    """Safely render API-provided text inside HTML."""
    if value is None:
        return ""
    return html.escape(str(value))


def status_class(value):
    """Map status text to a visual status class."""
    normalized = str(value).strip().upper()

    if normalized in {
        "VALID",
        "ACTIONABLE",
        "PASS",
        "COMPLETED",
        "TRUE",
        "AVAILABLE",
        "STRUCTURALLY_STRONG",
    }:
        return "status-positive"

    if normalized in {
        "HIGH",
        "MEDIUM",
        "WARNING",
        "PENDING",
        "INSUFFICIENT_LEARNING_DATA",
        "INSUFFICIENT-EVIDENCE",
    }:
        return "status-warning"

    if normalized in {
        "INVALID",
        "FAILED",
        "REJECTED",
        "FALSE",
        "ERROR",
    }:
        return "status-negative"

    return "status-neutral"


def render_status_badge(label, value):
    """Render a compact enterprise status badge."""
    return f"""
        <div class="decision-badge {status_class(value)}">
            <span class="decision-badge-label">
                {safe_text(label)}
            </span>
            <span class="decision-badge-value">
                {safe_text(value)}
            </span>
        </div>
    """


def render_section(kicker, title, description):
    """Render a consistent enterprise section header."""
    st.markdown(
        f"""
        <div class="section-heading">
            <div class="section-kicker">
                {safe_text(kicker)}
            </div>
            <div class="section-title">
                {safe_text(title)}
            </div>
            <div class="section-description">
                {safe_text(description)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# Visual Design System
# ---------------------------------------------------------------------

st.markdown(
    """
    <style>

    /* =============================================================
       DESIGN TOKENS
    ============================================================= */

    :root {
        --ink: #211f1b;
        --ink-soft: #514d46;
        --muted: #7c776e;
        --muted-2: #9a958b;

        --paper: #f8f7f3;
        --surface: #ffffff;
        --surface-soft: #f5f2ec;
        --surface-warm: #f0e8dc;

        --line: #e3ded5;
        --line-strong: #d5cec2;

        --accent: #a97946;
        --accent-dark: #815a35;
        --accent-soft: #efe1cf;

        --positive: #55745d;
        --positive-soft: #e7efe8;

        --warning: #956b38;
        --warning-soft: #f4eadb;

        --negative: #8a5149;
        --negative-soft: #f3e4e1;

        --shadow-sm:
            0 6px 20px rgba(40, 35, 28, 0.035);

        --shadow-md:
            0 12px 34px rgba(40, 35, 28, 0.055);

        --shadow-lg:
            0 20px 55px rgba(30, 27, 22, 0.12);
    }


    /* =============================================================
       GLOBAL
    ============================================================= */

    .stApp {
        background:
            radial-gradient(
                circle at 86% 3%,
                rgba(192, 160, 119, 0.10),
                transparent 27%
            ),
            radial-gradient(
                circle at 3% 38%,
                rgba(170, 140, 100, 0.045),
                transparent 25%
            ),
            linear-gradient(
                180deg,
                #fbfaf7 0%,
                #f7f5f0 48%,
                #f2f0eb 100%
            );

        color: var(--ink);
    }


    .block-container {
        max-width: 1460px;

        padding-top: 2rem;
        padding-bottom: 4.5rem;

        padding-left: 3rem;
        padding-right: 3rem;
    }


    /* =============================================================
       TYPOGRAPHY
    ============================================================= */

    h1,
    h2,
    h3,
    h4 {
        color: var(--ink) !important;
        letter-spacing: -0.035em;
    }


    h1 {
        font-size: 3rem !important;
        font-weight: 780 !important;
    }


    h2 {
        font-size: 1.65rem !important;
        font-weight: 720 !important;
    }


    h3 {
        font-size: 1.15rem !important;
        font-weight: 680 !important;
    }


    p {
        color: var(--ink-soft);
    }


    /* =============================================================
       TOP HEADER
    ============================================================= */

    .oracle-header {
        display: flex;

        justify-content: space-between;
        align-items: center;

        gap: 2rem;

        padding:
            0.25rem
            0
            1.65rem
            0;

        border-bottom: 1px solid var(--line);
    }


    .oracle-brand {
        display: flex;
        align-items: center;

        gap: 0.95rem;
    }


    .oracle-mark {
        width: 50px;
        height: 50px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 15px;

        background:
            linear-gradient(
                145deg,
                #2b2924,
                #161512
            );

        color: #e9c79e;

        font-size: 1.28rem;
        font-weight: 800;

        box-shadow:
            0 13px 32px rgba(35, 32, 27, 0.16);

        border:
            1px solid
            rgba(255, 255, 255, 0.08);
    }


    .oracle-title {
        font-size: 2rem;
        line-height: 1;

        font-weight: 800;

        color: var(--ink);

        letter-spacing: -0.05em;
    }


    .oracle-subtitle {
        margin-top: 0.38rem;

        font-size: 0.82rem;
        font-weight: 500;

        color: var(--muted);

        letter-spacing: 0.01em;
    }


    .system-state {
        display: flex;

        align-items: center;

        gap: 0.55rem;

        padding:
            0.55rem
            0.85rem;

        border-radius: 999px;

        background:
            rgba(255, 255, 255, 0.78);

        border:
            1px solid
            var(--line);

        color: var(--ink-soft);

        font-size: 0.71rem;
        font-weight: 750;

        letter-spacing: 0.08em;

        text-transform: uppercase;

        box-shadow:
            0 5px 18px rgba(40, 35, 28, 0.025);
    }


    .system-state-dot {
        width: 7px;
        height: 7px;

        border-radius: 50%;

        background: var(--positive);

        box-shadow:
            0 0 0 4px
            rgba(85, 116, 93, 0.10);
    }


    /* =============================================================
       PAGE INTRO
    ============================================================= */

    .page-intro {
        padding:
            2.15rem
            0
            1.35rem
            0;
    }


    .page-kicker {
        color: var(--accent);

        font-size: 0.66rem;
        font-weight: 850;

        letter-spacing: 0.18em;

        text-transform: uppercase;

        margin-bottom: 0.45rem;
    }


    .page-title {
        color: var(--ink);

        font-size: 2.15rem;
        font-weight: 760;

        letter-spacing: -0.045em;
    }


    .page-description {
        max-width: 790px;

        margin-top: 0.48rem;

        color: var(--muted);

        font-size: 0.91rem;

        line-height: 1.68;
    }


    /* =============================================================
       CONTROL PANEL
    ============================================================= */

    .control-panel {
        display: flex;

        align-items: center;
        justify-content: space-between;

        gap: 1.5rem;

        padding:
            1rem
            1.15rem;

        background:
            rgba(255, 255, 255, 0.84);

        border:
            1px solid
            var(--line);

        border-radius: 17px;

        box-shadow:
            var(--shadow-sm);

        margin-bottom: 1.8rem;
    }


    .control-copy {
        display: flex;

        align-items: center;

        gap: 0.8rem;
    }


    .control-icon {
        width: 36px;
        height: 36px;

        display: flex;

        align-items: center;
        justify-content: center;

        border-radius: 10px;

        background:
            var(--surface-warm);

        color:
            var(--accent);

        font-weight: 850;
        font-size: 0.85rem;
    }


    .control-label {
        color: var(--ink);

        font-size: 0.82rem;
        font-weight: 750;
    }


    .control-description {
        color: var(--muted);

        font-size: 0.72rem;

        margin-top: 0.12rem;
    }


    .control-meta {
        display: flex;

        align-items: center;

        gap: 0.45rem;

        margin-top: 0.3rem;
    }


    .control-meta-pill {
        display: inline-flex;

        padding:
            0.2rem
            0.45rem;

        border-radius: 6px;

        background:
            var(--surface-soft);

        border:
            1px solid
            var(--line);

        color:
            var(--muted);

        font-size: 0.58rem;
        font-weight: 700;

        letter-spacing: 0.05em;

        text-transform: uppercase;
    }


    /* =============================================================
       SECTION HEADERS
    ============================================================= */

    .section-heading {
        margin-top: 2rem;

        margin-bottom: 0.9rem;
    }


    .section-kicker {
        color: var(--accent);

        font-size: 0.64rem;
        font-weight: 850;

        letter-spacing: 0.17em;

        text-transform: uppercase;

        margin-bottom: 0.27rem;
    }


    .section-title {
        color: var(--ink);

        font-size: 1.4rem;
        font-weight: 740;

        letter-spacing: -0.035em;
    }


    .section-description {
        max-width: 790px;

        color: var(--muted);

        font-size: 0.79rem;

        line-height: 1.58;

        margin-top: 0.3rem;
    }


    /* =============================================================
       STATUS CARDS
    ============================================================= */

    .status-card {
        position: relative;

        overflow: hidden;

        background:
            rgba(255, 255, 255, 0.91);

        border:
            1px solid
            var(--line);

        border-radius: 17px;

        padding:
            1rem
            1.1rem;

        min-height: 118px;

        box-shadow:
            var(--shadow-sm);
    }


    .status-card::before {
        content: "";

        position: absolute;

        left: 0;
        top: 0;
        bottom: 0;

        width: 3px;

        background:
            var(--accent);

        opacity: 0.65;
    }


    .status-label {
        color: var(--muted-2);

        font-size: 0.61rem;
        font-weight: 850;

        letter-spacing: 0.14em;

        text-transform: uppercase;

        margin-bottom: 0.65rem;
    }


    .status-value {
        color: var(--ink);

        font-size: 1.48rem;
        font-weight: 770;

        letter-spacing: -0.04em;
    }


    .status-description {
        color: var(--muted);

        font-size: 0.69rem;

        margin-top: 0.38rem;

        line-height: 1.45;
    }


    /* =============================================================
       INCIDENT HERO
    ============================================================= */

    .incident-hero {
        position: relative;

        overflow: hidden;

        background:
            radial-gradient(
                circle at 91% 18%,
                rgba(218, 184, 139, 0.15),
                transparent 31%
            ),
            radial-gradient(
                circle at 72% 110%,
                rgba(171, 139, 99, 0.08),
                transparent 27%
            ),
            linear-gradient(
                145deg,
                #2a2823 0%,
                #1f1e1a 100%
            );

        border-radius: 21px;

        padding:
            1.55rem
            1.6rem;

        margin-top: 1rem;

        box-shadow:
            var(--shadow-lg);
    }


    .incident-hero::after {
        content: "";

        position: absolute;

        right: -90px;
        top: -100px;

        width: 240px;
        height: 240px;

        border-radius: 50%;

        border:
            1px solid
            rgba(255, 255, 255, 0.06);
    }


    .incident-overline {
        color: #d5bd9d;

        font-size: 0.62rem;
        font-weight: 850;

        letter-spacing: 0.16em;

        text-transform: uppercase;
    }


    .incident-title {
        color: #ffffff;

        font-size: 1.4rem;
        font-weight: 710;

        letter-spacing: -0.03em;

        margin-top: 0.45rem;
    }


    .incident-summary {
        max-width: 880px;

        color: #c4bfb6;

        font-size: 0.84rem;

        line-height: 1.65;

        margin-top: 0.55rem;
    }


    .incident-meta-row {
        display: flex;

        flex-wrap: wrap;

        align-items: center;

        gap: 0.5rem;

        margin-top: 1.15rem;
    }


    .incident-meta {
        padding:
            0.4rem
            0.65rem;

        border-radius: 8px;

        background:
            rgba(255, 255, 255, 0.055);

        border:
            1px solid
            rgba(255, 255, 255, 0.09);

        color: #bdb7ae;

        font-size: 0.64rem;
        font-weight: 620;
    }


    /* =============================================================
       DECISION BADGES
    ============================================================= */

    .decision-badge {
        display: inline-flex;

        align-items: center;

        gap: 0.5rem;

        padding:
            0.4rem
            0.65rem;

        border-radius: 8px;

        border:
            1px solid
            transparent;
    }


    .decision-badge-label {
        font-size: 0.59rem;
        font-weight: 720;

        letter-spacing: 0.08em;

        text-transform: uppercase;
    }


    .decision-badge-value {
        font-size: 0.67rem;
        font-weight: 850;
    }


    .status-positive {
        background:
            var(--positive-soft);

        border-color:
            #d5e2d6;

        color:
            var(--positive);
    }


    .status-warning {
        background:
            var(--warning-soft);

        border-color:
            #ead8bf;

        color:
            var(--warning);
    }


    .status-negative {
        background:
            var(--negative-soft);

        border-color:
            #e7d0cc;

        color:
            var(--negative);
    }


    .status-neutral {
        background:
            var(--surface-soft);

        border-color:
            var(--line);

        color:
            var(--ink-soft);
    }


    /* =============================================================
       KPI CARDS
    ============================================================= */

    .metric-shell {
        background:
            rgba(255, 255, 255, 0.93);

        border:
            1px solid
            var(--line);

        border-radius: 17px;

        padding:
            1rem
            1rem
            0.9rem
            1rem;

        min-height: 164px;

        box-shadow:
            var(--shadow-sm);
    }


    .metric-kicker {
        color: var(--muted-2);

        font-size: 0.6rem;
        font-weight: 850;

        letter-spacing: 0.14em;

        text-transform: uppercase;
    }


    .metric-name {
        color: var(--ink-soft);

        font-size: 0.72rem;

        margin-top: 0.52rem;
    }


    .metric-note {
        color: var(--muted-2);

        font-size: 0.64rem;

        line-height: 1.45;

        margin-top: 0.55rem;
    }


    /* =============================================================
       DECISION PANEL
    ============================================================= */

    .decision-panel {
        position: relative;

        overflow: hidden;

        background:
            linear-gradient(
                135deg,
                #f6eadb,
                #f0e4d4
            );

        border:
            1px solid
            #e4d1b8;

        border-radius: 19px;

        padding:
            1.4rem
            1.5rem;

        margin-top: 0.45rem;

        box-shadow:
            0 12px 32px
            rgba(103, 78, 48, 0.055);
    }


    .decision-panel::after {
        content: "DECISION";

        position: absolute;

        right: 1.35rem;
        top: 1.05rem;

        color:
            rgba(126, 91, 54, 0.08);

        font-size: 2.1rem;
        font-weight: 850;

        letter-spacing: 0.08em;
    }


    .decision-panel-label {
        color: #9a754c;

        font-size: 0.62rem;
        font-weight: 850;

        letter-spacing: 0.15em;

        text-transform: uppercase;
    }


    .decision-panel-action {
        color: #2e2821;

        font-size: 1.2rem;
        font-weight: 700;

        line-height: 1.5;

        margin-top: 0.52rem;

        max-width: 1050px;
    }


    .decision-panel-rationale {
        color: #70665a;

        font-size: 0.81rem;

        line-height: 1.68;

        margin-top: 0.75rem;

        max-width: 1050px;
    }


    /* =============================================================
       RCA
    ============================================================= */

    .rca-card {
        background:
            rgba(255, 255, 255, 0.91);

        border:
            1px solid
            var(--line);

        border-radius: 16px;

        padding:
            1.05rem
            1.15rem;

        margin-bottom: 0.7rem;

        box-shadow:
            var(--shadow-sm);
    }


    .rca-title {
        color: var(--ink);

        font-size: 0.94rem;
        font-weight: 730;

        letter-spacing: -0.015em;
    }


    .rca-confidence {
        color: var(--muted-2);

        font-size: 0.6rem;
        font-weight: 850;

        letter-spacing: 0.12em;

        text-transform: uppercase;
    }


    .confidence-value {
        color: var(--ink);

        font-size: 0.94rem;
        font-weight: 740;

        margin-top: 0.25rem;
    }


    .evidence-label {
        color: var(--accent);

        font-size: 0.58rem;
        font-weight: 850;

        letter-spacing: 0.12em;

        text-transform: uppercase;

        margin-top: 0.8rem;
    }


    .evidence-text {
        color: var(--ink-soft);

        font-size: 0.76rem;

        line-height: 1.58;

        margin-top: 0.2rem;
    }


    .evidence-type {
        color: var(--muted-2);

        font-size: 0.62rem;

        margin-top: 0.65rem;
    }


    /* =============================================================
       EXECUTIVE INTERPRETATION
    ============================================================= */

    .interpretation-card {
        background:
            #ffffff;

        border:
            1px solid
            var(--line);

        border-left:
            3px solid
            var(--accent);

        border-radius: 16px;

        padding:
            1.3rem
            1.45rem;

        box-shadow:
            var(--shadow-sm);
    }


    .interpretation-label {
        color: var(--accent);

        font-size: 0.6rem;
        font-weight: 850;

        letter-spacing: 0.13em;

        text-transform: uppercase;

        margin-bottom: 0.55rem;
    }


    .interpretation-summary {
        color: #45413a;

        font-size: 0.93rem;

        line-height: 1.82;
    }


    /* =============================================================
       TRACEABILITY
    ============================================================= */

    .traceability-grid {
        display: grid;

        grid-template-columns:
            repeat(
                2,
                minmax(0, 1fr)
            );

        gap: 0.65rem;

        margin-top: 0.7rem;
    }


    .traceability-item {
        background:
            var(--surface-soft);

        border:
            1px solid
            var(--line);

        border-radius: 12px;

        padding:
            0.78rem
            0.85rem;
    }


    .traceability-source {
        color: var(--muted);

        font-size: 0.62rem;
        font-weight: 720;
    }


    .traceability-classification {
        color: var(--ink);

        font-size: 0.69rem;
        font-weight: 760;

        margin-top: 0.25rem;
    }


    /* =============================================================
       INTEGRITY
    ============================================================= */

    .integrity-card {
        background:
            linear-gradient(
                135deg,
                #efede8,
                #e9e6df
            );

        border:
            1px solid
            #ddd8cf;

        border-radius: 18px;

        padding:
            1.15rem
            1.3rem;
    }


    .integrity-title {
        color: #5c574f;

        font-size: 0.64rem;
        font-weight: 850;

        letter-spacing: 0.13em;

        text-transform: uppercase;
    }


    .integrity-text {
        color: #767168;

        font-size: 0.75rem;

        line-height: 1.65;

        margin-top: 0.45rem;
    }


    /* =============================================================
       EMPTY / ERROR STATES
    ============================================================= */

    .empty-state {
        background:
            rgba(255, 255, 255, 0.75);

        border:
            1px dashed
            var(--line-strong);

        border-radius: 17px;

        padding:
            1.5rem;

        color:
            var(--muted);

        text-align: center;

        font-size: 0.78rem;
    }


    .api-status {
        display: inline-flex;

        align-items: center;

        gap: 0.45rem;

        padding:
            0.35rem
            0.6rem;

        border-radius: 999px;

        background:
            var(--positive-soft);

        color:
            var(--positive);

        border:
            1px solid
            #d5e2d6;

        font-size: 0.61rem;
        font-weight: 800;

        letter-spacing: 0.06em;

        text-transform: uppercase;
    }


    /* =============================================================
       STREAMLIT COMPONENTS
    ============================================================= */

    div[data-testid="stMetric"] {
        background: transparent;
        border: none;

        padding: 0;
    }


    div[data-testid="stMetricValue"] {
        color:
            var(--ink) !important;

        font-size:
            1.62rem !important;

        font-weight:
            760 !important;

        letter-spacing:
            -0.04em;
    }


    div[data-testid="stMetricLabel"] {
        color:
            var(--ink-soft) !important;

        font-size:
            0.72rem !important;
    }


    div[data-testid="stMetricDelta"] {
        font-size:
            0.69rem !important;
    }


    .stButton > button {
        min-height: 42px;

        border-radius: 11px;

        border:
            1px solid
            #282621;

        background:
            linear-gradient(
                135deg,
                #2b2924,
                #1f1e1a
            );

        color: #ffffff;

        font-weight: 720;

        padding:
            0.52rem
            1rem;

        box-shadow:
            0 8px 20px
            rgba(35, 32, 27, 0.13);

        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease,
            background 0.15s ease;
    }


    .stButton > button:hover {
        background:
            linear-gradient(
                135deg,
                #37342e,
                #25231f
            );

        border-color:
            #37342e;

        color: #ffffff;

        transform:
            translateY(-1px);

        box-shadow:
            0 11px 24px
            rgba(35, 32, 27, 0.17);
    }


    div[data-testid="stNumberInput"] input {
        border-radius: 10px;

        border-color:
            var(--line-strong);

        background:
            #ffffff;

        color:
            var(--ink);

        font-weight: 680;
    }


    div[data-testid="stNumberInput"] input:focus {
        border-color:
            var(--accent);

        box-shadow:
            0 0 0 1px
            rgba(169, 121, 70, 0.18);
    }


    div[data-testid="stExpander"] {
        border:
            1px solid
            var(--line);

        border-radius: 14px;

        background:
            rgba(255, 255, 255, 0.62);

        margin-bottom:
            0.65rem;

        overflow: hidden;
    }


    div[data-testid="stExpander"] summary {
        font-weight: 680;

        color:
            var(--ink);
    }


    .stAlert {
        border-radius: 12px;
    }


    .stCaption {
        color:
            var(--muted);
    }


    hr {
        border-color:
            var(--line) !important;

        margin-top:
            2rem !important;

        margin-bottom:
            1.4rem !important;
    }


    /* =============================================================
       MOBILE
    ============================================================= */

    @media (max-width: 900px) {

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }


        .oracle-header {
            align-items: flex-start;
        }


        .system-state {
            display: none;
        }


        .oracle-title {
            font-size: 1.7rem;
        }


        .page-title {
            font-size: 1.7rem;
        }


        .traceability-grid {
            grid-template-columns: 1fr;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.markdown(
    """
    <div class="oracle-header">
        <div class="oracle-brand">
            <div class="oracle-mark">
                ◈
            </div>
            <div>
                <div class="oracle-title">
                    ORACLE-X
                </div>
                <div class="oracle-subtitle">
                    Autonomous Enterprise Decision Engine
                </div>
            </div>
        </div>
        <div class="system-state">
            <span class="system-state-dot"></span>
            Decision Intelligence
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Page Introduction
# ---------------------------------------------------------------------

st.markdown(
    """
    <div class="page-intro">
        <div class="page-kicker">
            Executive Decision Console
        </div>
        <div class="page-title">
            Enterprise Situation Room
        </div>
        <div class="page-description">
            Investigate detected business conditions, review the evidence
            behind them, validate the recommended response, and understand
            the provenance of every decision signal.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Investigation Control
# ---------------------------------------------------------------------

st.markdown(
    """
    <div class="control-panel">
        <div class="control-copy">
            <div class="control-icon">
                ◈
            </div>
            <div>
                <div class="control-label">
                    Investigation Control
                </div>
                <div class="control-description">
                    Select a production incident and run the complete
                    ORACLE-X decision pipeline.
                </div>
                <div class="control-meta">
                    <span class="control-meta-pill">
                        Deterministic
                    </span>
                    <span class="control-meta-pill">
                        Auditable
                    </span>
                    <span class="control-meta-pill">
                        Read-only LLM
                    </span>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


control_left, control_right = st.columns(
    [1, 1],
    vertical_alignment="center",
)


with control_left:
    incident_id = st.number_input(
        "Incident ID",
        min_value=2,
        value=2,
        step=1,
        label_visibility="collapsed",
    )


with control_right:
    run_investigation = st.button(
        "Run Investigation",
        type="primary",
        use_container_width=True,
    )


# ---------------------------------------------------------------------
# Investigation
# ---------------------------------------------------------------------

if run_investigation:

    try:

        response = requests.get(
            f"{API_URL}/investigate/{int(incident_id)}/summary",
            timeout=120,
        )


        # -------------------------------------------------------------
        # HTTP handling
        # -------------------------------------------------------------

        if response.status_code == 404:

            st.error(
                f"Incident #{int(incident_id)} was not found "
                "in the production database."
            )

            st.stop()


        if response.status_code != 200:

            st.error(
                "Unable to complete the investigation. "
                f"API returned HTTP {response.status_code}."
            )

            st.stop()


        # -------------------------------------------------------------
        # JSON handling
        # -------------------------------------------------------------

        try:
            data = response.json()

        except ValueError:

            st.error(
                "The ORACLE-X API returned an invalid JSON response."
            )

            st.stop()


        # -------------------------------------------------------------
        # Contract validation
        # -------------------------------------------------------------

        required_sections = {
            "incident",
            "decision",
            "validation",
            "scenario_metrics",
            "llm_interpretation",
            "provenance",
        }


        missing_sections = (
            required_sections
            - set(data.keys())
        )


        if missing_sections:

            st.error(
                "The API response is missing required sections: "
                + ", ".join(
                    sorted(missing_sections)
                )
            )

            st.stop()


        # -------------------------------------------------------------
        # Extract API payload
        # -------------------------------------------------------------

        incident = data["incident"]

        decision = data["decision"]

        validation = data["validation"]

        scenario_metrics = data["scenario_metrics"]

        root_cause = data.get(
            "root_cause_analysis",
            {},
        )

        llm = data["llm_interpretation"]

        provenance = data["provenance"]


        # -------------------------------------------------------------
        # Success state
        # -------------------------------------------------------------

        st.success(
            f"Investigation completed for Incident #{int(incident_id)}."
        )


        # =============================================================
        # EXECUTIVE OVERVIEW
        # =============================================================

        render_section(
            "Executive Overview",
            "Current decision state",
            "The operational status of the detected situation, "
            "the resulting decision, and its deterministic validation.",
        )


        overview_col1, overview_col2, overview_col3 = st.columns(3)


        with overview_col1:

            st.markdown(
                f"""
                <div class="status-card">
                    <div class="status-label">
                        Severity
                    </div>
                    <div class="status-value">
                        {safe_text(incident["severity"])}
                    </div>
                    <div class="status-description">
                        Operational severity assigned to the detected condition.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


        with overview_col2:

            st.markdown(
                f"""
                <div class="status-card">
                    <div class="status-label">
                        Decision
                    </div>
                    <div class="status-value">
                        {safe_text(decision["status"])}
                    </div>
                    <div class="status-description">
                        Whether the available evidence supports action.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


        with overview_col3:

            st.markdown(
                f"""
                <div class="status-card">
                    <div class="status-label">
                        Validation
                    </div>
                    <div class="status-value">
                        {safe_text(validation["status"])}
                    </div>
                    <div class="status-description">
                        Deterministic validation result for the decision.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


        # =============================================================
        # INCIDENT
        # =============================================================

        incident_badges = (
            render_status_badge(
                "Decision",
                decision["status"],
            )
            +
            render_status_badge(
                "Validation",
                validation["status"],
            )
        )


        st.markdown(
            f"""
            <div class="incident-hero">
                <div class="incident-overline">
                    Incident #{safe_text(incident["incident_id"])}
                </div>
                <div class="incident-title">
                    {safe_text(incident["title"])}
                </div>
                <div class="incident-summary">
                    {safe_text(incident["summary"])}
                </div>
                <div class="incident-meta-row">
                    <div class="incident-meta">
                        Source ·
                        {safe_text(incident["source_type"])}
                    </div>
                    <div class="incident-meta">
                        Rule ·
                        {safe_text(incident["rule_name"])}
                    </div>
                    <div class="incident-meta">
                        Version ·
                        {safe_text(incident["rule_version"])}
                    </div>
                    {incident_badges}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


        # =============================================================
        # KPI STRIP
        # =============================================================

        render_section(
            "Business Signals",
            "Situation metrics",
            "Deterministic evidence describing the simulated "
            "business state under investigation.",
        )


        demand = scenario_metrics["demand"]

        inventory = scenario_metrics["inventory"]

        financial = scenario_metrics["financial"]

        customer = scenario_metrics["customer"]


        metric_col1, metric_col2, metric_col3, metric_col4 = (
            st.columns(4)
        )


        with metric_col1:

            st.markdown(
                """
                <div class="metric-shell">
                    <div class="metric-kicker">
                        Demand
                    </div>
                    <div class="metric-name">
                        Daily orders
                    </div>
                """,
                unsafe_allow_html=True,
            )


            st.metric(
                label="Daily demand",
                value=(
                    f"{demand['simulated_daily_orders']:,.2f}"
                ),
                delta=(
                    f"{demand['change_pct']:+.1f}%"
                ),
                label_visibility="collapsed",
            )


            st.markdown(
                """
                    <div class="metric-note">
                        Scenario-driven business activity
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


        with metric_col2:

            st.markdown(
                """
                <div class="metric-shell">
                    <div class="metric-kicker">
                        Inventory
                    </div>
                    <div class="metric-name">
                        Coverage
                    </div>
                """,
                unsafe_allow_html=True,
            )


            st.metric(
                label="Inventory coverage",
                value=(
                    f"{inventory['simulated_cover_days']:.2f} days"
                ),
                delta=(
                    f"{-inventory['decline_pct']:.1f}%"
                ),
                label_visibility="collapsed",
            )


            st.markdown(
                """
                    <div class="metric-note">
                        Model-derived inventory coverage
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


        with metric_col3:

            st.markdown(
                """
                <div class="metric-shell">
                    <div class="metric-kicker">
                        Revenue
                    </div>
                    <div class="metric-name">
                        Daily revenue
                    </div>
                """,
                unsafe_allow_html=True,
            )


            st.metric(
                label="Daily revenue",
                value=(
                    f"${financial['current_daily_revenue']:,.2f}"
                ),
                delta=(
                    f"{financial['change_pct']:+.1f}%"
                ),
                label_visibility="collapsed",
            )


            st.markdown(
                """
                    <div class="metric-note">
                        Scenario-driven daily revenue
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


        with metric_col4:

            st.markdown(
                """
                <div class="metric-shell">
                    <div class="metric-kicker">
                        Customer
                    </div>
                    <div class="metric-name">
                        Review score
                    </div>
                """,
                unsafe_allow_html=True,
            )


            st.metric(
                label="Customer review score",
                value=(
                    f"{customer['current_review_score']:.2f}"
                ),
                delta=(
                    f"{customer['change']:+.2f}"
                ),
                label_visibility="collapsed",
            )


            st.markdown(
                """
                    <div class="metric-note">
                        Scenario-driven customer signal
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


        st.caption(
            "Evidence classification: demand, financial and customer "
            "values are scenario-driven; inventory coverage is "
            "model-derived."
        )


        # =============================================================
        # DECISION
        # =============================================================

        render_section(
            "Decision",
            "Recommended response",
            "The decision generated from deterministic business "
            "evidence and subsequently validated by the decision layer.",
        )


        st.markdown(
            f"""
            <div class="decision-panel">
                <div class="decision-panel-label">
                    Recommended action
                </div>
                <div class="decision-panel-action">
                    {safe_text(decision["recommended_action"])}
                </div>
                <div class="decision-panel-rationale">
                    <strong>Decision rationale:</strong>
                    {safe_text(decision["rationale"])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


        # =============================================================
        # RCA
        # =============================================================

        candidates = root_cause.get(
            "candidate_causes",
            [],
        )


        if candidates:

            render_section(
                "Root Cause Analysis",
                "Evidence behind the situation",
                "Candidate contributing factors are ranked through "
                "deterministic evidence analysis. The system does not "
                "claim causal certainty where the evidence cannot prove it.",
            )


            for candidate in candidates:

                rca_col1, rca_col2 = st.columns(
                    [4.8, 1.2],
                    vertical_alignment="top",
                )


                with rca_col1:

                    st.markdown(
                        f"""
                        <div class="rca-card">
                            <div class="rca-title">
                                {safe_text(
                                    candidate["candidate_cause"]
                                )}
                            </div>
                            <div class="evidence-label">
                                Evidence supporting
                            </div>
                            <div class="evidence-text">
                                {safe_text(
                                    candidate["evidence_for"]
                                )}
                            </div>
                            <div class="evidence-label">
                                Evidence limiting confidence
                            </div>
                            <div class="evidence-text">
                                {safe_text(
                                    candidate["evidence_against"]
                                )}
                            </div>
                            <div class="evidence-type">
                                Evidence type ·
                                {safe_text(
                                    candidate["evidence_type"]
                                )}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


                with rca_col2:

                    st.markdown(
                        f"""
                        <div class="rca-card">
                            <div class="rca-confidence">
                                Confidence
                            </div>
                            <div class="confidence-value">
                                {safe_text(
                                    candidate["confidence"]
                                )}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


            rca_validation = root_cause.get(
                "validation",
                {},
            )


            st.caption(
                "RCA integrity · "
                f"Deterministic: "
                f"{rca_validation.get('deterministic')} · "
                f"Causal certainty claimed: "
                f"{rca_validation.get('causal_certainty_claimed')} · "
                f"Historical context available: "
                f"{rca_validation.get('historical_context_available')}"
            )


        # =============================================================
        # EXECUTIVE INTERPRETATION
        # =============================================================

        render_section(
            "Executive Interpretation",
            "What this means",
            "A read-only language-model interpretation of the evidence "
            "already produced by the deterministic investigation pipeline.",
        )


        st.markdown(
            f"""
            <div class="interpretation-card">
                <div class="interpretation-label">
                    Read-only evidence interpretation
                </div>
                <div class="interpretation-summary">
                    {safe_text(
                        llm["executive_summary"]
                    )}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


        # =============================================================
        # EVIDENCE & TRACEABILITY
        # =============================================================

        render_section(
            "Evidence & Traceability",
            "Decision evidence",
            "Supporting observations, uncertainty, unresolved questions, "
            "and provenance remain available for audit and review.",
        )


        with st.expander(
            "Key observations",
            expanded=True,
        ):

            observations = llm.get(
                "key_observations",
                [],
            )


            if observations:

                for observation in observations:

                    st.markdown(
                        f"- {safe_text(observation)}"
                    )

            else:

                st.write(
                    "No key observations available."
                )


        with st.expander(
            "What we are not certain about",
            expanded=False,
        ):

            uncertainty = llm.get(
                "uncertainty",
                [],
            )


            if uncertainty:

                for item in uncertainty:

                    st.markdown(
                        f"- {safe_text(item)}"
                    )

            else:

                st.write(
                    "No uncertainty signals reported."
                )


        with st.expander(
            "Questions that still need answers",
            expanded=False,
        ):

            unresolved_questions = llm.get(
                "unresolved_questions",
                [],
            )


            if unresolved_questions:

                for question in unresolved_questions:

                    st.markdown(
                        f"- {safe_text(question)}"
                    )

            else:

                st.write(
                    "No unresolved questions reported."
                )


        with st.expander(
            "Provenance & traceability",
            expanded=False,
        ):

            st.caption(
                "Every major evidence category is classified by provenance "
                "so users can distinguish observed, simulated, model-derived, "
                "deterministic, and LLM-generated information."
            )


            provenance_html = ""


            for source, classification in provenance.items():

                provenance_html += f"""
                    <div class="traceability-item">
                        <div class="traceability-source">
                            {safe_text(source)}
                        </div>
                        <div class="traceability-classification">
                            {safe_text(classification)}
                        </div>
                    </div>
                """


            if provenance_html:

                st.markdown(
                    f"""
                    <div class="traceability-grid">
                        {provenance_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:

                st.markdown(
                    """
                    <div class="empty-state">
                        No provenance records were returned.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


        # =============================================================
        # TECHNICAL INTEGRITY
        # =============================================================

        with st.expander(
            "Technical integrity",
            expanded=False,
        ):

            integrity_col1, integrity_col2, integrity_col3 = (
                st.columns(3)
            )


            with integrity_col1:

                st.caption("LLM STATUS")

                st.write(
                    llm["status"]
                )


            with integrity_col2:

                st.caption("INTERPRETATION MODEL")

                st.write(
                    llm["model"]
                )


            with integrity_col3:

                st.caption("DECISION CONTROL")

                st.write(
                    "READ-ONLY"
                )


            st.info(
                "The language model provides evidence interpretation only. "
                "Deterministic business logic remains authoritative for "
                "business facts, decision generation, and decision validation."
            )


        # =============================================================
        # DECISION INTEGRITY FOOTER
        # =============================================================

        st.divider()


        st.markdown(
            """
            <div class="integrity-card">
                <div class="integrity-title">
                    ORACLE-X · Decision Integrity
                </div>
                <div class="integrity-text">
                    Business decisions are generated and validated through
                    deterministic logic. Scenario inputs are explicitly
                    identified, model-derived values remain traceable,
                    root-cause analysis does not imply unsupported causal
                    certainty, and LLM output remains a read-only interpretation
                    layer rather than a source of business authority.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


    # -----------------------------------------------------------------
    # Error handling
    # -----------------------------------------------------------------

    except requests.Timeout:

        st.error(
            "The ORACLE-X API request timed out. "
            "The investigation may still be running."
        )


    except requests.ConnectionError:

        st.error(
            "Could not connect to the ORACLE-X API. "
            "Make sure the FastAPI service is running."
        )


    except requests.RequestException as exc:

        st.error(
            "The ORACLE-X API request failed: "
            f"{exc}"
        )


    except KeyError as exc:

        st.error(
            "The API response is missing an expected field: "
            f"{exc}"
        )


    except Exception as exc:

        st.error(
            f"Unexpected dashboard error: {exc}"
        )