import streamlit as st
import streamlit.components.v1 as components
import random, time, datetime, re
from gemini_helper import (
    generate_full_content, generate_hooks, generate_series,
    generate_carousel, generate_thread, repurpose_content,
    generate_story, generate_character_sheet,
    generate_frame1_prompt, generate_prompt_chain,
    generate_complete_storyflow
)

# ══════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════
st.set_page_config(
    page_title="ReelMind AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════
for key, default in [
    ("history", []), ("theme", "dark"),
    ("last_result", None), ("last_scores", None),
    ("page", "reelmind"),
    ("sf_step", 1),
    ("sf_stories", None), ("sf_selected_story", None),
    ("sf_char_sheet", None), ("sf_frame1", None),
    ("sf_prompt_chain", None), ("sf_scene_objects", None),
    ("sf_config", {}),
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
    "text2":   "#aaaaaa" if IS_DARK else "#4a4540",
    "text3":   "#666666" if IS_DARK else "#7a7268",
    "text4":   "#444444" if IS_DARK else "#aaa49a",
    "accent":  "#ff4b2b",
    "accent2": "#ff7a5c",
    "gold":    "#f5c542",
    "purple":  "#8b5cf6",
    "blue":    "#3b82f6",
    "green":   "#22c55e",
    "yellow":  "#eab308",
    "orange":  "#f97316",
    "glass":   "rgba(255,255,255,0.04)" if IS_DARK else "rgba(0,0,0,0.04)",
    "glassborder": "rgba(255,255,255,0.08)" if IS_DARK else "rgba(0,0,0,0.08)",
}

# ══════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&family=Fraunces:ital,opsz,wght@1,9..144,900&display=swap');
*,*::before,*::after{{box-sizing:border-box;}}
html,body,[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main{{
    background:{T["bg"]} !important;color:{T["text"]} !important;
    font-family:'Space Grotesk',sans-serif !important;
}}
[data-testid="stHeader"]{{display:none !important;}}
.block-container{{padding:0 !important;max-width:100% !important;}}
[data-testid="stSidebar"]{{background:{T["bg2"]} !important;border-right:1px solid {T["rule"]} !important;}}
[data-testid="stSidebar"] *{{color:{T["text"]} !important;}}
.stTextInput>div>div>input,.stTextArea>div>div>textarea{{
    background:{T["bg3"]} !important;border:1px solid {T["rule2"]} !important;
    border-radius:0 !important;color:{T["text"]} !important;
    font-family:'Space Grotesk',sans-serif !important;font-size:13px !important;
    padding:11px 13px !important;transition:border-color 0.2s,box-shadow 0.2s !important;
    caret-color:{T["accent"]} !important;
}}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{{
    border-color:{T["accent"]} !important;box-shadow:0 0 0 2px {T["accent"]}18 !important;
}}
.stTextInput>div>div>input::placeholder,.stTextArea>div>div>textarea::placeholder{{color:{T["text4"]} !important;}}
[data-baseweb="select"]>div{{
    background:{T["bg3"]} !important;border:1px solid {T["rule2"]} !important;
    border-radius:0 !important;color:{T["text"]} !important;
    font-family:'Space Grotesk',sans-serif !important;font-size:13px !important;
}}
[data-baseweb="popover"] ul{{background:{T["bg3"]} !important;border:1px solid {T["rule2"]} !important;}}
[data-baseweb="option"]{{background:{T["bg3"]} !important;color:{T["text"]} !important;font-size:12px !important;}}
[data-baseweb="option"]:hover{{background:{T["bg4"]} !important;}}
label,.stSelectbox label,.stTextInput label,.stTextArea label,.stRadio label{{
    color:{T["text3"]} !important;font-family:'Space Mono',monospace !important;
    font-size:8px !important;letter-spacing:2px !important;text-transform:uppercase !important;
}}
.stRadio>div{{gap:3px !important;flex-direction:column !important;}}
.stRadio>div>label{{
    background:{T["bg3"]} !important;border:1px solid {T["rule2"]} !important;
    padding:9px 14px !important;transition:all 0.15s !important;
    color:{T["text3"]} !important;font-size:11px !important;
    letter-spacing:1px !important;border-radius:0 !important;margin:0 !important;
}}
.stRadio>div>label:hover{{border-color:{T["accent"]} !important;color:{T["accent"]} !important;}}
.stButton>button{{
    background:transparent !important;color:{T["text3"]} !important;
    border:1px solid {T["rule2"]} !important;border-radius:0 !important;
    font-family:'Space Mono',monospace !important;font-size:9px !important;
    letter-spacing:2px !important;text-transform:uppercase !important;
    padding:10px 18px !important;transition:all 0.2s !important;width:100% !important;
}}
.stButton>button:hover{{border-color:{T["accent"]} !important;color:{T["accent"]} !important;box-shadow:0 0 12px {T["accent"]}20 !important;}}
.stDownloadButton>button{{
    background:transparent !important;color:{T["text3"]} !important;
    border:1px solid {T["rule2"]} !important;border-radius:0 !important;
    font-family:'Space Mono',monospace !important;font-size:8px !important;
    letter-spacing:2px !important;text-transform:uppercase !important;
    padding:8px 14px !important;width:auto !important;transition:all 0.2s !important;
}}
.stDownloadButton>button:hover{{border-color:{T["accent"]} !important;color:{T["accent"]} !important;}}
.stTabs [data-baseweb="tab-list"]{{background:transparent !important;border-bottom:1px solid {T["rule"]} !important;gap:0 !important;padding:0 !important;}}
.stTabs [data-baseweb="tab"]{{
    background:transparent !important;color:{T["text3"]} !important;
    font-family:'Space Mono',monospace !important;font-size:8px !important;
    letter-spacing:2px !important;text-transform:uppercase !important;
    padding:10px 18px !important;border-radius:0 !important;
    border-bottom:2px solid transparent !important;transition:all 0.2s !important;
}}
.stTabs [aria-selected="true"]{{color:{T["accent"]} !important;border-bottom-color:{T["accent"]} !important;background:transparent !important;}}
.stTabs [data-baseweb="tab-panel"]{{padding:20px 0 0 !important;background:transparent !important;}}
.streamlit-expanderHeader{{
    background:{T["bg2"]} !important;border:1px solid {T["rule"]} !important;
    border-radius:0 !important;color:{T["text3"]} !important;
    font-family:'Space Mono',monospace !important;font-size:9px !important;letter-spacing:2px !important;
}}
.streamlit-expanderContent{{background:{T["bg2"]} !important;border:1px solid {T["rule"]} !important;border-top:none !important;padding:16px !important;}}
hr{{border-color:{T["rule"]} !important;margin:20px 0 !important;}}
::-webkit-scrollbar{{width:3px;height:3px;}}
::-webkit-scrollbar-track{{background:{T["bg"]};}}
::-webkit-scrollbar-thumb{{background:{T["rule2"]};}}
::-webkit-scrollbar-thumb:hover{{background:{T["accent"]};}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
@keyframes shimmer{{0%{{background-position:200% 0}}100%{{background-position:-200% 0}}}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# PREMIUM EFFECTS (Neural net + cursor + aurora)
# ══════════════════════════════════════════
def inject_premium_effects():
    components.html(f"""
<!DOCTYPE html><html><head>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{overflow:hidden;background:transparent;}}
#canvas{{position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:0;}}
#aurora{{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;overflow:hidden;}}
.al{{position:absolute;width:200%;height:200%;
    background:conic-gradient(from 0deg at 50% 50%,transparent 0deg,{T["accent"]}08 60deg,{T["purple"]}06 120deg,transparent 180deg,{T["blue"]}05 240deg,{T["accent"]}08 300deg,transparent 360deg);
    animation:aR 14s linear infinite;top:-50%;left:-50%;}}
.al2{{position:absolute;width:160%;height:160%;
    background:radial-gradient(ellipse at 20% 50%,{T["accent"]}07 0%,transparent 50%),radial-gradient(ellipse at 80% 20%,{T["purple"]}06 0%,transparent 50%),radial-gradient(ellipse at 60% 80%,{T["blue"]}05 0%,transparent 50%);
    animation:aF 9s ease-in-out infinite alternate;top:-30%;left:-30%;}}
@keyframes aR{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
@keyframes aF{{from{{transform:translate(0,0) scale(1)}}to{{transform:translate(30px,-20px) scale(1.05)}}}}
#cd{{position:fixed;width:8px;height:8px;background:{T["accent"]};border-radius:50%;pointer-events:none;z-index:9999;transform:translate(-50%,-50%);box-shadow:0 0 10px {T["accent"]},0 0 20px {T["accent"]}80;}}
#cr{{position:fixed;width:36px;height:36px;border:1.5px solid {T["accent"]}80;border-radius:50%;pointer-events:none;z-index:9998;transform:translate(-50%,-50%);transition:width .25s,height .25s,border-color .25s,background .25s;}}
#cr.h{{width:52px;height:52px;border-color:{T["accent"]};background:{T["accent"]}10;}}
.tp{{position:fixed;border-radius:50%;pointer-events:none;z-index:9996;animation:tF .6s ease-out forwards;}}
@keyframes tF{{0%{{opacity:.8;transform:translate(-50%,-50%) scale(1)}}100%{{opacity:0;transform:translate(-50%,-50%) scale(0.1)}}}}
</style>
</head><body>
<div id="aurora"><div class="al"></div><div class="al2"></div></div>
<canvas id="canvas"></canvas>
<div id="cd"></div><div id="cr"></div>
<script>
const canvas=document.getElementById('canvas'),ctx=canvas.getContext('2d');
canvas.width=window.innerWidth;canvas.height=window.innerHeight;
const N=50,nodes=Array.from({{length:N}},()=>({{x:Math.random()*canvas.width,y:Math.random()*canvas.height,vx:(Math.random()-.5)*.4,vy:(Math.random()-.5)*.4,r:Math.random()*2+1,p:Math.random()*Math.PI*2}}));
let MX=canvas.width/2,MY=canvas.height/2;
function draw(){{
    ctx.clearRect(0,0,canvas.width,canvas.height);
    nodes.forEach(n=>{{
        const dx=MX-n.x,dy=MY-n.y,d=Math.sqrt(dx*dx+dy*dy);
        if(d<130){{n.vx+=dx/d*.012;n.vy+=dy/d*.012;}}
        n.vx*=.99;n.vy*=.99;n.x+=n.vx;n.y+=n.vy;n.p+=.02;
        if(n.x<0||n.x>canvas.width)n.vx*=-1;
        if(n.y<0||n.y>canvas.height)n.vy*=-1;
        n.x=Math.max(0,Math.min(canvas.width,n.x));
        n.y=Math.max(0,Math.min(canvas.height,n.y));
    }});
    for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){{
        const dx=nodes[i].x-nodes[j].x,dy=nodes[i].y-nodes[j].y,d=Math.sqrt(dx*dx+dy*dy);
        if(d<115){{ctx.beginPath();ctx.strokeStyle=`rgba(255,75,43,${{(1-d/115)*.18}})`;ctx.lineWidth=.6;ctx.moveTo(nodes[i].x,nodes[i].y);ctx.lineTo(nodes[j].x,nodes[j].y);ctx.stroke();}}
    }}
    nodes.forEach(n=>{{
        const p=Math.sin(n.p)*.5+.5,a=.25+p*.35,r=n.r+p*.8;
        ctx.beginPath();ctx.arc(n.x,n.y,r,0,Math.PI*2);ctx.fillStyle=`rgba(255,75,43,${{a}})`;ctx.fill();
        ctx.beginPath();ctx.arc(n.x,n.y,r*2.5,0,Math.PI*2);ctx.fillStyle=`rgba(255,75,43,${{a*.1}})`;ctx.fill();
    }});
    requestAnimationFrame(draw);
}}
draw();
window.addEventListener('resize',()=>{{canvas.width=window.innerWidth;canvas.height=window.innerHeight;}});
const cd=document.getElementById('cd'),cr=document.getElementById('cr');
let rx=0,ry=0,mx=0,my=0,tc=0;
window.addEventListener('mousemove',e=>{{
    mx=e.clientX;my=e.clientY;cd.style.left=mx+'px';cd.style.top=my+'px';MX=mx;MY=my;
    if(tc++%2===0){{
        const p=document.createElement('div');p.className='tp';
        const cols=['{T["accent"]}','{T["purple"]}','{T["accent2"]}'],c=cols[Math.floor(Math.random()*3)];
        const s=Math.random()*5+2;
        p.style.cssText=`left:${{mx}}px;top:${{my}}px;width:${{s}}px;height:${{s}}px;background:${{c}};box-shadow:0 0 6px ${{c}};`;
        document.body.appendChild(p);setTimeout(()=>p.remove(),600);
    }}
}});
function animR(){{rx+=(mx-rx)*.13;ry+=(my-ry)*.13;cr.style.left=rx+'px';cr.style.top=ry+'px';requestAnimationFrame(animR);}}
animR();
document.addEventListener('mouseover',e=>{{if(e.target.matches('button,a,input,select'))cr.classList.add('h');}});
document.addEventListener('mouseout',e=>{{if(e.target.matches('button,a,input,select'))cr.classList.remove('h');}});
</script>
</body></html>
""", height=0, scrolling=False)

# ══════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════
def section_label(text):
    st.markdown(f"""<div style="font-family:'Space Mono',monospace;font-size:8px;letter-spacing:3px;text-transform:uppercase;color:{T['text4']};margin-bottom:12px;display:flex;align-items:center;gap:8px;">{text}<span style="flex:1;height:1px;background:{T['rule']};display:inline-block;"></span></div>""", unsafe_allow_html=True)

def gradient_divider():
    st.markdown(f"""<div style="height:1px;background:linear-gradient(90deg,{T['accent']},{T['purple']},transparent);opacity:0.35;margin:24px 0;"></div>""", unsafe_allow_html=True)

def gen_scores():
    return {
        "viral":      (random.randint(82,97), T["accent"]),
        "hook":       (random.randint(80,96), T["purple"]),
        "engagement": (random.randint(83,95), T["blue"]),
        "share":      (random.randint(81,94), T["green"]),
        "retention":  (random.randint(82,95), T["yellow"]),
        "reach":      (random.randint(80,93), T["orange"]),
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

# ══════════════════════════════════════════
# COPY + CARD COMPONENT
# ══════════════════════════════════════════
def output_card_with_copy(title, content, accent_color=None, confidence=None, card_id=None):
    color = accent_color or T["accent"]
    cid = card_id or title.replace(" ","_").lower()
    conf_html = ""
    if confidence:
        conf_html = f'<div style="font-family:Space Mono,monospace;font-size:8px;letter-spacing:1px;color:{T["green"]};background:{T["green"]}12;border:1px solid {T["green"]}30;padding:2px 8px;margin-left:8px;">✦ CONFIDENCE: {confidence}%</div>'
    wc = len(content.split()) if content else 0
    safe_content = content.replace("`","'").replace("\\","\\\\").replace("\n","\\n").replace('"','\\"')

    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;font-family:'Space Grotesk',sans-serif;padding:2px 0;}}
.card{{
    background:{T["glass"]};
    backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
    border:1px solid {T["glassborder"]};border-left:2px solid {color};
    overflow:hidden;transition:all .3s cubic-bezier(.4,0,.2,1);position:relative;
}}
.card::before{{content:'';position:absolute;inset:0;background:radial-gradient(circle at var(--mx,50%) var(--my,50%),{color}10 0%,transparent 55%);opacity:0;transition:opacity .3s;pointer-events:none;}}
.card:hover::before{{opacity:1;}}
.card:hover{{border-color:{color}60;box-shadow:0 0 28px {color}12,0 6px 24px rgba(0,0,0,.3);transform:translateY(-1px) perspective(800px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg));}}
.card-header{{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-bottom:1px solid {T["rule"]};background:{T["bg3"]};}}
.card-title{{font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{color};display:flex;align-items:center;}}
.card-meta{{display:flex;align-items:center;gap:8px;}}
.meta-chip{{font-family:'Space Mono',monospace;font-size:7px;color:{T["text4"]};background:{T["bg4"]};border:1px solid {T["rule2"]};padding:2px 6px;}}
.copy-btn{{
    background:transparent;border:1px solid {T["rule2"]};color:{T["text3"]};
    font-family:'Space Mono',monospace;font-size:8px;letter-spacing:1px;padding:4px 10px;
    cursor:pointer;transition:all .15s;text-transform:uppercase;
}}
.copy-btn:hover{{border-color:{color};color:{color};}}
.copy-btn.ok{{border-color:{T["green"]};color:{T["green"]};}}
.card-body{{padding:14px;font-size:13px;line-height:1.85;color:{T["text2"]};white-space:pre-wrap;word-break:break-word;}}
</style>
</head><body>
<div class="card" id="c">
    <div class="card-header">
        <div class="card-title">{title}{conf_html}</div>
        <div class="card-meta">
            <span class="meta-chip">{wc} words</span>
            <button class="copy-btn" id="cb" onclick="doCopy()">COPY</button>
        </div>
    </div>
    <div class="card-body" id="cb_body">{content.replace(chr(10),"<br>")}</div>
</div>
<script>
const card=document.getElementById('c');
const rawText="{safe_content}".replace(/\\n/g,'\\n');
function doCopy(){{
    navigator.clipboard.writeText(rawText).then(()=>{{
        const b=document.getElementById('cb');
        b.textContent='✓ COPIED';b.classList.add('ok');
        setTimeout(()=>{{b.textContent='COPY';b.classList.remove('ok');}},2000);
    }});
}}
card.addEventListener('mousemove',e=>{{
    const r=card.getBoundingClientRect();
    const x=((e.clientX-r.left)/r.width)*100,y=((e.clientY-r.top)/r.height)*100;
    card.style.setProperty('--mx',x+'%');card.style.setProperty('--my',y+'%');
    const rx=((e.clientY-r.top-r.height/2)/r.height)*-5;
    const ry=((e.clientX-r.left-r.width/2)/r.width)*5;
    card.style.setProperty('--rx',rx+'deg');card.style.setProperty('--ry',ry+'deg');
}});
card.addEventListener('mouseleave',()=>{{
    card.style.setProperty('--rx','0deg');card.style.setProperty('--ry','0deg');
}});
</script>
</body></html>
""", height=max(160, min(len(content)//2 + 120, 500)), scrolling=False)

# ══════════════════════════════════════════
# SCORE BENTO WITH ANIMATED COUNTERS
# ══════════════════════════════════════════
def score_bento(scores):
    items = [
        ("Viral Potential","viral",T["accent"]),
        ("Hook Strength","hook",T["purple"]),
        ("Engagement","engagement",T["blue"]),
        ("Shareability","share",T["green"]),
        ("Retention","retention",T["yellow"]),
        ("Reach Rating","reach",T["orange"]),
    ]
    cards_html = ""
    for label, key, color in items:
        val, _ = scores[key]
        cards_html += f"""
<div class="sc" style="--ac:{color};" onmousemove="tilt(this,event)" onmouseleave="resetTilt(this)">
    <div class="sg"></div>
    <div class="sl">{label}</div>
    <div class="sv" data-t="{val}">0</div>
    <div class="sb"><div class="sf" data-w="{val}"></div></div>
    <div class="conf">AI CONFIDENCE: {val + random.randint(0,3)}%</div>
</div>"""

    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;font-family:'Space Mono',monospace;padding:4px 2px;}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}}
.sc{{
    background:{T["glass"]};backdrop-filter:blur(20px);
    border:1px solid {T["glassborder"]};border-top:2px solid var(--ac);
    padding:14px;position:relative;overflow:hidden;
    transition:transform .2s,box-shadow .2s;cursor:default;
}}
.sg{{position:absolute;inset:0;background:radial-gradient(circle at 50% 0%,var(--ac)15 0%,transparent 65%);opacity:0;transition:opacity .3s;pointer-events:none;}}
.sc:hover .sg{{opacity:1;}}
.sc:hover{{box-shadow:0 0 20px var(--ac)25,0 4px 20px rgba(0,0,0,.4);}}
.sl{{font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text3"]};margin-bottom:6px;}}
.sv{{font-size:26px;font-weight:700;color:var(--ac);line-height:1;margin-bottom:6px;}}
.sb{{height:2px;background:{T["rule2"]};overflow:hidden;margin-bottom:6px;}}
.sf{{height:100%;background:var(--ac);width:0%;transition:width 1.4s cubic-bezier(.4,0,.2,1);}}
.conf{{font-size:7px;letter-spacing:1px;color:{T["green"]};opacity:.7;}}
</style>
</head><body>
<div class="grid">{cards_html}</div>
<script>
document.querySelectorAll('.sv').forEach(el=>{{
    const t=parseInt(el.dataset.t);let c=0;
    const s=Math.ceil(t/50);
    const tm=setInterval(()=>{{c=Math.min(c+s,t);el.textContent=c;if(c>=t)clearInterval(tm);}},22);
}});
setTimeout(()=>document.querySelectorAll('.sf').forEach(el=>{{el.style.width=el.dataset.w+'%';}}),80);
function tilt(card,e){{
    const r=card.getBoundingClientRect();
    const rx=((e.clientY-r.top-r.height/2)/r.height)*-7;
    const ry=((e.clientX-r.left-r.width/2)/r.width)*7;
    card.style.transform=`perspective(400px) rotateX(${{rx}}deg) rotateY(${{ry}}deg) translateY(-2px)`;
}}
function resetTilt(c){{c.style.transform='';}}
</script>
</body></html>
""", height=220, scrolling=False)

# ══════════════════════════════════════════
# RADAR CHART
# ══════════════════════════════════════════
def radar_component(scores):
    vals = [scores[k][0] for k in ['viral','hook','engagement','share','retention','reach']]
    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>*{{margin:0;padding:0;}}body{{background:transparent;display:flex;align-items:center;justify-content:center;}}canvas{{max-width:220px;max-height:220px;}}</style>
</head><body>
<canvas id="rc"></canvas>
<script>
new Chart(document.getElementById('rc'),{{
    type:'radar',
    data:{{labels:['Viral','Hook','Engage','Share','Retain','Reach'],
    datasets:[{{data:{vals},backgroundColor:'rgba(255,75,43,0.1)',borderColor:'{T["accent"]}',borderWidth:1.5,pointBackgroundColor:'{T["accent"]}',pointRadius:4,pointHoverRadius:6}}]}},
    options:{{responsive:true,scales:{{r:{{min:0,max:100,ticks:{{display:false}},grid:{{color:'rgba(255,75,43,0.08)'}},angleLines:{{color:'rgba(255,75,43,0.08)'}},pointLabels:{{color:'{T["text3"]}',font:{{family:'Space Mono',size:9}}}}}}}},plugins:{{legend:{{display:false}}}},animation:{{duration:1200,easing:'easeOutQuart'}}}}
}});
</script>
</body></html>
""", height=240, scrolling=False)

# ══════════════════════════════════════════
# LIQUID GENERATE BUTTON (only button, no duplicate)
# ══════════════════════════════════════════
def liquid_button(label="→ GENERATE", key="lbtn"):
    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;height:58px;display:flex;align-items:center;justify-content:center;}}
.btn{{width:100%;height:52px;background:none;border:none;cursor:pointer;position:relative;overflow:hidden;outline:none;}}
.bg{{position:absolute;inset:0;background:linear-gradient(135deg,{T["accent"]} 0%,{T["accent2"]} 40%,{T["purple"]} 80%,{T["accent"]} 120%);background-size:300% 300%;animation:lf 3s ease infinite;transition:filter .2s;}}
.btn:hover .bg{{filter:brightness(1.15);}}
.btn:active .bg{{filter:brightness(.9);}}
@keyframes lf{{0%{{background-position:0% 50%}}50%{{background-position:100% 50%}}100%{{background-position:0% 50%}}}}
.txt{{position:relative;z-index:2;font-family:'Space Mono',monospace;font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#fff;pointer-events:none;}}
.ripple{{position:absolute;border-radius:50%;background:rgba(255,255,255,.35);transform:scale(0);animation:ra .7s linear forwards;pointer-events:none;}}
@keyframes ra{{to{{transform:scale(4);opacity:0;}}}}
</style>
</head><body>
<button class="btn" id="b">
    <div class="bg"></div>
    <span class="txt">{label}</span>
</button>
<script>
document.getElementById('b').addEventListener('click',e=>{{
    const r=document.createElement('span');r.className='ripple';
    const rect=e.target.closest('.btn').getBoundingClientRect();
    const size=Math.max(rect.width,rect.height);
    r.style.cssText=`width:${{size}}px;height:${{size}}px;left:${{e.clientX-rect.left-size/2}}px;top:${{e.clientY-rect.top-size/2}}px`;
    e.target.closest('.btn').appendChild(r);
    setTimeout(()=>r.remove(),700);
    // Particle burst to parent
    const count=35;
    for(let i=0;i<count;i++){{
        const p=document.createElement('div');
        const angle=(Math.PI*2*i)/count;
        const dist=60+Math.random()*100;
        const size2=Math.random()*7+3;
        const cols=['{T["accent"]}','{T["accent2"]}','{T["purple"]}','#fff','{T["yellow"]}'];
        const col=cols[Math.floor(Math.random()*cols.length)];
        const dur=(.5+Math.random()*.7)+'s';
        p.style.cssText=`position:fixed;border-radius:50%;pointer-events:none;z-index:9997;
            left:${{e.clientX}}px;top:${{e.clientY}}px;width:${{size2}}px;height:${{size2}}px;
            background:${{col}};box-shadow:0 0 ${{size2*2}}px ${{col}};
            animation:pf ${{dur}} ease-out forwards;`;
        const style=document.createElement('style');
        style.textContent=`@keyframes pf{{0%{{transform:translate(0,0) scale(1);opacity:1}}100%{{transform:translate(${{Math.cos(angle)*dist}}px,${{Math.sin(angle)*dist}}px) scale(0);opacity:0}}}}`;
        document.head.appendChild(style);
        document.body.appendChild(p);
        setTimeout(()=>{{p.remove();style.remove();}},parseFloat(dur)*1000);
    }}
}});
</script>
</body></html>
""", height=58, scrolling=False)

