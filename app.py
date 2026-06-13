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
    ("history", []), ("mode_theme", "dark"),
    ("last_result", None), ("last_scores", None),
    ("page", "home"),
    ("video_stories", None), ("video_package", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

IS_DARK = st.session_state.mode_theme == "dark"

# ══════════════════════════════════════════
# THEMES — each studio + each mode gets a distinct premium palette
# ══════════════════════════════════════════
HOME_DARK = {
    "bg": "#070707", "bg2": "#0e0e0e", "bg3": "#161616",
    "text": "#f5f3ef", "text2": "#a8a39c", "text3": "#6e6a64", "text4": "#3a3733",
    "rule": "#1c1c1c", "rule2": "#2a2a2a",
    "accentA": "#ff4b2b", "accentB": "#f59e0b",
    "glass": "rgba(255,255,255,0.035)", "glassborder": "rgba(255,255,255,0.08)",
}
HOME_LIGHT = {
    "bg": "#f7f4ef", "bg2": "#ffffff", "bg3": "#ece7df",
    "text": "#15120e", "text2": "#544e46", "text3": "#9a938a", "text4": "#c9c2b8",
    "rule": "#e6e0d6", "rule2": "#d8d0c3",
    "accentA": "#e8431f", "accentB": "#d97f06",
    "glass": "rgba(0,0,0,0.025)", "glassborder": "rgba(0,0,0,0.06)",
}
STUDIO_DARK = {
    "bg": "#0a0707", "bg2": "#120c0c", "bg3": "#1c1414",
    "text": "#f7f1ee", "text2": "#b8a8a2", "text3": "#7a6862", "text4": "#3d3230",
    "rule": "#241818", "rule2": "#352424",
    "accent": "#ff4b2b", "accent2": "#ff7a5c", "purple": "#a78bfa", "blue": "#60a5fa",
    "green": "#4ade80", "yellow": "#fbbf24", "orange": "#fb923c",
    "glass": "rgba(255,75,43,0.04)", "glassborder": "rgba(255,255,255,0.07)",
}
STUDIO_LIGHT = {
    "bg": "#fbf4f1", "bg2": "#ffffff", "bg3": "#f5e8e3",
    "text": "#1c0f0a", "text2": "#5c4640", "text3": "#a18a82", "text4": "#dcc8c0",
    "rule": "#f0ddd6", "rule2": "#e3cbc1",
    "accent": "#e8431f", "accent2": "#c2330f", "purple": "#7c3aed", "blue": "#2563eb",
    "green": "#16a34a", "yellow": "#d97706", "orange": "#ea580c",
    "glass": "rgba(232,67,31,0.035)", "glassborder": "rgba(0,0,0,0.06)",
}
VIDEO_DARK = {
    "bg": "#070604", "bg2": "#0e0c08", "bg3": "#181410",
    "text": "#f7f4ec", "text2": "#bdb29c", "text3": "#7e7461", "text4": "#3c362b",
    "rule": "#1f1a12", "rule2": "#2e2719",
    "gold": "#f5b942", "gold2": "#ffd874", "accent": "#ff7a3d", "green": "#4ade80",
    "glass": "rgba(245,185,66,0.045)", "glassborder": "rgba(255,255,255,0.07)",
}
VIDEO_LIGHT = {
    "bg": "#faf6ec", "bg2": "#ffffff", "bg3": "#f1e7d2",
    "text": "#1a1408", "text2": "#5c5038", "text3": "#a59578", "text4": "#ddd0b3",
    "rule": "#ece0c4", "rule2": "#ddcca5",
    "gold": "#b8780a", "gold2": "#8a5a06", "accent": "#d9551f", "green": "#15803d",
    "glass": "rgba(184,120,10,0.04)", "glassborder": "rgba(0,0,0,0.06)",
}

def theme_for(page):
    if page == "main":
        return STUDIO_DARK if IS_DARK else STUDIO_LIGHT
    elif page == "video":
        return VIDEO_DARK if IS_DARK else VIDEO_LIGHT
    else:
        return HOME_DARK if IS_DARK else HOME_LIGHT

T = theme_for(st.session_state.page)

FONTS = "@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,900&display=swap');"

def gen_scores():
    return {
        "viral":      random.randint(82,97),
        "hook":       random.randint(80,96),
        "engagement": random.randint(83,95),
        "share":      random.randint(81,94),
        "retention":  random.randint(82,95),
        "reach":      random.randint(80,93),
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

def parse_script_sections(text):
    patterns = {
        "hook":     r'HOOK[^:]*:\s*([\s\S]*?)(?=VISUAL DIRECTION|BODY|$)',
        "visual":   r'VISUAL DIRECTION[^:]*:\s*([\s\S]*?)(?=BODY|$)',
        "body":     r'BODY[^:]*:\s*([\s\S]*?)(?=CTA|$)',
        "cta":      r'CTA[^:]*:\s*([\s\S]*?)(?=SUGGESTED AUDIO|AUDIO|$)',
        "audio":    r'(?:SUGGESTED AUDIO|AUDIO)[^:]*:\s*([\s\S]*?)(?=PRODUCTION NOTES|$)',
        "notes":    r'PRODUCTION NOTES[^:]*:\s*([\s\S]*?)$',
    }
    out = {}
    for key, pat in patterns.items():
        m = re.search(pat, text, re.I)
        out[key] = m.group(1).strip() if m else ""
    return out

# ══════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════
def inject_css():
    accent = T.get("accent", T.get("accentA", "#ff4b2b"))
    st.markdown(f"""
<style>
{FONTS}
*, *::before, *::after {{ box-sizing:border-box; }}
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {{
    background:{T["bg"]} !important;
    color:{T["text"]} !important;
    font-family:'Space Grotesk',sans-serif !important;
    transition: background 0.4s ease, color 0.4s ease;
}}
[data-testid="stHeader"] {{ display:none !important; }}
[data-testid="stSidebar"] {{ display:none !important; }}
.block-container {{ padding:0 !important; max-width:100% !important; }}

.reveal {{
    opacity:0; transform:translateY(28px);
    animation: revealUp 0.9s cubic-bezier(.16,1,.3,1) forwards;
}}
@keyframes revealUp {{ to {{ opacity:1; transform:translateY(0); }} }}
.reveal-d1 {{ animation-delay:0.08s; }}
.reveal-d2 {{ animation-delay:0.18s; }}
.reveal-d3 {{ animation-delay:0.28s; }}
.reveal-d4 {{ animation-delay:0.38s; }}

.page-zoom-in {{
    animation: zoomFadeIn 0.6s cubic-bezier(.16,1,.3,1) forwards;
}}
@keyframes zoomFadeIn {{
    0% {{ opacity:0; transform:scale(0.97); filter:blur(6px); }}
    100% {{ opacity:1; transform:scale(1); filter:blur(0); }}
}}

.stTextInput>div>div>input,.stTextArea>div>div>textarea {{
    background:{T["bg3"]} !important; border:1px solid {T["rule2"]} !important;
    border-radius:2px !important; color:{T["text"]} !important;
    font-family:'Space Grotesk',sans-serif !important; font-size:13px !important;
    padding:11px 13px !important;
    transition:border-color 0.2s, box-shadow 0.2s !important;
    caret-color:{accent} !important;
}}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus {{
    border-color:{accent} !important;
    box-shadow:0 0 0 2px {accent}18 !important;
}}
.stTextInput>div>div>input::placeholder,.stTextArea>div>div>textarea::placeholder {{
    color:{T["text4"]} !important;
}}
[data-baseweb="select"]>div {{
    background:{T["bg3"]} !important; border:1px solid {T["rule2"]} !important;
    border-radius:2px !important; color:{T["text"]} !important;
    font-family:'Space Grotesk',sans-serif !important; font-size:13px !important;
}}
[data-baseweb="popover"] ul {{
    background:{T["bg3"]} !important; border:1px solid {T["rule2"]} !important;
}}
[data-baseweb="option"] {{
    background:{T["bg3"]} !important; color:{T["text"]} !important;
    font-family:'Space Grotesk',sans-serif !important; font-size:12px !important;
}}
[data-baseweb="option"]:hover {{ background:{T["bg2"]} !important; }}
label,.stSelectbox label,.stTextInput label,.stTextArea label,.stRadio label,.stNumberInput label {{
    color:{T["text3"]} !important; font-family:'Space Mono',monospace !important;
    font-size:8px !important; letter-spacing:2px !important; text-transform:uppercase !important;
}}
.stNumberInput>div>div>input {{
    background:{T["bg3"]} !important; border:1px solid {T["rule2"]} !important;
    color:{T["text"]} !important; border-radius:2px !important;
    font-family:'Space Mono',monospace !important;
}}
.stRadio>div {{ gap:6px !important; flex-direction:row !important; flex-wrap:wrap !important; }}
.stRadio>div>label {{
    background:{T["bg3"]} !important; border:1px solid {T["rule2"]} !important;
    padding:8px 14px !important; transition:all 0.15s !important;
    color:{T["text3"]} !important; font-size:11px !important;
    letter-spacing:1px !important; border-radius:2px !important; margin:0 !important;
}}
.stRadio>div>label:hover {{ border-color:{accent} !important; color:{accent} !important; }}

.stButton>button {{
    background:transparent !important; color:{T["text3"]} !important;
    border:1px solid {T["rule2"]} !important; border-radius:2px !important;
    font-family:'Space Mono',monospace !important; font-size:9px !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
    padding:10px 18px !important; transition:all 0.2s !important;
    width:100% !important;
}}
.stButton>button:hover {{
    border-color:{accent} !important; color:{accent} !important;
    box-shadow:0 0 12px {accent}20 !important;
    transform: translateY(-1px);
}}
.stDownloadButton>button {{
    background:transparent !important; color:{T["text3"]} !important;
    border:1px solid {T["rule2"]} !important; border-radius:2px !important;
    font-family:'Space Mono',monospace !important; font-size:8px !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
    padding:8px 14px !important; width:auto !important; transition:all 0.2s !important;
}}
.stDownloadButton>button:hover {{ border-color:{accent} !important; color:{accent} !important; }}

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
    color:{accent} !important; border-bottom-color:{accent} !important;
    background:transparent !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding:20px 0 0 !important; background:transparent !important; }}

[data-testid="stMetric"] {{
    background:{T["bg2"]} !important; border:1px solid {T["rule"]} !important;
    padding:14px !important; border-radius:2px !important;
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
    border-radius:2px !important; color:{T["text3"]} !important;
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
::-webkit-scrollbar-thumb:hover {{ background:{accent}; }}

div[data-testid="stButton"] button[kind="primary"],
.generate-btn > div > button {{
    background: linear-gradient(135deg, {accent} 0%, {T.get("accent2", accent)} 50%, {T.get("purple", T.get("gold", accent))} 100%) !important;
    background-size: 200% 200% !important;
    color: #fff !important;
    border: none !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 4px !important;
    text-transform: uppercase !important;
    padding: 15px 20px !important;
    cursor: pointer !important;
    animation: liquidFlow 3s ease infinite !important;
    box-shadow: 0 0 24px {accent}40, 0 4px 20px rgba(0,0,0,0.4) !important;
    border-radius: 2px !important;
}}
@keyframes liquidFlow {{
    0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }}
}}

.gold-btn-container > div > button {{
    background: linear-gradient(135deg, {T.get("gold","#f5b942")}33 0%, {T.get("gold","#f5b942")} 45%, {T.get("gold2","#ffd874")} 75%, {T.get("gold","#f5b942")}33 100%) !important;
    background-size: 300% 300% !important;
    color: {"#000" if IS_DARK else "#fff"} !important;
    border: 1px solid {T.get("gold","#f5b942")}80 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important; font-weight: 700 !important;
    letter-spacing: 3px !important; text-transform: uppercase !important;
    padding: 14px 20px !important; cursor: pointer !important;
    animation: goldFlow 4s ease infinite !important;
    box-shadow: 0 0 30px {T.get("gold","#f5b942")}40, 0 4px 20px rgba(0,0,0,0.4) !important;
    border-radius: 2px !important;
}}
@keyframes goldFlow {{ 0% {{background-position:0% 50%;}} 50% {{background-position:100% 50%;}} 100% {{background-position:0% 50%;}} }}

.nav-btn-container > div > button {{
    background: {T["bg2"]} !important;
    color: {T["text2"]} !important;
    border: 1px solid {T["rule2"]} !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 9px !important; letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 10px 18px !important; width: auto !important;
    border-radius: 2px !important;
}}
.nav-btn-container > div > button:hover {{
    border-color: {accent} !important; color: {accent} !important;
    box-shadow: 0 0 14px {accent}25 !important;
}}

.confidence-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: linear-gradient(135deg, {T.get("green","#4ade80")}20, {T.get("green","#4ade80")}10);
    border: 1px solid {T.get("green","#4ade80")}40; padding: 4px 10px;
    font-family: 'Space Mono', monospace; font-size: 9px; letter-spacing: 2px;
    color: {T.get("green","#4ade80")}; text-transform: uppercase;
}}
@keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }} }}
</style>
""", unsafe_allow_html=True)

inject_css()

# ══════════════════════════════════════════
# AMBIENT BACKGROUNDS — distinct per studio
# ══════════════════════════════════════════
def inject_ambient(variant="home"):
    if variant == "video":
        accent_rgb = "245,185,66" if IS_DARK else "184,120,10"
        secondary_rgb = "255,122,61" if IS_DARK else "217,85,31"
        body = f"""
<div id="filmgrain"></div>
<div id="aurora"><div class="layer l1"></div><div class="layer l2"></div></div>
<canvas id="canvas"></canvas>
<style>
#filmgrain {{
    position:fixed; inset:0; pointer-events:none; z-index:1; opacity:{0.05 if IS_DARK else 0.025};
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E");
    animation: grain 1s steps(4) infinite;
}}
@keyframes grain {{ 0%,100% {{transform:translate(0,0);}} 25% {{transform:translate(-1%,1%);}} 50% {{transform:translate(1%,-1%);}} 75% {{transform:translate(-1%,-1%);}} }}
.layer {{ position:absolute; }}
.l1 {{
    width:160%; height:160%; top:-30%; left:-30%;
    background: radial-gradient(ellipse at 30% 30%, rgba({accent_rgb},0.08) 0%, transparent 55%),
                radial-gradient(ellipse at 75% 70%, rgba({secondary_rgb},0.06) 0%, transparent 50%);
    animation: driftA 22s ease-in-out infinite alternate;
}}
.l2 {{
    width:140%; height:140%; top:-20%; left:-20%;
    background: conic-gradient(from 0deg at 50% 50%, transparent 0deg, rgba({accent_rgb},0.05) 90deg, transparent 180deg, rgba({secondary_rgb},0.04) 270deg, transparent 360deg);
    animation: spin 60s linear infinite;
}}
@keyframes driftA {{ from {{ transform:translate(0,0) scale(1); }} to {{ transform:translate(4%,-3%) scale(1.06); }} }}
@keyframes spin {{ from {{ transform:rotate(0deg); }} to {{ transform:rotate(360deg); }} }}
</style>
<script>
const canvas = document.getElementById('canvas');
canvas.style.position='fixed'; canvas.style.inset='0'; canvas.style.width='100vw'; canvas.style.height='100vh'; canvas.style.zIndex='1'; canvas.style.pointerEvents='none';
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth; canvas.height = window.innerHeight;
const particles = Array.from({{length:36}}, () => ({{
    x:Math.random()*canvas.width, y:Math.random()*canvas.height,
    r:Math.random()*1.6+0.4, vy:-(Math.random()*0.25+0.08), vx:(Math.random()-0.5)*0.08,
    a:Math.random()*0.5+0.1
}}));
function draw() {{
    ctx.clearRect(0,0,canvas.width,canvas.height);
    particles.forEach(p => {{
        p.x+=p.vx; p.y+=p.vy;
        if(p.y<0) {{ p.y=canvas.height; p.x=Math.random()*canvas.width; }}
        ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
        ctx.fillStyle=`rgba({accent_rgb},${{p.a}})`; ctx.fill();
    }});
    requestAnimationFrame(draw);
}}
draw();
window.addEventListener('resize',()=>{{ canvas.width=window.innerWidth; canvas.height=window.innerHeight; }});
</script>
"""
    elif variant == "studio":
        accent_rgb = "255,75,43" if IS_DARK else "232,67,31"
        body = f"""
<div id="grid"></div>
<canvas id="canvas"></canvas>
<style>
#grid {{
    position:fixed; inset:0; pointer-events:none; z-index:1;
    background-image:
        linear-gradient(rgba({accent_rgb},{0.05 if IS_DARK else 0.04}) 1px, transparent 1px),
        linear-gradient(90deg, rgba({accent_rgb},{0.05 if IS_DARK else 0.04}) 1px, transparent 1px);
    background-size: 64px 64px;
    mask: radial-gradient(ellipse 70% 60% at 50% 0%, black 0%, transparent 75%);
    animation: gridFloat 30s ease-in-out infinite alternate;
}}
@keyframes gridFloat {{ from {{ background-position:0 0; }} to {{ background-position:32px 32px; }} }}
</style>
<script>
const canvas = document.getElementById('canvas');
canvas.style.position='fixed'; canvas.style.inset='0'; canvas.style.width='100vw'; canvas.style.height='100vh'; canvas.style.zIndex='1'; canvas.style.pointerEvents='none';
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth; canvas.height = window.innerHeight;
const nodes = Array.from({{length:42}}, () => ({{
    x:Math.random()*canvas.width, y:Math.random()*canvas.height,
    vx:(Math.random()-0.5)*0.3, vy:(Math.random()-0.5)*0.3, r:Math.random()*1.6+0.6, pulse:Math.random()*Math.PI*2
}}));
let mouseX=canvas.width/2, mouseY=canvas.height/2;
function draw() {{
    ctx.clearRect(0,0,canvas.width,canvas.height);
    nodes.forEach(n => {{
        const dx=mouseX-n.x, dy=mouseY-n.y, dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<110) {{ n.vx+=dx/dist*0.012; n.vy+=dy/dist*0.012; }}
        n.vx*=0.99; n.vy*=0.99; n.x+=n.vx; n.y+=n.vy; n.pulse+=0.02;
        if(n.x<0||n.x>canvas.width) n.vx*=-1;
        if(n.y<0||n.y>canvas.height) n.vy*=-1;
    }});
    for(let i=0;i<nodes.length;i++) for(let j=i+1;j<nodes.length;j++) {{
        const dx=nodes[i].x-nodes[j].x, dy=nodes[i].y-nodes[j].y, dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<100) {{
            ctx.beginPath(); ctx.strokeStyle=`rgba({accent_rgb},${{(1-dist/100)*0.15}})`; ctx.lineWidth=0.6;
            ctx.moveTo(nodes[i].x,nodes[i].y); ctx.lineTo(nodes[j].x,nodes[j].y); ctx.stroke();
        }}
    }}
    nodes.forEach(n => {{
        const p=Math.sin(n.pulse)*0.5+0.5, a=0.2+p*0.3;
        ctx.beginPath(); ctx.arc(n.x,n.y,n.r+p*0.6,0,Math.PI*2);
        ctx.fillStyle=`rgba({accent_rgb},${{a}})`; ctx.fill();
    }});
    requestAnimationFrame(draw);
}}
draw();
window.addEventListener('resize',()=>{{ canvas.width=window.innerWidth; canvas.height=window.innerHeight; }});
window.addEventListener('mousemove',e=>{{ mouseX=e.clientX; mouseY=e.clientY; }});
</script>
"""
    else:
        a1 = "255,75,43" if IS_DARK else "232,67,31"
        a2 = "245,158,11" if IS_DARK else "184,120,10"
        body = f"""
<div id="aurora"><div class="layer l1"></div><div class="layer l2"></div></div>
<style>
.layer {{ position:absolute; }}
.l1 {{
    width:180%; height:180%; top:-40%; left:-40%;
    background: radial-gradient(ellipse at 25% 30%, rgba({a1},0.07) 0%, transparent 50%),
                radial-gradient(ellipse at 75% 70%, rgba({a2},0.06) 0%, transparent 50%);
    animation: driftHome 26s ease-in-out infinite alternate;
}}
.l2 {{
    width:150%; height:150%; top:-25%; left:-25%;
    background: conic-gradient(from 90deg at 50% 50%, transparent 0deg, rgba({a1},0.04) 100deg, transparent 200deg, rgba({a2},0.04) 300deg, transparent 360deg);
    animation: spinHome 70s linear infinite;
}}
@keyframes driftHome {{ from {{ transform:translate(0,0) scale(1); }} to {{ transform:translate(3%,-4%) scale(1.05); }} }}
@keyframes spinHome {{ from {{ transform:rotate(0deg); }} to {{ transform:rotate(360deg); }} }}
</style>
"""
    components.html(f"""
<!DOCTYPE html><html><head><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ overflow:hidden; background:transparent; width:100%; height:100%; }}
#aurora {{ position:fixed; inset:0; pointer-events:none; z-index:1; overflow:hidden; }}
</style></head><body>{body}</body></html>
""", height=0, scrolling=False)

# ══════════════════════════════════════════
# OUTPUT CARD
# ══════════════════════════════════════════
def output_card(title, content, accent_color=None, show_copy=True, confidence=None, height=None):
    color = accent_color or T.get("accent", T.get("accentA", "#ff4b2b"))
    h_style = f"max-height:{height}px;overflow-y:auto;" if height else ""
    green = T.get("green", "#4ade80")
    conf_badge = ""
    if confidence:
        conf_badge = f'<div style="display:inline-flex;align-items:center;gap:6px;background:{green}15;border:1px solid {green}40;padding:3px 9px;font-family:Space Mono,monospace;font-size:8px;letter-spacing:2px;color:{green};text-transform:uppercase;"><span style="width:5px;height:5px;background:{green};border-radius:50%;display:inline-block;animation:confPulse 1.5s infinite;"></span>Confidence: {confidence}%</div>'

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
@keyframes confPulse {{ 0%,100%{{opacity:1;box-shadow:0 0 4px {green};}} 50%{{opacity:0.4;box-shadow:none;}} }}
.card {{
    background:{T["glass"]};backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
    border:1px solid {T["glassborder"]};border-left:2px solid {color};
    padding:16px;position:relative;overflow:hidden;{h_style} border-radius:2px;
}}
.card:hover {{ border-color:{color}80;box-shadow:0 0 30px {color}15,0 8px 32px rgba(0,0,0,0.18); }}
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
# READABLE SCRIPT RENDERER
# ══════════════════════════════════════════
def script_teleprompter(sections, confidence=None):
    accent = T.get("purple", T.get("gold", T.get("accent","#ff4b2b")))
    green = T.get("green", "#4ade80")

    rows = []
    if sections.get("hook"):
        rows.append(("HOOK · 0–3 SEC", sections["hook"], T.get("accent","#ff4b2b"), "🔴"))
    if sections.get("visual"):
        rows.append(("ON-SCREEN VISUAL", sections["visual"], T.get("blue", T.get("gold","#f5b942")), "🎥"))
    if sections.get("body"):
        rows.append(("BODY · 3–25 SEC", sections["body"], T.get("text2","#999"), "⚪"))
    if sections.get("cta"):
        rows.append(("CALL TO ACTION · 25–30 SEC", sections["cta"], green, "🟢"))
    if sections.get("audio"):
        rows.append(("AUDIO VIBE", sections["audio"], accent, "🎵"))
    if sections.get("notes"):
        rows.append(("PRODUCTION NOTES", sections["notes"], T.get("text3","#777"), "📝"))

    if not rows:
        full_raw = "\n\n".join(v for v in sections.values() if v)
        output_card("Reel Script", full_raw or "No script generated.", accent, True, confidence, 380)
        return

    conf_html = ""
    if confidence:
        conf_html = f'<div style="display:inline-flex;align-items:center;gap:6px;background:{green}15;border:1px solid {green}40;padding:3px 9px;font-family:Space Mono,monospace;font-size:8px;letter-spacing:2px;color:{green};text-transform:uppercase;margin-bottom:14px;"><span style="width:5px;height:5px;background:{green};border-radius:50%;display:inline-block;"></span>Confidence: {confidence}%</div>'

    blocks = ""
    for label, content, color, icon in rows:
        body_html = content.replace("\n", "<br>")
        blocks += f"""
<div style="border-left:2px solid {color}; padding:12px 16px; margin-bottom:10px; background:{T["glass"]}; border-radius:2px;">
  <div style="font-family:'Space Mono',monospace; font-size:8px; letter-spacing:3px; text-transform:uppercase; color:{color}; margin-bottom:8px;">{icon} {label}</div>
  <div style="font-size:14px; line-height:1.85; color:{T["text"]}; font-family:'Space Grotesk',sans-serif;">{body_html}</div>
</div>"""

    st.markdown(f"""
<div class="reveal">
{conf_html}
{blocks}
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# SCORE BENTO
# ══════════════════════════════════════════
def score_bento(scores, confidence):
    color_map = {
        "viral": T.get("accent", T.get("accentA","#ff4b2b")),
        "hook": T.get("purple", T.get("gold","#f5b942")),
        "engagement": T.get("blue", T.get("gold","#f5b942")),
        "share": T.get("green","#4ade80"),
        "retention": T.get("yellow", T.get("gold","#f5b942")),
        "reach": T.get("orange", T.get("accent","#ff4b2b")),
    }
    labels = {
        "viral": "Viral Potential", "hook": "Hook Strength", "engagement": "Engagement",
        "share": "Shareability", "retention": "Retention", "reach": "Reach Rating"
    }
    cards_html = ""
    for key, val in scores.items():
        color = color_map[key]
        cards_html += f"""
<div class="score-card" style="--accent:{color};" onmousemove="tilt(this,event)" onmouseleave="resetTilt(this)">
    <div class="card-glow"></div>
    <div class="score-label">{labels[key]}</div>
    <div class="score-value" data-target="{val}">0</div>
    <div class="score-bar"><div class="score-fill" data-width="{val}"></div></div>
</div>"""

    green = T.get("green","#4ade80")
    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
* {{ margin:0;padding:0;box-sizing:border-box; }}
body {{ background:transparent;font-family:'Space Mono',monospace;padding:4px 2px; }}
.conf-row {{
    display:flex;align-items:center;gap:12px;margin-bottom:14px;
    padding:10px 14px;background:{T["glass"]};border:1px solid {green}30;
    border-left:2px solid {green}; border-radius:2px;
}}
.conf-label {{ font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text3"]}; }}
.conf-value {{ font-size:22px;font-weight:700;color:{green}; }}
.conf-bar-wrap {{ flex:1;height:3px;background:{T["rule2"]};overflow:hidden; }}
.conf-bar {{ height:100%;background:linear-gradient(90deg,{green},{green}80);width:0;transition:width 1.6s cubic-bezier(0.4,0,0.2,1); }}
.conf-dot {{ width:7px;height:7px;background:{green};border-radius:50%;animation:cpulse 1.5s infinite;flex-shrink:0; }}
@keyframes cpulse {{ 0%,100%{{opacity:1;box-shadow:0 0 6px {green};}} 50%{{opacity:0.3;box-shadow:none;}} }}
.grid {{ display:grid;grid-template-columns:repeat(3,1fr);gap:8px; }}
.score-card {{
    background:{T["glass"]};backdrop-filter:blur(20px);
    border:1px solid {T["glassborder"]};border-top:2px solid var(--accent);
    padding:14px;position:relative;overflow:hidden;border-radius:2px;
    transition:transform 0.2s,box-shadow 0.2s;cursor:default;
}}
.card-glow {{ position:absolute;inset:0;background:radial-gradient(circle at 50% 0%,var(--accent)15 0%,transparent 70%);opacity:0;transition:opacity 0.3s;pointer-events:none; }}
.score-card:hover .card-glow {{ opacity:1; }}
.score-card:hover {{ box-shadow:0 0 20px var(--accent)20,0 4px 20px rgba(0,0,0,0.25); }}
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
    const timer = setInterval(()=>{{ cur = Math.min(cur+step, target); el.textContent = cur + '%'; if(cur>=target) clearInterval(timer); }}, 20);
}})();
document.querySelectorAll('.score-value').forEach(el => {{
    const target = parseInt(el.dataset.target);
    let cur = 0; const step = Math.ceil(target/50);
    const timer = setInterval(()=>{{ cur = Math.min(cur+step, target); el.textContent = cur; if(cur>=target) clearInterval(timer); }}, 25);
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
    vals = [scores[k] for k in ['viral','hook','engagement','share','retention','reach']]
    labels = ['Viral','Hook','Engage','Share','Retain','Reach']
    accent = T.get("accent", T.get("accentA","#ff4b2b"))
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
    data:{{ labels:{labels}, datasets:[{{ data:{vals}, backgroundColor:'{accent}1a', borderColor:'{accent}', borderWidth:1.5, pointBackgroundColor:'{accent}', pointRadius:4, pointHoverRadius:6 }}] }},
    options:{{ responsive:true, scales:{{ r:{{ min:0,max:100, ticks:{{display:false}}, grid:{{color:'{accent}15'}}, angleLines:{{color:'{accent}15'}}, pointLabels:{{color:'{T["text3"]}',font:{{family:'Space Mono',size:9}}}} }} }}, plugins:{{legend:{{display:false}}}}, animation:{{duration:1200,easing:'easeOutQuart'}} }}
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

    accent = T.get("accent", T.get("accentA","#ff4b2b"))
    blue = T.get("blue", T.get("gold","#f5b942"))
    green = T.get("green","#4ade80")

    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Space+Grotesk:wght@400&display=swap" rel="stylesheet">
<style>
* {{ margin:0;padding:0;box-sizing:border-box; }}
body {{ background:transparent;font-family:'Space Grotesk',sans-serif;padding:4px 2px; }}
.group {{ margin-bottom:16px; }}
.group-label {{ font-family:'Space Mono',monospace;font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text3"]};margin-bottom:8px;display:flex;align-items:center;justify-content:space-between; }}
.copy-all {{ background:transparent;border:1px solid {T["rule2"]};color:{T["text4"]};font-family:'Space Mono',monospace;font-size:7px;letter-spacing:1px;padding:2px 7px;cursor:pointer;transition:all 0.15s;text-transform:uppercase; }}
.copy-all:hover {{ border-color:{accent};color:{accent}; }}
.tags {{ display:flex;flex-wrap:wrap;gap:5px; }}
.tag {{ background:{T["bg3"]};border:1px solid {T["rule2"]};color:{T["text2"]};font-family:'Space Mono',monospace;font-size:10px;padding:4px 9px;cursor:pointer;transition:all 0.2s;display:inline-block;position:relative;overflow:hidden;border-radius:2px; }}
.tag::before {{ content:'';position:absolute;inset:0;background:var(--c);opacity:0;transition:opacity 0.2s; }}
.tag:hover::before {{ opacity:0.1; }}
.tag:hover {{ border-color:var(--c);color:var(--c);transform:translateY(-1px); }}
.toast {{ position:fixed;bottom:10px;right:10px;background:{accent};color:#fff;font-family:'Space Mono',monospace;font-size:9px;letter-spacing:2px;padding:6px 12px;opacity:0;transition:opacity 0.2s;pointer-events:none;z-index:999;text-transform:uppercase; }}
.toast.show {{ opacity:1; }}
</style>
</head><body>
<div class="group">
    <div class="group-label"><span>High Volume — 1M+ posts ({len(hv)} tags)</span><button class="copy-all" onclick="copyGroup('hv')">COPY ALL</button></div>
    <div class="tags" id="hv">{tags_html(hv, accent)}</div>
</div>
<div class="group">
    <div class="group-label"><span>Medium Volume — 100K–1M ({len(mv)} tags)</span><button class="copy-all" onclick="copyGroup('mv')">COPY ALL</button></div>
    <div class="tags" id="mv">{tags_html(mv, blue)}</div>
</div>
<div class="group">
    <div class="group-label"><span>Niche Community — Under 100K ({len(nv)} tags)</span><button class="copy-all" onclick="copyGroup('nv')">COPY ALL</button></div>
    <div class="tags" id="nv">{tags_html(nv, green)}</div>
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
# SECTION LABEL / DIVIDERS / TOPBAR / THEME TOGGLE
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
    a1 = T.get("accent", T.get("accentA","#ff4b2b"))
    a2 = T.get("purple", T.get("gold","#f5b942"))
    st.markdown(f"""<div style="height:1px;background:linear-gradient(90deg,{a1},{a2},transparent);
opacity:0.35;margin:24px 0;"></div>""", unsafe_allow_html=True)

def render_topbar(page_label, accent, status_label="STUDIO READY"):
    st.markdown(f"""
<div class="reveal" style="display:flex;align-items:center;justify-content:space-between;
padding:0 24px 0 20px;height:56px;background:{T["bg2"]}cc;
border-bottom:1px solid {T["rule"]};backdrop-filter:blur(20px);position:sticky;top:0;z-index:100;">
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="width:28px;height:28px;background:{accent};
    display:flex;align-items:center;justify-content:center;font-size:14px;border-radius:3px;
    box-shadow:0 0 16px {accent}60;">🎬</div>
    <div style="font-family:'Space Mono',monospace;font-size:13px;font-weight:700;color:{T["text"]};letter-spacing:1px;">
        Reel<span style="color:{accent};">Mind</span> <span style="color:{T["text4"]};">/ {page_label}</span></div>
  </div>
  <div style="display:flex;align-items:center;gap:14px;">
    <div style="display:flex;align-items:center;gap:6px;font-family:'Space Mono',monospace;font-size:8px;color:{T.get('green','#4ade80')};">
        <div style="width:5px;height:5px;background:{T.get('green','#4ade80')};border-radius:50%;animation:pulse 2s infinite;"></div>{status_label}
    </div>
    <div style="font-family:'Space Mono',monospace;font-size:8px;color:{T["text4"]};background:{T["bg3"]};border:1px solid {T["rule2"]};padding:3px 8px;border-radius:2px;">v6.0</div>
  </div>
</div>
""", unsafe_allow_html=True)

def theme_toggle_button():
    icon = "☀️ LIGHT" if IS_DARK else "🌙 DARK"
    st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True)
    if st.button(icon, key="theme_toggle_btn"):
        st.session_state.mode_theme = "light" if IS_DARK else "dark"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# ── PAGE: HOME / LANDING ──
# ══════════════════════════════════════════
if st.session_state.page == "home":
    inject_ambient("home")

    tc1, tc2 = st.columns([6,1])
    with tc1:
        st.markdown(f"""
<div class="reveal" style="display:flex;align-items:center;gap:12px;padding:20px 32px 0;">
    <div style="width:28px;height:28px;background:{T["accentA"]};
    display:flex;align-items:center;justify-content:center;font-size:14px;border-radius:3px;
    box-shadow:0 0 16px {T["accentA"]}60;">🎬</div>
    <div style="font-family:'Space Mono',monospace;font-size:13px;font-weight:700;color:{T["text"]};letter-spacing:1px;">
        Reel<span style="color:{T["accentA"]};">Mind</span> AI</div>
</div>
""", unsafe_allow_html=True)
    with tc2:
        st.markdown("<div style='padding:18px 24px 0 0;'>", unsafe_allow_html=True)
        theme_toggle_button()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
<div class="reveal reveal-d1" style="padding:50px 40px 28px;">
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:6px;text-transform:uppercase;color:{T["text4"]};margin-bottom:22px;">
    AI CREATIVE STUDIO — V6
  </div>
  <div style="font-family:'Fraunces',serif;font-size:clamp(48px,9vw,108px);font-weight:900;font-style:italic;line-height:0.92;letter-spacing:-3px;color:{T["text"]};">
    Two Studios.<br>
    <span style="color:{T["accentA"]};">One</span> <span style="-webkit-text-stroke:1.5px {T["text"]}; color:transparent;">Engine</span>.
  </div>
  <div style="font-size:14px;color:{T["text2"]};max-width:540px;margin:24px 0 0;line-height:1.8;">
    Pick your workspace. Write viral captions, scripts, and hashtag strategy in the Content Studio —
    or storyboard a full cinematic AI animal short in the Video Engine.
  </div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(f"""
<div class="reveal reveal-d2" style="
    border:1px solid {T["rule"]}; border-radius:4px; overflow:hidden;
    margin:0 40px 16px; min-height:340px; position:relative;
    background: linear-gradient(165deg, {STUDIO_DARK['accent'] if IS_DARK else STUDIO_LIGHT['accent']}14, transparent 65%), {T["bg2"]};
    transition: transform 0.35s cubic-bezier(.16,1,.3,1), box-shadow 0.35s;
">
  <div style="padding:32px;">
    <div style="font-family:'Space Mono',monospace;font-size:8px;letter-spacing:4px;text-transform:uppercase;color:{T["accentA"]};margin-bottom:18px;">
      01 / CONTENT STUDIO
    </div>
    <div style="font-family:'Fraunces',serif;font-size:42px;font-weight:900;font-style:italic;color:{T["text"]};margin-bottom:14px;line-height:1;">
      Write &amp;<br>Strategize
    </div>
    <div style="font-size:13px;color:{T["text2"]};line-height:1.8;margin-bottom:28px;max-width:360px;">
      Full caption stacks, hashtag tiers, viral hooks, content series, carousels,
      X threads, and readable reel scripts — every output scored for virality, hook strength, and reach.
    </div>
    <div style="display:flex;gap:24px;flex-wrap:wrap;font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">
      <span>6 generation modes</span><span>·</span><span>30 hashtags</span><span>·</span><span>readable scripts</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
        st.markdown('<div class="generate-btn">', unsafe_allow_html=True)
        if st.button("ENTER CONTENT STUDIO →", key="enter_main"):
            st.session_state.page = "main"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        gold = VIDEO_DARK["gold"] if IS_DARK else VIDEO_LIGHT["gold"]
        st.markdown(f"""
<div class="reveal reveal-d3" style="
    border:1px solid {T["rule"]}; border-radius:4px; overflow:hidden;
    margin:0 40px 16px; min-height:340px; position:relative;
    background: linear-gradient(165deg, {gold}16, transparent 65%), {T["bg2"]};
    transition: transform 0.35s cubic-bezier(.16,1,.3,1), box-shadow 0.35s;
">
  <div style="padding:32px;">
    <div style="font-family:'Space Mono',monospace;font-size:8px;letter-spacing:4px;text-transform:uppercase;color:{gold};margin-bottom:18px;">
      02 / VIDEO ENGINE
    </div>
    <div style="font-family:'Fraunces',serif;font-size:42px;font-weight:900;font-style:italic;color:{T["text"]};margin-bottom:14px;line-height:1;">
      Direct &amp;<br>Produce
    </div>
    <div style="font-size:13px;color:{T["text2"]};line-height:1.8;margin-bottom:28px;max-width:360px;">
      Cinematic AI animal shorts of any length. Pick clip length — 8s or 10s —
      enter total runtime, and get a complete prompt chain with character sheets, first frame, and continuity checklist.
    </div>
    <div style="display:flex;gap:24px;flex-wrap:wrap;font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">
      <span>any duration</span><span>·</span><span>4K Pixar quality</span><span>·</span><span>9:16 vertical</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
        st.markdown('<div class="gold-btn-container">', unsafe_allow_html=True)
        if st.button("ENTER VIDEO ENGINE →", key="enter_video"):
            st.session_state.page = "video"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
<div class="reveal reveal-d4" style="display:flex;gap:48px;flex-wrap:wrap;padding:48px 40px 8px;">
{"".join([f'<div><div style="font-family:Fraunces,serif;font-size:34px;font-weight:900;font-style:italic;color:{T["text"]};">{n}</div><div style="font-family:Space Mono,monospace;font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};margin-top:4px;">{l}</div></div>' for n,l in [("16","Content Niches"),("4","Outputs / Run"),("∞","Video Duration"),("Gemini 2.5","Flash Powered")]])}
</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="padding:48px 40px 24px;border-top:1px solid {T["rule"]};margin-top:40px;
display:flex;justify-content:space-between;align-items:center;">
  <div style="font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">
    REELMIND AI — v6.0 — GEMINI 2.5 FLASH</div>
  <div style="font-family:'Space Mono',monospace;font-size:8px;color:{T["text4"]};background:{T["bg3"]};border:1px solid {T["rule2"]};padding:3px 8px;border-radius:2px;">
    BUILT BY SATVIK SHARMA · NIET 2024–28</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# ── PAGE: CONTENT STUDIO ──
# ══════════════════════════════════════════
elif st.session_state.page == "main":
    inject_ambient("studio")
    st.markdown('<div class="page-zoom-in">', unsafe_allow_html=True)
    render_topbar("Content Studio", T["accent"], "GEMINI LIVE")

    nc1, nc2, nc3 = st.columns([1,5,1])
    with nc1:
        st.markdown("<div style='padding:14px 0 0 24px;'>", unsafe_allow_html=True)
        st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True)
        if st.button("← HOME", key="home_from_main"):
            st.session_state.page = "home"
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)
    with nc3:
        st.markdown("<div style='padding:14px 24px 0 0;'>", unsafe_allow_html=True)
        theme_toggle_button()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
