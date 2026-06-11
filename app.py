import streamlit as st
import json
import time
from gemini_helper import (
    generate_all_content,
    generate_hooks,
    generate_series,
    generate_scores,
    generate_carousel,
    generate_youtube_script,
    generate_twitter_thread,
    repurpose_content,
    check_api_status
)

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="ReelMind AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================
# INITIALIZE SESSION STATE
# =====================================

if "history" not in st.session_state:
    st.session_state.history = []
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_scores" not in st.session_state:
    st.session_state.last_scores = None
if "last_meta" not in st.session_state:
    st.session_state.last_meta = {}
if "gen_count" not in st.session_state:
    st.session_state.gen_count = 0

# =====================================
# PREMIUM CSS + JS EFFECTS
# =====================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:       #050508;
  --bg2:      #0b0b12;
  --bg3:      #111120;
  --surface:  #13131f;
  --border:   rgba(255,255,255,0.06);
  --border2:  rgba(255,255,255,0.12);
  --text:     #e8e6f0;
  --muted:    #6b6882;
  --dim:      #2a2840;
  --accent:   #7c5cfc;
  --accent2:  #c94fff;
  --fire:     #ff4b2b;
  --cyan:     #00e5ff;
  --gold:     #ffd166;
  --green:    #06ffa5;
  --glow1: rgba(124,92,252,0.15);
  --glow2: rgba(201,79,255,0.12);
  --glow3: rgba(0,229,255,0.10);
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

[data-testid="stAppViewContainer"] > .main {
    background: var(--bg) !important;
}

[data-testid="stHeader"] { background: transparent !important; display: none; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── AURORA BACKGROUND ── */
#aurora-bg {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.aurora-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    animation: auroraDrift linear infinite;
    opacity: 0.35;
}

.aurora-orb:nth-child(1) {
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(124,92,252,0.6), transparent 70%);
    top: -200px; left: -100px;
    animation-duration: 20s;
}
.aurora-orb:nth-child(2) {
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(201,79,255,0.5), transparent 70%);
    top: 30%; right: -150px;
    animation-duration: 25s;
    animation-delay: -8s;
}
.aurora-orb:nth-child(3) {
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(0,229,255,0.4), transparent 70%);
    bottom: -100px; left: 40%;
    animation-duration: 18s;
    animation-delay: -4s;
}
.aurora-orb:nth-child(4) {
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,75,43,0.3), transparent 70%);
    top: 60%; left: 20%;
    animation-duration: 22s;
    animation-delay: -12s;
}

@keyframes auroraDrift {
    0%   { transform: translate(0, 0) scale(1); }
    25%  { transform: translate(60px, -40px) scale(1.08); }
    50%  { transform: translate(30px, 70px) scale(0.95); }
    75%  { transform: translate(-50px, 30px) scale(1.05); }
    100% { transform: translate(0, 0) scale(1); }
}

/* ── NEURAL NETWORK CANVAS ── */
#neural-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 1;
    opacity: 0.35;
}

/* ── CURSOR GLOW ── */
#cursor-glow {
    position: fixed;
    pointer-events: none;
    z-index: 9999;
    width: 300px; height: 300px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(124,92,252,0.12) 0%, transparent 70%);
    transform: translate(-50%, -50%);
    transition: transform 0.1s ease;
    top: -999px; left: -999px;
}

#cursor-dot {
    position: fixed;
    pointer-events: none;
    z-index: 10000;
    width: 8px; height: 8px;
    background: var(--accent);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    top: -999px; left: -999px;
    box-shadow: 0 0 12px var(--accent), 0 0 24px var(--accent2);
    transition: width 0.2s, height 0.2s, background 0.2s;
}

/* ── CONTENT WRAPPER ── */
.rm-wrapper {
    position: relative;
    z-index: 10;
}

/* ── HERO ── */
.rm-hero {
    padding: 48px 60px 40px;
    border-bottom: 1px solid var(--border);
    position: relative;
    overflow: hidden;
}

.rm-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(124,92,252,0.12);
    border: 1px solid rgba(124,92,252,0.3);
    padding: 6px 14px;
    border-radius: 100px;
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 20px;
}

.rm-badge-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: pulse 2s ease infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.5; transform: scale(0.7); }
}

.rm-logo {
    font-family: 'Syne', sans-serif;
    font-size: clamp(44px, 5.5vw, 80px);
    font-weight: 800;
    line-height: 0.95;
    letter-spacing: -3px;
    color: var(--text);
    margin-bottom: 16px;
    position: relative;
    display: inline-block;
}

.rm-logo .acc { 
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 20px rgba(124,92,252,0.5));
}

.rm-logo-glow {
    position: absolute;
    top: 50%; left: -20px;
    transform: translateY(-50%);
    width: 120%; height: 150%;
    background: radial-gradient(ellipse, rgba(124,92,252,0.15) 0%, transparent 70%);
    pointer-events: none;
    z-index: -1;
}