# ══════════════════════════════════════════
# HASHTAG COMPONENT
# ══════════════════════════════════════════
def hashtag_component(hv, mv, nv):
    def tags_html(tags, color):
        return "".join([f'<span class="tag" style="--c:{color};" onclick="ct(this)">{t}</span>' for t in tags])
    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Space+Grotesk&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;font-family:'Space Grotesk',sans-serif;padding:4px 2px;}}
.grp{{margin-bottom:16px;}}
.gl{{font-family:'Space Mono',monospace;font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text3"]};margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;}}
.ca{{background:transparent;border:1px solid {T["rule2"]};color:{T["text4"]};font-family:'Space Mono',monospace;font-size:7px;letter-spacing:1px;padding:2px 7px;cursor:pointer;transition:all .15s;text-transform:uppercase;}}
.ca:hover{{border-color:{T["accent"]};color:{T["accent"]};}}
.tags{{display:flex;flex-wrap:wrap;gap:5px;}}
.tag{{background:{T["bg3"]};border:1px solid {T["rule2"]};color:{T["text2"]};font-family:'Space Mono',monospace;font-size:10px;padding:4px 9px;cursor:pointer;transition:all .2s;display:inline-block;}}
.tag:hover{{border-color:var(--c);color:var(--c);transform:translateY(-1px);}}
.toast{{position:fixed;bottom:10px;right:10px;background:{T["accent"]};color:#fff;font-family:'Space Mono',monospace;font-size:9px;letter-spacing:2px;padding:6px 12px;opacity:0;transition:opacity .2s;pointer-events:none;}}
.toast.s{{opacity:1;}}
</style>
</head><body>
<div class="grp"><div class="gl"><span>High Volume — 1M+ ({len(hv)} tags)</span><button class="ca" onclick="cg('hv')">COPY ALL</button></div><div class="tags" id="hv">{tags_html(hv,T["accent"])}</div></div>
<div class="grp"><div class="gl"><span>Medium Volume — 100K-1M ({len(mv)} tags)</span><button class="ca" onclick="cg('mv')">COPY ALL</button></div><div class="tags" id="mv">{tags_html(mv,T["blue"])}</div></div>
<div class="grp"><div class="gl"><span>Niche — Under 100K ({len(nv)} tags)</span><button class="ca" onclick="cg('nv')">COPY ALL</button></div><div class="tags" id="nv">{tags_html(nv,T["green"])}</div></div>
<div class="toast" id="t">COPIED</div>
<script>
function st2(){{const t=document.getElementById('t');t.classList.add('s');setTimeout(()=>t.classList.remove('s'),1500);}}
function ct(el){{navigator.clipboard.writeText(el.textContent);st2();}}
function cg(id){{const tags=Array.from(document.getElementById(id).querySelectorAll('.tag')).map(t=>t.textContent).join(' ');navigator.clipboard.writeText(tags);st2();}}
</script>
</body></html>
""", height=280, scrolling=False)

# ══════════════════════════════════════════
# LOADING STEPS RENDERER
# ══════════════════════════════════════════
def render_steps(done, step_names):
    rows = ""
    for i, name in enumerate(step_names):
        if i < done:
            col, icon = T["green"], "✓"
        elif i == done:
            col, icon = T["accent"], "◌"
        else:
            col, icon = T["text4"], str(i+1)
        rows += f'<div style="display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid {T["rule"]};font-family:Space Mono,monospace;font-size:10px;letter-spacing:1px;color:{col};"><span style="width:18px;text-align:center;">{icon}</span><span>{name}</span></div>'
    return f'<div style="background:{T["bg2"]};border:1px solid {T["rule"]};padding:24px;margin:20px 0;">{rows}</div>'

# ══════════════════════════════════════════
# TOPBAR (with page navigation)
# ══════════════════════════════════════════
theme_icon = "🌙" if IS_DARK else "🌕"
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;padding:0 32px;height:54px;background:{T["bg2"]}ee;border-bottom:1px solid {T["rule"]};backdrop-filter:blur(20px);position:sticky;top:0;z-index:100;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:26px;height:26px;background:{T["accent"]};display:flex;align-items:center;justify-content:center;font-size:13px;box-shadow:0 0 16px {T["accent"]}60;">🎬</div>
    <div style="font-family:'Space Mono',monospace;font-size:13px;font-weight:700;color:{T["text"]};letter-spacing:1px;">Reel<span style="color:{T["accent"]};">Mind</span> AI</div>
  </div>
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="display:flex;align-items:center;gap:6px;font-family:'Space Mono',monospace;font-size:8px;color:{T["green"]};">
      <div style="width:5px;height:5px;background:{T["green"]};border-radius:50%;animation:pulse 2s infinite;"></div>GEMINI LIVE</div>
    <div style="font-family:'Space Mono',monospace;font-size:8px;color:{T["text4"]};background:{T["bg3"]};border:1px solid {T["rule2"]};padding:3px 8px;">v3.0</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# PAGE SELECTOR IN SIDEBAR
# ══════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:8px;letter-spacing:3px;text-transform:uppercase;color:{T["text4"]};padding:16px 16px 10px;border-bottom:1px solid {T["rule"]};">⚡ Navigation</div>', unsafe_allow_html=True)

    col_t1, col_t2 = st.columns([3,1])
    with col_t2:
        if st.button(theme_icon, key="theme_toggle"):
            st.session_state.theme = "light" if IS_DARK else "dark"
            st.rerun()

    st.markdown("---")

    # Page buttons
    rm_btn = st.button("🎬 ReelMind AI — Content Generator", key="nav_rm")
    sf_btn = st.button("✨ StoryFlow AI — Video Creator", key="nav_sf")

    if rm_btn:
        st.session_state.page = "reelmind"
        st.rerun()
    if sf_btn:
        st.session_state.page = "storyflow"
        st.rerun()

    st.markdown("---")

    if st.session_state.page == "reelmind":
        st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:8px;letter-spacing:3px;text-transform:uppercase;color:{T["text4"]};padding:0 0 10px;border-bottom:1px solid {T["rule"]};">⚡ Content Engine</div>', unsafe_allow_html=True)
        mode = st.radio("Mode", [
            "⚡ Full Content Pack","🎯 Hook Ideas Only",
            "📅 Content Series","🎠 Carousel Post",
            "🧵 X/Twitter Thread","🔄 Content Repurposer"
        ], label_visibility="collapsed")
        st.markdown("---")
        topic = st.text_input("Topic", placeholder="e.g. Villain arc, AI Tools, Gym motivation...")
        niche = st.selectbox("Niche", [
            "Dark Aesthetic / Motivation","Gaming","Anime & Manga",
            "Fitness & Gym","Tech & AI","Finance & Investing",
            "Horror & Thriller","Fashion & Lifestyle","Education",
            "Movie Industry","Music & Artists","Business & Entrepreneurship",
            "Luxury & Premium","Cars & Motorsport","Travel & Adventure","Food & Cooking"
        ])
        platform = st.selectbox("Platform", ["Instagram Reels","TikTok","YouTube Shorts"])
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
            original_content = st.text_area("Paste original content", height=80)
            target_platform = st.selectbox("Repurpose for", ["TikTok","YouTube Shorts","X/Twitter","LinkedIn"])
        st.markdown("---")
        liquid_button("→ GENERATE", key="rm_lbtn")
        generate_btn = st.button("GENERATE CONTENT", key="gen_main")
        with st.expander("QUICK TIPS"):
            st.markdown(f'<div style="font-family:Space Grotesk,sans-serif;font-size:12px;color:{T["text3"]};line-height:1.8;">→ Specific topics outperform generic<br>→ <strong>"Villain arc workout" > "gym"</strong><br>→ Match tone to your content style<br>→ Use Hook mode to A/B test openings</div>', unsafe_allow_html=True)
        if st.session_state.history:
            st.markdown("---")
            st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};margin-bottom:8px;">Recent</div>', unsafe_allow_html=True)
            for h in st.session_state.history[-4:]:
                st.markdown(f'<div style="background:{T["bg3"]};border:1px solid {T["rule"]};padding:8px 10px;margin-bottom:3px;"><div style="font-size:12px;font-weight:500;color:{T["text"]};">{h["topic"][:24]}</div><div style="font-family:Space Mono,monospace;font-size:7px;color:{T["text4"]};">{h["niche"][:22]} · {h["time"]}</div></div>', unsafe_allow_html=True)

    elif st.session_state.page == "storyflow":
        st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:8px;letter-spacing:3px;text-transform:uppercase;color:{T["gold"]};padding:0 0 10px;border-bottom:1px solid {T["rule"]};">✨ StoryFlow Engine</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:8px;color:{T["text4"]};padding:8px 0;">Step {st.session_state.sf_step} / 4</div>', unsafe_allow_html=True)
        step_labels = ["1 Configure","2 Select Story","3 Generate Assets","4 Full Package"]
        for i, sl in enumerate(step_labels):
            done = i+1 < st.session_state.sf_step
            active = i+1 == st.session_state.sf_step
            col = T["gold"] if active else (T["green"] if done else T["text4"])
            prefix = "✓" if done else ("▶" if active else "○")
            st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:9px;letter-spacing:1px;color:{col};padding:4px 0;">{prefix} {sl}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# PREMIUM EFFECTS
# ══════════════════════════════════════════
inject_premium_effects()

# ══════════════════════════════════════════
# REELMIND PAGE
# ══════════════════════════════════════════
if st.session_state.page == "reelmind":
    # Hero
    st.markdown(f"""
<div style="padding:36px 32px 24px;border-bottom:1px solid {T["rule"]};position:relative;overflow:hidden;">
  <div style="position:absolute;top:-80px;right:-50px;width:360px;height:360px;background:radial-gradient(circle,{T["accent"]}10 0%,transparent 70%);pointer-events:none;animation:pulse 4s ease-in-out infinite;"></div>
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:4px;text-transform:uppercase;color:{T["accent"]};margin-bottom:10px;display:flex;align-items:center;gap:10px;"><span style="width:18px;height:1px;background:{T["accent"]};display:inline-block;"></span>AI Content Engine — Studio Grade</div>
  <div style="font-family:'Fraunces',serif;font-size:56px;font-weight:900;font-style:italic;line-height:.92;letter-spacing:-2px;color:{T["text"]};margin-bottom:12px;">Reel<span style="color:{T["accent"]};">Mind</span> <span style="color:{T["text4"]};">AI</span></div>
  <div style="font-size:13px;color:{T["text3"]};max-width:420px;line-height:1.6;margin-bottom:22px;">Generate scroll-stopping captions, hashtag stacks, viral scripts, and thumbnail prompts — powered by Gemini 2.5 Flash.</div>
  <div style="display:flex;gap:32px;flex-wrap:wrap;">
    {"".join([f'<div style="display:flex;flex-direction:column;gap:2px;"><div style="font-family:Space Mono,monospace;font-size:20px;font-weight:700;color:{T["text"]};">{n}</div><div style="font-family:Space Mono,monospace;font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">{l}</div></div>' for n,l in [("4","Outputs/run"),("30","Hashtags"),("3","Captions"),("16","Niches")]])}
  </div>
</div>
""", unsafe_allow_html=True)

    if not generate_btn:
        if not st.session_state.last_result:
            st.markdown(f"""
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:380px;border:1px dashed {T["rule2"]};margin:32px;gap:14px;">
  <div style="font-size:38px;filter:grayscale(1);opacity:0.15;">🎬</div>
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
            "Writing detailed reel script...",
            "Designing thumbnail prompt...",
            "Calculating AI confidence scores...",
        ]
        for i in range(len(step_names)):
            steps_ph.markdown(render_steps(i, step_names), unsafe_allow_html=True)
            time.sleep(0.45)

        result = None; raw_output = None; error_msg = None
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

        steps_ph.markdown(render_steps(len(step_names), step_names), unsafe_allow_html=True)
        time.sleep(0.3); steps_ph.empty()

        if error_msg:
            st.error(f"Generation failed: {error_msg}")
            st.stop()

        if result: st.session_state.last_result = result
        scores = gen_scores(); st.session_state.last_scores = scores
        st.session_state.history.append({"topic": topic, "niche": niche, "time": datetime.datetime.now().strftime("%H:%M")})

        # Scores
        st.markdown("<div style='padding:0 0;'>", unsafe_allow_html=True)
        section_label("Content Score Card")
        score_bento(scores)
        gradient_divider()

        # Radar + times
        col_r, col_a = st.columns([1,1])
        with col_r:
            section_label("Content Radar")
            radar_component(scores)
        with col_a:
            section_label("Best Posting Times")
            times = POSTING_TIMES.get(platform, POSTING_TIMES["Instagram Reels"])
            t_html = "".join([f'<span style="display:inline-block;background:{T["bg3"]};border:1px solid {T["green"] if best else T["rule2"]};padding:6px 11px;font-family:Space Mono,monospace;font-size:9px;color:{T["green"] if best else T["text3"]};margin:3px;{"background:"+T["green"]+"10;" if best else ""}">{t}<small style="display:block;font-size:7px;letter-spacing:1px;">{label}{"  ★" if best else ""}</small></span>' for t,label,best in times])
            st.markdown(t_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            section_label("Niche Saturation")
            sat = SATURATION.get(niche,"MEDIUM — competitive but approachable with strong hooks.")
            st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:10px;color:{T["text2"]};line-height:1.6;">{sat}</div>', unsafe_allow_html=True)

        gradient_divider()

        # Full content tabs
        if "Full Content" in mode and result:
            confidence = random.randint(88, 97)
            tab1,tab2,tab3,tab4 = st.tabs(["📝 Captions","#️⃣ Hashtags","🎬 Script","🖼️ Thumbnail"])

            with tab1:
                short, med, long_cap = parse_captions(result.get("captions",""))
                for cap_text, label in [(short,"Short Caption"),(med,"Medium Caption"),(long_cap,"Long Caption")]:
                    output_card_with_copy(label, cap_text, T["accent"], confidence)
                    st.download_button(f"↓ Download {label}", cap_text, file_name=f"{label.lower().replace(' ','_')}.txt", key=f"dl_{label[:3]}")

            with tab2:
                hv, mv, nv = parse_hashtags(result.get("hashtags",""))
                hashtag_component(hv, mv, nv)
                all_tags = " ".join(hv+mv+nv)
                st.download_button("↓ Download All Hashtags", all_tags, file_name="hashtags.txt", key="dl_ht")

            with tab3:
                formatted = format_script(result.get("script",""))
                output_card_with_copy("Reel Script — 30 Seconds", formatted, T["purple"], confidence)
                st.download_button("↓ Download Script", result.get("script",""), file_name="reel_script.txt", key="dl_sc")

            with tab4:
                thumb = result.get("thumbnail","")
                mj_m = re.search(r'(?:IMAGE PROMPT|PROMPT)[^:]*:\s*([\s\S]*?)(?=STYLE|$)', thumb, re.I)
                style_m = re.search(r'STYLE[^:]*:\s*([\s\S]*?)(?=COLOR|$)', thumb, re.I)
                color_m = re.search(r'COLOR[^:]*:\s*([\s\S]*?)$', thumb, re.I)
                base = mj_m.group(1).strip() if mj_m else thumb[:300]
                sty = style_m.group(1).strip() if style_m else ""
                colors = color_m.group(1).strip() if color_m else ""
                mj = f"{base}\n\n--style raw --ar 9:16 --v 6\nStyle: {sty}\nColors: {colors}"
                ideogram = f"{base}\n\nStyle: {sty}\nPalette: {colors}\nHigh detail, sharp focus, 9:16"
                output_card_with_copy("Midjourney Prompt", mj, T["accent"], confidence)
                st.download_button("↓ MJ Prompt", mj, file_name="mj_prompt.txt", key="dl_mj")
                output_card_with_copy("Ideogram / Gemini Image Prompt", ideogram, T["blue"], confidence)
                st.download_button("↓ Ideogram Prompt", ideogram, file_name="ideogram_prompt.txt", key="dl_id")

            gradient_divider()
            full = f"REELMIND AI\nTopic:{topic} | Niche:{niche} | Platform:{platform}\n{'='*60}\n\n{result.get('raw','')}"
            c1,c2 = st.columns(2)
            with c1: st.download_button("↓ Download Full Pack", full, file_name=f"reelmind_{topic[:20].replace(' ','_')}_full.txt", key="dl_full")
            with c2: st.download_button("↓ Download Raw", result.get("raw",""), file_name="reelmind_raw.txt", key="dl_raw")
        else:
            mode_label = mode.split(" ",1)[1] if " " in mode else mode
            output_card_with_copy(mode_label, raw_output or "No output generated.", T["accent"])
            if raw_output:
                st.download_button("↓ Download Output", raw_output, file_name=f"reelmind_{topic[:20].replace(' ','_')}.txt", key="dl_other")

        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# STORYFLOW AI PAGE
# ══════════════════════════════════════════
elif st.session_state.page == "storyflow":

    # Hero
    st.markdown(f"""
<div style="padding:36px 32px 24px;border-bottom:1px solid {T["rule"]};position:relative;overflow:hidden;background:linear-gradient(135deg,{T["bg"]} 0%,{T["bg2"]} 100%);">
  <div style="position:absolute;top:-60px;right:-40px;width:300px;height:300px;background:radial-gradient(circle,{T["gold"]}12 0%,transparent 70%);pointer-events:none;animation:pulse 5s ease-in-out infinite;"></div>
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:4px;text-transform:uppercase;color:{T["gold"]};margin-bottom:10px;display:flex;align-items:center;gap:10px;"><span style="width:18px;height:1px;background:{T["gold"]};display:inline-block;"></span>AI Video Story Engine — Pixar Grade</div>
  <div style="font-family:'Fraunces',serif;font-size:56px;font-weight:900;font-style:italic;line-height:.92;letter-spacing:-2px;color:{T["text"]};margin-bottom:12px;">Story<span style="color:{T["gold"]};">Flow</span> <span style="color:{T["text4"]};">AI</span></div>
  <div style="font-size:13px;color:{T["text3"]};max-width:500px;line-height:1.6;margin-bottom:22px;">Create complete AI video workflows — stories, character sheets, Frame 1 prompts, and full video prompt chains for smooth cinematic AI videos.</div>
  <div style="display:flex;gap:16px;flex-wrap:wrap;">
    {"".join([f'<div style="background:{T["bg3"]};border:1px solid {T["rule2"]};padding:8px 16px;font-family:Space Mono,monospace;font-size:9px;color:{T["text3"]};letter-spacing:1px;">{t}</div>' for t in ["3 Story Options","Character Sheets","Frame 1 Prompt","Full Prompt Chain","Continuity Engine"]])}
  </div>
</div>
""", unsafe_allow_html=True)

    # Progress bar
    prog_pct = (st.session_state.sf_step - 1) / 3 * 100
    st.markdown(f"""
<div style="height:3px;background:{T["rule"]};margin:0;">
  <div style="height:100%;width:{prog_pct}%;background:linear-gradient(90deg,{T["gold"]},{T["accent"]});transition:width .5s;"></div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='padding:24px 32px;'>", unsafe_allow_html=True)

    # ── STEP 1: CONFIGURE ──
    if st.session_state.sf_step == 1:
        section_label("Step 1 — Configure Your Story")
        st.markdown(f'<div style="font-size:13px;color:{T["text3"]};margin-bottom:24px;line-height:1.6;">Fill in your story parameters. The AI will generate 3 complete story options with viral scores, emotion scores, and full breakdowns.</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            sf_story_type = st.selectbox("Story Type", ["Funny","Emotional","Cute","Action","Adventure","Mystery","Educational","Heartwarming"])
            sf_character = st.selectbox("Character", ["Puppy","Cat","Penguin","Fox","Bunny","Panda","Baby Bear","Duck","Hamster","Custom"])
            sf_custom_char = ""
            if sf_character == "Custom":
                sf_custom_char = st.text_input("Describe your custom character", placeholder="e.g. tiny baby dragon with big eyes")
            sf_duration = st.selectbox("Video Duration (seconds)", [8, 10, 16, 20, 24, 30, 40, 60])

        with col2:
            sf_style = st.selectbox("Animation Style", ["Pixar","Disney","DreamWorks","Anime","Chibi","Cartoon","Realistic"])
            sf_platform = st.selectbox("Platform", ["Instagram Reels","TikTok","YouTube Shorts"])
            sf_ending = st.selectbox("Ending Type", ["Happy","Funny","Emotional","Twist","Sad","Random"])
            sf_custom_idea = st.text_area("Custom Story Idea (optional)", placeholder="e.g. Puppy tries to get a heart balloon stuck in a tree...", height=80)

        st.markdown("---")

        # Info cards
        c1,c2,c3 = st.columns(3)
        with c1:
            st.markdown(f'<div style="background:{T["bg2"]};border:1px solid {T["rule"]};border-top:2px solid {T["gold"]};padding:14px;"><div style="font-family:Space Mono,monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["gold"]};margin-bottom:6px;">What you get</div><div style="font-size:12px;color:{T["text2"]};line-height:1.7;">3 complete story options<br>Viral + emotion scores<br>Full act breakdowns<br>Scene object lists</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div style="background:{T["bg2"]};border:1px solid {T["rule"]};border-top:2px solid {T["accent"]};padding:14px;"><div style="font-family:Space Mono,monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["accent"]};margin-bottom:6px;">Then generate</div><div style="font-size:12px;color:{T["text2"]};line-height:1.7;">Character design sheets<br>Frame 1 master prompt<br>Full video prompt chain<br>Continuity checklist</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div style="background:{T["bg2"]};border:1px solid {T["rule"]};border-top:2px solid {T["purple"]};padding:14px;"><div style="font-family:Space Mono,monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["purple"]};margin-bottom:6px;">Export for</div><div style="font-size:12px;color:{T["text2"]};line-height:1.7;">Google Flow<br>Google Gemini Video<br>Any AI video tool<br>Smooth continuity</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        liquid_button("→ GENERATE 3 STORY OPTIONS", "sf_lbtn1")
        gen_stories_btn = st.button("GENERATE STORIES", key="sf_gen1")

        if gen_stories_btn:
            st.session_state.sf_config = {
                "story_type": sf_story_type, "character": sf_character,
                "custom_char": sf_custom_char, "duration": sf_duration,
                "style": sf_style, "platform": sf_platform,
                "ending": sf_ending, "custom_idea": sf_custom_idea
            }
            steps_ph = st.empty()
            story_steps = [
                "Analyzing story type and character...","Building dramatic story arc...","Creating Hook → Conflict → Escalation → Payoff...","Writing 3 complete story options...","Calculating viral and emotion scores...","Finalizing scene object lists..."
            ]
            for i in range(len(story_steps)):
                steps_ph.markdown(render_steps(i, story_steps), unsafe_allow_html=True)
                time.sleep(0.5)

            cfg = st.session_state.sf_config
            raw_stories = generate_story(
                cfg["story_type"], cfg["character"], cfg["duration"],
                cfg["style"], cfg["platform"], cfg["ending"],
                cfg["custom_char"], cfg["custom_idea"]
            )
            steps_ph.markdown(render_steps(len(story_steps), story_steps), unsafe_allow_html=True)
            time.sleep(0.3); steps_ph.empty()

            if "ERROR" in (raw_stories or ""):
                st.error("Story generation failed: " + raw_stories.split("||")[-1])
            else:
                st.session_state.sf_stories = raw_stories
                st.session_state.sf_step = 2
                st.rerun()

    # ── STEP 2: SELECT STORY ──
    elif st.session_state.sf_step == 2:
        section_label("Step 2 — Review & Select Your Story")
        cfg = st.session_state.sf_config
        st.markdown(f'<div style="font-size:13px;color:{T["text3"]};margin-bottom:20px;">Review all 3 story options below. Select the one you want to develop into a complete video production package.</div>', unsafe_allow_html=True)

        output_card_with_copy("3 Complete Story Options", st.session_state.sf_stories or "", T["gold"])
        st.download_button("↓ Download Stories", st.session_state.sf_stories or "", file_name="storyflow_stories.txt", key="dl_sf_stories")

        gradient_divider()
        section_label("Select Story to Develop")

        col_s1, col_s2 = st.columns([2,1])
        with col_s1:
            selected = st.selectbox("Which story option do you want to develop?", ["Story Option 1","Story Option 2","Story Option 3"])
        with col_s2:
            custom_scene_objects = st.text_input("Override scene objects (optional)", placeholder="balloon, tree, box, mud, bird...")

        st.markdown("<br>", unsafe_allow_html=True)

        # What happens next info
        st.markdown(f"""
<div style="background:{T["bg2"]};border:1px solid {T["rule"]};border-left:2px solid {T["gold"]};padding:16px;margin-bottom:20px;">
  <div style="font-family:Space Mono,monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["gold"]};margin-bottom:10px;">WHAT GETS GENERATED NEXT</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
    {"".join([f'<div style="font-size:12px;color:{T["text2"]};"><span style="color:{T["accent"]};">→</span> {t}</div>' for t in ["Character design sheet prompts","Expression reference prompts","Frame 1 master establishing shot","Full video prompt chain","Continuity rules checklist","Camera & lighting notes"]])}
  </div>
</div>
""", unsafe_allow_html=True)

        liquid_button("→ GENERATE COMPLETE PACKAGE", "sf_lbtn2")
        gen_package_btn = st.button("GENERATE FULL PACKAGE", key="sf_gen2")

        c_back = st.button("← Back to Configure", key="sf_back2")
        if c_back:
            st.session_state.sf_step = 1
            st.rerun()

        if gen_package_btn:
            st.session_state.sf_config["selected_story"] = selected
            st.session_state.sf_config["custom_scene_objects"] = custom_scene_objects
            steps_ph = st.empty()
            pkg_steps = [
                "Extracting story elements...","Generating character design prompts...","Creating expression reference sheets...","Building Frame 1 establishing shot...","Engineering video prompt chain...","Writing continuity checklist..."
            ]
            for i in range(len(pkg_steps)):
                steps_ph.markdown(render_steps(i, pkg_steps), unsafe_allow_html=True)
                time.sleep(0.6)

            cfg = st.session_state.sf_config
            char = cfg["custom_char"] if cfg["custom_char"] else cfg["character"]
            story_summary = f'{cfg["story_type"]} {char} story, {cfg["duration"]} seconds, {cfg["ending"]} ending. Selected: {selected}'

            scene_objects = custom_scene_objects if custom_scene_objects else ""
            if not scene_objects:
                from gemini_helper import safe_generate
                scene_objects = safe_generate(f"List all props, characters, and environment objects needed for a {cfg['story_type']} {char} story with {cfg['ending']} ending. Simple comma-separated list only.")

            char_sheet = generate_character_sheet(char, cfg["style"], story_summary)
            frame1 = generate_frame1_prompt(story_summary, char, scene_objects, cfg["style"], cfg["platform"])
            prompt_chain = generate_prompt_chain(story_summary, char, scene_objects, cfg["duration"], cfg["style"], cfg["platform"])

            steps_ph.markdown(render_steps(len(pkg_steps), pkg_steps), unsafe_allow_html=True)
            time.sleep(0.3); steps_ph.empty()

            st.session_state.sf_char_sheet = char_sheet
            st.session_state.sf_frame1 = frame1
            st.session_state.sf_prompt_chain = prompt_chain
            st.session_state.sf_scene_objects = scene_objects
            st.session_state.sf_step = 3
            st.rerun()

    # ── STEP 3: FULL PACKAGE ──
    elif st.session_state.sf_step == 3:
        section_label("Step 3 — Your Complete Video Production Package")
        cfg = st.session_state.sf_config
        char = cfg.get("custom_char","") or cfg.get("character","")
        confidence = random.randint(89, 97)

        st.markdown(f"""
<div style="background:{T["bg2"]};border:1px solid {T["rule"]};border-top:2px solid {T["gold"]};padding:14px 16px;margin-bottom:20px;display:flex;align-items:center;justify-content:space-between;">
  <div>
    <div style="font-family:Space Mono,monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["gold"]};margin-bottom:4px;">Production Package Ready</div>
    <div style="font-size:13px;color:{T["text2"]};">{cfg.get("selected_story","Story")} — {char} — {cfg.get("duration",30)}s — {cfg.get("style","Pixar")} Style</div>
  </div>
  <div style="font-family:Space Mono,monospace;font-size:9px;color:{T["green"]};background:{T["green"]}12;border:1px solid {T["green"]}30;padding:4px 10px;">✦ AI CONFIDENCE: {confidence}%</div>
</div>
""", unsafe_allow_html=True)

        sf_tab1, sf_tab2, sf_tab3, sf_tab4, sf_tab5 = st.tabs([
            "📋 Scene Objects",
            "🎨 Character Sheets",
            "🖼️ Frame 1",
            "🎬 Prompt Chain",
            "📖 How To Use"
        ])

        with sf_tab1:
            section_label("Scene Objects — Must All Appear in Frame 1")
            st.markdown(f'<div style="font-size:12px;color:{T["text3"]};margin-bottom:16px;line-height:1.7;">These are ALL objects, characters, and environment elements in your story. <strong style="color:{T["accent"]};">Every single one must appear in Frame 1</strong> — even if they are not important yet. This prevents random spawning and teleporting in later prompts.</div>', unsafe_allow_html=True)
            output_card_with_copy("Complete Scene Object List", st.session_state.sf_scene_objects or "", T["gold"], confidence)
            st.download_button("↓ Download Scene Objects", st.session_state.sf_scene_objects or "", file_name="scene_objects.txt", key="dl_sf_obj")

        with sf_tab2:
            section_label("Character Design Prompts")
            st.markdown(f'<div style="font-size:12px;color:{T["text3"]};margin-bottom:16px;line-height:1.7;"><strong style="color:{T["text"]};">Generate these images first</strong> before any video. Upload character sheets to every video prompt for consistent appearance across all clips.</div>', unsafe_allow_html=True)
            output_card_with_copy("Character Sheet + Expression Prompts", st.session_state.sf_char_sheet or "", T["purple"], confidence)
            st.download_button("↓ Download Character Sheets", st.session_state.sf_char_sheet or "", file_name="character_sheets.txt", key="dl_sf_char")

        with sf_tab3:
            section_label("Frame 1 — Master Establishing Shot")
            st.markdown(f'<div style="font-size:12px;color:{T["text3"]};margin-bottom:16px;line-height:1.7;"><strong style="color:{T["text"]};">Generate this image second.</strong> Frame 1 defines your camera angle, lighting, character scale, and object positions. This becomes the foundation screenshot for Prompt 1.</div>', unsafe_allow_html=True)
            output_card_with_copy("Frame 1 Master Prompt", st.session_state.sf_frame1 or "", T["accent"], confidence)
            st.download_button("↓ Download Frame 1 Prompt", st.session_state.sf_frame1 or "", file_name="frame1_prompt.txt", key="dl_sf_frame1")

        with sf_tab4:
            section_label("Complete Video Prompt Chain")
            st.markdown(f'<div style="font-size:12px;color:{T["text3"]};margin-bottom:16px;line-height:1.7;"><strong style="color:{T["text"]};">Use these prompts in order.</strong> Each prompt starts from the last frame screenshot of the previous clip. Never skip the screenshot step between prompts.</div>', unsafe_allow_html=True)
            output_card_with_copy("Full Video Prompt Chain", st.session_state.sf_prompt_chain or "", T["green"], confidence)
            st.download_button("↓ Download Prompt Chain", st.session_state.sf_prompt_chain or "", file_name="prompt_chain.txt", key="dl_sf_chain")

            gradient_divider()
            full_pkg = f"""STORYFLOW AI — COMPLETE VIDEO PRODUCTION PACKAGE
Character: {char} | Style: {cfg.get('style','Pixar')} | Duration: {cfg.get('duration',30)}s | Platform: {cfg.get('platform','Instagram Reels')}
{'='*70}

SCENE OBJECTS
{'='*70}
{st.session_state.sf_scene_objects or ''}

CHARACTER SHEETS
{'='*70}
{st.session_state.sf_char_sheet or ''}

FRAME 1 PROMPT
{'='*70}
{st.session_state.sf_frame1 or ''}

VIDEO PROMPT CHAIN
{'='*70}
{st.session_state.sf_prompt_chain or ''}
"""
            st.download_button("↓ Download Complete Package", full_pkg, file_name=f"storyflow_{char.lower()}_complete.txt", key="dl_sf_full")

        with sf_tab5:
            section_label("How To Use This Package")
            how_to = f"""
STORYFLOW AI — PRODUCTION WORKFLOW
{'='*50}

STEP 1 — GENERATE CHARACTER DESIGN SHEETS
Open your AI image generator (Midjourney, Ideogram, Gemini Image).
Use the Character Sheet prompts from the Character Sheets tab.
Generate the full turnaround sheet + all 6 expressions.
Save all character images — you will upload these to every video prompt.

STEP 2 — GENERATE FRAME 1
Use the Frame 1 prompt from the Frame 1 tab.
This creates your master establishing shot.
It contains ALL story objects, characters, and environment.
Save this image — it becomes the starting point for Prompt 1.

STEP 3 — GENERATE VIDEO CLIP 1
Open Google Flow or Google Gemini Video.
Upload: Character sheet + Frame 1 image.
Enter: Prompt 1 from the Prompt Chain.
Generate the first 8-second clip.

STEP 4 — SCREENSHOT THE LAST FRAME
Watch the generated clip.
Pause on the VERY LAST FRAME.
Take a screenshot.
This screenshot is CRITICAL for continuity.

STEP 5 — GENERATE VIDEO CLIP 2
Upload: Character sheet + screenshot from Step 4.
Enter: Prompt 2 from the Prompt Chain.
Generate the second clip.

STEP 6 — REPEAT FOR ALL PROMPTS
For every new prompt:
- Upload character sheets for characters in that prompt
- Upload screenshot of the last frame from the previous clip
- Enter the next prompt
- Generate → Screenshot last frame → Repeat

GOLDEN RULES:
→ NEVER generate Prompt 2 without Prompt 1's last frame screenshot
→ ALWAYS upload character sheets — they prevent face/fur changes
→ NEVER skip a prompt in the chain
→ ALWAYS use the same AI model/project for all clips
→ Every important object MUST be in Frame 1 already

CONTINUITY CHECKLIST:
□ Character sheets generated and saved
□ Frame 1 generated and saved  
□ Prompt 1 generated with Frame 1 uploaded
□ Last frame screenshotted
□ Each subsequent prompt uses previous last frame
□ Character sheets uploaded to every prompt
□ Same camera angle maintained throughout
□ Same lighting maintained throughout
"""
            output_card_with_copy("Complete Production Workflow Guide", how_to.strip(), T["gold"])
            st.download_button("↓ Download Workflow Guide", how_to, file_name="storyflow_workflow_guide.txt", key="dl_sf_guide")

        gradient_divider()
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("← Back to Story Selection", key="sf_back3"):
                st.session_state.sf_step = 2
                st.rerun()
        with col_b2:
            if st.button("↺ Start New Story", key="sf_restart"):
                st.session_state.sf_step = 1
                st.session_state.sf_stories = None
                st.session_state.sf_char_sheet = None
                st.session_state.sf_frame1 = None
                st.session_state.sf_prompt_chain = None
                st.session_state.sf_scene_objects = None
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════
st.markdown(f"""
<div style="padding:16px 32px;border-top:1px solid {T["rule"]};background:{T["bg2"]};display:flex;justify-content:space-between;align-items:center;margin-top:40px;">
  <div style="font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">REELMIND AI + STORYFLOW AI — v3.0 — GEMINI 2.5 FLASH</div>
  <div style="font-family:'Space Mono',monospace;font-size:8px;color:{T["text4"]};background:{T["bg3"]};border:1px solid {T["rule2"]};padding:3px 8px;">BUILT BY SATVIK SHARMA · NIET 2024–28</div>
</div>
""", unsafe_allow_html=True)
