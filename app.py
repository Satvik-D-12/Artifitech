import streamlit as st
import streamlit.components.v1 as components
import random
import time
import datetime
import re
from gemini_helper import (
    generate_full_content, generate_hooks,
    generate_series, generate_carousel,
    generate_thread, repurpose_content,
    generate_video_story, generate_video_full_package
)

# ══════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════
st.set_page_config(
    page_title="ReelMind AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════
for key, default in [
    ("history", []), ("theme", "dark"),
    ("last_result", None), ("last_scores", None),
    ("generated", False), ("page", "home"),
    ("video_stories", None), ("video_package", None),
    ("transition", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════
# THEME
# ══════════════════════════════════════════
IS_DARK = st.session_state.theme == "dark"
T = {
    "bg":      "#080808" if IS_DARK else "#f0ede8",
    "bg2":     "#0f0f0f" if IS_DARK else "#e8e4de",
    "bg3":     "#161616" if IS_DARK else "#dedad3",
    "bg4":     "#1e1e1e" if IS_DARK else "#d0ccc4",
    "rule":    "#1e1e1e" if IS_DARK else "#ccc8bf",
    "rule2":   "#2a2a2a" if IS_DARK else "#b8b3a8",
    "text":    "#f0ede8" if IS_DARK else "#0f0d0a",
    "text2":   "#999"    if IS_DARK else "#4a4540",
    "text3":   "#555"    if IS_DARK else "#7a7268",
    "text4":   "#333"    if IS_DARK else "#aaa49a",
    "accent":  "#ff4b2b",
    "accent2": "#ff7a5c",
    "purple":  "#8b5cf6",
    "blue":    "#3b82f6",
    "green":   "#22c55e",
    "yellow":  "#eab308",
    "orange":  "#f97316",
    "gold":    "#f59e0b",
    "gold2":   "#fbbf24",
    "glass":   "rgba(255,255,255,0.04)" if IS_DARK else "rgba(0,0,0,0.04)",
    "glassborder": "rgba(255,255,255,0.08)" if IS_DARK else "rgba(0,0,0,0.08)",
}

# ══════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════
def section_label(text):
    st.markdown(f"""
<div style="font-family:'Space Mono',monospace;font-size:8px;letter-spacing:3px;
text-transform:uppercase;color:{T['text4']};margin-bottom:12px;
display:flex;align-items:center;gap:8px;">
{text}
<span style="flex:1;height:1px;background:{T['rule']};display:inline-block;"></span>
</div>""", unsafe_allow_html=True)

def gradient_divider():
    st.markdown(f"""<div style="height:1px;background:linear-gradient(90deg,{T['accent']},{T['purple']},transparent);
opacity:0.35;margin:24px 0;"></div>""", unsafe_allow_html=True)

def gold_divider():
    st.markdown(f"""<div style="height:1px;background:linear-gradient(90deg,{T['gold']},{T['gold2']},transparent);
opacity:0.5;margin:24px 0;"></div>""", unsafe_allow_html=True)

def gen_scores():
    return {
        "viral":      (random.randint(82,97), T["accent"]),
        "hook":       (random.randint(80,96), T["purple"]),
        "engagement": (random.randint(83,95), T["blue"]),
        "share":      (random.randint(81,94), T["green"]),
        "retention":  (random.randint(82,95), T["yellow"]),
        "reach":      (random.randint(80,93), T["orange"]),
    }

def gen_confidence():
    return random.randint(87, 98)

POSTING_TIMES = {
    "Instagram Reels": [("6–8 AM","Morning",False),("12–2 PM","Lunch",False),("7–9 PM","Evening",True),("10 PM","Night",False)],
    "TikTok":          [("7–9 AM","Morning",False),("3–5 PM","Afternoon",False),("7–9 PM","Prime",True),("11 PM","Late",False)],
    "YouTube Shorts":  [("8–10 AM","Morning",False),("2–4 PM","Afternoon",True),("6–8 PM","Evening",False)],
}

SATURATION = {
    "Dark Aesthetic / Motivation": "HIGH — competitive. Use micro-angles.",
    "Gaming": "VERY HIGH — niche down to specific game/genre.",
    "Tech & AI": "MEDIUM-HIGH — fast growing. Early mover advantage.",
    "Finance & Investing": "MEDIUM — evergreen. Authority content wins.",
    "Fitness & Gym": "VERY HIGH — specific transformation angles win.",
    "Horror & Thriller": "MEDIUM — underserved on Reels. Opportunity.",
    "Luxury & Premium": "LOW-MEDIUM — aspirational, high engagement.",
}

def parse_captions(text):
    s = re.search(r'SHORT[^:]*:\s*([\s\S]*?)(?=MEDIUM[^:]*:|$)', text, re.I)
    m = re.search(r'MEDIUM[^:]*:\s*([\s\S]*?)(?=LONG[^:]*:|$)', text, re.I)
    l = re.search(r'LONG[^:]*:\s*([\s\S]*?)$', text, re.I)
    return (
        s.group(1).strip() if s else text[:200],
        m.group(1).strip() if m else "",
        l.group(1).strip() if l else ""
    )

def parse_hashtags(text):
    hv = re.search(r'HIGH VOLUME[^:]*:\s*([\s\S]*?)(?=MEDIUM VOLUME|$)', text, re.I)
    mv = re.search(r'MEDIUM VOLUME[^:]*:\s*([\s\S]*?)(?=NICHE|$)', text, re.I)
    nv = re.search(r'NICHE[^:]*:\s*([\s\S]*?)$', text, re.I)
    def tags(raw): return re.findall(r'#\w+', raw) if raw else []
    return (tags(hv.group(1) if hv else ""), tags(mv.group(1) if mv else ""), tags(nv.group(1) if nv else ""))

def format_script(text):
    hook  = re.search(r'HOOK[^:]*:\s*([\s\S]*?)(?=BODY|MIDDLE|$)', text, re.I)
    body  = re.search(r'(?:BODY|MIDDLE)[^:]*:\s*([\s\S]*?)(?=CTA|$)', text, re.I)
    cta   = re.search(r'CTA[^:]*:\s*([\s\S]*?)(?=SUGGESTED AUDIO|AUDIO|$)', text, re.I)
    audio = re.search(r'(?:SUGGESTED AUDIO|AUDIO)[^:]*:\s*([\s\S]*?)$', text, re.I)
    parts = []
    if hook:  parts.append(f"🔴 HOOK (0–3s)\n{hook.group(1).strip()}")
    if body:  parts.append(f"⚪ BODY (3–25s)\n{body.group(1).strip()}")
    if cta:   parts.append(f"🟢 CTA (25–30s)\n{cta.group(1).strip()}")
    if audio: parts.append(f"🟣 AUDIO VIBE\n{audio.group(1).strip()}")
    return "\n\n".join(parts) if parts else text

# ══════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&family=Fraunces:ital,opsz,wght@1,9..144,900&display=swap');
*, *::before, *::after {{ box-sizing:border-box; }}
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {{
    background:{T["bg"]} !important;
    color:{T["text"]} !important;
    font-family:'Space Grotesk',sans-serif !important;
}}
[data-testid="stHeader"] {{ display:none !important; }}
[data-testid="stSidebar"] {{ display:none !important; }}
.block-container {{ padding:0 !important; max-width:100% !important; }}
.stTextInput>div>div>input,.stTextArea>div>div>textarea {{
    background:{T["bg3"]} !important; border:1px solid {T["rule2"]} !important;
    border-radius:0 !important; color:{T["text"]} !important;
    font-family:'Space Grotesk',sans-serif !important; font-size:13px !important;
    padding:11px 13px !important;
    transition:border-color 0.2s, box-shadow 0.2s !important;
    caret-color:{T["accent"]} !important;
}}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus {{
    border-color:{T["accent"]} !important;
    box-shadow:0 0 0 2px {T["accent"]}18 !important;
}}
.stTextInput>div>div>input::placeholder,.stTextArea>div>div>textarea::placeholder {{
    color:{T["text4"]} !important;
}}
[data-baseweb="select"]>div {{
    background:{T["bg3"]} !important; border:1px solid {T["rule2"]} !important;
    border-radius:0 !important; color:{T["text"]} !important;
    font-family:'Space Grotesk',sans-serif !important; font-size:13px !important;
}}
[data-baseweb="popover"] ul {{
    background:{T["bg3"]} !important; border:1px solid {T["rule2"]} !important;
}}
[data-baseweb="option"] {{
    background:{T["bg3"]} !important; color:{T["text"]} !important;
    font-family:'Space Grotesk',sans-serif !important; font-size:12px !important;
}}
[data-baseweb="option"]:hover {{ background:{T["bg4"]} !important; }}
label,.stSelectbox label,.stTextInput label,.stTextArea label,.stRadio label {{
    color:{T["text3"]} !important; font-family:'Space Mono',monospace !important;
    font-size:8px !important; letter-spacing:2px !important; text-transform:uppercase !important;
}}
.stRadio>div {{ gap:6px !important; flex-direction:row !important; flex-wrap:wrap !important; }}
.stRadio>div>label {{
    background:{T["bg3"]} !important; border:1px solid {T["rule2"]} !important;
    padding:8px 14px !important; transition:all 0.15s !important;
    color:{T["text3"]} !important; font-size:11px !important;
    letter-spacing:1px !important; border-radius:0 !important; margin:0 !important;
}}
.stRadio>div>label:hover {{ border-color:{T["accent"]} !important; color:{T["accent"]} !important; }}
.stButton>button {{
    background:transparent !important; color:{T["text3"]} !important;
    border:1px solid {T["rule2"]} !important; border-radius:0 !important;
    font-family:'Space Mono',monospace !important; font-size:9px !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
    padding:10px 18px !important; transition:all 0.2s !important;
    width:100% !important;
}}
.stButton>button:hover {{
    border-color:{T["accent"]} !important; color:{T["accent"]} !important;
    box-shadow:0 0 12px {T["accent"]}20 !important;
}}
.stDownloadButton>button {{
    background:transparent !important; color:{T["text3"]} !important;
    border:1px solid {T["rule2"]} !important; border-radius:0 !important;
    font-family:'Space Mono',monospace !important; font-size:8px !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
    padding:8px 14px !important; width:auto !important; transition:all 0.2s !important;
}}
.stDownloadButton>button:hover {{
    border-color:{T["accent"]} !important; color:{T["accent"]} !important;
}}
.stTabs [data-baseweb="tab-list"] {{
    background:transparent !important; border-bottom:1px solid {T["rule"]} !important;
    gap:0 !important; padding:0 !important;
}}
.stTabs [data-baseweb="tab"] {{
    background:transparent !important; color:{T["text3"]} !important;
    font-family:'Space Mono',monospace !important; font-size:8px !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
    padding:10px 18px !important; border-radius:0 !important;
    border-bottom:2px solid transparent !important; transition:all 0.2s !important;
}}
.stTabs [aria-selected="true"] {{
    color:{T["accent"]} !important; border-bottom-color:{T["accent"]} !important;
    background:transparent !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding:20px 0 0 !important; background:transparent !important; }}
[data-testid="stMetric"] {{
    background:{T["bg2"]} !important; border:1px solid {T["rule"]} !important;
    padding:14px !important; border-radius:0 !important;
}}
[data-testid="stMetricLabel"]>div {{
    font-family:'Space Mono',monospace !important; font-size:8px !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
    color:{T["text4"]} !important;
}}
[data-testid="stMetricValue"]>div {{
    font-family:'Space Mono',monospace !important; color:{T["text"]} !important; font-size:24px !important;
}}
.streamlit-expanderHeader {{
    background:{T["bg2"]} !important; border:1px solid {T["rule"]} !important;
    border-radius:0 !important; color:{T["text3"]} !important;
    font-family:'Space Mono',monospace !important; font-size:9px !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
}}
.streamlit-expanderContent {{
    background:{T["bg2"]} !important; border:1px solid {T["rule"]} !important;
    border-top:none !important; padding:16px !important;
}}
hr {{ border-color:{T["rule"]} !important; margin:20px 0 !important; }}
::-webkit-scrollbar {{ width:3px; height:3px; }}
::-webkit-scrollbar-track {{ background:{T["bg"]}; }}
::-webkit-scrollbar-thumb {{ background:{T["rule2"]}; }}
::-webkit-scrollbar-thumb:hover {{ background:{T["accent"]}; }}

div[data-testid="stButton"] button[kind="primary"],
.generate-btn > div > button {{
    background: linear-gradient(135deg, {T["accent"]} 0%, {T["accent2"]} 40%, {T["purple"]} 100%) !important;
    background-size: 200% 200% !important;
    color: #fff !important;
    border: none !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 4px !important;
    text-transform: uppercase !important;
    padding: 14px 20px !important;
    cursor: pointer !important;
    animation: liquidFlow 3s ease infinite !important;
    box-shadow: 0 0 24px {T["accent"]}40, 0 4px 20px rgba(0,0,0,0.4) !important;
}}
@keyframes liquidFlow {{
    0%   {{ background-position: 0% 50%; }}
    50%  {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

.gold-btn-container > div > button {{
    background: linear-gradient(135deg, #92400e 0%, {T["gold"]} 40%, {T["gold2"]} 70%, #92400e 100%) !important;
    background-size: 300% 300% !important;
    color: #000 !important;
    border: 1px solid {T["gold2"]}80 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    padding: 13px 20px !important;
    cursor: pointer !important;
    animation: goldFlow 4s ease infinite !important;
    box-shadow: 0 0 30px {T["gold"]}50, 0 4px 20px rgba(0,0,0,0.5) !important;
}}
@keyframes goldFlow {{
    0%   {{ background-position: 0% 50%; }}
    50%  {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* HOME BUTTON */
.home-btn-container > div > button {{
    background: {T["bg3"]} !important;
    color: {T["text2"]} !important;
    border: 1px solid {T["rule2"]} !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 9px 16px !important;
    width: auto !important;
}}
.home-btn-container > div > button:hover {{
    border-color: {T["accent"]} !important;
    color: {T["accent"]} !important;
    box-shadow: 0 0 14px {T["accent"]}25 !important;
}}

/* OUTPUT CARD */
.output-card {{
    background: {T["glass"]};
    border: 1px solid {T["glassborder"]};
    padding: 18px;
    position: relative;
    margin-bottom: 8px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 13px;
    line-height: 1.8;
    color: {T["text2"]};
    white-space: pre-wrap;
}}

.confidence-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, {T["green"]}20, {T["green"]}10);
    border: 1px solid {T["green"]}40;
    padding: 4px 10px;
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    color: {T["green"]};
    text-transform: uppercase;
}}
@keyframes pulse {{
    0%,100% {{ opacity:1; }}
    50% {{ opacity:0.3; }}
}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# NEURAL NETWORK BACKGROUND (ambient, all pages)
# ══════════════════════════════════════════
def inject_premium_effects(accent_hex="255,75,43"):
    components.html(f"""
<!DOCTYPE html><html><head>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ overflow:hidden; background:transparent; }}
#canvas {{ position:fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none; z-index:0; }}
#aurora {{ position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:0; overflow:hidden; }}
.aurora-layer {{
    position:absolute; width:200%; height:200%;
    background: conic-gradient(from var(--angle, 0deg) at 50% 50%,
        transparent 0deg, {T["accent"]}08 60deg, {T["purple"]}06 120deg,
        transparent 180deg, {T["blue"]}05 240deg, {T["accent"]}08 300deg, transparent 360deg);
    animation: auroraRotate 12s linear infinite; top:-50%; left:-50%;
}}
.aurora-layer-2 {{
    position:absolute; width:150%; height:150%;
    background: radial-gradient(ellipse at 20% 50%, {T["accent"]}07 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, {T["purple"]}06 0%, transparent 50%),
                radial-gradient(ellipse at 60% 80%, {T["blue"]}05 0%, transparent 50%);
    animation: auroraFloat 8s ease-in-out infinite alternate; top:-25%; left:-25%;
}}
@keyframes auroraRotate {{ from {{ transform:rotate(0deg); }} to {{ transform:rotate(360deg); }} }}
@keyframes auroraFloat {{ from {{ transform:translate(0px,0px) scale(1); }} to {{ transform:translate(30px,-20px) scale(1.05); }} }}
@property --angle {{ syntax:'<angle>'; initial-value:0deg; inherits:false; }}
</style>
</head><body>
<div id="aurora"><div class="aurora-layer"></div><div class="aurora-layer-2"></div></div>
<canvas id="canvas"></canvas>
<script>
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth; canvas.height = window.innerHeight;
const nodes = Array.from({{length:55}}, () => ({{
    x:Math.random()*canvas.width, y:Math.random()*canvas.height,
    vx:(Math.random()-0.5)*0.4, vy:(Math.random()-0.5)*0.4,
    r:Math.random()*2+1, pulse:Math.random()*Math.PI*2
}}));
let mouseX=canvas.width/2, mouseY=canvas.height/2;
function drawNetwork() {{
    ctx.clearRect(0,0,canvas.width,canvas.height);
    nodes.forEach(n => {{
        const dx=mouseX-n.x, dy=mouseY-n.y, dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<120) {{ n.vx+=dx/dist*0.015; n.vy+=dy/dist*0.015; }}
        n.vx*=0.99; n.vy*=0.99; n.x+=n.vx; n.y+=n.vy; n.pulse+=0.02;
        if(n.x<0||n.x>canvas.width) n.vx*=-1;
        if(n.y<0||n.y>canvas.height) n.vy*=-1;
        n.x=Math.max(0,Math.min(canvas.width,n.x)); n.y=Math.max(0,Math.min(canvas.height,n.y));
    }});
    for(let i=0;i<nodes.length;i++) {{
        for(let j=i+1;j<nodes.length;j++) {{
            const dx=nodes[i].x-nodes[j].x, dy=nodes[i].y-nodes[j].y;
            const dist=Math.sqrt(dx*dx+dy*dy);
            if(dist<110) {{
                ctx.beginPath(); ctx.strokeStyle=`rgba({accent_hex},${{(1-dist/110)*0.18}})`; ctx.lineWidth=0.6;
                ctx.moveTo(nodes[i].x,nodes[i].y); ctx.lineTo(nodes[j].x,nodes[j].y); ctx.stroke();
            }}
        }}
    }}
    nodes.forEach(n => {{
        const p=Math.sin(n.pulse)*0.5+0.5, alpha=0.25+p*0.35, r=n.r+p*0.8;
        ctx.beginPath(); ctx.arc(n.x,n.y,r,0,Math.PI*2);
        ctx.fillStyle=`rgba({accent_hex},${{alpha}})`; ctx.fill();
        ctx.beginPath(); ctx.arc(n.x,n.y,r*2.5,0,Math.PI*2);
        ctx.fillStyle=`rgba({accent_hex},${{alpha*0.1}})`; ctx.fill();
    }});
    requestAnimationFrame(drawNetwork);
}}
drawNetwork();
window.addEventListener('resize',()=>{{ canvas.width=window.innerWidth; canvas.height=window.innerHeight; }});
window.addEventListener('mousemove',e=>{{ mouseX=e.clientX; mouseY=e.clientY; }});
</script>
</body></html>
""", height=0, scrolling=False)

# ══════════════════════════════════════════
# GLASS SHATTER TRANSITION OVERLAY
# Plays a full-screen shatter animation, then sends a
# message back to Streamlit (via query param reload) to
# switch pages once the animation completes.
# ══════════════════════════════════════════
def shatter_overlay(accent_color, target_page, label="ENTERING"):
    """Renders a full-viewport shattering glass overlay that plays once,
    then triggers a rerun into target_page by writing to sessionStorage
    and forcing Streamlit's component to send a value back."""
    shards = ""
    cols, rows = 10, 6
    cell_w, cell_h = 100/cols, 100/rows
    for r in range(rows):
        for c in range(cols):
            x = c*cell_w
            y = r*cell_h
            # randomized fall direction & rotation per shard
            dx = random.randint(-260, 260)
            dy = random.randint(180, 520)
            rot = random.randint(-260, 260)
            delay = round(random.uniform(0, 0.18), 2)
            dur = round(random.uniform(0.6, 1.05), 2)
            # irregular triangle-ish clip via polygon jitter
            jitter = lambda: random.randint(-6,6)
            poly = f"polygon({jitter()+0}% {jitter()+0}%, {100+jitter()}% {jitter()}%, {100+jitter()}% {100+jitter()}%, {jitter()}% {100+jitter()}%)"
            shards += f"""
<div class="shard" style="
    left:{x}vw; top:{y}vh; width:{cell_w}vw; height:{cell_h}vh;
    --dx:{dx}px; --dy:{dy}px; --rot:{rot}deg;
    animation-delay:{delay}s; animation-duration:{dur}s;
    clip-path:{poly};
"></div>"""

    components.html(f"""
<!DOCTYPE html><html><head>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:100%; height:100%; overflow:hidden; background:transparent; }}
.stage {{
    position:fixed; inset:0; width:100vw; height:100vh; z-index:99999;
    pointer-events:none;
}}
.shard {{
    position:absolute;
    background:
        linear-gradient(135deg, {accent_color}22, transparent 60%),
        rgba(255,255,255,0.045);
    border:1px solid {accent_color}33;
    backdrop-filter: blur(6px);
    animation-name: fall;
    animation-timing-function: cubic-bezier(.5,0,.85,1);
    animation-fill-mode: forwards;
    box-shadow: 0 0 18px {accent_color}22 inset;
}}
@keyframes fall {{
    0% {{ transform: translate(0,0) rotate(0deg) scale(1); opacity:1; }}
    60% {{ opacity:1; }}
    100% {{ transform: translate(var(--dx), var(--dy)) rotate(var(--rot)) scale(0.85); opacity:0; }}
}}
.flash {{
    position:fixed; inset:0; background:{accent_color};
    opacity:0; animation: flashpop 0.5s ease-out forwards;
    mix-blend-mode: screen;
}}
@keyframes flashpop {{
    0% {{ opacity:0.55; }}
    100% {{ opacity:0; }}
}}
.label {{
    position:fixed; bottom:36px; left:50%; transform:translateX(-50%);
    font-family:'Space Mono',monospace; font-size:10px; letter-spacing:6px;
    text-transform:uppercase; color:{accent_color};
    opacity:0; animation: labelpop 1s ease-out 0.15s forwards;
}}
@keyframes labelpop {{ 0% {{opacity:0;}} 30% {{opacity:1;}} 100% {{opacity:0;}} }}
</style>
</head><body>
<div class="stage">
<div class="flash"></div>
{shards}
<div class="label">{label}</div>
</div>
</body></html>
""", height=0, scrolling=False)

# ══════════════════════════════════════════
# COPY-ENABLED OUTPUT CARD
# ══════════════════════════════════════════
def output_card(title, content, accent_color=None, show_copy=True, confidence=None, height=None):
    color = accent_color or T["accent"]
    h_style = f"max-height:{height}px;overflow-y:auto;" if height else ""
    conf_badge = ""
    if confidence:
        conf_badge = f'<div style="display:inline-flex;align-items:center;gap:6px;background:{T["green"]}15;border:1px solid {T["green"]}40;padding:3px 9px;font-family:Space Mono,monospace;font-size:8px;letter-spacing:2px;color:{T["green"]};text-transform:uppercase;"><span style="width:5px;height:5px;background:{T["green"]};border-radius:50%;display:inline-block;animation:confPulse 1.5s infinite;"></span>Confidence: {confidence}%</div>'

    copy_btn = ""
    if show_copy:
        copy_btn = f'<button onclick="copyContent(this)" style="background:transparent;border:1px solid {T["rule2"]};color:{T["text4"]};font-family:Space Mono,monospace;font-size:7px;letter-spacing:2px;padding:4px 10px;cursor:pointer;text-transform:uppercase;transition:all 0.2s;" onmouseover="this.style.borderColor=\'{color}\';this.style.color=\'{color}\';" onmouseout="this.style.borderColor=\'{T["rule2"]}\';this.style.color=\'{T["text4"]}\';">COPY</button>'

    escaped_content = content.replace("`", "&#96;").replace("\\", "\\\\").replace("\n", "\\n").replace("'", "\\'")

    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
* {{ margin:0;padding:0;box-sizing:border-box; }}
body {{ background:transparent;font-family:'Space Grotesk',sans-serif;padding:2px; }}
@keyframes confPulse {{ 0%,100%{{opacity:1;box-shadow:0 0 4px {T["green"]};}} 50%{{opacity:0.4;box-shadow:none;}} }}
.card {{
    background:{T["glass"]};backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
    border:1px solid {T["glassborder"]};border-left:2px solid {color};
    padding:16px;position:relative;overflow:hidden;{h_style}
}}
.card:hover {{ border-color:{color}80;box-shadow:0 0 30px {color}15,0 8px 32px rgba(0,0,0,0.3); }}
.card-header {{ display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;flex-wrap:wrap;gap:8px; }}
.card-title {{ font-family:'Space Mono',monospace;font-size:8px;letter-spacing:3px;text-transform:uppercase;color:{color}; }}
.card-actions {{ display:flex;align-items:center;gap:8px;flex-wrap:wrap; }}
.card-body {{ font-size:13px;line-height:1.8;color:{T["text2"]};white-space:pre-wrap; }}
.toast {{ position:fixed;bottom:12px;right:12px;background:{color};color:#fff;
    font-family:'Space Mono',monospace;font-size:9px;letter-spacing:2px;padding:7px 14px;
    opacity:0;transition:opacity 0.2s;pointer-events:none;z-index:9999;text-transform:uppercase; }}
.toast.show {{ opacity:1; }}
</style>
</head><body>
<div class="card">
    <div class="card-header">
        <div class="card-title">{title}</div>
        <div class="card-actions">
            {conf_badge}
            {copy_btn}
        </div>
    </div>
    <div class="card-body" id="content">{content}</div>
</div>
<div class="toast" id="toast">COPIED ✓</div>
<script>
function copyContent(btn) {{
    const text = `{escaped_content}`;
    navigator.clipboard.writeText(text).then(()=>{{
        const t = document.getElementById('toast');
        t.classList.add('show');
        setTimeout(()=>t.classList.remove('show'), 1600);
    }}).catch(()=>{{
        const ta = document.createElement('textarea');
        ta.value = text; document.body.appendChild(ta);
        ta.select(); document.execCommand('copy');
        document.body.removeChild(ta);
        const t = document.getElementById('toast');
        t.classList.add('show');
        setTimeout(()=>t.classList.remove('show'), 1600);
    }});
}}
</script>
</body></html>
""", height=(height or 200) + 80, scrolling=False)

# ══════════════════════════════════════════
# SCORE BENTO WITH ANIMATED COUNTERS
# ══════════════════════════════════════════
def score_bento(scores, confidence):
    items = [
        ("Viral Potential", "viral",      T["accent"]),
        ("Hook Strength",   "hook",       T["purple"]),
        ("Engagement",      "engagement", T["blue"]),
        ("Shareability",    "share",      T["green"]),
        ("Retention",       "retention",  T["yellow"]),
        ("Reach Rating",    "reach",      T["orange"]),
    ]
    cards_html = ""
    for label, key, color in items:
        val, _ = scores[key]
        cards_html += f"""
<div class="score-card" style="--accent:{color};" onmousemove="tilt(this,event)" onmouseleave="resetTilt(this)">
    <div class="card-glow"></div>
    <div class="score-label">{label}</div>
    <div class="score-value" data-target="{val}">0</div>
    <div class="score-bar"><div class="score-fill" data-width="{val}"></div></div>
</div>"""

    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
* {{ margin:0;padding:0;box-sizing:border-box; }}
body {{ background:transparent;font-family:'Space Mono',monospace;padding:4px 2px; }}
.conf-row {{
    display:flex;align-items:center;gap:12px;margin-bottom:14px;
    padding:10px 14px;background:{T["glass"]};border:1px solid {T["green"]}30;
    border-left:2px solid {T["green"]};
}}
.conf-label {{ font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text3"]}; }}
.conf-value {{ font-size:22px;font-weight:700;color:{T["green"]}; }}
.conf-bar-wrap {{ flex:1;height:3px;background:{T["rule2"]};overflow:hidden; }}
.conf-bar {{ height:100%;background:linear-gradient(90deg,{T["green"]},{T["green"]}80);width:0;transition:width 1.6s cubic-bezier(0.4,0,0.2,1); }}
.conf-dot {{ width:7px;height:7px;background:{T["green"]};border-radius:50%;animation:cpulse 1.5s infinite;flex-shrink:0; }}
@keyframes cpulse {{ 0%,100%{{opacity:1;box-shadow:0 0 6px {T["green"]};}} 50%{{opacity:0.3;box-shadow:none;}} }}
.grid {{ display:grid;grid-template-columns:repeat(3,1fr);gap:8px; }}
.score-card {{
    background:{T["glass"]};backdrop-filter:blur(20px);
    border:1px solid {T["glassborder"]};border-top:2px solid var(--accent);
    padding:14px;position:relative;overflow:hidden;
    transition:transform 0.2s,box-shadow 0.2s;cursor:default;
}}
.card-glow {{ position:absolute;inset:0;background:radial-gradient(circle at 50% 0%,var(--accent)15 0%,transparent 70%);opacity:0;transition:opacity 0.3s;pointer-events:none; }}
.score-card:hover .card-glow {{ opacity:1; }}
.score-card:hover {{ box-shadow:0 0 20px var(--accent)20,0 4px 20px rgba(0,0,0,0.4); }}
.score-label {{ font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text3"]};margin-bottom:6px; }}
.score-value {{ font-size:28px;font-weight:700;color:var(--accent);line-height:1;margin-bottom:8px; }}
.score-bar {{ height:2px;background:{T["rule2"]};overflow:hidden; }}
.score-fill {{ height:100%;background:var(--accent);width:0%;transition:width 1.4s cubic-bezier(0.4,0,0.2,1); }}
</style>
</head><body>
<div class="conf-row">
    <div class="conf-dot"></div>
    <div>
        <div class="conf-label">AI Confidence</div>
        <div class="conf-value" id="confVal">0%</div>
    </div>
    <div class="conf-bar-wrap"><div class="conf-bar" id="confBar" data-width="{confidence}"></div></div>
</div>
<div class="grid">{cards_html}</div>
<script>
(function() {{
    const target = {confidence};
    let cur = 0; const step = Math.ceil(target/50);
    const el = document.getElementById('confVal');
    const timer = setInterval(()=>{{
        cur = Math.min(cur+step, target);
        el.textContent = cur + '%';
        if(cur>=target) clearInterval(timer);
    }}, 20);
}})();
document.querySelectorAll('.score-value').forEach(el => {{
    const target = parseInt(el.dataset.target);
    let cur = 0; const step = Math.ceil(target/50);
    const timer = setInterval(()=>{{
        cur = Math.min(cur+step, target);
        el.textContent = cur;
        if(cur>=target) clearInterval(timer);
    }}, 25);
}});
setTimeout(()=>{{
    document.querySelectorAll('.score-fill').forEach(el=>{{ el.style.width = el.dataset.width + '%'; }});
    document.getElementById('confBar').style.width = document.getElementById('confBar').dataset.width + '%';
}}, 80);
function tilt(card,e) {{
    const r=card.getBoundingClientRect();
    const rx=((e.clientY-r.top-r.height/2)/r.height)*-8;
    const ry=((e.clientX-r.left-r.width/2)/r.width)*8;
    card.style.transform=`perspective(400px) rotateX(${{rx}}deg) rotateY(${{ry}}deg) translateY(-2px)`;
}}
function resetTilt(card) {{ card.style.transform=''; }}
</script>
</body></html>
""", height=290, scrolling=False)

# ══════════════════════════════════════════
# RADAR CHART
# ══════════════════════════════════════════
def radar_component(scores):
    vals = [scores[k][0] for k in ['viral','hook','engagement','share','retention','reach']]
    labels = ['Viral','Hook','Engage','Share','Retain','Reach']
    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>* {{ margin:0;padding:0;box-sizing:border-box; }} body {{ background:transparent;display:flex;align-items:center;justify-content:center; }} canvas {{ max-width:220px;max-height:220px; }}</style>
</head><body>
<canvas id="rc"></canvas>
<script>
new Chart(document.getElementById('rc'), {{
    type:'radar',
    data:{{ labels:{labels}, datasets:[{{ data:{vals}, backgroundColor:'rgba(255,75,43,0.1)', borderColor:'{T["accent"]}', borderWidth:1.5, pointBackgroundColor:'{T["accent"]}', pointRadius:4, pointHoverRadius:6 }}] }},
    options:{{ responsive:true, scales:{{ r:{{ min:0,max:100, ticks:{{display:false}}, grid:{{color:'rgba(255,75,43,0.08)'}}, angleLines:{{color:'rgba(255,75,43,0.08)'}}, pointLabels:{{color:'{T["text3"]}',font:{{family:'Space Mono',size:9}}}} }} }}, plugins:{{legend:{{display:false}}}}, animation:{{duration:1200,easing:'easeOutQuart'}} }}
}});
</script>
</body></html>
""", height=240, scrolling=False)

# ══════════════════════════════════════════
# HASHTAG COMPONENT
# ══════════════════════════════════════════
def hashtag_component(hv, mv, nv):
    def tags_html(tags, color):
        return "".join([f'<span class="tag" style="--c:{color};" onclick="copyTag(this)">{t}</span>' for t in tags])

    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Space+Grotesk:wght@400&display=swap" rel="stylesheet">
<style>
* {{ margin:0;padding:0;box-sizing:border-box; }}
body {{ background:transparent;font-family:'Space Grotesk',sans-serif;padding:4px 2px; }}
.group {{ margin-bottom:16px; }}
.group-label {{ font-family:'Space Mono',monospace;font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text3"]};margin-bottom:8px;display:flex;align-items:center;justify-content:space-between; }}
.copy-all {{ background:transparent;border:1px solid {T["rule2"]};color:{T["text4"]};font-family:'Space Mono',monospace;font-size:7px;letter-spacing:1px;padding:2px 7px;cursor:pointer;transition:all 0.15s;text-transform:uppercase; }}
.copy-all:hover {{ border-color:{T["accent"]};color:{T["accent"]}; }}
.tags {{ display:flex;flex-wrap:wrap;gap:5px; }}
.tag {{ background:{T["bg3"]};border:1px solid {T["rule2"]};color:{T["text2"]};font-family:'Space Mono',monospace;font-size:10px;padding:4px 9px;cursor:pointer;transition:all 0.2s;display:inline-block;position:relative;overflow:hidden; }}
.tag::before {{ content:'';position:absolute;inset:0;background:var(--c);opacity:0;transition:opacity 0.2s; }}
.tag:hover::before {{ opacity:0.1; }}
.tag:hover {{ border-color:var(--c);color:var(--c);transform:translateY(-1px); }}
.toast {{ position:fixed;bottom:10px;right:10px;background:{T["accent"]};color:#fff;font-family:'Space Mono',monospace;font-size:9px;letter-spacing:2px;padding:6px 12px;opacity:0;transition:opacity 0.2s;pointer-events:none;z-index:999;text-transform:uppercase; }}
.toast.show {{ opacity:1; }}
</style>
</head><body>
<div class="group">
    <div class="group-label"><span>High Volume — 1M+ posts ({len(hv)} tags)</span><button class="copy-all" onclick="copyGroup('hv')">COPY ALL</button></div>
    <div class="tags" id="hv">{tags_html(hv, T["accent"])}</div>
</div>
<div class="group">
    <div class="group-label"><span>Medium Volume — 100K–1M ({len(mv)} tags)</span><button class="copy-all" onclick="copyGroup('mv')">COPY ALL</button></div>
    <div class="tags" id="mv">{tags_html(mv, T["blue"])}</div>
</div>
<div class="group">
    <div class="group-label"><span>Niche Community — Under 100K ({len(nv)} tags)</span><button class="copy-all" onclick="copyGroup('nv')">COPY ALL</button></div>
    <div class="tags" id="nv">{tags_html(nv, T["green"])}</div>
</div>
<div class="toast" id="toast">COPIED ✓</div>
<script>
function showToast() {{ const t=document.getElementById('toast'); t.classList.add('show'); setTimeout(()=>t.classList.remove('show'),1500); }}
function copyTag(el) {{ navigator.clipboard.writeText(el.textContent); showToast(); }}
function copyGroup(id) {{ const tags=Array.from(document.getElementById(id).querySelectorAll('.tag')).map(t=>t.textContent).join(' '); navigator.clipboard.writeText(tags); showToast(); }}
</script>
</body></html>
""", height=300, scrolling=False)

# ══════════════════════════════════════════
# TOPBAR
# ══════════════════════════════════════════
def render_topbar(show_home=False, status_label="GEMINI LIVE"):
    home_html = ""
    cols = st.columns([0.06, 0.94]) if show_home else None
    st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
padding:0 20px 0 16px;height:52px;background:{T["bg2"]}ee;
border-bottom:1px solid {T["rule"]};backdrop-filter:blur(20px);position:sticky;top:0;z-index:100;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:26px;height:26px;background:{T["accent"]};
    display:flex;align-items:center;justify-content:center;font-size:13px;
    box-shadow:0 0 16px {T["accent"]}60;">🎬</div>
    <div style="font-family:'Space Mono',monospace;font-size:13px;font-weight:700;color:{T["text"]};letter-spacing:1px;">
        Reel<span style="color:{T["accent"]};">Mind</span> AI</div>
  </div>
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="display:flex;align-items:center;gap:6px;font-family:'Space Mono',monospace;font-size:8px;color:{T["green"]};">
        <div style="width:5px;height:5px;background:{T["green"]};border-radius:50%;animation:pulse 2s infinite;"></div>{status_label}
    </div>
    <div style="font-family:'Space Mono',monospace;font-size:8px;color:{T["text4"]};background:{T["bg3"]};border:1px solid {T["rule2"]};padding:3px 8px;">v5.0</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# HANDLE PENDING NAVIGATION (shatter transition)
# ══════════════════════════════════════════
if st.session_state.transition:
    target, accent, label = st.session_state.transition
    inject_premium_effects(accent)
    shatter_overlay(accent, target, label)
    time.sleep(1.05)
    st.session_state.page = target
    st.session_state.transition = None
    st.rerun()

# ══════════════════════════════════════════
# ── PAGE: HOME / LANDING ──
# ══════════════════════════════════════════
if st.session_state.page == "home":
    inject_premium_effects("255,75,43")
    render_topbar(status_label="STUDIO READY")

    st.markdown(f"""
<div style="padding:54px 40px 10px;text-align:center;">
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:5px;text-transform:uppercase;color:{T["text4"]};margin-bottom:18px;">
    AI CREATIVE STUDIO — PICK YOUR WORKSPACE
  </div>
  <div style="font-family:'Fraunces',serif;font-size:64px;font-weight:900;font-style:italic;line-height:0.95;letter-spacing:-2px;color:{T["text"]};margin-bottom:14px;">
    Reel<span style="color:{T["accent"]};">Mind</span> <span style="color:{T["text4"]};">AI</span>
  </div>
  <div style="font-size:13px;color:{T["text3"]};max-width:520px;margin:0 auto 40px;line-height:1.7;">
    Two studios, one engine. Step through the glass into the workspace you need —
    written content & strategy, or full cinematic AI video production.
  </div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(f"""
<div class="panel-glass" style="
    border:1px solid {T["accent"]}30; border-top:2px solid {T["accent"]};
    background:linear-gradient(160deg, {T["accent"]}0d, transparent 70%), {T["glass"]};
    backdrop-filter:blur(14px); padding:36px 30px; margin:0 40px 8px; min-height:300px;
    position:relative; overflow:hidden; transition:all 0.3s;
">
  <div style="position:absolute; inset:0; background:
    repeating-linear-gradient(0deg, transparent 0 38px, {T["accent"]}08 38px 39px),
    repeating-linear-gradient(90deg, transparent 0 38px, {T["accent"]}08 38px 39px);
    opacity:0.5; pointer-events:none;"></div>
  <div style="font-family:'Space Mono',monospace;font-size:8px;letter-spacing:4px;text-transform:uppercase;color:{T["accent"]};margin-bottom:14px;">
    01 — STUDIO A
  </div>
  <div style="font-family:'Fraunces',serif;font-size:36px;font-weight:900;font-style:italic;color:{T["text"]};margin-bottom:10px;line-height:1;">
    Content Studio
  </div>
  <div style="font-size:13px;color:{T["text3"]};line-height:1.7;margin-bottom:24px;max-width:340px;">
    Captions, hashtag stacks, hooks, content series, carousels, X threads,
    and full reel scripts — scored and ready to post.
  </div>
  <div style="display:flex;gap:18px;flex-wrap:wrap;font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">
    <span>6 modes</span><span>·</span><span>30 hashtags</span><span>·</span><span>score card</span>
  </div>
</div>
""", unsafe_allow_html=True)
        st.markdown('<div class="generate-btn">', unsafe_allow_html=True)
        if st.button("→ ENTER CONTENT STUDIO", key="enter_main"):
            st.session_state.transition = ("main", T["accent"], "ENTERING CONTENT STUDIO")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
<div class="panel-glass" style="
    border:1px solid {T["gold"]}30; border-top:2px solid {T["gold"]};
    background:linear-gradient(160deg, {T["gold"]}0d, transparent 70%), {T["glass"]};
    backdrop-filter:blur(14px); padding:36px 30px; margin:0 40px 8px; min-height:300px;
    position:relative; overflow:hidden; transition:all 0.3s;
">
  <div style="position:absolute; inset:0; background:
    repeating-linear-gradient(0deg, transparent 0 38px, {T["gold"]}08 38px 39px),
    repeating-linear-gradient(90deg, transparent 0 38px, {T["gold"]}08 38px 39px);
    opacity:0.5; pointer-events:none;"></div>
  <div style="font-family:'Space Mono',monospace;font-size:8px;letter-spacing:4px;text-transform:uppercase;color:{T["gold"]};margin-bottom:14px;">
    02 — STUDIO B
  </div>
  <div style="font-family:'Fraunces',serif;font-size:36px;font-weight:900;font-style:italic;color:{T["text"]};margin-bottom:10px;line-height:1;">
    Video Story Engine
  </div>
  <div style="font-size:13px;color:{T["text3"]};line-height:1.7;margin-bottom:24px;max-width:340px;">
    Cinematic AI animal shorts — 3 viral story options, character design sheets,
    first-frame prompts, and a full Google Flow / Gemini Video prompt chain.
  </div>
  <div style="display:flex;gap:18px;flex-wrap:wrap;font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">
    <span>3 story options</span><span>·</span><span>4K Pixar quality</span><span>·</span><span>9:16</span>
  </div>
</div>
""", unsafe_allow_html=True)
        st.markdown('<div class="gold-btn-container">', unsafe_allow_html=True)
        if st.button("→ ENTER VIDEO STUDIO", key="enter_video"):
            st.session_state.transition = ("video", T["gold"], "ENTERING VIDEO STUDIO")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
<div style="padding:48px 40px 16px;border-top:1px solid {T["rule"]};background:{T["bg2"]};
display:flex;justify-content:space-between;align-items:center;margin-top:48px;">
  <div style="font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">
    REELMIND AI — v5.0 — GEMINI 2.5 FLASH</div>
  <div style="font-family:'Space Mono',monospace;font-size:8px;color:{T["text4"]};background:{T["bg3"]};border:1px solid {T["rule2"]};padding:3px 8px;">
    BUILT BY SATVIK SHARMA · NIET 2024–28</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# ── PAGE: VIDEO STORY CREATOR ──
# ══════════════════════════════════════════
elif st.session_state.page == "video":
    inject_premium_effects("245,158,11")
    render_topbar(status_label="GEMINI LIVE")

    # Home button
    st.markdown("<div style='padding:14px 40px 0;'>", unsafe_allow_html=True)
    st.markdown('<div class="home-btn-container">', unsafe_allow_html=True)
    if st.button("← SHATTER BACK TO HOME", key="home_from_video"):
        st.session_state.transition = ("home", T["gold"], "RETURNING HOME")
        st.session_state.video_stories = None
        st.session_state.video_package = None
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Hero for video page
    st.markdown(f"""
<div style="padding:24px 40px 24px;border-bottom:1px solid {T["gold"]}30;position:relative;overflow:hidden;">
  <div style="position:absolute;inset:0;background:radial-gradient(ellipse at 20% 50%,{T["gold"]}08 0%,transparent 60%);pointer-events:none;"></div>
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:4px;text-transform:uppercase;color:{T["gold"]};margin-bottom:10px;display:flex;align-items:center;gap:10px;">
    <span style="width:18px;height:1px;background:{T["gold"]};display:inline-block;"></span>
    AI Video Story Engine — Cinematic Grade
  </div>
  <div style="font-family:'Fraunces',serif;font-size:48px;font-weight:900;font-style:italic;line-height:0.95;letter-spacing:-2px;color:{T["text"]};margin-bottom:12px;">
    Video <span style="color:{T["gold"]};">Story</span>
    <span style="color:{T["text4"]};">Creator</span>
  </div>
  <div style="font-size:13px;color:{T["text3"]};max-width:560px;line-height:1.7;margin-bottom:8px;">
    Generate complete production-ready video packages: 3 story options with viral scores,
    character design sheets, first frame prompts, and a full prompt chain for Google Flow or Gemini Video.
  </div>
  <div style="display:flex;gap:24px;flex-wrap:wrap;margin-top:14px;">
    {"".join([f'<div style="display:flex;flex-direction:column;gap:2px;"><div style="font-family:Space Mono,monospace;font-size:18px;font-weight:700;color:{T["gold"]};">{n}</div><div style="font-family:Space Mono,monospace;font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">{l}</div></div>' for n,l in [("3","Story Options"),("Full","Prompt Chain"),("4K","Pixar Quality"),("9:16","Vertical")]]) }
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='padding:0 40px;'>", unsafe_allow_html=True)

    # ── CONTROL DECK (was sidebar) ──
    gold_divider()
    section_label("Configure Your Story")

    cd1, cd2, cd3 = st.columns(3)
    with cd1:
        v_animal = st.selectbox("Character", [
            "Puppy 🐶","Kitten 🐱","Baby Penguin 🐧","Baby Fox 🦊",
            "Baby Panda 🐼","Baby Bunny 🐰","Baby Duck 🦆","Custom..."
        ])
        if v_animal == "Custom...":
            v_animal = st.text_input("Describe your character", placeholder="e.g. tiny orange dragon")
        v_story_type = st.selectbox("Story Type", [
            "Funny","Emotional","Cute & Heartwarming",
            "Adventure","Action","Mystery","Educational"
        ])
    with cd2:
        v_duration = st.selectbox("Video Duration (seconds)", [8,16,24,30,40,60])
        v_style = st.selectbox("Animation Style", [
            "Pixar","Disney","DreamWorks","Anime","Chibi","Realistic"
        ])
    with cd3:
        v_platform = st.selectbox("Platform", ["Instagram Reels","TikTok","YouTube Shorts"])
        v_ending = st.selectbox("Ending Type", [
            "Funny / Comedic","Emotional / Heartwarming",
            "Twist / Unexpected","Happy","Random"
        ])

    st.markdown('<div class="generate-btn">', unsafe_allow_html=True)
    generate_stories_btn = st.button("→ GENERATE STORIES", key="gen_stories", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("📖 HOW TO USE THIS — FULL WORKFLOW GUIDE"):
        st.markdown(f"""
<div style="font-family:'Space Grotesk',sans-serif;font-size:13px;color:{T["text2"]};line-height:1.9;padding:8px 0;">

<strong style="color:{T["text"]};font-family:'Space Mono',monospace;font-size:10px;letter-spacing:2px;">STEP 1 — GENERATE STORIES</strong><br>
Select your character, story type, duration and style. The AI generates 3 different story options with viral scores, emotion scores, and retention estimates. Pick the one that resonates most.

<br><br><strong style="color:{T["text"]};font-family:'Space Mono',monospace;font-size:10px;letter-spacing:2px;">STEP 2 — GET YOUR PRODUCTION PACKAGE</strong><br>
Paste your chosen story below. The AI generates: character design sheet prompts (front/back/side/expressions), environment analysis, and a master First Frame prompt.

<br><br><strong style="color:{T["text"]};font-family:'Space Mono',monospace;font-size:10px;letter-spacing:2px;">STEP 3 — GENERATE CHARACTER DESIGNS</strong><br>
Take the character sheet prompt → paste into Midjourney or Ideogram → generate the character turnaround sheet. This keeps your character consistent across all clips.

<br><br><strong style="color:{T["text"]};font-family:'Space Mono',monospace;font-size:10px;letter-spacing:2px;">STEP 4 — GENERATE FIRST FRAME</strong><br>
Use the First Frame prompt to create your establishing shot in an image generator. This image becomes the visual foundation for the entire video.

<br><br><strong style="color:{T["text"]};font-family:'Space Mono',monospace;font-size:10px;letter-spacing:2px;">STEP 5 — CREATE VIDEO CLIPS IN ORDER</strong><br>
In Google Flow or Gemini Video: Upload character sheets + First Frame image → paste Prompt 1 → generate clip 1.<br>
After clip 1: screenshot the LAST FRAME → upload that screenshot + character sheets → paste Prompt 2 → generate clip 2.<br>
Repeat for each prompt. Each clip must start from the previous clip's final frame.

<br><br><strong style="color:{T["accent"]};font-family:'Space Mono',monospace;font-size:10px;letter-spacing:2px;">⚠️ GOLDEN RULE</strong><br>
Never skip the last-frame screenshot. This is what prevents teleporting, object spawning, and environment changes between clips.

</div>
""", unsafe_allow_html=True)

    # Trigger story generation
    if generate_stories_btn:
        v_animal_clean = v_animal.split(" ")[0] if " " in v_animal else v_animal
        st.session_state["v_animal_stored"] = v_animal_clean
        st.session_state["v_style_stored"] = v_style
        st.session_state["v_duration_stored"] = v_duration
        st.session_state["v_platform_stored"] = v_platform

        story_ph = st.empty()
        story_ph.markdown(f"""
<div style="background:{T["bg2"]};border:1px solid {T["gold"]}30;border-left:3px solid {T["gold"]};padding:24px;margin:20px 0;">
<div style="font-family:Space Mono,monospace;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:{T["gold"]};margin-bottom:12px;">⚡ Generating viral story options...</div>
<div style="font-family:Space Grotesk,sans-serif;font-size:13px;color:{T["text3"]};">Analyzing viral patterns for {v_animal_clean} {v_story_type} story...</div>
</div>
""", unsafe_allow_html=True)

        stories = generate_video_story(
            animal=v_animal_clean,
            story_type=v_story_type,
            duration=v_duration,
            style=v_style,
            platform=v_platform,
            ending_type=v_ending
        )
        st.session_state.video_stories = stories
        st.session_state.video_package = None

        story_ph.empty()
        st.rerun()

    # ── EMPTY STATE ──
    if not st.session_state.video_stories:
        st.markdown(f"""
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
min-height:280px;border:1px dashed {T["rule2"]};margin:32px 0;gap:14px;">
  <div style="font-size:38px;filter:grayscale(1);opacity:0.15;">🎥</div>
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:{T["text4"]};">Configure & Generate</div>
  <div style="font-size:12px;color:{T["text4"]};font-family:'Space Mono',monospace;">Your story options will appear here</div>
</div>""", unsafe_allow_html=True)

    # ── STORY OPTIONS ──
    if st.session_state.video_stories:
        gold_divider()
        section_label("Choose Your Story")

        output_card(
            "3 STORY OPTIONS — SELECT YOUR FAVOURITE",
            st.session_state.video_stories.get("stories", ""),
            T["gold"],
            show_copy=True,
            height=500
        )

        st.markdown("<br>", unsafe_allow_html=True)
        section_label("Generate Full Production Package")
        story_input = st.text_area(
            "Paste your chosen story details here (copy from above)",
            placeholder="Paste the STORY [N] section you want to use, including the title, logline, hook, goal, conflict, escalation, payoff, and ending...",
            height=120,
            key="chosen_story"
        )
        story_title_input = st.text_input("Story Title", placeholder="e.g. The Puppy and the Balloon", key="story_title")

        st.markdown('<div class="gold-btn-container">', unsafe_allow_html=True)
        gen_package_btn = st.button("🎬 GENERATE FULL PRODUCTION PACKAGE", key="gen_package")
        st.markdown('</div>', unsafe_allow_html=True)

        if gen_package_btn and story_input.strip():
            v_animal_stored = st.session_state.get("v_animal_stored", "Puppy")
            v_style_stored = st.session_state.get("v_style_stored", "Pixar")
            v_duration_stored = st.session_state.get("v_duration_stored", 24)
            v_platform_stored = st.session_state.get("v_platform_stored", "Instagram Reels")

            pkg_ph = st.empty()
            pkg_steps = [
                "Analyzing story structure...",
                "Designing character sheets...",
                "Building environment map...",
                "Creating first frame prompt...",
                "Writing prompt chain...",
                "Building continuity checklist...",
            ]

            def render_pkg_steps(done):
                rows = ""
                for i, name in enumerate(pkg_steps):
                    if i < done: col, icon = T["gold"], "✓"
                    elif i == done: col, icon = T["accent"], "◌"
                    else: col, icon = T["text4"], str(i+1)
                    rows += f'<div style="display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid {T["rule"]};font-family:Space Mono,monospace;font-size:10px;letter-spacing:1px;color:{col};"><span style="width:18px;text-align:center;">{icon}</span><span>{name}</span></div>'
                return f'<div style="background:{T["bg2"]};border:1px solid {T["gold"]}30;border-left:2px solid {T["gold"]};padding:24px;margin:20px 0;">{rows}</div>'

            for i in range(len(pkg_steps)):
                pkg_ph.markdown(render_pkg_steps(i), unsafe_allow_html=True)
                time.sleep(0.5)

            pkg = generate_video_full_package(
                animal=v_animal_stored,
                story_title=story_title_input or "My Story",
                story_logline=story_input[:200],
                story_details=story_input,
                style=v_style_stored,
                duration=v_duration_stored,
                platform=v_platform_stored
            )
            st.session_state.video_package = pkg

            pkg_ph.markdown(render_pkg_steps(len(pkg_steps)), unsafe_allow_html=True)
            time.sleep(0.3)
            pkg_ph.empty()
            st.rerun()

        if st.session_state.video_package:
            pkg = st.session_state.video_package
            gold_divider()
            section_label("Production Package")

            tab_char, tab_frame, tab_prompts, tab_cont = st.tabs([
                "🎨 Character & Environment",
                "🖼️ First Frame",
                f"🎬 Prompt Chain ({pkg.get('num_prompts',0)} clips)",
                "📋 Continuity Checklist"
            ])

            with tab_char:
                output_card("CHARACTER DESIGN & ENVIRONMENT ANALYSIS",
                    pkg.get("character_analysis",""), T["gold"], show_copy=True, height=400)
                st.download_button("↓ DOWNLOAD CHARACTER PACKAGE",
                    pkg.get("character_analysis",""),
                    file_name="character_design.txt", key="dl_char")

            with tab_frame:
                output_card("MASTER FIRST FRAME PROMPT",
                    pkg.get("first_frame",""), T["gold"], show_copy=True, height=350)
                st.markdown(f"""
<div style="background:{T["gold"]}10;border:1px solid {T["gold"]}30;border-left:2px solid {T["gold"]};padding:14px;margin-top:12px;font-family:'Space Mono',monospace;font-size:9px;letter-spacing:1px;color:{T["gold"]};">
⚡ USAGE: Paste this prompt into Midjourney (--ar 9:16 --v 6) or Ideogram. 
This establishes your entire scene. Use the generated image as the starting point for Prompt 1 in Google Flow.
</div>
""", unsafe_allow_html=True)
                st.download_button("↓ DOWNLOAD FIRST FRAME PROMPT",
                    pkg.get("first_frame",""),
                    file_name="first_frame_prompt.txt", key="dl_frame")

            with tab_prompts:
                prompts = pkg.get("prompts", [])
                if prompts:
                    for p in prompts:
                        n = p["number"]
                        is_last = (n == len(prompts))
                        label_suffix = " — FINAL CLIP" if is_last else f" of {len(prompts)}"
                        accent = T["gold"] if is_last else T["accent"]
                        output_card(
                            f"PROMPT {n}{label_suffix}",
                            p["text"],
                            accent, show_copy=True, height=350
                        )
                        if n < len(prompts):
                            st.markdown(f"""
<div style="background:{T["bg3"]};border:1px solid {T["rule"]};padding:10px 14px;margin:8px 0;font-family:'Space Mono',monospace;font-size:9px;color:{T["text4"]};letter-spacing:1px;">
📸 AFTER GENERATING CLIP {n}: Pause at the very last frame → Screenshot it → Upload that screenshot + character sheets when generating Prompt {n+1}
</div>
""", unsafe_allow_html=True)

                    all_prompts_text = f"REELMIND AI — VIDEO PROMPT CHAIN\n{'='*60}\n\n"
                    all_prompts_text += pkg.get("first_frame","") + "\n\n" + "="*60 + "\n\n"
                    for p in prompts:
                        all_prompts_text += f"PROMPT {p['number']}:\n{p['text']}\n\n{'='*60}\n\n"
                    st.download_button("↓ DOWNLOAD ALL PROMPTS", all_prompts_text,
                        file_name="video_prompt_chain.txt", key="dl_all_prompts")

            with tab_cont:
                output_card("CONTINUITY CHECKLIST — CHECK BETWEEN EVERY CLIP",
                    pkg.get("continuity",""), T["green"], show_copy=True, height=350)
                st.download_button("↓ DOWNLOAD CHECKLIST",
                    pkg.get("continuity",""),
                    file_name="continuity_checklist.txt", key="dl_cont")

    st.markdown("</div>", unsafe_allow_html=True)

    # GOLD CTA → back home
    st.markdown("<div style='padding:0 40px;'>", unsafe_allow_html=True)
    gold_divider()
    st.markdown(f"""
<div style="background:linear-gradient(135deg,{T["accent"]}10,transparent);border:1px solid {T["accent"]}30;border-left:3px solid {T["accent"]};padding:20px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
  <div>
    <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:{T["accent"]};margin-bottom:6px;">✍️ NEED WRITTEN CONTENT TOO?</div>
    <div style="font-size:13px;color:{T["text3"]};">Generate captions, hashtags, and scripts for this same content in the Content Studio.</div>
  </div>
</div>
""", unsafe_allow_html=True)
    st.markdown('<div class="generate-btn">', unsafe_allow_html=True)
    if st.button("→ OPEN CONTENT STUDIO", key="goto_main_from_video"):
        st.session_state.transition = ("main", T["accent"], "ENTERING CONTENT STUDIO")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════
# ── PAGE: MAIN CONTENT GENERATOR ──
# ══════════════════════════════════════════
elif st.session_state.page == "main":
    inject_premium_effects("255,75,43")
    render_topbar(status_label="GEMINI LIVE")

    # Home button
    st.markdown("<div style='padding:14px 40px 0;'>", unsafe_allow_html=True)
    st.markdown('<div class="home-btn-container">', unsafe_allow_html=True)
    if st.button("← SHATTER BACK TO HOME", key="home_from_main"):
        st.session_state.transition = ("home", T["accent"], "RETURNING HOME")
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

    # HERO
    st.markdown(f"""
<div style="padding:24px 40px 28px;border-bottom:1px solid {T["rule"]};position:relative;overflow:hidden;">
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:4px;text-transform:uppercase;color:{T["accent"]};margin-bottom:10px;display:flex;align-items:center;gap:10px;">
    <span style="width:18px;height:1px;background:{T["accent"]};display:inline-block;"></span>
    AI Content Engine — Studio Grade
  </div>
  <div style="font-family:'Fraunces',serif;font-size:52px;font-weight:900;font-style:italic;line-height:0.92;letter-spacing:-2px;color:{T["text"]};margin-bottom:14px;">
    Content<span style="color:{T["accent"]};"> Studio</span>
  </div>
  <div style="font-size:13px;color:{T["text3"]};max-width:480px;line-height:1.6;margin-bottom:20px;">
    Generate scroll-stopping captions, hashtag stacks, viral scripts, and thumbnail prompts — powered by Gemini 2.5 Flash.
  </div>
  <div style="display:flex;gap:32px;flex-wrap:wrap;">
    {"".join([f'<div style="display:flex;flex-direction:column;gap:2px;"><div style="font-family:Space Mono,monospace;font-size:20px;font-weight:700;color:{T["text"]};">{n}</div><div style="font-family:Space Mono,monospace;font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">{l}</div></div>' for n,l in [("4","Outputs/run"),("30","Hashtags"),("3","Captions"),("16","Niches")]])}
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='padding:0 40px;'>", unsafe_allow_html=True)

    # ── CONTROL DECK (was sidebar) ──
    gradient_divider()
    section_label("Configure Generation")

    mode = st.radio("Mode", [
        "⚡ Full Content Pack","🎯 Hook Ideas Only",
        "📅 Content Series","🎠 Carousel Post",
        "🧵 X/Twitter Thread","🔄 Content Repurposer"
    ], horizontal=True)

    cd1, cd2, cd3, cd4 = st.columns(4)
    with cd1:
        topic = st.text_input("Topic", placeholder="e.g. Villain arc, AI Tools, Gym motivation...")
    with cd2:
        niche = st.selectbox("Niche", [
            "Dark Aesthetic / Motivation","Gaming","Anime & Manga",
            "Fitness & Gym","Tech & AI","Finance & Investing",
            "Horror & Thriller","Fashion & Lifestyle","Education",
            "Movie Industry","Music & Artists","Business & Entrepreneurship",
            "Luxury & Premium","Cars & Motorsport","Travel & Adventure","Food & Cooking"
        ])
    with cd3:
        platform = st.selectbox("Platform", ["Instagram Reels","TikTok","YouTube Shorts"])
    with cd4:
        tone = st.selectbox("Tone", [
            "Viral & Bold","Dark & Cinematic","Motivational & Intense",
            "Minimal & Clean","Edgy & Controversial","Informative & Professional"
        ])

    num_posts = 5
    original_content = ""
    target_platform = "TikTok"

    if "Series" in mode:
        num_posts = st.selectbox("Posts in Series", [3,5,7])

    if "Repurposer" in mode:
        rc1, rc2 = st.columns([3,1])
        with rc1:
            original_content = st.text_area("Paste original content", height=80)
        with rc2:
            target_platform = st.selectbox("Repurpose for", ["TikTok","YouTube Shorts","X/Twitter","LinkedIn"])

    st.markdown('<div class="generate-btn">', unsafe_allow_html=True)
    generate_btn = st.button("→ GENERATE CONTENT", key="gen_main", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("QUICK TIPS"):
        st.markdown(f'<div style="font-family:Space Grotesk,sans-serif;font-size:12px;color:{T["text3"]};line-height:1.8;">→ Specific topics outperform generic<br>→ <strong style="color:{T["text2"]};">"Villain arc workout" &gt; "gym"</strong><br>→ Match tone to your content style<br>→ Use Hook mode to A/B test openings</div>', unsafe_allow_html=True)

    if st.session_state.history:
        with st.expander("RECENT GENERATIONS"):
            for h in st.session_state.history[-4:]:
                st.markdown(f'<div style="background:{T["bg3"]};border:1px solid {T["rule"]};padding:8px 10px;margin-bottom:3px;"><div style="font-size:12px;font-weight:500;color:{T["text"]};">{h["topic"][:40]}</div><div style="font-family:Space Mono,monospace;font-size:7px;color:{T["text4"]};">{h["niche"][:30]} · {h["time"]}</div></div>', unsafe_allow_html=True)

    # ── EMPTY STATE ──
    if not generate_btn:
        if not st.session_state.last_result:
            st.markdown(f"""
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
min-height:380px;border:1px dashed {T["rule2"]};margin:32px 0;gap:14px;">
  <div style="font-size:38px;filter:grayscale(1);opacity:0.15;">🎬</div>
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:{T["text4"]};">Configure & Generate</div>
  <div style="font-size:12px;color:{T["text4"]};font-family:'Space Mono',monospace;">Your content will appear here</div>
</div>""", unsafe_allow_html=True)

    if generate_btn:
        if not topic.strip():
            st.warning("Please enter a topic first.")
            st.stop()

        # Loading
        steps_ph = st.empty()
        step_names = [
            "Analyzing topic & niche...",
            "Building caption stack...",
            "Generating hashtag strategy...",
            "Writing reel script...",
            "Designing thumbnail prompt...",
            "Calculating content scores...",
        ]

        def render_steps(done):
            rows = ""
            for i, name in enumerate(step_names):
                if i < done: col, icon = T["green"], "✓"
                elif i == done: col, icon = T["accent"], "◌"
                else: col, icon = T["text4"], str(i+1)
                rows += f'<div style="display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid {T["rule"]};font-family:Space Mono,monospace;font-size:10px;letter-spacing:1px;color:{col};"><span style="width:18px;text-align:center;">{icon}</span><span>{name}</span></div>'
            return f'<div style="background:{T["bg2"]};border:1px solid {T["rule"]};padding:24px;margin:20px 0;">{rows}</div>'

        for i in range(len(step_names)):
            steps_ph.markdown(render_steps(i), unsafe_allow_html=True)
            time.sleep(0.45)

        result = None
        raw_output = None
        error_msg = None

        try:
            if "Full Content" in mode:
                result = generate_full_content(topic, niche, platform, tone)
                if "ERROR" in result.get("raw",""):
                    error_msg = result["raw"].split("||")[-1]
            elif "Hook" in mode:
                raw_output = generate_hooks(topic, niche)
                if "ERROR" in (raw_output or ""): error_msg = raw_output.split("||")[-1]
            elif "Series" in mode:
                raw_output = generate_series(topic, niche, platform, num_posts)
                if "ERROR" in (raw_output or ""): error_msg = raw_output.split("||")[-1]
            elif "Carousel" in mode:
                raw_output = generate_carousel(topic, niche, platform)
                if "ERROR" in (raw_output or ""): error_msg = raw_output.split("||")[-1]
            elif "Thread" in mode:
                raw_output = generate_thread(topic, niche)
                if "ERROR" in (raw_output or ""): error_msg = raw_output.split("||")[-1]
            elif "Repurposer" in mode:
                raw_output = repurpose_content(original_content, target_platform)
                if "ERROR" in (raw_output or ""): error_msg = raw_output.split("||")[-1]
        except Exception as e:
            error_msg = str(e)

        steps_ph.markdown(render_steps(len(step_names)), unsafe_allow_html=True)
        time.sleep(0.3)
        steps_ph.empty()

        if error_msg:
            st.error(f"Generation failed: {error_msg}")
            st.stop()

        if result:
            st.session_state.last_result = result
        scores = gen_scores()
        confidence = gen_confidence()
        st.session_state.last_scores = scores
        st.session_state.last_confidence = confidence
        st.session_state.history.append({
            "topic": topic, "niche": niche,
            "time": datetime.datetime.now().strftime("%H:%M")
        })

        # ── SCORES ──
        section_label("Content Score Card")
        score_bento(scores, confidence)
        gradient_divider()

        # ── RADAR + ANALYTICS ──
        col_r, col_a = st.columns([1,1])
        with col_r:
            section_label("Content Radar")
            radar_component(scores)

        with col_a:
            section_label("Best Posting Times")
            times = POSTING_TIMES.get(platform, POSTING_TIMES["Instagram Reels"])
            t_html = "".join([
                f'<span style="display:inline-block;background:{T["bg3"]};border:1px solid {T["green"] if best else T["rule2"]};padding:6px 11px;font-family:Space Mono,monospace;font-size:9px;color:{T["green"] if best else T["text3"]};margin:3px;{"background:" + T["green"] + "10;" if best else ""}">{t}<small style="display:block;font-size:7px;letter-spacing:1px;">{label}{"  ★" if best else ""}</small></span>'
                for t, label, best in times
            ])
            st.markdown(t_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            section_label("Niche Saturation")
            sat = SATURATION.get(niche, "MEDIUM — competitive but approachable with strong hooks.")
            st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:10px;color:{T["text2"]};line-height:1.6;">{sat}</div>', unsafe_allow_html=True)

        gradient_divider()

        # ── FULL CONTENT TABS ──
        if "Full Content" in mode and result:
            tab1, tab2, tab3, tab4 = st.tabs(["📝 Captions","#️⃣ Hashtags","🎬 Script","🖼️ Thumbnail"])

            with tab1:
                short, med, long_cap = parse_captions(result.get("captions",""))
                cap_data = [
                    (short, "Short Caption", "s", T["accent"]),
                    (med, "Medium Caption", "m", T["blue"]),
                    (long_cap, "Long Caption", "l", T["purple"])
                ]
                for cap_text, label, key, color in cap_data:
                    wc = len(cap_text.split())
                    output_card(
                        f"{label} — {wc} words",
                        cap_text, color,
                        show_copy=True,
                        confidence=confidence,
                        height=140
                    )
                    st.download_button(f"↓ DOWNLOAD {label.split()[0].upper()}", cap_text,
                        file_name=f"{label.lower().replace(' ','_')}.txt", key=f"dl_{key}")

            with tab2:
                hv, mv, nv = parse_hashtags(result.get("hashtags",""))
                hashtag_component(hv, mv, nv)
                all_tags = " ".join(hv+mv+nv)
                col_ht1, col_ht2 = st.columns(2)
                with col_ht1:
                    st.download_button("↓ DOWNLOAD ALL HASHTAGS", all_tags,
                        file_name="hashtags.txt", key="dl_ht")

            with tab3:
                formatted = format_script(result.get("script",""))
                output_card(
                    "Reel Script — 30 Seconds",
                    formatted, T["purple"],
                    show_copy=True,
                    confidence=confidence,
                    height=380
                )
                st.markdown(f"""
<div style="background:{T["purple"]}10;border:1px solid {T["purple"]}30;border-left:2px solid {T["purple"]};padding:12px 14px;margin-top:8px;font-family:'Space Mono',monospace;font-size:9px;color:{T["purple"]};letter-spacing:1px;">
💡 TIP: Read the script out loud before recording. Each line is a complete spoken sentence — no filler words needed between them.
</div>
""", unsafe_allow_html=True)
                st.download_button("↓ DOWNLOAD SCRIPT", result.get("script",""),
                    file_name="reel_script.txt", key="dl_sc")

            with tab4:
                thumb = result.get("thumbnail","")
                mj_m = re.search(r'(?:IMAGE PROMPT|PROMPT)[^:]*:\s*([\s\S]*?)(?=STYLE|$)', thumb, re.I)
                style_m = re.search(r'STYLE[^:]*:\s*([\s\S]*?)(?=COLOR|$)', thumb, re.I)
                color_m = re.search(r'COLOR[^:]*:\s*([\s\S]*?)$', thumb, re.I)
                base = mj_m.group(1).strip() if mj_m else thumb[:300]
                style = style_m.group(1).strip() if style_m else ""
                colors = color_m.group(1).strip() if color_m else ""
                mj = f"{base}\n\n--style raw --ar 9:16 --v 6\nStyle: {style}\nColors: {colors}"
                ideogram = f"{base}\n\nStyle: {style}\nPalette: {colors}\nHigh detail, sharp focus, 9:16"

                output_card("Midjourney Prompt", mj, T["accent"], show_copy=True, height=180)
                st.download_button("↓ MJ PROMPT", mj, file_name="mj_prompt.txt", key="dl_mj")
                output_card("Ideogram / Gemini Image Prompt", ideogram, T["blue"], show_copy=True, height=180)
                st.download_button("↓ IDEOGRAM PROMPT", ideogram, file_name="ideogram_prompt.txt", key="dl_id")

            gradient_divider()
            full = f"REELMIND AI v5.0\nTopic:{topic} | Niche:{niche} | Platform:{platform}\n{'='*60}\n\n{result.get('raw','')}"
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("↓ DOWNLOAD FULL PACK", full,
                    file_name=f"reelmind_{topic[:20].replace(' ','_')}_full.txt", key="dl_full")
            with c2:
                st.download_button("↓ DOWNLOAD RAW", result.get("raw",""),
                    file_name="reelmind_raw.txt", key="dl_raw")

            # Gold CTA at bottom → video studio
            gradient_divider()
            st.markdown(f"""
<div style="background:linear-gradient(135deg,{T["gold"]}10,transparent);border:1px solid {T["gold"]}30;border-left:3px solid {T["gold"]};padding:20px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
  <div>
    <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:{T["gold"]};margin-bottom:6px;">🎥 READY TO CREATE A VIDEO?</div>
    <div style="font-size:13px;color:{T["text3"]};">Turn this content into a complete AI video production package with story options, character sheets, and a full prompt chain.</div>
  </div>
</div>
""", unsafe_allow_html=True)
            st.markdown('<div class="gold-btn-container">', unsafe_allow_html=True)
            if st.button("🎥 OPEN VIDEO STORY CREATOR", key="goto_video_bottom"):
                st.session_state.transition = ("video", T["gold"], "ENTERING VIDEO STUDIO")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            mode_label = mode.split(" ",1)[1] if " " in mode else mode
            output_card(mode_label, raw_output or "No output generated.", T["accent"],
                show_copy=True, confidence=confidence, height=500)
            if raw_output:
                st.download_button("↓ DOWNLOAD OUTPUT", raw_output,
                    file_name=f"reelmind_{topic[:20].replace(' ','_')}.txt", key="dl_other")

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════
# FOOTER (main + video pages)
# ══════════════════════════════════════════
if st.session_state.page in ("main","video"):
    st.markdown(f"""
<div style="padding:16px 40px;border-top:1px solid {T["rule"]};background:{T["bg2"]};
display:flex;justify-content:space-between;align-items:center;margin-top:40px;">
  <div style="font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">
    REELMIND AI — v5.0 — GEMINI 2.5 FLASH</div>
  <div style="font-family:'Space Mono',monospace;font-size:8px;color:{T["text4"]};background:{T["bg3"]};border:1px solid {T["rule2"]};padding:3px 8px;">
    BUILT BY SATVIK SHARMA · NIET 2024–28</div>
</div>
""", unsafe_allow_html=True)