.rm-sub {
    font-size: 14px;
    color: var(--muted);
    font-weight: 300;
    max-width: 460px;
    line-height: 1.7;
    margin-bottom: 28px;
}

.rm-stats {
    display: flex;
    gap: 0;
    border: 1px solid var(--border);
    display: inline-flex;
}

.rm-stat {
    padding: 12px 24px;
    border-right: 1px solid var(--border);
    text-align: center;
}

.rm-stat:last-child { border-right: none; }

.rm-stat-num {
    font-family: 'Space Mono', monospace;
    font-size: 20px;
    font-weight: 700;
    color: var(--text);
    display: block;
}

.rm-stat-label {
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    display: block;
    margin-top: 2px;
}

/* ── API STATUS ── */
.api-status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    color: var(--muted);
    margin-left: 20px;
}

.api-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
}

.api-dot.online { background: var(--green); box-shadow: 0 0 8px var(--green); }
.api-dot.offline { background: var(--fire); box-shadow: 0 0 8px var(--fire); }

/* ── STREAMLIT OVERRIDES ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 14px !important;
    padding: 14px 16px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    backdrop-filter: blur(10px) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124,92,252,0.15), 0 0 20px rgba(124,92,252,0.1) !important;
    outline: none !important;
}

.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: var(--dim) !important;
}

[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
    backdrop-filter: blur(10px) !important;
    color: var(--text) !important;
}

[data-baseweb="popover"], [data-baseweb="menu"] {
    background: #14141f !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
}

[data-baseweb="option"] {
    background: transparent !important;
    color: var(--text) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

[data-baseweb="option"]:hover { background: rgba(124,92,252,0.12) !important; }

label, .stSelectbox label, .stTextInput label, .stTextArea label {
    color: var(--muted) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* ── GENERATE BUTTON ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    padding: 16px 32px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.3s !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow: 0 4px 24px rgba(124,92,252,0.3), 0 0 40px rgba(124,92,252,0.15) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 40px rgba(124,92,252,0.5), 0 0 60px rgba(201,79,255,0.2) !important;
    filter: brightness(1.1) !important;
}

.stButton > button:active {
    transform: scale(0.98) !important;
}

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {
    background: transparent !important;
    color: var(--muted) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
}

.stDownloadButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    box-shadow: 0 0 16px rgba(124,92,252,0.2) !important;
    background: rgba(124,92,252,0.06) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 12px 20px !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s !important;
}

.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
    text-shadow: 0 0 16px rgba(124,92,252,0.6) !important;
}

.stTabs [data-baseweb="tab-panel"] {
    padding: 0 !important;
    background: transparent !important;
}

/* ── GLASS OUTPUT CARD ── */
.rm-glass-card {
    background: rgba(19,19,31,0.7);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid var(--border2);
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    transition: all 0.35s ease;
}

.rm-glass-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(124,92,252,0.08) 0%, transparent 60%);
    pointer-events: none;
}

.rm-glass-card:hover {
    border-color: rgba(124,92,252,0.4);
    box-shadow: 0 8px 48px rgba(124,92,252,0.15), 0 0 0 1px rgba(124,92,252,0.1);
    transform: translateY(-2px);
}

/* ── ELECTRIC BORDER (active panel) ── */
@keyframes electricFlow {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.rm-electric {
    position: relative;
}

.rm-electric::after {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 18px;
    background: linear-gradient(90deg, var(--accent), var(--accent2), var(--cyan), var(--accent));
    background-size: 300% 300%;
    animation: electricFlow 3s ease infinite;
    z-index: -1;
    opacity: 0.6;
}

/* ── CARD LABEL ── */
.rm-card-label {
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.rm-card-label::before {
    content: '';
    width: 16px; height: 1px;
    background: var(--accent);
    display: inline-block;
}

.rm-card-body {
    font-size: 13px;
    line-height: 1.85;
    color: #9994bb;
    white-space: pre-wrap;
    font-family: 'Space Grotesk', sans-serif;
}

/* ── COPY BUTTON ── */
.copy-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(124,92,252,0.08);
    border: 1px solid rgba(124,92,252,0.2);
    border-radius: 6px;
    padding: 6px 14px;
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--accent);
    cursor: pointer;
    transition: all 0.2s;
    margin-top: 16px;
    margin-right: 8px;
}

.copy-btn:hover {
    background: rgba(124,92,252,0.16);
    border-color: rgba(124,92,252,0.4);
    box-shadow: 0 0 16px rgba(124,92,252,0.2);
}

/* ── SCORE METER ── */
.score-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-top: 8px;
}

.score-item {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    transition: all 0.3s;
}

.score-item:hover {
    border-color: var(--border2);
    background: rgba(124,92,252,0.06);
}

.score-label {
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
    display: block;
}

