import html
import json
import re
import uuid
from pathlib import Path

import streamlit as st

# =========================================================
# STUDYPILOT — ADAPTIVE STUDY PLANNER (Premium motion UI)
# Rule-based planning + persistent local JSON storage
# + simulated Alexa+ conversational assistant
# Requires Streamlit >= 1.39 (keyed containers)
# =========================================================

st.set_page_config(
    page_title="StudyPilot | Study Smarter",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).parent / "tasks.json"

DIFFICULTY_SCORE = {
    "Easy": 1,
    "Medium": 2,
    "Hard": 3,
}

# ------------------------- DESIGN -------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --page: #0D0F17;
    --surface: #161A28;
    --surface-2: #1C2133;
    --surface-soft: #202744;
    --blue: #7C9BF5;
    --blue-hover: #94AEFA;
    --blue-dim: rgba(124, 155, 245, 0.14);
    --text: #E8EBF5;
    --soft: #AEB6D3;
    --muted: #8189A3;
    --border: #262C42;
    --ease: cubic-bezier(0.22, 1, 0.36, 1);
    --spring: cubic-bezier(0.34, 1.56, 0.64, 1);
    --green: #3DDC97;
    --green-soft: #7BEBBB;
    --green-dim: rgba(61, 220, 151, 0.14);
    --red: #F5657A;
    --red-soft: #FF9AA8;
    --red-dim: rgba(245, 101, 122, 0.14);
}

html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif !important;
}

.stApp {
    background:
        radial-gradient(900px 500px at 85% -10%, rgba(80, 105, 220, 0.18), transparent 60%),
        radial-gradient(700px 400px at 0% 100%, rgba(60, 80, 180, 0.10), transparent 60%),
        var(--page);
    color: var(--text);
}

[data-testid="stHeader"] { background: transparent; }

[data-testid="stSidebar"] {
    background: #0A0C13;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text);
}

h1, h2, h3, h4 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text) !important;
    letter-spacing: -0.6px;
    font-weight: 700 !important;
}
p, label, .stMarkdown, [data-testid="stCaptionContainer"] { color: var(--text); }