<div class="reveal" style="padding:20px 40px 28px;border-bottom:1px solid {T["rule"]};position:relative;overflow:hidden;">
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:4px;text-transform:uppercase;color:{T["accent"]};margin-bottom:10px;display:flex;align-items:center;gap:10px;">
    <span style="width:18px;height:1px;background:{T["accent"]};display:inline-block;"></span>
    AI Content Engine — Studio Grade
  </div>
  <div style="font-family:'Fraunces',serif;font-size:clamp(36px,6vw,58px);font-weight:900;font-style:italic;line-height:0.95;letter-spacing:-2px;color:{T["text"]};margin-bottom:14px;">
    Content<span style="color:{T["accent"]};"> Studio</span>
  </div>
  <div style="font-size:13px;color:{T["text2"]};max-width:480px;line-height:1.7;margin-bottom:20px;">
    Generate scroll-stopping captions, hashtag stacks, fully readable viral scripts, and thumbnail prompts — powered by Gemini 2.5 Flash.
  </div>
  <div style="display:flex;gap:32px;flex-wrap:wrap;">
    {"".join([f'<div><div style="font-family:Space Mono,monospace;font-size:20px;font-weight:700;color:{T["text"]};">{n}</div><div style="font-family:Space Mono,monospace;font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">{l}</div></div>' for n,l in [("4","Outputs/run"),("30","Hashtags"),("3","Captions"),("16","Niches")]])}
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='padding:0 40px;'>", unsafe_allow_html=True)

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
                st.markdown(f'<div style="background:{T["bg3"]};border:1px solid {T["rule"]};padding:8px 10px;margin-bottom:3px;border-radius:2px;"><div style="font-size:12px;font-weight:500;color:{T["text"]};">{h["topic"][:40]}</div><div style="font-family:Space Mono,monospace;font-size:7px;color:{T["text4"]};">{h["niche"][:30]} · {h["time"]}</div></div>', unsafe_allow_html=True)

    if not generate_btn:
        if not st.session_state.last_result:
            st.markdown(f"""
<div class="reveal" style="display:flex;flex-direction:column;align-items:center;justify-content:center;
min-height:340px;border:1px dashed {T["rule2"]};margin:32px 0;gap:14px;border-radius:4px;">
  <div style="font-size:38px;filter:grayscale(1);opacity:0.18;">🎬</div>
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:{T["text4"]};">Configure & Generate</div>
  <div style="font-size:12px;color:{T["text4"]};font-family:'Space Mono',monospace;">Your content will appear here</div>
</div>""", unsafe_allow_html=True)

    if generate_btn:
        if not topic.strip():
            st.warning("Please enter a topic first.")
            st.stop()

        steps_ph = st.empty()
        step_names = [
            "Analyzing topic & niche...",
            "Building caption stack...",
            "Generating hashtag strategy...",
            "Writing readable reel script...",
            "Designing thumbnail prompt...",
            "Calculating content scores...",
        ]

        def render_steps(done):
            rows = ""
            for i, name in enumerate(step_names):
                if i < done: col, icon = T.get("green","#4ade80"), "✓"
                elif i == done: col, icon = T["accent"], "◌"
                else: col, icon = T["text4"], str(i+1)
                rows += f'<div style="display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid {T["rule"]};font-family:Space Mono,monospace;font-size:10px;letter-spacing:1px;color:{col};"><span style="width:18px;text-align:center;">{icon}</span><span>{name}</span></div>'
            return f'<div style="background:{T["bg2"]};border:1px solid {T["rule"]};padding:24px;margin:20px 0;border-radius:2px;">{rows}</div>'

        for i in range(len(step_names)):
            steps_ph.markdown(render_steps(i), unsafe_allow_html=True)
            time.sleep(0.4)

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

        section_label("Content Score Card")
        score_bento(scores, confidence)
        gradient_divider()

        col_r, col_a = st.columns([1,1])
        with col_r:
            section_label("Content Radar")
            radar_component(scores)
        with col_a:
            section_label("Best Posting Times")
            times = POSTING_TIMES.get(platform, POSTING_TIMES["Instagram Reels"])
            green = T.get("green","#4ade80")
            t_html = "".join([
                f'<span style="display:inline-block;background:{T["bg3"]};border:1px solid {green if best else T["rule2"]};padding:6px 11px;font-family:Space Mono,monospace;font-size:9px;color:{green if best else T["text3"]};margin:3px;border-radius:2px;{"background:" + green + "10;" if best else ""}">{t}<small style="display:block;font-size:7px;letter-spacing:1px;">{label}{"  ★" if best else ""}</small></span>'
                for t, label, best in times
            ])
            st.markdown(t_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            section_label("Niche Saturation")
            sat = SATURATION.get(niche, "MEDIUM — competitive but approachable with strong hooks.")
            st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:10px;color:{T["text2"]};line-height:1.6;">{sat}</div>', unsafe_allow_html=True)

        gradient_divider()

        if "Full Content" in mode and result:
            tab1, tab2, tab3, tab4 = st.tabs(["📝 Captions","#️⃣ Hashtags","🎬 Script","🖼️ Thumbnail"])

            with tab1:
                short, med, long_cap = parse_captions(result.get("captions",""))
                cap_data = [
                    (short, "Short Caption", "s", T["accent"]),
                    (med, "Medium Caption", "m", T.get("blue", T["accent"])),
                    (long_cap, "Long Caption", "l", T.get("purple", T["accent"]))
                ]
                for cap_text, label, key, color in cap_data:
                    wc = len(cap_text.split())
                    output_card(f"{label} — {wc} words", cap_text, color, show_copy=True, confidence=confidence, height=140)
                    st.download_button(f"↓ DOWNLOAD {label.split()[0].upper()}", cap_text,
                        file_name=f"{label.lower().replace(' ','_')}.txt", key=f"dl_{key}")

            with tab2:
                hv, mv, nv = parse_hashtags(result.get("hashtags",""))
                hashtag_component(hv, mv, nv)
                all_tags = " ".join(hv+mv+nv)
                st.download_button("↓ DOWNLOAD ALL HASHTAGS", all_tags, file_name="hashtags.txt", key="dl_ht")

            with tab3:
                script_sections = parse_script_sections(result.get("script",""))
                section_label("Reel Script — Ready to Perform")
                script_teleprompter(script_sections, confidence)
                st.markdown(f"""
<div style="background:{T.get("purple",T["accent"])}10;border:1px solid {T.get("purple",T["accent"])}30;border-left:2px solid {T.get("purple",T["accent"])};padding:12px 14px;margin-top:8px;font-family:'Space Mono',monospace;font-size:9px;color:{T.get("purple",T["accent"])};letter-spacing:1px;border-radius:2px;">
💡 TIP: Read each section out loud exactly as written — every line is a complete spoken sentence, ready to perform.
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
                output_card("Ideogram / Gemini Image Prompt", ideogram, T.get("blue",T["accent"]), show_copy=True, height=180)
                st.download_button("↓ IDEOGRAM PROMPT", ideogram, file_name="ideogram_prompt.txt", key="dl_id")

            gradient_divider()
            full = f"REELMIND AI v6.0\nTopic:{topic} | Niche:{niche} | Platform:{platform}\n{'='*60}\n\n{result.get('raw','')}"
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("↓ DOWNLOAD FULL PACK", full,
                    file_name=f"reelmind_{topic[:20].replace(' ','_')}_full.txt", key="dl_full")
            with c2:
                st.download_button("↓ DOWNLOAD RAW", result.get("raw",""),
                    file_name="reelmind_raw.txt", key="dl_raw")

            gradient_divider()
            gold = T.get("gold", T["accent"])
            st.markdown(f"""
<div style="background:linear-gradient(135deg,{gold}10,transparent);border:1px solid {gold}30;border-left:3px solid {gold};padding:20px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;border-radius:2px;">
  <div>
    <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:{gold};margin-bottom:6px;">🎥 READY TO CREATE A VIDEO?</div>
    <div style="font-size:13px;color:{T["text3"]};">Turn this content into a complete AI video production package with story options, character sheets, and a full prompt chain.</div>
  </div>
</div>
""", unsafe_allow_html=True)
            st.markdown('<div class="gold-btn-container">', unsafe_allow_html=True)
            if st.button("🎥 OPEN VIDEO ENGINE", key="goto_video_bottom"):
                st.session_state.page = "video"
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
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# ── PAGE: VIDEO ENGINE ──
# ══════════════════════════════════════════
elif st.session_state.page == "video":
    inject_ambient("video")
    st.markdown('<div class="page-zoom-in">', unsafe_allow_html=True)
    render_topbar("Video Engine", T["gold"], "GEMINI LIVE")

    nc1, nc2, nc3 = st.columns([1,5,1])
    with nc1:
        st.markdown("<div style='padding:14px 0 0 24px;'>", unsafe_allow_html=True)
        st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True)
        if st.button("← HOME", key="home_from_video"):
            st.session_state.page = "home"
            st.session_state.video_stories = None
            st.session_state.video_package = None
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)
    with nc3:
        st.markdown("<div style='padding:14px 24px 0 0;'>", unsafe_allow_html=True)
        theme_toggle_button()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
<div class="reveal" style="padding:20px 40px 24px;border-bottom:1px solid {T["gold"]}30;position:relative;overflow:hidden;">
  <div style="position:absolute;inset:0;background:radial-gradient(ellipse at 20% 50%,{T["gold"]}08 0%,transparent 60%);pointer-events:none;"></div>
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:4px;text-transform:uppercase;color:{T["gold"]};margin-bottom:10px;display:flex;align-items:center;gap:10px;">
    <span style="width:18px;height:1px;background:{T["gold"]};display:inline-block;"></span>
    AI Video Story Engine — Cinematic Grade
  </div>
  <div style="font-family:'Fraunces',serif;font-size:clamp(32px,6vw,48px);font-weight:900;font-style:italic;line-height:0.95;letter-spacing:-2px;color:{T["text"]};margin-bottom:12px;">
    Video <span style="color:{T["gold"]};">Story</span>
    <span style="color:{T["text4"]};">Engine</span>
  </div>
  <div style="font-size:13px;color:{T["text3"]};max-width:560px;line-height:1.7;margin-bottom:8px;">
    Generate complete production-ready video packages for ANY duration: 3 story options with viral scores,
    character design sheets, first frame prompts, and a full prompt chain for Google Flow or Gemini Video.
  </div>
  <div style="display:flex;gap:24px;flex-wrap:wrap;margin-top:14px;">
    {"".join([f'<div><div style="font-family:Space Mono,monospace;font-size:18px;font-weight:700;color:{T["gold"]};">{n}</div><div style="font-family:Space Mono,monospace;font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">{l}</div></div>' for n,l in [("Any","Duration"),("8/10s","Clip Length"),("4K","Pixar Quality"),("9:16","Vertical")]]) }
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='padding:0 40px;'>", unsafe_allow_html=True)

    gradient_divider()
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
        v_style = st.selectbox("Animation Style", [
            "Pixar","Disney","DreamWorks","Anime","Chibi","Realistic"
        ])
        v_platform = st.selectbox("Platform", ["Instagram Reels","TikTok","YouTube Shorts"])
    with cd3:
        v_ending = st.selectbox("Ending Type", [
            "Funny / Comedic","Emotional / Heartwarming",
            "Twist / Unexpected","Happy","Random"
        ])

    section_label("Video Length")
    dl1, dl2, dl3 = st.columns([1.2,1,1.5])
    with dl1:
        v_duration = st.number_input("Total Duration (seconds)", min_value=8, max_value=600, value=24, step=8,
            help="Enter any total runtime, e.g. 32, 60, 160 — any positive number works.")
    with dl2:
        v_clip_length = st.radio("Clip Length", ["8s","10s"], horizontal=True)
        clip_len = int(v_clip_length.replace("s",""))
    with dl3:
        num_prompts_preview = max(1, round(v_duration / clip_len))
        actual_total = num_prompts_preview * clip_len
        diff_note = "" if actual_total == v_duration else f" (≈{actual_total}s actual)"
        st.markdown(f"""
<div style="background:{T["glass"]};border:1px solid {T["gold"]}30;border-left:2px solid {T["gold"]};padding:14px;border-radius:2px;margin-top:18px;">
  <div style="font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["gold"]};margin-bottom:4px;">CLIPS TO GENERATE</div>
  <div style="font-family:'Fraunces',serif;font-size:28px;font-weight:900;font-style:italic;color:{T["text"]};">{num_prompts_preview} × {clip_len}s{diff_note}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="generate-btn">', unsafe_allow_html=True)
    generate_stories_btn = st.button("→ GENERATE STORIES", key="gen_stories", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("📖 HOW TO USE THIS — FULL WORKFLOW GUIDE"):
        st.markdown(f"""
<div style="font-family:'Space Grotesk',sans-serif;font-size:13px;color:{T["text2"]};line-height:1.9;padding:8px 0;">

<strong style="color:{T["text"]};font-family:'Space Mono',monospace;font-size:10px;letter-spacing:2px;">STEP 1 — GENERATE STORIES</strong><br>
Select your character, story type, duration and style. The AI generates 3 different story options with viral scores, emotion scores, and retention estimates. Pick the one that resonates most.

<br><br><strong style="color:{T["text"]};font-family:'Space Mono',monospace;font-size:10px;letter-spacing:2px;">STEP 2 — GET YOUR PRODUCTION PACKAGE</strong><br>
Paste your chosen story below. The AI generates: character design sheet prompts (front/back/side/expressions), environment analysis, a story beat plan, and a master First Frame prompt.

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

    if generate_stories_btn:
        v_animal_clean = v_animal.split(" ")[0] if " " in v_animal else v_animal
        st.session_state["v_animal_stored"] = v_animal_clean
        st.session_state["v_style_stored"] = v_style
        st.session_state["v_duration_stored"] = v_duration
        st.session_state["v_platform_stored"] = v_platform
        st.session_state["v_clip_len_stored"] = clip_len

        story_ph = st.empty()
        story_ph.markdown(f"""
<div style="background:{T["bg2"]};border:1px solid {T["gold"]}30;border-left:3px solid {T["gold"]};padding:24px;margin:20px 0;border-radius:2px;">
<div style="font-family:Space Mono,monospace;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:{T["gold"]};margin-bottom:12px;">⚡ Generating viral story options...</div>
<div style="font-family:Space Grotesk,sans-serif;font-size:13px;color:{T["text3"]};">Analyzing viral patterns for {v_animal_clean} {v_story_type} story ({v_duration}s)...</div>
</div>
""", unsafe_allow_html=True)

        stories = generate_video_story(
            animal=v_animal_clean, story_type=v_story_type, duration=v_duration,
            style=v_style, platform=v_platform, ending_type=v_ending
        )
        st.session_state.video_stories = stories
        st.session_state.video_package = None

        story_ph.empty()
        st.rerun()

    if not st.session_state.video_stories:
        st.markdown(f"""
<div class="reveal" style="display:flex;flex-direction:column;align-items:center;justify-content:center;
min-height:260px;border:1px dashed {T["rule2"]};margin:32px 0;gap:14px;border-radius:4px;">
  <div style="font-size:38px;filter:grayscale(1);opacity:0.18;">🎥</div>
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:{T["text4"]};">Configure & Generate</div>
  <div style="font-size:12px;color:{T["text4"]};font-family:'Space Mono',monospace;">Your story options will appear here</div>
</div>""", unsafe_allow_html=True)

    if st.session_state.video_stories:
        gradient_divider()
        section_label("Choose Your Story")

        output_card("3 STORY OPTIONS — SELECT YOUR FAVOURITE",
            st.session_state.video_stories.get("stories", ""), T["gold"], show_copy=True, height=500)

        st.markdown("<br>", unsafe_allow_html=True)
        section_label("Generate Full Production Package")
        story_input = st.text_area(
            "Paste your chosen story details here (copy from above)",
            placeholder="Paste the STORY [N] section you want to use, including the title, logline, hook, goal, conflict, escalation, payoff, and ending...",
            height=120, key="chosen_story"
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
            v_clip_len_stored = st.session_state.get("v_clip_len_stored", 8)

            pkg_ph = st.empty()
            pkg_steps = [
                "Analyzing story structure...",
                "Planning story beats per clip...",
                "Designing character sheets...",
                "Building environment map...",
                "Creating first frame prompt...",
                "Writing full prompt chain...",
                "Building continuity checklist...",
            ]

            def render_pkg_steps(done):
                rows = ""
                for i, name in enumerate(pkg_steps):
                    if i < done: col, icon = T["gold"], "✓"
                    elif i == done: col, icon = T["accent"], "◌"
                    else: col, icon = T["text4"], str(i+1)
                    rows += f'<div style="display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid {T["rule"]};font-family:Space Mono,monospace;font-size:10px;letter-spacing:1px;color:{col};"><span style="width:18px;text-align:center;">{icon}</span><span>{name}</span></div>'
                return f'<div style="background:{T["bg2"]};border:1px solid {T["gold"]}30;border-left:2px solid {T["gold"]};padding:24px;margin:20px 0;border-radius:2px;">{rows}</div>'

            for i in range(len(pkg_steps)):
                pkg_ph.markdown(render_pkg_steps(i), unsafe_allow_html=True)
                time.sleep(0.4)

            pkg = generate_video_full_package(
                animal=v_animal_stored, story_title=story_title_input or "My Story",
                story_logline=story_input[:200], story_details=story_input,
                style=v_style_stored, duration=v_duration_stored,
                platform=v_platform_stored, clip_length=v_clip_len_stored
            )
            st.session_state.video_package = pkg

            pkg_ph.markdown(render_pkg_steps(len(pkg_steps)), unsafe_allow_html=True)
            time.sleep(0.3)
            pkg_ph.empty()
            st.rerun()

        if st.session_state.video_package:
            pkg = st.session_state.video_package
            gradient_divider()
            section_label(f"Production Package — {pkg.get('num_prompts',0)} × {pkg.get('clip_length',8)}s clips ({pkg.get('duration',0)}s total)")

            if pkg.get("beats"):
                with st.expander("📋 STORY BEAT PLAN (one beat per clip)"):
                    output_card("STORY BEATS", pkg.get("beats",""), T["gold"], show_copy=True, height=240)

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
                    pkg.get("character_analysis",""), file_name="character_design.txt", key="dl_char")

            with tab_frame:
                output_card("MASTER FIRST FRAME PROMPT",
                    pkg.get("first_frame",""), T["gold"], show_copy=True, height=350)
                st.markdown(f"""
<div style="background:{T["gold"]}10;border:1px solid {T["gold"]}30;border-left:2px solid {T["gold"]};padding:14px;margin-top:12px;font-family:'Space Mono',monospace;font-size:9px;letter-spacing:1px;color:{T["gold"]};border-radius:2px;">
⚡ USAGE: Paste this prompt into Midjourney (--ar 9:16 --v 6) or Ideogram. 
This establishes your entire scene. Use the generated image as the starting point for Prompt 1 in Google Flow.
</div>
""", unsafe_allow_html=True)
                st.download_button("↓ DOWNLOAD FIRST FRAME PROMPT",
                    pkg.get("first_frame",""), file_name="first_frame_prompt.txt", key="dl_frame")

            with tab_prompts:
                prompts = pkg.get("prompts", [])
                if prompts:
                    for p in prompts:
                        n = p["number"]
                        is_last = (n == len(prompts))
                        label_suffix = " — FINAL CLIP" if is_last else f" of {len(prompts)}"
                        accent = T["gold"] if is_last else T["accent"]
                        title = f"PROMPT {n}{label_suffix}"
                        if p.get("beat"):
                            title += f" — {p['beat'][:60]}"
                        output_card(title, p["text"], accent, show_copy=True, height=350)
                        if n < len(prompts):
                            st.markdown(f"""
<div style="background:{T["bg3"]};border:1px solid {T["rule"]};padding:10px 14px;margin:8px 0;font-family:'Space Mono',monospace;font-size:9px;color:{T["text4"]};letter-spacing:1px;border-radius:2px;">
📸 AFTER GENERATING CLIP {n}: Pause at the very last frame → Screenshot it → Upload that screenshot + character sheets when generating Prompt {n+1}
</div>
""", unsafe_allow_html=True)

                    all_prompts_text = f"REELMIND AI — VIDEO PROMPT CHAIN ({pkg.get('num_prompts',0)} x {pkg.get('clip_length',8)}s = {pkg.get('duration',0)}s)\n{'='*60}\n\n"
                    all_prompts_text += pkg.get("first_frame","") + "\n\n" + "="*60 + "\n\n"
                    for p in prompts:
                        all_prompts_text += f"PROMPT {p['number']}:\n{p['text']}\n\n{'='*60}\n\n"
                    st.download_button("↓ DOWNLOAD ALL PROMPTS", all_prompts_text,
                        file_name="video_prompt_chain.txt", key="dl_all_prompts")

            with tab_cont:
                output_card("CONTINUITY CHECKLIST — CHECK BETWEEN EVERY CLIP",
                    pkg.get("continuity",""), T.get("green","#4ade80"), show_copy=True, height=350)
                st.download_button("↓ DOWNLOAD CHECKLIST",
                    pkg.get("continuity",""), file_name="continuity_checklist.txt", key="dl_cont")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='padding:0 40px;'>", unsafe_allow_html=True)
    gradient_divider()
    st.markdown(f"""
<div style="background:linear-gradient(135deg,{T["accent"]}10,transparent);border:1px solid {T["accent"]}30;border-left:3px solid {T["accent"]};padding:20px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;border-radius:2px;">
  <div>
    <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:{T["accent"]};margin-bottom:6px;">✍️ NEED WRITTEN CONTENT TOO?</div>
    <div style="font-size:13px;color:{T["text3"]};">Generate captions, hashtags, and scripts for this same content in the Content Studio.</div>
  </div>
</div>
""", unsafe_allow_html=True)
    st.markdown('<div class="generate-btn">', unsafe_allow_html=True)
    if st.button("→ OPEN CONTENT STUDIO", key="goto_main_from_video"):
        st.session_state.page = "main"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════
if st.session_state.page in ("main","video"):
    st.markdown(f"""
<div style="padding:16px 40px;border-top:1px solid {T["rule"]};background:{T["bg2"]};
display:flex;justify-content:space-between;align-items:center;margin-top:40px;">
  <div style="font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">
    REELMIND AI — v6.0 — GEMINI 2.5 FLASH</div>
  <div style="font-family:'Space Mono',monospace;font-size:8px;color:{T["text4"]};background:{T["bg3"]};border:1px solid {T["rule2"]};padding:3px 8px;border-radius:2px;">
    BUILT BY SATVIK SHARMA · NIET 2024–28</div>
</div>
""", unsafe_allow_html=True)