.score-bar-wrap {
    background: rgba(255,255,255,0.04);
    border-radius: 100px;
    height: 4px;
    margin-bottom: 6px;
    overflow: hidden;
}

.score-bar {
    height: 4px;
    border-radius: 100px;
    transition: width 1.2s cubic-bezier(0.23,1,0.32,1);
}

.score-val {
    font-family: 'Space Mono', monospace;
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
}

.score-val span {
    font-size: 10px;
    color: var(--muted);
}

/* Score color helpers */
.s-purple { background: linear-gradient(90deg, var(--accent), var(--accent2)); }
.s-cyan   { background: linear-gradient(90deg, var(--cyan), var(--accent)); }
.s-fire   { background: linear-gradient(90deg, var(--fire), var(--gold)); }
.s-green  { background: linear-gradient(90deg, var(--green), var(--cyan)); }

/* ── PROGRESS STEPS ── */
.gen-progress {
    padding: 20px 0;
}

.gen-step {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--dim);
    transition: all 0.3s;
}

.gen-step.active {
    color: var(--accent);
}

.gen-step.done {
    color: var(--green);
}

.gen-step-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--dim);
    flex-shrink: 0;
    transition: all 0.3s;
}

.gen-step.active .gen-step-dot {
    background: var(--accent);
    box-shadow: 0 0 12px var(--accent);
    animation: pulse 1s ease infinite;
}

.gen-step.done .gen-step-dot {
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
}

/* ── VIRAL VERDICT ── */
.viral-verdict {
    background: linear-gradient(135deg, rgba(124,92,252,0.1), rgba(201,79,255,0.06));
    border: 1px solid rgba(124,92,252,0.25);
    border-radius: 12px;
    padding: 20px 24px;
    margin: 16px 0;
    position: relative;
    overflow: hidden;
}

.viral-verdict::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), var(--accent2), transparent);
}

.viral-verdict-label {
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 8px;
}

.viral-verdict-text {
    font-size: 15px;
    font-weight: 600;
    color: var(--text);
    line-height: 1.5;
}

.viral-tip {
    font-size: 12px;
    color: var(--muted);
    margin-top: 8px;
}

/* ── SECTION DIVIDER ── */
.rm-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border2), transparent);
    margin: 32px 0;
}

/* ── HISTORY ITEM ── */
.history-item {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.history-item:hover {
    border-color: var(--border2);
    background: rgba(124,92,252,0.05);
}

.history-topic {
    font-size: 13px;
    font-weight: 500;
    color: var(--text);
}

.history-meta {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: var(--muted);
    margin-top: 4px;
    letter-spacing: 1px;
}

/* ── WORD COUNT BADGE ── */
.wc-badge {
    display: inline-block;
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 3px 10px;
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 1px;
    color: var(--muted);
    margin-left: 8px;
}

/* ── POST TIME ── */
.post-time {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(6,255,165,0.06);
    border: 1px solid rgba(6,255,165,0.2);
    border-radius: 8px;
    padding: 10px 16px;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 1px;
    color: var(--green);
    margin-top: 12px;
}

/* ── SKELETON LOADER ── */
.skeleton {
    background: linear-gradient(90deg, var(--surface) 25%, var(--bg3) 50%, var(--surface) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 6px;
    height: 14px;
    margin-bottom: 10px;
}

.skeleton.wide { width: 100%; }
.skeleton.mid  { width: 75%; }
.skeleton.short { width: 45%; }
.skeleton.tall  { height: 120px; }

@keyframes shimmer {
    0%   { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 2px !important;
}

.streamlit-expanderContent {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}

/* ── SUCCESS / WARNING / ERROR ── */
.stSuccess {
    background: rgba(6,255,165,0.06) !important;
    border: 1px solid rgba(6,255,165,0.2) !important;
    border-radius: 8px !important;
}

.stWarning {
    background: rgba(255,209,102,0.06) !important;
    border: 1px solid rgba(255,209,102,0.2) !important;
    border-radius: 8px !important;
}

.stSpinner > div {
    border-top-color: var(--accent) !important;
}

/* ── RADIO ── */
.stRadio > div {
    gap: 8px !important;
}

.stRadio > div > label {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--border) !important;
    padding: 10px 18px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    color: var(--muted) !important;
    font-size: 12px !important;
}

.stRadio > div > label:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(124,92,252,0.06) !important;
}

/* ── METRIC ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 16px !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 8px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Space Mono', monospace !important;
    color: var(--text) !important;
    font-size: 24px !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--dim); border-radius: 100px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── FOOTER ── */
.rm-footer {
    padding: 20px 60px;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}

.rm-footer-text {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    color: var(--dim);
}

/* ── PARTICLE CANVAS ── */
#particle-canvas {
    position: fixed;
    pointer-events: none;
    z-index: 9998;
    top: 0; left: 0;
    width: 100%; height: 100%;
}