/* ================= KEYFRAMES ================= */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes floatGlow {
    0%, 100% { transform: translate(0, 0) scale(1); opacity: .9; }
    50%      { transform: translate(-18px, 12px) scale(1.08); opacity: 1; }
}
@keyframes shimmer {
    from { background-position: 200% 0; }
    to   { background-position: -200% 0; }
}
@keyframes popIn {
    0%   { transform: scale(0.4); opacity: 0; }
    60%  { transform: scale(1.18); opacity: 1; }
    100% { transform: scale(1); }
}
@keyframes drawCheck {
    from { stroke-dashoffset: 24; }
    to   { stroke-dashoffset: 0; }
}
@keyframes ringBurst {
    0%   { transform: scale(0.6); opacity: 0.9; }
    100% { transform: scale(2.6); opacity: 0; }
}
@keyframes strikeDraw {
    from { background-size: 0% 2px; }
    to   { background-size: 100% 2px; }
}
@keyframes freshCard {
    0%   { transform: scale(0.97); box-shadow: 0 0 0 0 rgba(61,220,151,0); border-color: var(--green); }
    35%  { transform: scale(1.015); box-shadow: 0 0 0 6px rgba(61,220,151,0.22), 0 18px 50px rgba(61,220,151,0.30); border-color: var(--green); }
    100% { transform: scale(1); box-shadow: 0 6px 20px rgba(0,0,0,0.25); }
}
@keyframes undoCard {
    0%   { transform: scale(1.02); box-shadow: 0 0 0 0 rgba(245,101,122,0); border-color: var(--red); }
    20%  { transform: translateX(-6px); }
    40%  { transform: translateX(5px); box-shadow: 0 0 0 6px rgba(245,101,122,0.22), 0 18px 50px rgba(245,101,122,0.30); border-color: var(--red); }
    60%  { transform: translateX(-3px); }
    80%  { transform: translateX(1px); }
    100% { transform: translateX(0); box-shadow: 0 6px 20px rgba(0,0,0,0.25); }
}
@keyframes strikeUndo {
    from { background-size: 100% 2px; }
    to   { background-size: 0% 2px; }
}
@keyframes flashRed {
    0%   { background: var(--red); color: #1A0D10; border-color: var(--red); transform: scale(1.15); }
    100% { background: transparent; color: var(--muted); border-color: #323A57; transform: scale(1); }
}
@keyframes bannerLife {
    0%   { opacity: 0; transform: translateY(-12px) scale(0.97); max-height: 0; margin-bottom: 0; }
    12%  { opacity: 1; transform: translateY(0) scale(1); max-height: 120px; margin-bottom: 14px; }
    80%  { opacity: 1; transform: translateY(0) scale(1); max-height: 120px; margin-bottom: 14px; }
    100% { opacity: 0; transform: translateY(-8px) scale(0.98); max-height: 0; margin-bottom: 0; padding-top: 0; padding-bottom: 0; }
}
@keyframes confetti {
    0%   { transform: translate(0,0) scale(1); opacity: 1; }
    100% { transform: translate(var(--x), var(--y)) scale(0.2); opacity: 0; }
}

/* ---------- Brand ---------- */
.brand { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
.brand-mark {
    width: 34px; height: 34px; border-radius: 10px;
    background: linear-gradient(135deg, #8DA8F8, #4F66C8);
    box-shadow: 0 6px 18px rgba(92, 120, 230, 0.35);
    display: flex; align-items: center; justify-content: center;
    color: #0D1226 !important;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800; font-size: 16px;
    transition: transform .5s var(--spring), box-shadow .3s ease;
}
.brand:hover .brand-mark {
    transform: rotate(-8deg) scale(1.12);
    box-shadow: 0 10px 28px rgba(92, 120, 230, 0.6);
}
.brand-name { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 20px; font-weight: 800; letter-spacing: -0.5px; }
.side-label {
    font-size: 11px; font-weight: 700; letter-spacing: 1.8px;
    color: var(--muted) !important; text-transform: uppercase; margin: 6px 0 10px;
}
.side-step {
    display: flex; gap: 12px; align-items: flex-start;
    margin-bottom: 6px; padding: 7px 8px; border-radius: 10px;
    font-size: 14px; color: var(--soft) !important; line-height: 1.5;
    transition: transform .3s var(--ease), background .3s ease;
    cursor: default;
}
.side-step:hover { transform: translateX(5px); background: var(--blue-dim); }
.side-step span.n {
    flex: 0 0 22px; height: 22px; border-radius: 50%;
    border: 1px solid #323B6B; background: var(--blue-dim);
    color: var(--blue) !important; font-size: 11px; font-weight: 700;
    display: flex; align-items: center; justify-content: center; margin-top: 1px;
    transition: all .3s var(--spring);
}
.side-step:hover span.n { background: var(--blue); color: #0D1226 !important; transform: scale(1.18); }

/* ---------- Hero ---------- */
.hero {
    position: relative; overflow: hidden;
    background: linear-gradient(135deg, #1B2142, #11152A);
    border: 1px solid #2D3563;
    padding: 36px; border-radius: 22px; margin: 8px 0 26px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35);
    animation: fadeUp .8s var(--ease) both;
    transition: border-color .4s ease, box-shadow .4s ease, transform .5s var(--ease);
}
.hero::before {
    content: ""; position: absolute; top: -90px; right: -60px;
    width: 380px; height: 300px; border-radius: 50%;
    background: radial-gradient(circle, rgba(124,155,245,0.32), transparent 70%);
    animation: floatGlow 9s ease-in-out infinite;
    pointer-events: none;
}
.hero:hover {
    border-color: #4A5799; transform: translateY(-3px);
    box-shadow: 0 22px 60px rgba(60, 80, 200, 0.28);
}
.hero > * { position: relative; }
.hero-kicker { color: var(--blue); font-size: 11px; font-weight: 700; letter-spacing: 2.4px; }
.hero-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: linear-gradient(90deg, #FFFFFF 0%, #C9D5FF 45%, #FFFFFF 90%);
    background-size: 200% 100%;
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 8s linear infinite;
    font-size: clamp(27px, 3vw, 38px); font-weight: 800;
    letter-spacing: -1.2px; line-height: 1.25; margin: 14px 0;
}
.hero-copy { color: var(--soft); font-size: 15px; line-height: 1.8; max-width: 680px; }

/* ---------- Metric cards ---------- */
.metric-card {
    position: relative; overflow: hidden;
    background: linear-gradient(160deg, #1A1F33, #141827);
    border: 1px solid var(--border); border-radius: 17px;
    padding: 22px; min-height: 112px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.30);
    animation: fadeUp .7s var(--ease) both;
    animation-delay: var(--d, 0s);
    transition: transform .4s var(--ease), border-color .3s ease, box-shadow .4s ease;
}
.metric-card::before {
    content: ""; position: absolute; top: 0; left: 22px;
    width: 34px; height: 2px;
    background: linear-gradient(90deg, var(--blue), transparent);
    transition: width .6s var(--ease);
}
.metric-card::after {
    content: ""; position: absolute; inset: 0;
    background: radial-gradient(260px 120px at var(--mx, 80%) -20%, rgba(124,155,245,0.22), transparent 70%);
    opacity: 0; transition: opacity .4s ease; pointer-events: none;
}
.metric-card:hover {
    transform: translateY(-6px);
    border-color: #3A4580;
    box-shadow: 0 18px 40px rgba(60, 85, 210, 0.28);
}
.metric-card:hover::before { width: calc(100% - 44px); }
.metric-card:hover::after { opacity: 1; }
.metric-label {
    color: var(--muted); font-size: 11px; font-weight: 700;
    letter-spacing: 1.6px; text-transform: uppercase; margin-bottom: 14px;
}
.metric-value {
    font-family: 'Plus Jakarta Sans', sans-serif; color: var(--text);
    font-size: 30px; font-weight: 800; letter-spacing: -0.8px;
    transition: transform .4s var(--spring), color .3s ease;
    display: inline-block; transform-origin: left center;
}
.metric-card:hover .metric-value { transform: scale(1.08); color: #FFFFFF; }

.section-note { color: var(--muted); font-size: 14px; margin-top: -7px; margin-bottom: 20px; }

/* ---------- Containers / cards ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(160deg, #1A1F33, #141827);
    border-color: var(--border) !important;
    border-radius: 17px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}

/* Keyed cards (plan + task list): lift, glow, border light-up on hover */
[class*="st-key-card_"] {
    border-radius: 17px;
    animation: fadeUp .55s var(--ease) both;
    transition: transform .4s var(--ease), box-shadow .4s ease,
                border-color .3s ease, background .4s ease;
}
[class*="st-key-card_"]:hover {
    transform: translateY(-4px) scale(1.006);
    border-color: #4A5799 !important;
    background: linear-gradient(160deg, #1E2440, #161B2E);
    box-shadow: 0 18px 44px rgba(70, 95, 220, 0.30), 0 0 0 1px rgba(124,155,245,0.25);
}
[class*="st-key-card_"]:hover .plan-title,
[class*="st-key-card_"]:hover .task-title:not(.done) { color: #FFFFFF; }
[class*="st-key-card_"]:active { transform: translateY(-1px) scale(0.998); }

/* Freshly completed task card */
[class*="st-key-card_list_"][class*="_fresh"] {
    animation: freshCard 1.1s var(--ease) both;
}
/* Freshly undone task card (red) */
[class*="st-key-card_list_"][class*="_undo"] {
    animation: undoCard .8s var(--ease) both;
}
/* Completed cards keep a calm green edge */
[class*="st-key-card_list_"][class*="_done"] {
    border-left: 3px solid var(--green) !important;
}

[data-testid="stMetric"] {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 15px; padding: 16px;
    transition: transform .35s var(--ease), border-color .3s ease, box-shadow .35s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px); border-color: #3A4580;
    box-shadow: 0 12px 28px rgba(60, 85, 210, 0.22);
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; }
[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 750 !important;
}

/* ---------- Progress ---------- */
[data-testid="stProgressBar"] > div { background: #232A42; border-radius: 20px; }
[data-testid="stProgressBar"] [data-testid="stProgressBarFill"] {
    background: linear-gradient(90deg, #5C78E6, var(--blue), #A9BDFB, var(--blue), #5C78E6);
    background-size: 200% 100%;
    animation: shimmer 3.5s linear infinite;
    border-radius: 20px;
    transition: width 1s var(--ease);
    box-shadow: 0 0 14px rgba(124,155,245,0.55);
}

/* ---------- Buttons ---------- */
.stButton > button,
.stFormSubmitButton > button {
    position: relative; overflow: hidden;
    border-radius: 12px;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700; min-height: 44px; letter-spacing: 0.2px;
    transition: transform .3s var(--ease), box-shadow .3s ease,
                background .3s ease, border-color .3s ease, color .3s ease;
}
/* light sweep on hover */
.stButton > button::after,
.stFormSubmitButton > button::after {
    content: ""; position: absolute; top: 0; left: -80%;
    width: 50%; height: 100%;
    background: linear-gradient(100deg, transparent, rgba(255,255,255,0.35), transparent);
    transform: skewX(-20deg);
    transition: left .7s var(--ease);
    pointer-events: none;
}
.stButton > button:hover::after,
.stFormSubmitButton > button:hover::after { left: 130%; }
.stButton > button:active,
.stFormSubmitButton > button:active { transform: scale(0.95) !important; transition-duration: .1s; }

.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"],
.stFormSubmitButton > button[data-testid="stBaseButton-primaryFormSubmit"] {
    background: var(--blue); color: #0D1226; border: 1px solid var(--blue);
}
.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover,
.stFormSubmitButton > button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    background: var(--blue-hover); border-color: var(--blue-hover); color: #0D1226;
    transform: translateY(-2px);
    box-shadow: 0 10px 26px rgba(124, 155, 245, 0.45);
}

.stButton > button[kind="secondary"],
.stButton > button[data-testid="stBaseButton-secondary"] {
    background: transparent; color: var(--blue); border: 1px solid #36407A;
}
.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="stBaseButton-secondary"]:hover {
    background: var(--blue); border-color: var(--blue); color: #0D1226;
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(124, 155, 245, 0.35);
}
.stButton > button:focus,
.stFormSubmitButton > button:focus { box-shadow: 0 0 0 3px rgba(124, 155, 245, 0.30); }

/* ---------- Inputs ---------- */
input, textarea, [data-baseweb="input"] input {
    background: var(--surface-2) !important; color: var(--text) !important;
    border-radius: 10px !important;
}
[data-baseweb="input"], [data-baseweb="textarea"] {
    background: var(--surface-2) !important; border-color: var(--border) !important;
    border-radius: 10px !important;
    transition: border-color .3s ease, box-shadow .3s ease, transform .3s var(--ease);
}
[data-baseweb="input"]:hover, [data-baseweb="textarea"]:hover { border-color: #3A4580 !important; }
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(124,155,245,0.22);
}
[data-baseweb="select"] > div {
    background: var(--surface-2); border-color: var(--border); color: var(--text);
    border-radius: 10px; transition: border-color .3s ease, box-shadow .3s ease;
}
[data-baseweb="select"] > div:hover { border-color: #3A4580; }
[data-baseweb="popover"] ul, [data-baseweb="menu"] {
    background: var(--surface-2) !important; color: var(--text) !important;
}
[data-testid="stCaptionContainer"] { color: var(--muted); }
.stCheckbox label, .stRadio label { color: var(--text) !important; }
.stCheckbox label, .stRadio label { transition: transform .25s var(--ease), color .25s ease; }
.stCheckbox label:hover, .stRadio label:hover { transform: translateX(3px); color: var(--blue-hover) !important; }

hr { border-color: var(--border); }

/* ---------- Alerts ---------- */
[data-testid="stAlert"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-left: 3px solid var(--blue) !important;
    border-radius: 12px;
    animation: fadeUp .5s var(--ease) both;
}
[data-testid="stAlert"] * { color: var(--soft) !important; }

/* ---------- Chat (Alexa+ assistant) ---------- */
[data-testid="stChatMessage"] {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 14px;
    animation: fadeUp .4s var(--ease) both;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li { color: var(--text); }
[data-testid="stChatInput"] { border-radius: 14px; }

/* ---------- Expander ---------- */
[data-testid="stExpander"] {
    background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
    transition: border-color .3s ease, box-shadow .3s ease;
}
[data-testid="stExpander"]:hover { border-color: #3A4580; box-shadow: 0 8px 22px rgba(60,85,210,0.15); }

/* ---------- Plan & task text ---------- */
.plan-number { color: var(--blue); font-size: 11px; font-weight: 800; letter-spacing: 2px; }
.plan-title {
    color: var(--text); font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 19px; font-weight: 750; margin: 7px 0 10px;
    overflow-wrap: anywhere; transition: color .3s ease;
}
.task-row { display: flex; align-items: center; gap: 14px; }
.task-title {
    color: var(--text); font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 16px; font-weight: 700; overflow-wrap: anywhere;
    transition: color .4s ease;
}
.task-title.done { color: var(--muted); }
.task-title.done .t {
    background: linear-gradient(#6A7399, #6A7399) no-repeat 0 55% / 100% 2px;
}
.task-title.done.fresh .t { animation: strikeDraw .7s var(--ease) .25s both; background-size: 0% 2px; background-image: linear-gradient(var(--green), var(--green)); }
.task-title.done .t { background-image: linear-gradient(#3F9E78, #3F9E78); }
.task-title.undo .t {
    background: linear-gradient(var(--red), var(--red)) no-repeat 0 55% / 0% 2px;
    animation: strikeUndo .6s var(--ease) both;
    color: var(--text);
}

/* Check badge */
.check {
    position: relative; flex: 0 0 26px; width: 26px; height: 26px;
    border-radius: 50%; border: 2px solid #3A4580;
    display: flex; align-items: center; justify-content: center;
    transition: border-color .3s ease, background .3s ease, transform .4s var(--spring);
}
.check svg { width: 14px; height: 14px; opacity: 0; }
[class*="st-key-card_"]:hover .check:not(.on) {
    border-color: var(--blue); background: var(--blue-dim); transform: scale(1.12);
}
[class*="st-key-card_"]:hover .check:not(.on) svg { opacity: .55; }
[class*="st-key-card_"]:hover .check:not(.on) path { stroke-dashoffset: 0; }
.check.on { background: linear-gradient(135deg, var(--green-soft), var(--green)); border-color: var(--green); box-shadow: 0 0 14px rgba(61,220,151,0.45); }
.check.undo { border-color: var(--red); background: var(--red-dim); animation: popIn .5s var(--spring) both; }
.check.undo::after {
    content: ""; position: absolute; inset: -2px; border-radius: 50%;
    border: 2px solid var(--red); animation: ringBurst .8s ease-out both;
}
.check.on svg { opacity: 1; }
.check path { stroke-dasharray: 24; stroke-dashoffset: 24; transition: stroke-dashoffset .35s ease; }
.check.on path { stroke-dashoffset: 0; }
.check.on.fresh { animation: popIn .6s var(--spring) both; }
.check.on.fresh path { animation: drawCheck .5s ease .3s both; stroke-dashoffset: 24; }
.check.on.fresh::after {
    content: ""; position: absolute; inset: -2px; border-radius: 50%;
    border: 2px solid var(--green); animation: ringBurst .9s ease-out .1s both;
}

.task-meta { color: var(--muted); font-size: 13px; margin-top: 7px; }

/* ---------- Completed banner ---------- */
.done-banner {
    position: relative; overflow: visible;
    display: flex; align-items: center; gap: 14px;
    padding: 14px 18px; border-radius: 14px;
    background: linear-gradient(120deg, rgba(61,220,151,0.24), rgba(61,220,151,0.06));
    border: 1px solid var(--green);
    box-shadow: 0 10px 34px rgba(61,220,151,0.28);
    animation: bannerLife 3.6s var(--ease) forwards;
    color: var(--text); font-weight: 600; font-size: 14px;
}
.done-banner.undo-banner {
    background: linear-gradient(120deg, rgba(245,101,122,0.24), rgba(245,101,122,0.06));
    border-color: var(--red);
    box-shadow: 0 10px 34px rgba(245,101,122,0.28);
}
.done-banner.undo-banner .check { background: var(--red-dim); border-color: var(--red); }
.done-banner .check { flex-basis: 30px; width: 30px; height: 30px; }
.done-banner .burst { position: absolute; left: 33px; top: 50%; width: 0; height: 0; }
.done-banner .burst i {
    position: absolute; width: 6px; height: 6px; border-radius: 50%;
    background: var(--green); animation: confetti .9s ease-out .15s both;
}
.undo-banner .burst i { background: var(--red); }
.done-banner .burst i:nth-child(1) { --x: -34px; --y: -28px; background: var(--green-soft); }
.done-banner .burst i:nth-child(2) { --x:  34px; --y: -30px; background: #A9F5D4; }
.done-banner .burst i:nth-child(3) { --x: -42px; --y:  10px; }
.done-banner .burst i:nth-child(4) { --x:  44px; --y:  14px; background: var(--green-soft); }
.done-banner .burst i:nth-child(5) { --x:  -8px; --y: -42px; background: #A9F5D4; }
.undo-banner .burst i:nth-child(odd) { background: var(--red-soft); }
.done-banner .burst i:nth-child(6) { --x:  10px; --y:  38px; }

/* ---------- Pills ---------- */
.pill {
    display: inline-block; border-radius: 20px; padding: 5px 12px;
    font-size: 10.5px; font-weight: 700; letter-spacing: 1px;
    margin-right: 8px; text-transform: uppercase;
    transition: transform .3s var(--spring), box-shadow .3s ease;
}
.pill:hover { transform: translateY(-2px) scale(1.06); box-shadow: 0 6px 14px rgba(124,155,245,0.25); }
.pill-priority { background: var(--surface-soft); color: var(--blue); border: 1px solid #323B6B; }
.pill-weak { background: rgba(167,139,250,0.12); color: #B9A6FA; border: 1px solid rgba(167,139,250,0.30); }
.pill-pending { background: transparent; color: var(--muted); border: 1px solid #323A57; }
.pill-done { background: var(--green-dim); color: var(--green); border: 1px solid rgba(61,220,151,0.40); }
.pill.fresh { animation: popIn .6s var(--spring) .2s both; }
.pill-pending.undo { animation: flashRed 1.2s var(--ease) both; }

.footer {
    text-align: center; color: #5D657E; font-size: 11px;
    padding: 30px 0 12px; letter-spacing: 1.6px; transition: color .4s ease, letter-spacing .5s var(--ease);
}
.footer:hover { color: var(--blue); letter-spacing: 2.4px; }

@media (max-width: 640px) {
    .hero { padding: 24px; border-radius: 17px; }
    .metric-card { padding: 16px; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; }
}
</style>
""", unsafe_allow_html=True)


# ---------------------- STORAGE ---------------------------

def load_tasks():
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        valid_tasks = []

        for task in data:
            if not isinstance(task, dict) or not task.get("name"):
                continue

            task.setdefault("id", str(uuid.uuid4()))
            task.setdefault("duration", 30)
            task.setdefault("difficulty", "Medium")
            task.setdefault("weak", False)
            task.setdefault("completed", False)

            if task["difficulty"] not in DIFFICULTY_SCORE:
                task["difficulty"] = "Medium"

            task["duration"] = max(5, int(task["duration"]))
            task["weak"] = bool(task["weak"])
            task["completed"] = bool(task["completed"])

            valid_tasks.append(task)

        return valid_tasks

    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        st.error("Unable to read tasks.json. Your original file has not been deleted.")
        return []


def save_tasks():
    temp_file = DATA_FILE.with_suffix(".tmp")

    try:
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(
                st.session_state.tasks,
                file,
                indent=2,
                ensure_ascii=False,
            )

        temp_file.replace(DATA_FILE)
        return True

    except OSError as error:
        st.error(f"Could not save tasks: {error}")
        return False


if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False

# id of the task completed on the previous click (drives the celebration animation)
if "just_done" not in st.session_state:
    st.session_state.just_done = None

# id of the task that was just undone (drives the red animation)
if "just_undone" not in st.session_state:
    st.session_state.just_undone = None

# Alexa+ assistant conversation history: list of (role, message)
if "chat" not in st.session_state:
    st.session_state.chat = [(
        "assistant",
        "Hi, I'm your Alexa+ study assistant. Ask me for today's plan, "
        "add a topic, or tell me what you've finished.",
    )]


CHECK_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="#0D1226" stroke-width="3.5" '
    'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
)


def check_badge(done=False, fresh=False, undo=False):
    cls = "check"
    if done:
        cls += " on"
    if fresh:
        cls += " fresh"
    if undo:
        cls += " undo"
    return f'<span class="{cls}">{CHECK_SVG}</span>'


# -------------------- PLANNING LOGIC ----------------------

def priority_score(task):
    score = DIFFICULTY_SCORE.get(task["difficulty"], 2)

    if task["weak"]:
        score += 3

    return score


def generate_plan(tasks, available_minutes):
    pending = [t for t in tasks if not t["completed"]]

    ranked = sorted(
        pending,
        key=lambda t: (
            priority_score(t),
            -t["duration"],
            t["name"].lower(),
        ),
        reverse=True,
    )

    scheduled = []
    skipped = []
    remaining = available_minutes

    for task in ranked:
        if task["duration"] <= remaining:
            scheduled.append(task)
            remaining -= task["duration"]
        else:
            skipped.append(task)

    return scheduled, skipped, remaining


def mark_done(task):
    task["completed"] = True
    st.session_state.just_done = task["id"]
    st.session_state.just_undone = None


def mark_undone(task):
    task["completed"] = False
    st.session_state.just_undone = task["id"]
    st.session_state.just_done = None


# ------------------ ALEXA+ ASSISTANT LOGIC ----------------
# CHAT-LOGIC-START
# A small rule-based "natural language" layer. It understands a handful of
# intents (plan, add, complete, undo, progress, pending) and calls the same
# planner and storage functions that the dashboard uses.

DURATION_RE = re.compile(
    r"\b(?:for\s+)?(\d+(?:\.\d+)?)\s*(hours?|hrs?|h|minutes?|mins?|m)\b",
    re.IGNORECASE,
)


def md_safe(text):
    """Escape characters that would be read as Markdown formatting."""
    return re.sub(r"([\\`*_{}\[\]<>#~|])", r"\\\1", str(text))


def extract_duration(text):
    """Return (total_minutes_or_None, text_with_duration_phrases_removed)."""
    total = 0.0
    found = False

    for match in DURATION_RE.finditer(text):
        found = True
        value = float(match.group(1))
        unit = match.group(2).lower()
        total += value * 60 if unit.startswith("h") else value

    cleaned = DURATION_RE.sub(" ", text)
    return (int(round(total)) if found else None), cleaned


def parse_minutes(text):
    minutes, _ = extract_duration(text)
    return minutes


def describe_task(task):
    parts = [f"{task['duration']} min", task["difficulty"]]
    if task["weak"]:
        parts.append("weak topic")
    return " · ".join(parts)


def extract_target(text):
    """Strip filler words so only the task name the user mentioned remains."""
    cleaned = text.lower().strip()
    cleaned = re.sub(r"[?!.,;:]+$", "", cleaned)
    cleaned = re.sub(
        r"\b(?:please|alexa|mark|complete|completed|finish|finished|done|undo|"
        r"reopen|re-open|unmark|as|pending|incomplete|undone|not|with|task|topic|"
        r"the|i['’]ve|i['’]m|ive|i|have|just|my|is|it)\b",
        " ",
        cleaned,
    )
    return re.sub(r"\s+", " ", cleaned).strip()


def find_task(target, completed):
    """Find exactly one task by (partial) name among completed or pending ones."""
    state = "completed" if completed else "pending"
    pool = [t for t in st.session_state.tasks if t["completed"] == completed]

    if not target:
        return None, "Which task do you mean? Tell me its name, for example “complete Physics”."

    exact = [t for t in pool if t["name"].lower() == target]
    if len(exact) == 1:
        return exact[0], None

    partial = [t for t in pool if target in t["name"].lower()]
    if not partial:
        words = target.split()
        partial = [t for t in pool if all(w in t["name"].lower() for w in words)]

    if len(partial) == 1:
        return partial[0], None

    if len(partial) > 1:
        names = ", ".join(md_safe(t["name"]) for t in partial[:5])
        return None, f"That matches more than one task: {names}. Which one do you mean?"

    return None, f"I couldn't find a {state} task matching “{md_safe(target)}”."


def reply_add(text):
    body = re.sub(
        r"^\s*(?:please\s+)?(?:add|create|new)\b\s*(?:a\s+|an\s+|the\s+)?(?:new\s+)?"
        r"(?:study\s+)?(?:(?:task|topic)\b)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    minutes, body = extract_duration(body)

    difficulty = "Medium"
    diff_match = re.search(
        r"\b(easy|medium|hard|difficult)\b(?:\s+difficulty)?", body, re.IGNORECASE
    )
    if diff_match:
        word = diff_match.group(1).lower()
        difficulty = "Hard" if word == "difficult" else word.capitalize()
        body = body[:diff_match.start()] + " " + body[diff_match.end():]

    body, weak_count = re.subn(
        r"\bweak\b(?:\s+(?:topic|subject|area))?", " ", body, flags=re.IGNORECASE
    )
    weak = weak_count > 0

    name = re.sub(r"\s+", " ", body).strip(" ,.-:;—")
    for _ in range(3):
        name = re.sub(r"^(?:and|for|as|with|of|called|named)\s+", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\s+(?:and|for|as|with|is|a|an)$", "", name, flags=re.IGNORECASE)
        name = name.strip(" ,.-:;—")

    if not name:
        return "What should I call it? Try: “add Physics 30 minutes hard weak”."

    name = name[:80]
    duration = max(5, min(300, minutes if minutes else 30))

    st.session_state.tasks.append({
        "id": str(uuid.uuid4()),
        "name": name,
        "duration": duration,
        "difficulty": difficulty,
        "weak": weak,
        "completed": False,
    })
    save_tasks()

    return (
        f"Done. I added **{md_safe(name)}** — {duration} min, {difficulty}"
        f"{', weak topic' if weak else ''}. "
        "Ask me to plan your day to see where it ranks."
    )


def reply_complete(text, undo=False):
    target = extract_target(text)
    task, error = find_task(target, completed=undo)

    if error:
        return error

    if undo:
        mark_undone(task)
        save_tasks()
        return f"No problem. **{md_safe(task['name'])}** is back on your pending list."

    mark_done(task)
    save_tasks()
    left = sum(1 for t in st.session_state.tasks if not t["completed"])

    if left == 0:
        return f"Nice work! **{md_safe(task['name'])}** is complete — you're all caught up."

    return f"Nice work! **{md_safe(task['name'])}** is complete. {left} task(s) left."


def reply_plan(text, default_minutes):
    minutes = parse_minutes(text) or default_minutes
    tasks = st.session_state.tasks
    pending_now = [t for t in tasks if not t["completed"]]

    if not tasks:
        return "Your study list is empty. Try: “add Physics 30 minutes hard weak”."

    if not pending_now:
        return "You're all caught up — there's nothing pending. Add another topic whenever you're ready."

    if minutes < 5:
        return "Give me at least 5 minutes and I'll build a plan."

    scheduled_now, skipped_now, free_now = generate_plan(tasks, minutes)

    if not scheduled_now:
        shortest = min(t["duration"] for t in pending_now)
        return (
            f"Nothing fits in {minutes} minutes — your shortest pending task needs "
            f"{shortest}. Try a longer window or shorten a task."
        )

    lines = [
        f"{i}. **{md_safe(t['name'])}** — {describe_task(t)}"
        for i, t in enumerate(scheduled_now, start=1)
    ]

    extra = f" {len(skipped_now)} other task(s) didn't fit." if skipped_now else ""

    return (
        f"With **{minutes} minutes**, here's what I'd study:\n\n"
        + "\n".join(lines)
        + "\n\nWeak topics come first, then harder ones. "
        + f"You'd have {free_now} min free.{extra}"
    )


def reply_progress():
    tasks = st.session_state.tasks

    if not tasks:
        return "Your study list is empty, so there's no progress yet."

    done = sum(1 for t in tasks if t["completed"])
    pending_now = [t for t in tasks if not t["completed"]]
    minutes_left = sum(t["duration"] for t in pending_now)
    rate = done / len(tasks)

    return (
        f"You've completed **{done} of {len(tasks)}** tasks ({rate:.0%}). "
        f"{len(pending_now)} left, about {minutes_left} minutes of study."
    )


def reply_pending():
    tasks = st.session_state.tasks
    ranked, _, _ = generate_plan(tasks, 10**6)

    if not ranked:
        return "Nothing is pending right now. Nice and clear!"

    lines = [
        f"{i}. **{md_safe(t['name'])}** — {describe_task(t)}"
        for i, t in enumerate(ranked[:8], start=1)
    ]
    more = f"\n\n…and {len(ranked) - 8} more." if len(ranked) > 8 else ""

    return "Here's what's pending, highest priority first:\n\n" + "\n".join(lines) + more


def reply_help():
    return (
        "I can help with:\n\n"
        "1. **Planning** — “I have 90 minutes, what should I study?”\n"
        "2. **Adding topics** — “add Physics 30 minutes hard weak”\n"
        "3. **Completing** — “complete Physics”\n"
        "4. **Undoing** — “undo Physics”\n"
        "5. **Progress** — “how is my progress?” or “what's pending?”"
    )


def alexa_reply(text, default_minutes):
    low = text.lower().strip()

    if re.match(r"^(?:please\s+)?(?:add|create|new)\b", low):
        return reply_add(text)

    is_undo = bool(re.match(r"^(?:please\s+)?(?:undo|reopen|re-open|unmark)\b", low)) or (
        bool(re.match(r"^(?:please\s+)?mark\b", low))
        and bool(re.search(r"\b(?:pending|incomplete|undone|not done)\b", low))
    )
    if is_undo:
        return reply_complete(text, undo=True)

    is_complete = (
        re.match(r"^(?:please\s+)?(?:complete|completed|finish|finished|done|mark)\b", low)
        or re.match(r"^i(?:['’]ve|\s+have)?\s+(?:just\s+)?(?:completed|finished|done)\b", low)
        or re.match(r"^i['’]m\s+done\b", low)
    )
    if is_complete:
        return reply_complete(text)

    if re.search(r"\b(?:progress|status|how am i|how many|how much|summary|stats)\b", low):
        return reply_progress()

    if re.search(
        r"\b(?:pending|remaining|to do|todo|my tasks|task list|list|what['’]?s left)\b", low
    ):
        return reply_pending()

    if re.search(
        r"\b(?:plan|schedule|study|what next|what should|what do i|minutes?|mins?|hours?|hrs?|time)\b",
        low,
    ):
        return reply_plan(text, default_minutes)

    if re.search(r"\b(?:hi|hello|hey|help|what can you do)\b", low):
        return reply_help()

    return (
        "I'm not sure I got that. Try “I have 60 minutes, what should I study?”, "
        "“add Physics 30 minutes hard weak”, or say “help”."
    )


def handle_chat(text, default_minutes):
    text = text.strip()
    if not text:
        return

    reply = alexa_reply(text, default_minutes)
    st.session_state.chat.append(("user", text))
    st.session_state.chat.append(("assistant", reply))
    st.session_state.chat = st.session_state.chat[-30:]
# CHAT-LOGIC-END


# ------------------------- SIDEBAR ------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">S</div>
            <div class="brand-name">StudyPilot</div>
        </div>
        <div class="side-label">Your personal study co-pilot</div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown('<div class="side-label">Today\'s availability</div>', unsafe_allow_html=True)

    available_minutes = st.number_input(
        "Study time (minutes)",
        min_value=15,
        max_value=720,
        value=120,
        step=15,
    )

    st.caption(
        f"That's {available_minutes // 60} hr "
        f"{available_minutes % 60} min available."
    )

    st.divider()
    st.markdown('<div class="side-label">How it works</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="side-step"><span class="n">1</span><div>Add your study topics.</div></div>
        <div class="side-step"><span class="n">2</span><div>Mark weak and difficult topics.</div></div>
        <div class="side-step"><span class="n">3</span><div>Follow your recommended plan.</div></div>
        <div class="side-step"><span class="n">4</span><div>Mark tasks complete to track progress.</div></div>
        <div class="side-step"><span class="n">5</span><div>Or just talk to the Alexa+ assistant.</div></div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.caption("Tasks are stored locally in tasks.json.")
    st.caption("Planning uses transparent rules, not an external AI service.")
    st.caption("The Alexa+ assistant is a simulated conversational layer.")


# ------------------------- DASHBOARD ----------------------

tasks = st.session_state.tasks
just_done_id = st.session_state.just_done
just_undone_id = st.session_state.just_undone
completed_count = sum(t["completed"] for t in tasks)
pending = [t for t in tasks if not t["completed"]]
remaining_task_minutes = sum(t["duration"] for t in pending)
completion_rate = completed_count / len(tasks) if tasks else 0

st.markdown("""
<div class="hero">
    <div class="hero-kicker">YOUR PERSONAL LEARNING SPACE</div>
    <div class="hero-title">Let's make today count.</div>
    <div class="hero-copy">
        Focus on what matters most. StudyPilot prioritizes your weak topics
        and difficult subjects, then builds a study plan around your available time.
    </div>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)

metrics = [
    (m1, "Total tasks", len(tasks)),
    (m2, "Completed", completed_count),
    (m3, "To study", len(pending)),
    (m4, "Pending time", f"{remaining_task_minutes} min"),
]

for i, (column, label, value) in enumerate(metrics):
    with column:
        st.markdown(
            f"""
            <div class="metric-card" style="--d:{i * 0.08:.2f}s">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")

if tasks:
    st.markdown("### Your progress")
    st.progress(
        completion_rate,
        text=f"{completed_count} of {len(tasks)} tasks completed · {completion_rate:.0%}",
    )

st.divider()


# ---------------------- ALEXA+ ASSISTANT ------------------

st.markdown("## Ask Alexa+")
st.markdown(
    '<div class="section-note">A simulated Alexa+ conversation that uses the same planner '
    'as the dashboard. Try "I have 90 minutes, what should I study?" or '
    '"add Physics 30 minutes hard weak".</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    quick_message = None

    q1, q2, q3 = st.columns(3)

    if q1.button("Plan my day", key="quick_plan", use_container_width=True):
        quick_message = f"I have {int(available_minutes)} minutes, what should I study?"

    if q2.button("My progress", key="quick_progress", use_container_width=True):
        quick_message = "How is my progress?"

    if q3.button("What's pending?", key="quick_pending", use_container_width=True):
        quick_message = "What's pending?"

    for role, message in st.session_state.chat[-8:]:
        with st.chat_message(role, avatar="🔷" if role == "assistant" else None):
            st.markdown(message if role == "assistant" else md_safe(message))

    typed_message = st.chat_input("Ask Alexa+ about your study plan...")

    chat_input_text = quick_message or typed_message
    if chat_input_text:
        handle_chat(chat_input_text, int(available_minutes))
        st.rerun()

st.divider()


# ----------------------- ADD TASK -------------------------

st.markdown("## Build your study list")
st.markdown(
    '<div class="section-note">Add a topic and let StudyPilot help decide what to study first.</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input(
            "Topic or task name",
            placeholder="e.g. DAA — Dynamic Programming",
        )

        col1, col2 = st.columns(2)

        with col1:
            duration = st.number_input(
                "Estimated duration (minutes)",
                min_value=5,
                max_value=300,
                value=30,
                step=5,
            )

        with col2:
            difficulty = st.selectbox(
                "Difficulty",
                ["Easy", "Medium", "Hard"],
                index=1,
            )

        weak_topic = st.checkbox("This is a weak topic for me")

        submitted = st.form_submit_button(
            "Add study task",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not task_name.strip():
                st.warning("Please enter a topic name first.")
            else:
                st.session_state.tasks.append({
                    "id": str(uuid.uuid4()),
                    "name": task_name.strip(),
                    "duration": int(duration),
                    "difficulty": difficulty,
                    "weak": weak_topic,
                    "completed": False,
                })

                if save_tasks():
                    st.toast("Study task added and saved.")
                    st.rerun()


# --------------------- STUDY PLAN -------------------------

st.divider()
st.markdown("## Your recommended plan")
st.markdown(
    '<div class="section-note">Weak topics rank higher, followed by difficulty and estimated duration.</div>',
    unsafe_allow_html=True,
)

# Celebration banner for the task that was just completed
if just_done_id:
    done_task = next((t for t in tasks if t["id"] == just_done_id and t["completed"]), None)
    if done_task:
        st.markdown(
            f"""
            <div class="done-banner">
                {check_badge(done=True, fresh=True)}
                <span class="burst"><i></i><i></i><i></i><i></i><i></i><i></i></span>
                <div>Nice work — <b>{html.escape(done_task["name"])}</b> completed.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Red banner for the task that was just moved back to pending
if just_undone_id:
    undone_task = next((t for t in tasks if t["id"] == just_undone_id and not t["completed"]), None)
    if undone_task:
        st.markdown(
            f"""
            <div class="done-banner undo-banner">
                {check_badge(fresh=False, undo=True)}
                <span class="burst"><i></i><i></i><i></i><i></i><i></i><i></i></span>
                <div><b>{html.escape(undone_task["name"])}</b> moved back to pending.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

scheduled, skipped, free_minutes = generate_plan(
    st.session_state.tasks,
    int(available_minutes),
)

if not pending:
    st.info("You're all caught up. Add another topic whenever you're ready.")

elif not scheduled:
    st.warning(
        "None of your unfinished tasks fits the available time. "
        "Increase today's time budget or shorten a task."
    )

else:
    planned_minutes = sum(t["duration"] for t in scheduled)

    p1, p2 = st.columns(2)
    p1.metric("Planned study time", f"{planned_minutes} min")
    p2.metric("Free time remaining", f"{free_minutes} min")

    for index, task in enumerate(scheduled, start=1):
        with st.container(border=True, key=f"card_plan_{task['id']}"):
            left, right = st.columns([5, 1])

            with left:
                weak_pill = '<span class="pill pill-weak">Weak topic</span>' if task["weak"] else ""

                st.markdown(
                    f"""
                    <div class="plan-number">SESSION {index:02d}</div>
                    <div class="plan-title">{html.escape(task["name"])}</div>
                    <span class="pill pill-priority">Priority {priority_score(task)}/6</span>{weak_pill}
                    """,
                    unsafe_allow_html=True,
                )

                st.caption(f'{task["duration"]} min · {task["difficulty"]} difficulty')

            with right:
                st.write("")
                st.write("")
                if st.button(
                    "Complete",
                    key=f"plan_done_{task['id']}",
                    type="primary",
                    use_container_width=True,
                ):
                    mark_done(task)
                    if save_tasks():
                        st.rerun()

    st.info(
        f"Your plan fits: {len(scheduled)} tasks scheduled for "
        f"{planned_minutes} minutes."
    )

if skipped:
    with st.expander(f"Other tasks that don't fit ({len(skipped)})"):
        st.caption("These tasks can be included if you have more time.")

        for task in skipped:
            st.write(f"• **{task['name']}** — {task['duration']} min")


# --------------------- TASK MANAGEMENT --------------------

st.divider()
st.markdown("## All your study tasks")

if not st.session_state.tasks:
    st.info("Your study list is empty. Add your first task above.")

else:
    filter_choice = st.radio(
        "Show tasks",
        ["All", "Pending", "Completed"],
        horizontal=True,
        label_visibility="collapsed",
    )

    for task in st.session_state.tasks:
        if filter_choice == "Pending" and task["completed"]:
            continue
        if filter_choice == "Completed" and not task["completed"]:
            continue

        is_fresh = task["completed"] and task["id"] == just_done_id
        is_undo = (not task["completed"]) and task["id"] == just_undone_id
        card_key = f"card_list_{task['id']}"
        if is_fresh:
            card_key += "_fresh_done"
        elif is_undo:
            card_key += "_undo"
        elif task["completed"]:
            card_key += "_done"

        with st.container(border=True, key=card_key):
            left, middle, right = st.columns([5, 1.4, 1])

            with left:
                title_class = "task-title"
                if task["completed"]:
                    title_class += " done"
                if is_fresh:
                    title_class += " fresh"
                if is_undo:
                    title_class += " undo"

                st.markdown(
                    f"""
                    <div class="task-row">
                        {check_badge(done=task["completed"], fresh=is_fresh, undo=is_undo)}
                        <div class="{title_class}"><span class="t">{html.escape(task["name"])}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.caption(
                    f'{task["duration"]} min · {task["difficulty"]} · '
                    f'{"Weak topic" if task["weak"] else "Regular topic"}'
                )

            with middle:
                st.write("")
                if task["completed"]:
                    pill_cls = "pill pill-done fresh" if is_fresh else "pill pill-done"
                    st.markdown(f'<span class="{pill_cls}">Completed</span>', unsafe_allow_html=True)
                else:
                    pend_cls = "pill pill-pending undo" if is_undo else "pill pill-pending"
                    st.markdown(f'<span class="{pend_cls}">Pending</span>', unsafe_allow_html=True)

            with right:
                button_label = "Undo" if task["completed"] else "Done"

                if st.button(
                    button_label,
                    key=f"toggle_{task['id']}",
                    use_container_width=True,
                ):
                    if task["completed"]:
                        mark_undone(task)
                    else:
                        mark_done(task)

                    if save_tasks():
                        st.rerun()

    st.write("")

    with st.expander("Manage your study list"):
        st.warning("Clearing the list permanently deletes all its saved tasks.")

        if not st.session_state.confirm_clear:
            if st.button("Clear all tasks", type="secondary"):
                st.session_state.confirm_clear = True
                st.rerun()
        else:
            st.write("Are you sure you want to delete every task?")
            yes, no = st.columns(2)

            with yes:
                if st.button("Yes, delete all", type="primary"):
                    old_tasks = st.session_state.tasks
                    st.session_state.tasks = []

                    if save_tasks():
                        st.session_state.confirm_clear = False
                        st.session_state.just_done = None
                        st.session_state.just_undone = None
                        st.rerun()
                    else:
                        st.session_state.tasks = old_tasks

            with no:
                if st.button("Cancel"):
                    st.session_state.confirm_clear = False
                    st.rerun()


# ------------------------- FOOTER -------------------------

st.markdown("""
<div class="footer">
    STUDYPILOT · PLAN SMARTER. LEARN BETTER. · LOCAL DATA STORAGE
</div>
""", unsafe_allow_html=True)

# Animations play once: clear the flags so later reruns don't replay them
st.session_state.just_done = None
st.session_state.just_undone = None