/* ── MOBILE ── */
@media (max-width: 768px) {
    .rm-hero { padding: 28px 20px 24px; }
    .rm-stats { flex-wrap: wrap; }
    .rm-stat { padding: 10px 16px; }
    .score-grid { grid-template-columns: 1fr; }
    .rm-footer { padding: 16px 20px; flex-direction: column; text-align: center; }
}

/* Ensure content is above background layers */
section[data-testid="stSidebar"] { z-index: 100; }
.main .block-container { position: relative; z-index: 10; }

</style>

<!-- Aurora + Neural + Cursor layers -->
<div id="aurora-bg">
  <div class="aurora-orb"></div>
  <div class="aurora-orb"></div>
  <div class="aurora-orb"></div>
  <div class="aurora-orb"></div>
</div>
<canvas id="neural-canvas"></canvas>
<canvas id="particle-canvas"></canvas>
<div id="cursor-glow"></div>
<div id="cursor-dot"></div>

<script>
// ── CURSOR EFFECTS ──
(function() {
    const glow = document.getElementById('cursor-glow');
    const dot  = document.getElementById('cursor-dot');
    let mx = -999, my = -999;
    let gx = -999, gy = -999;

    document.addEventListener('mousemove', e => {
        mx = e.clientX; my = e.clientY;
        dot.style.left = mx + 'px';
        dot.style.top  = my + 'px';
    });

    function lerpCursor() {
        gx += (mx - gx) * 0.06;
        gy += (my - gy) * 0.06;
        glow.style.left = gx + 'px';
        glow.style.top  = gy + 'px';
        requestAnimationFrame(lerpCursor);
    }
    lerpCursor();

    // Magnetic button effect
    document.addEventListener('mouseover', e => {
        const btn = e.target.closest('button');
        if (btn) {
            dot.style.width = '40px';
            dot.style.height = '40px';
            dot.style.background = 'rgba(124,92,252,0.3)';
        }
    });
    document.addEventListener('mouseout', e => {
        const btn = e.target.closest('button');
        if (btn) {
            dot.style.width = '8px';
            dot.style.height = '8px';
            dot.style.background = '';
        }
    });
})();

// ── NEURAL NETWORK ANIMATION ──
(function() {
    const canvas = document.getElementById('neural-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    const nodes = Array.from({length: 55}, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35,
        r: Math.random() * 2 + 1
    }));

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Connections
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const dx = nodes[i].x - nodes[j].x;
                const dy = nodes[i].y - nodes[j].y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 160) {
                    ctx.beginPath();
                    ctx.moveTo(nodes[i].x, nodes[i].y);
                    ctx.lineTo(nodes[j].x, nodes[j].y);
                    const alpha = (1 - dist / 160) * 0.18;
                    ctx.strokeStyle = `rgba(124,92,252,${alpha})`;
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        }

        // Nodes
        nodes.forEach(n => {
            ctx.beginPath();
            ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(124,92,252,0.5)';
            ctx.fill();
            // Glow
            ctx.beginPath();
            ctx.arc(n.x, n.y, n.r + 3, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(124,92,252,0.08)';
            ctx.fill();
            
            n.x += n.vx;
            n.y += n.vy;
            if (n.x < 0 || n.x > canvas.width)  n.vx *= -1;
            if (n.y < 0 || n.y > canvas.height) n.vy *= -1;
        });
        
        requestAnimationFrame(draw);
    }
    draw();
})();

// ── PARTICLE EXPLOSION ON CLICK ──
(function() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });

    let particles = [];
    const COLORS = ['#7c5cfc','#c94fff','#00e5ff','#ffd166','#06ffa5','#ff4b2b'];

    window.burstParticles = function(x, y) {
        for (let i = 0; i < 60; i++) {
            const angle = (Math.PI * 2 / 60) * i + Math.random() * 0.3;
            const speed = 3 + Math.random() * 8;
            particles.push({
                x, y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                r: 2 + Math.random() * 4,
                color: COLORS[Math.floor(Math.random() * COLORS.length)],
                alpha: 1,
                decay: 0.015 + Math.random() * 0.02
            });
        }
    };

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles = particles.filter(p => p.alpha > 0);
        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.12; // gravity
            p.alpha -= p.decay;
            p.vx *= 0.98;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.alpha;
            ctx.shadowBlur = 10;
            ctx.shadowColor = p.color;
            ctx.fill();
            ctx.globalAlpha = 1;
            ctx.shadowBlur = 0;
        });
        requestAnimationFrame(animate);
    }
    animate();

    // Attach to generate button clicks
    document.addEventListener('click', e => {
        const btn = e.target.closest('button');
        if (btn && (btn.innerText.includes('GENERATE') || btn.innerText.includes('GET HOOKS') || btn.innerText.includes('BUILD') || btn.innerText.includes('CREATE'))) {
            const rect = btn.getBoundingClientRect();
            window.burstParticles(rect.left + rect.width/2, rect.top + rect.height/2);
        }
    });
})();

// ── 3D CARD TILT ──
(function() {
    function applyTilt() {
        document.querySelectorAll('.rm-glass-card').forEach(card => {
            if (card._tiltSet) return;
            card._tiltSet = true;
            card.addEventListener('mousemove', e => {
                const rect = card.getBoundingClientRect();
                const x = (e.clientX - rect.left) / rect.width  - 0.5;
                const y = (e.clientY - rect.top)  / rect.height - 0.5;
                card.style.transform = `perspective(800px) rotateY(${x * 6}deg) rotateX(${y * -6}deg) translateY(-2px)`;
                card.style.transition = 'transform 0.1s ease';
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(800px) rotateY(0deg) rotateX(0deg) translateY(0)';
                card.style.transition = 'transform 0.5s ease';
            });
        });
    }
    // Re-run periodically to catch dynamically rendered cards
    setInterval(applyTilt, 1000);
})();

// ── ANIMATED NUMBER COUNTER ──
window.animateCount = function(el, target, duration) {
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
        start = Math.min(start + step, target);
        el.textContent = Math.round(start);
        if (start >= target) clearInterval(timer);
    }, 16);
};

// ── PARALLAX on scroll/mouse ──
(function() {
    document.addEventListener('mousemove', e => {
        const x = (e.clientX / window.innerWidth  - 0.5) * 20;
        const y = (e.clientY / window.innerHeight - 0.5) * 20;
        const logo = document.querySelector('.rm-logo');
        if (logo) logo.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
        const orbs = document.querySelectorAll('.aurora-orb');
        orbs.forEach((o, i) => {
            const f = (i + 1) * 0.04;
            o.style.transform += ` translate(${x * f}px, ${y * f}px)`;
        });
    });
})();
</script>
""", unsafe_allow_html=True)

# =====================================
# HERO
# =====================================

st.markdown("""
<div class="rm-wrapper">
<div class="rm-hero">
    <div class="rm-badge">
        <span class="rm-badge-dot"></span>
        AI Content Engine — v4.0
    </div>
    <div class="rm-logo">
        Reel<span class="acc">Mind</span> AI
        <div class="rm-logo-glow"></div>
    </div>
    <div class="rm-sub">
        Generate scroll-stopping captions, hashtag stacks, viral scripts,
        and thumbnail prompts — powered by Gemini 2.5 Flash.
    </div>
    <div class="rm-stats">
        <div class="rm-stat">
            <span class="rm-stat-num">4+</span>
            <span class="rm-stat-label">Output types</span>
        </div>
        <div class="rm-stat">
            <span class="rm-stat-num">30</span>
            <span class="rm-stat-label">Hashtags</span>
        </div>
        <div class="rm-stat">
            <span class="rm-stat-num">8</span>
            <span class="rm-stat-label">AI Scores</span>
        </div>
        <div class="rm-stat">
            <span class="rm-stat-num">∞</span>
            <span class="rm-stat-label">Niches</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================
# MODE SELECTOR
# =====================================

st.markdown("<div style='padding: 20px 60px 0;'>", unsafe_allow_html=True)

mode = st.radio(
    "",
    ["Full Content Pack", "Hook Ideas", "Content Series", "Carousel Post", "YouTube Script", "X/Twitter Thread", "Repurpose Content"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("</div>", unsafe_allow_html=True)

# =====================================
# MAIN LAYOUT
# =====================================

st.markdown("<div style='padding: 32px 60px;'>", unsafe_allow_html=True)

col_in, col_out = st.columns([1, 1.9], gap="large")

# ── INPUT PANEL ──
with col_in:
    topic = st.text_input(
        "Topic",
        placeholder="e.g. Super Villain Arc, Morning Routine...",
        key="topic_input"
    )

    niche = st.selectbox("Niche", [
        "Dark Aesthetic / Motivation",
        "Gaming", "Anime & Manga", "Fitness & Gym", "Tech & AI",
        "Finance & Investing", "Horror & Thriller", "Fashion & Lifestyle",
        "Education", "Movie Industry", "Music & Artists",
        "Business & Entrepreneurship", "Luxury & Wealth", "Cars & Automotive",
        "Travel & Adventure", "Food & Cooking"
    ])

    platform = st.selectbox("Platform", [
        "Instagram Reels", "TikTok", "YouTube Shorts"
    ])

    tone = st.selectbox("Tone", [
        "Viral & Bold", "Dark & Cinematic", "Motivational & Intense",
        "Minimal & Clean", "Edgy & Controversial", "Informative & Professional"
    ])

    if mode == "Content Series":
        num_posts = st.selectbox("Posts in Series", [3, 5, 7, 10])
    if mode == "Carousel Post":
        num_slides = st.selectbox("Number of Slides", [5, 7, 10])
    if mode == "YouTube Script":
        yt_duration = st.selectbox("Video Duration", [3, 5, 8, 10, 15])
    if mode == "X/Twitter Thread":
        tweet_count = st.selectbox("Number of Tweets", [5, 7, 10, 12])
    if mode == "Repurpose Content":
        original_content = st.text_area("Paste Your Original Content", height=120, placeholder="Paste your existing caption, script, or post here...")
        original_platform = st.selectbox("Original Platform", ["Instagram Reels", "TikTok", "YouTube Shorts", "X/Twitter", "LinkedIn"])
        target_platform = st.selectbox("Repurpose To", ["TikTok", "Instagram Reels", "YouTube Shorts", "X/Twitter", "LinkedIn"])

    generate_btn = st.button("→ GENERATE" if mode == "Full Content Pack"
        else "→ GET HOOKS"   if mode == "Hook Ideas"
        else "→ BUILD SERIES" if mode == "Content Series"
        else "→ CREATE CAROUSEL" if mode == "Carousel Post"
        else "→ WRITE SCRIPT" if mode == "YouTube Script"
        else "→ WRITE THREAD" if mode == "X/Twitter Thread"
        else "→ REPURPOSE")

    with st.expander("QUICK TIPS"):
        st.markdown("""
<div style='font-family: Space Grotesk, sans-serif; font-size: 12px; color: #6b6882; line-height: 1.8;'>
→ Specific topics outperform generic ones<br>
→ <strong style='color: #9994bb;'>"Villain arc workout" &gt; "gym"</strong><br>
→ Match tone to your existing content style<br>
→ Use Hook Ideas to A/B test your openings<br>
→ Build a Series for consistent daily posting
</div>""", unsafe_allow_html=True)

    # Generation history
    if st.session_state.history:
        st.markdown("<div style='margin-top: 24px;'>", unsafe_allow_html=True)
        st.markdown('<div style="font-family: Space Mono, monospace; font-size: 8px; letter-spacing: 3px; color: #2a2840; text-transform: uppercase; margin-bottom: 12px;">Recent</div>', unsafe_allow_html=True)
        for h in st.session_state.history[-4:][::-1]:
            st.markdown(f"""
<div class="history-item">
  <div class="history-topic">{h['topic']}</div>
  <div class="history-meta">{h['niche']} · {h['platform']}</div>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ── OUTPUT PANEL ──
with col_out:

    if generate_btn:
        if not topic.strip() and mode != "Repurpose Content":
            st.warning("Please enter a topic first.")
        elif mode == "Repurpose Content" and not original_content.strip():
            st.warning("Please paste your original content.")
        else:
            # Add to history
            if topic.strip():
                st.session_state.history.append({
                    "topic": topic, "niche": niche, "platform": platform
                })
                st.session_state.gen_count += 1

            # ── FULL CONTENT PACK ──
            if mode == "Full Content Pack":
                progress_placeholder = st.empty()

                steps = [
                    "Analyzing topic...",
                    "Building captions...",
                    "Generating hashtags...",
                    "Creating script...",
                    "Designing thumbnail...",
                    "Computing viral scores..."
                ]

                def show_progress(done_steps, active_idx):
                    html = '<div class="gen-progress">'
                    for i, s in enumerate(steps):
                        cls = "done" if i < done_steps else ("active" if i == active_idx else "")
                        icon = "✓ " if i < done_steps else ""
                        html += f'<div class="gen-step {cls}"><div class="gen-step-dot"></div>{icon}{s.upper()}</div>'
                    html += '</div>'
                    progress_placeholder.markdown(html, unsafe_allow_html=True)

                show_progress(0, 0)
                time.sleep(0.4)
                show_progress(1, 1)

                result = generate_all_content(topic, niche, platform, tone)

                show_progress(4, 4)
                time.sleep(0.3)

                scores = generate_scores(topic, niche, platform, tone)
                st.session_state.last_result = result
                st.session_state.last_scores = scores
                st.session_state.last_meta = {"topic": topic, "niche": niche, "platform": platform, "tone": tone}

                show_progress(6, 5)
                time.sleep(0.3)
                progress_placeholder.empty()

                if "ERROR" in result.get("raw", "") or not result["captions"]:
                    st.error(result.get("raw", "Generation failed. Try again."))
                else:
                    st.markdown('<div style="font-family: Space Mono, monospace; font-size: 9px; letter-spacing: 3px; color: #06ffa5; margin-bottom: 20px;">✓ CONTENT READY</div>', unsafe_allow_html=True)

                    # ── VIRAL SCORES ──
                    if scores:
                        st.markdown(f"""
<div class="viral-verdict">
  <div class="viral-verdict-label">AI Verdict</div>
  <div class="viral-verdict-text">{scores.get('viral_verdict','')}</div>
  <div class="viral-tip">💡 {scores.get('top_tip','')}</div>
</div>""", unsafe_allow_html=True)

                        score_colors = ["s-purple","s-cyan","s-fire","s-green","s-purple","s-cyan","s-fire","s-green"]
                        score_keys = [
                            ("viral_potential",   "Viral Potential"),
                            ("hook_strength",     "Hook Strength"),
                            ("shareability",      "Shareability"),
                            ("engagement_rate",   "Engagement Rate"),
                            ("retention_score",   "Retention Score"),
                            ("trend_compatibility","Trend Match"),
                            ("audience_match",    "Audience Match"),
                            ("niche_saturation",  "Niche Space"),
                        ]

                        score_html = '<div class="score-grid">'
                        for i, (k, lbl) in enumerate(score_keys):
                            val = scores.get(k, 80)
                            col_cls = score_colors[i % len(score_colors)]
                            score_html += f"""
<div class="score-item">
  <span class="score-label">{lbl}</span>
  <div class="score-bar-wrap"><div class="score-bar {col_cls}" style="width:{val}%"></div></div>
  <span class="score-val">{val}<span>/100</span></span>
</div>"""
                        score_html += '</div>'

                        best_time = scores.get("best_post_time", "—")
                        score_html += f'<div class="post-time">⏰ Best Post Time: {best_time}</div>'

                        st.markdown(score_html, unsafe_allow_html=True)

                        st.markdown('<div class="rm-divider"></div>', unsafe_allow_html=True)

                    # ── TABS ──
                    tab1, tab2, tab3, tab4 = st.tabs(["CAPTIONS", "HASHTAGS", "SCRIPT", "THUMBNAIL"])

                    with tab1:
                        wc = len(result['captions'].split())
                        st.markdown(f"""
<div class="rm-glass-card rm-electric">
  <div class="rm-card-label">Caption Stack <span class="wc-badge">{wc} words</span></div>
  <div class="rm-card-body">{result['captions']}</div>
</div>""", unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        with c1:
                            st.download_button("↓ DOWNLOAD", result["captions"],
                                file_name=f"captions_{topic[:20].replace(' ','_')}.txt", mime="text/plain", key="dl_cap")
                        with c2:
                            st.code(result["captions"][:200] + "...", language=None)

                    with tab2:
                        ht_count = result['hashtags'].count('#')
                        st.markdown(f"""
<div class="rm-glass-card">
  <div class="rm-card-label">Hashtag Stack — {ht_count} tags</div>
  <div class="rm-card-body">{result['hashtags']}</div>
</div>""", unsafe_allow_html=True)
                        st.download_button("↓ DOWNLOAD HASHTAGS", result["hashtags"],
                            file_name=f"hashtags_{topic[:20].replace(' ','_')}.txt", mime="text/plain", key="dl_ht")

                    with tab3:
                        st.markdown(f"""
<div class="rm-glass-card">
  <div class="rm-card-label">Reel Script — 30 Seconds</div>
  <div class="rm-card-body">{result['script']}</div>
</div>""", unsafe_allow_html=True)
                        st.download_button("↓ DOWNLOAD SCRIPT", result["script"],
                            file_name=f"script_{topic[:20].replace(' ','_')}.txt", mime="text/plain", key="dl_sc")

                    with tab4:
                        st.markdown(f"""
<div class="rm-glass-card">
  <div class="rm-card-label">Thumbnail Prompt — Multi-Platform</div>
  <div class="rm-card-body">{result['thumbnail']}</div>
</div>""", unsafe_allow_html=True)
                        st.download_button("↓ DOWNLOAD PROMPT", result["thumbnail"],
                            file_name=f"thumbnail_{topic[:20].replace(' ','_')}.txt", mime="text/plain", key="dl_th")

                    # Full pack
                    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                    full = f"""REELMIND AI — FULL CONTENT PACK
Topic: {topic} | Niche: {niche} | Platform: {platform} | Tone: {tone}
{'='*60}

CAPTIONS
{'='*60}
{result['captions']}

HASHTAGS
{'='*60}
{result['hashtags']}

SCRIPT
{'='*60}
{result['script']}

THUMBNAIL PROMPT
{'='*60}
{result['thumbnail']}

AI SCORES
{'='*60}
{json.dumps(scores, indent=2) if scores else 'N/A'}
"""
                    st.download_button("↓ DOWNLOAD FULL PACK", full,
                        file_name=f"reelmind_{topic[:20].replace(' ','_')}_full.txt", mime="text/plain", key="dl_all")

            # ── HOOK IDEAS ──
            elif mode == "Hook Ideas":
                with st.spinner(""):
                    hooks = generate_hooks(topic, niche)
                if hooks and "ERROR" not in hooks:
                    st.markdown(f"""
<div class="rm-glass-card rm-electric">
  <div class="rm-card-label">5 Hook Variations — {topic}</div>
  <div class="rm-card-body">{hooks}</div>
</div>""", unsafe_allow_html=True)
                    st.download_button("↓ DOWNLOAD HOOKS", hooks,
                        file_name=f"hooks_{topic[:20].replace(' ','_')}.txt", mime="text/plain")
                else:
                    st.error(hooks or "Generation failed.")

            # ── CONTENT SERIES ──
            elif mode == "Content Series":
                with st.spinner(""):
                    series = generate_series(topic, niche, platform, num_posts)
                if series and "ERROR" not in series:
                    st.markdown(f"""
<div class="rm-glass-card rm-electric">
  <div class="rm-card-label">{num_posts}-Post Content Series — {topic}</div>
  <div class="rm-card-body">{series}</div>
</div>""", unsafe_allow_html=True)
                    st.download_button("↓ DOWNLOAD SERIES", series,
                        file_name=f"series_{topic[:20].replace(' ','_')}.txt", mime="text/plain")
                else:
                    st.error(series or "Generation failed.")

            # ── CAROUSEL ──
            elif mode == "Carousel Post":
                with st.spinner(""):
                    carousel = generate_carousel(topic, niche, num_slides)
                if carousel and "ERROR" not in carousel:
                    st.markdown(f"""
<div class="rm-glass-card rm-electric">
  <div class="rm-card-label">{num_slides}-Slide Carousel — {topic}</div>
  <div class="rm-card-body">{carousel}</div>
</div>""", unsafe_allow_html=True)
                    st.download_button("↓ DOWNLOAD CAROUSEL", carousel,
                        file_name=f"carousel_{topic[:20].replace(' ','_')}.txt", mime="text/plain")
                else:
                    st.error(carousel or "Generation failed.")

            # ── YOUTUBE SCRIPT ──
            elif mode == "YouTube Script":
                with st.spinner(""):
                    yt = generate_youtube_script(topic, niche, yt_duration)
                if yt and "ERROR" not in yt:
                    st.markdown(f"""
<div class="rm-glass-card rm-electric">
  <div class="rm-card-label">{yt_duration}-Minute YouTube Script — {topic}</div>
  <div class="rm-card-body">{yt}</div>
</div>""", unsafe_allow_html=True)
                    st.download_button("↓ DOWNLOAD SCRIPT", yt,
                        file_name=f"yt_script_{topic[:20].replace(' ','_')}.txt", mime="text/plain")
                else:
                    st.error(yt or "Generation failed.")

            # ── TWITTER THREAD ──
            elif mode == "X/Twitter Thread":
                with st.spinner(""):
                    thread = generate_twitter_thread(topic, niche, tweet_count)
                if thread and "ERROR" not in thread:
                    st.markdown(f"""
<div class="rm-glass-card rm-electric">
  <div class="rm-card-label">{tweet_count}-Tweet Thread — {topic}</div>
  <div class="rm-card-body">{thread}</div>
</div>""", unsafe_allow_html=True)
                    st.download_button("↓ DOWNLOAD THREAD", thread,
                        file_name=f"thread_{topic[:20].replace(' ','_')}.txt", mime="text/plain")
                else:
                    st.error(thread or "Generation failed.")

            # ── REPURPOSE ──
            elif mode == "Repurpose Content":
                with st.spinner(""):
                    repurposed = repurpose_content(original_content, original_platform, target_platform, niche)
                if repurposed and "ERROR" not in repurposed:
                    st.markdown(f"""
<div class="rm-glass-card rm-electric">
  <div class="rm-card-label">Repurposed for {target_platform}</div>
  <div class="rm-card-body">{repurposed}</div>
</div>""", unsafe_allow_html=True)
                    st.download_button("↓ DOWNLOAD", repurposed,
                        file_name=f"repurposed_{target_platform.replace(' ','_')}.txt", mime="text/plain")
                else:
                    st.error(repurposed or "Generation failed.")

    else:
        # Empty state
        st.markdown("""
<div style="border: 1px dashed rgba(255,255,255,0.06); border-radius: 16px; padding: 80px 40px;
text-align: center; margin-top: 8px; background: rgba(255,255,255,0.01);">
    <div style="font-family: Space Mono, monospace; font-size: 9px; letter-spacing: 3px;
    text-transform: uppercase; color: #2a2840; margin-bottom: 16px;">Awaiting Input</div>
    <div style="font-size: 32px; margin-bottom: 16px; opacity: 0.3;">🎬</div>
    <div style="font-size: 13px; color: #2a2840; line-height: 1.7; font-family: Space Grotesk, sans-serif;">
        Configure your parameters on the left<br>and hit Generate.
    </div>
</div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# =====================================
# FOOTER
# =====================================

st.markdown(f"""
<div class="rm-footer">
    <div class="rm-footer-text">REELMIND AI — v4.0 — POWERED BY GEMINI 2.5 FLASH</div>
    <div class="rm-footer-text">{st.session_state.gen_count} generations this session · BUILT BY SATVIK SHARMA</div>
</div>
</div>
""", unsafe_allow_html=True)