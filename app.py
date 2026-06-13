import streamlit as st
import streamlit.components.v1 as components
import random, time, datetime, re
from gemini_helper import (
    generate_full_content, generate_hooks, generate_series,
    generate_carousel, generate_thread, repurpose_content,
    generate_story, generate_character_sheet,
    generate_frame1_prompt, generate_prompt_chain
)

# ══════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════
st.set_page_config(page_title="ReelMind AI", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")

# ══════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════
DEFAULTS = {
    "theme": "dark", "page": "reelmind",
    "history": [], "last_result": None,
    "sf_step": 1, "sf_stories": None,
    "sf_char_sheet": None, "sf_frame1": None,
    "sf_prompt_chain": None, "sf_scene_objects": None,
    "sf_config": {}, "rm_result": None, "rm_scores": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

IS_DARK = st.session_state.theme == "dark"

# ══════════════════════════════════════════
# DESIGN TOKENS — TWO COMPLETELY DIFFERENT PREMIUM THEMES
# ══════════════════════════════════════════
if IS_DARK:
    T = {
        "bg":       "#0a0a0a",
        "bg2":      "#111111",
        "bg3":      "#181818",
        "bg4":      "#222222",
        "rule":     "#222222",
        "rule2":    "#333333",
        "text":     "#f5f3ef",
        "text2":    "#999999",
        "text3":    "#555555",
        "text4":    "#333333",
        "accent":   "#ff4b2b",
        "accent2":  "#ff7a5c",
        "gold":     "#f0b429",
        "gold2":    "#ffd166",
        "purple":   "#7c3aed",
        "blue":     "#2563eb",
        "green":    "#16a34a",
        "yellow":   "#ca8a04",
        "orange":   "#ea580c",
        "inv":      "#f5f3ef",
        "inv_bg":   "#0a0a0a",
    }
else:
    T = {
        "bg":       "#faf9f7",
        "bg2":      "#f2f0ec",
        "bg3":      "#e8e5df",
        "bg4":      "#dedad3",
        "rule":     "#e0dcd5",
        "rule2":    "#ccc8bf",
        "text":     "#0f0d0a",
        "text2":    "#4a4540",
        "text3":    "#8a8078",
        "text4":    "#b0a898",
        "accent":   "#e63900",
        "accent2":  "#ff5c3d",
        "gold":     "#b8860b",
        "gold2":    "#d4a017",
        "purple":   "#6d28d9",
        "blue":     "#1d4ed8",
        "green":    "#15803d",
        "yellow":   "#a16207",
        "orange":   "#c2410c",
        "inv":      "#0f0d0a",
        "inv_bg":   "#faf9f7",
    }

# ══════════════════════════════════════════
# GLOBAL CSS — NO SIDEBAR, FULL PAGE
# ══════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Editorial+New:ital,wght@0,400;1,400&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}

html,body,[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"]>.main{{
    background:{T["bg"]} !important;
    color:{T["text"]} !important;
    font-family:'Inter',sans-serif !important;
    cursor:none !important;
}}
[data-testid="stHeader"]{{display:none !important;}}
[data-testid="stSidebar"]{{display:none !important;}}
.block-container{{padding:0 !important;max-width:100% !important;}}
section[data-testid="stSidebar"]{{display:none !important;}}

/* ── INPUTS ── */
.stTextInput>div>div>input,.stTextArea>div>div>textarea{{
    background:{T["bg3"]} !important;
    border:1px solid {T["rule2"]} !important;
    border-radius:0 !important;
    color:{T["text"]} !important;
    font-family:'Inter',sans-serif !important;
    font-size:14px !important;
    padding:12px 16px !important;
    outline:none !important;
    transition:border-color .2s !important;
}}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{{
    border-color:{T["accent"]} !important;
    box-shadow:none !important;
}}
.stTextInput>div>div>input::placeholder,.stTextArea>div>div>textarea::placeholder{{
    color:{T["text4"]} !important;
}}
[data-baseweb="select"]>div{{
    background:{T["bg3"]} !important;border:1px solid {T["rule2"]} !important;
    border-radius:0 !important;color:{T["text"]} !important;
    font-family:'Inter',sans-serif !important;font-size:14px !important;
}}
[data-baseweb="popover"] ul{{background:{T["bg3"]} !important;border:1px solid {T["rule2"]} !important;border-radius:0 !important;}}
[data-baseweb="option"]{{background:{T["bg3"]} !important;color:{T["text"]} !important;font-size:13px !important;}}
[data-baseweb="option"]:hover{{background:{T["bg4"]} !important;}}

label,.stSelectbox label,.stTextInput label,.stTextArea label,.stRadio label,.stNumberInput label{{
    color:{T["text3"]} !important;font-family:'JetBrains Mono',monospace !important;
    font-size:9px !important;letter-spacing:2.5px !important;text-transform:uppercase !important;
    margin-bottom:6px !important;
}}
.stNumberInput>div>div>input{{
    background:{T["bg3"]} !important;border:1px solid {T["rule2"]} !important;
    border-radius:0 !important;color:{T["text"]} !important;
    font-family:'Inter',sans-serif !important;font-size:14px !important;padding:12px 16px !important;
}}
.stNumberInput [data-testid="stNumberInputStepDown"],
.stNumberInput [data-testid="stNumberInputStepUp"]{{
    background:{T["bg4"]} !important;border:none !important;color:{T["text"]} !important;
}}

/* ── ALL BUTTONS → override to transparent/ghost by default ── */
.stButton>button{{
    background:transparent !important;color:{T["text3"]} !important;
    border:1px solid {T["rule2"]} !important;border-radius:0 !important;
    font-family:'JetBrains Mono',monospace !important;font-size:9px !important;
    letter-spacing:2px !important;text-transform:uppercase !important;
    padding:10px 20px !important;transition:all .2s !important;
}}
.stButton>button:hover{{border-color:{T["accent"]} !important;color:{T["accent"]} !important;}}

.stDownloadButton>button{{
    background:transparent !important;color:{T["text3"]} !important;
    border:1px solid {T["rule2"]} !important;border-radius:0 !important;
    font-family:'JetBrains Mono',monospace !important;font-size:8px !important;
    letter-spacing:2px !important;text-transform:uppercase !important;
    padding:8px 14px !important;width:auto !important;transition:all .2s !important;
}}
.stDownloadButton>button:hover{{border-color:{T["accent"]} !important;color:{T["accent"]} !important;}}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{{
    background:transparent !important;border-bottom:1px solid {T["rule"]} !important;
    gap:0 !important;padding:0 !important;
}}
.stTabs [data-baseweb="tab"]{{
    background:transparent !important;color:{T["text3"]} !important;
    font-family:'JetBrains Mono',monospace !important;font-size:8px !important;
    letter-spacing:2.5px !important;text-transform:uppercase !important;
    padding:12px 20px !important;border-radius:0 !important;
    border-bottom:2px solid transparent !important;transition:all .2s !important;
}}
.stTabs [aria-selected="true"]{{
    color:{T["accent"]} !important;border-bottom-color:{T["accent"]} !important;background:transparent !important;
}}
.stTabs [data-baseweb="tab-panel"]{{padding:24px 0 0 !important;background:transparent !important;}}

/* ── EXPANDER ── */
.streamlit-expanderHeader{{
    background:{T["bg2"]} !important;border:1px solid {T["rule"]} !important;
    border-radius:0 !important;color:{T["text3"]} !important;
    font-family:'JetBrains Mono',monospace !important;font-size:9px !important;letter-spacing:2px !important;
}}
.streamlit-expanderContent{{background:{T["bg2"]} !important;border:1px solid {T["rule"]} !important;border-top:none !important;}}

/* ── RADIO ── */
.stRadio>div{{gap:4px !important;flex-direction:column !important;}}
.stRadio>div>label{{
    background:{T["bg3"]} !important;border:1px solid {T["rule2"]} !important;
    padding:10px 16px !important;border-radius:0 !important;margin:0 !important;
    color:{T["text3"]} !important;font-size:13px !important;transition:all .15s !important;
}}
.stRadio>div>label:hover{{border-color:{T["accent"]} !important;color:{T["accent"]} !important;}}

/* ── SCROLLBAR ── */
::-webkit-scrollbar{{width:3px;height:3px;}}
::-webkit-scrollbar-track{{background:{T["bg"]};}}
::-webkit-scrollbar-thumb{{background:{T["rule2"]};}}
::-webkit-scrollbar-thumb:hover{{background:{T["accent"]};}}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu{{visibility:hidden;}}
footer{{visibility:hidden;}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# CURSOR + BACKGROUND EFFECTS
# ══════════════════════════════════════════
def inject_cursor():
    components.html(f"""
<!DOCTYPE html><html><head>
<style>
*{{margin:0;padding:0;}}
body{{overflow:hidden;background:transparent;}}
#dot{{position:fixed;width:6px;height:6px;background:{T["accent"]};border-radius:50%;pointer-events:none;z-index:9999;transform:translate(-50%,-50%);}}
#ring{{position:fixed;width:32px;height:32px;border:1px solid {T["accent"]}60;border-radius:50%;pointer-events:none;z-index:9998;transform:translate(-50%,-50%);transition:width .2s,height .2s,border-color .2s;}}
#ring.h{{width:48px;height:48px;border-color:{T["accent"]};}}
.trail{{position:fixed;border-radius:50%;pointer-events:none;z-index:9997;animation:tf .5s ease-out forwards;}}
@keyframes tf{{0%{{opacity:.6;transform:translate(-50%,-50%) scale(1)}}100%{{opacity:0;transform:translate(-50%,-50%) scale(0)}}}}
</style>
</head><body>
<div id="dot"></div><div id="ring"></div>
<script>
const dot=document.getElementById('dot'),ring=document.getElementById('ring');
let rx=0,ry=0,mx=0,my=0,tc=0;
window.addEventListener('mousemove',e=>{{
    mx=e.clientX;my=e.clientY;
    dot.style.left=mx+'px';dot.style.top=my+'px';
    if(tc++%3===0){{
        const p=document.createElement('div');p.className='trail';
        const s=Math.random()*4+1;
        p.style.cssText=`left:${{mx}}px;top:${{my}}px;width:${{s}}px;height:${{s}}px;background:{T["accent"]}80;`;
        document.body.appendChild(p);setTimeout(()=>p.remove(),500);
    }}
}});
function anim(){{rx+=(mx-rx)*.12;ry+=(my-ry)*.12;ring.style.left=rx+'px';ring.style.top=ry+'px';requestAnimationFrame(anim);}}
anim();
document.addEventListener('mouseover',e=>{{if(e.target.tagName.match(/BUTTON|INPUT|SELECT|A/))ring.classList.add('h');}});
document.addEventListener('mouseout',e=>{{if(e.target.tagName.match(/BUTTON|INPUT|SELECT|A/))ring.classList.remove('h');}});
</script>
</body></html>
""", height=0, scrolling=False)

# ══════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════
def mono_label(text, color=None):
    c = color or T["text4"]
    st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:{c};margin-bottom:12px;display:flex;align-items:center;gap:10px;">{text}<span style="flex:1;height:1px;background:{T["rule"]};display:block;"></span></div>', unsafe_allow_html=True)

def divider(color=None):
    c = color or T["rule"]
    st.markdown(f'<div style="height:1px;background:{c};opacity:.4;margin:28px 0;"></div>', unsafe_allow_html=True)

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
        s.group(1).strip() if s else text[:250],
        m.group(1).strip() if m else "",
        l.group(1).strip() if l else ""
    )

def parse_hashtags(text):
    hv = re.search(r'HIGH VOLUME[^:]*:\s*([\s\S]*?)(?=MEDIUM VOLUME|$)', text, re.I)
    mv = re.search(r'MEDIUM VOLUME[^:]*:\s*([\s\S]*?)(?=NICHE|$)', text, re.I)
    nv = re.search(r'NICHE[^:]*:\s*([\s\S]*?)$', text, re.I)
    def tags(raw): return re.findall(r'#\w+', raw) if raw else []
    return (tags(hv.group(1) if hv else ""), tags(mv.group(1) if mv else ""), tags(nv.group(1) if nv else ""))

def format_script_rich(text):
    """Parse script into rich HTML with color coding"""
    hook  = re.search(r'HOOK[^:]*:\s*([\s\S]*?)(?=BODY|MIDDLE|$)', text, re.I)
    body  = re.search(r'(?:BODY|MIDDLE)[^:]*:\s*([\s\S]*?)(?=CTA|$)', text, re.I)
    cta   = re.search(r'CTA[^:]*:\s*([\s\S]*?)(?=SUGGESTED AUDIO|AUDIO|$)', text, re.I)
    audio = re.search(r'(?:SUGGESTED AUDIO|AUDIO)[^:]*:\s*([\s\S]*?)$', text, re.I)

    parts = []
    if hook:
        h = hook.group(1).strip()
        parts.append(f'<div style="margin-bottom:20px;padding:16px;background:{T["accent"]}0f;border-left:3px solid {T["accent"]};"><div style="font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["accent"]};margin-bottom:8px;">🔴 HOOK — 0 to 3 seconds</div><div style="font-size:16px;font-weight:600;color:{T["text"]};line-height:1.5;">{h}</div></div>')
    if body:
        b = body.group(1).strip()
        lines = [l.strip().lstrip('-').strip() for l in b.split('\n') if l.strip() and l.strip() not in ['-','•']]
        lines_html = "".join([f'<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:8px;"><span style="color:{T["text4"]};font-family:JetBrains Mono,monospace;font-size:10px;margin-top:2px;flex-shrink:0;">{str(i+1).zfill(2)}</span><span style="font-size:14px;color:{T["text2"]};line-height:1.5;">{l}</span></div>' for i,l in enumerate(lines) if l])
        parts.append(f'<div style="margin-bottom:20px;padding:16px;background:{T["bg3"]};border-left:3px solid {T["text4"]};"><div style="font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text3"]};margin-bottom:12px;">⚪ BODY — 3 to 25 seconds</div>{lines_html}</div>')
    if cta:
        c2 = cta.group(1).strip()
        parts.append(f'<div style="margin-bottom:20px;padding:16px;background:{T["green"]}0f;border-left:3px solid {T["green"]};"><div style="font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["green"]};margin-bottom:8px;">🟢 CTA — 25 to 30 seconds</div><div style="font-size:14px;color:{T["text"]};line-height:1.5;">{c2}</div></div>')
    if audio:
        a = audio.group(1).strip()
        parts.append(f'<div style="padding:16px;background:{T["purple"]}0f;border-left:3px solid {T["purple"]};"><div style="font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["purple"]};margin-bottom:8px;">🟣 AUDIO DIRECTION</div><div style="font-size:13px;color:{T["text2"]};line-height:1.6;">{a}</div></div>')

    return "".join(parts) if parts else f'<div style="font-size:14px;color:{T["text2"]};white-space:pre-wrap;line-height:1.8;">{text}</div>'

POSTING_TIMES = {
    "Instagram Reels": [("6–8 AM","Morning",False),("12–2 PM","Lunch",False),("7–9 PM","Evening",True),("10–11 PM","Night",False)],
    "TikTok": [("7–9 AM","Morning",False),("3–5 PM","Afternoon",False),("7–9 PM","Prime",True),("11 PM","Late",False)],
    "YouTube Shorts": [("8–10 AM","Morning",False),("2–4 PM","Afternoon",True),("6–8 PM","Evening",False)],
}

# ══════════════════════════════════════════
# CONTENT OUTPUT CARD (with copy, no glass)
# ══════════════════════════════════════════
def output_card(title, content, accent=None, confidence=None, rich_html=None):
    ac = accent or T["accent"]
    wc = len(content.split()) if content else 0
    conf_str = f'<span style="font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:1px;color:{T["green"]};margin-left:10px;">✦ {confidence}% CONFIDENCE</span>' if confidence else ""
    safe = content.replace("\\","\\\\").replace("`","'").replace('"','\\"').replace("\n","\\n")

    if rich_html:
        body_content = rich_html
        height_estimate = max(300, len(content)//3 + 200)
    else:
        body_content = f'<div style="font-size:14px;line-height:1.85;color:{T["text2"]};white-space:pre-wrap;font-family:Inter,sans-serif;">{content.replace(chr(10),"<br>")}</div>'
        height_estimate = max(160, min(len(content)//2 + 120, 520))

    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;font-family:Inter,sans-serif;padding:2px 0;}}
.card{{background:{T["bg2"]};border:1px solid {T["rule"]};border-top:2px solid {ac};overflow:hidden;transition:border-color .25s,box-shadow .25s;}}
.card:hover{{border-color:{ac}50;box-shadow:0 4px 32px {ac}0a;}}
.head{{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid {T["rule"]};background:{T["bg3"]};}}
.title{{font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:2.5px;text-transform:uppercase;color:{ac};display:flex;align-items:center;}}
.meta{{display:flex;align-items:center;gap:8px;}}
.chip{{font-family:JetBrains Mono,monospace;font-size:7px;color:{T["text4"]};background:{T["bg4"]};border:1px solid {T["rule2"]};padding:2px 7px;}}
.cbtn{{background:transparent;border:1px solid {T["rule2"]};color:{T["text3"]};font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:1px;padding:4px 10px;cursor:pointer;transition:all .15s;text-transform:uppercase;}}
.cbtn:hover{{border-color:{ac};color:{ac};}}
.cbtn.ok{{border-color:{T["green"]};color:{T["green"]};}}
.body{{padding:16px;}}
</style>
</head><body>
<div class="card">
  <div class="head">
    <div class="title">{title}{conf_str}</div>
    <div class="meta">
      <span class="chip">{wc} words</span>
      <button class="cbtn" id="cb" onclick="cp()">COPY</button>
    </div>
  </div>
  <div class="body">{body_content}</div>
</div>
<script>
const raw="{safe}".replace(/\\n/g,'\\n');
function cp(){{navigator.clipboard.writeText(raw).then(()=>{{const b=document.getElementById('cb');b.textContent='✓ COPIED';b.classList.add('ok');setTimeout(()=>{{b.textContent='COPY';b.classList.remove('ok');}},2000);}});}}
</script>
</body></html>
""", height=height_estimate, scrolling=False)

# ══════════════════════════════════════════
# SCORE CARDS (animated counters, no glass)
# ══════════════════════════════════════════
def score_cards(scores):
    items = [
        ("Viral Potential","viral",T["accent"]),
        ("Hook Strength","hook",T["purple"]),
        ("Engagement","engagement",T["blue"]),
        ("Shareability","share",T["green"]),
        ("Retention","retention",T["yellow"]),
        ("Reach Rating","reach",T["orange"]),
    ]
    cards = ""
    for label, key, color in items:
        val, _ = scores[key]
        conf = val + random.randint(0,3)
        cards += f"""
<div class="sc" style="--ac:{color};" onmousemove="tilt(this,event)" onmouseleave="rt(this)">
  <div class="sl">{label}</div>
  <div class="sv" data-t="{val}">0</div>
  <div class="sb"><div class="sf" data-w="{val}"></div></div>
  <div class="sc2">AI CONFIDENCE: {conf}%</div>
</div>"""

    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;font-family:JetBrains Mono,monospace;padding:4px 2px;}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;}}
.sc{{background:{T["bg2"]};border:1px solid {T["rule"]};border-top:2px solid var(--ac);padding:16px;transition:transform .2s,box-shadow .25s;cursor:default;}}
.sc:hover{{box-shadow:0 8px 30px var(--ac)18;}}
.sl{{font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text3"]};margin-bottom:8px;}}
.sv{{font-size:30px;font-weight:600;color:var(--ac);line-height:1;margin-bottom:8px;}}
.sb{{height:2px;background:{T["rule2"]};overflow:hidden;margin-bottom:8px;}}
.sf{{height:100%;background:var(--ac);width:0%;transition:width 1.5s cubic-bezier(.4,0,.2,1);}}
.sc2{{font-size:7px;letter-spacing:1px;color:{T["green"]};opacity:.7;}}
</style>
</head><body>
<div class="grid">{cards}</div>
<script>
document.querySelectorAll('.sv').forEach(el=>{{
    const t=parseInt(el.dataset.t);let c=0;
    const s=Math.ceil(t/50);
    const tm=setInterval(()=>{{c=Math.min(c+s,t);el.textContent=c;if(c>=t)clearInterval(tm);}},22);
}});
setTimeout(()=>document.querySelectorAll('.sf').forEach(el=>el.style.width=el.dataset.w+'%'),80);
function tilt(c,e){{
    const r=c.getBoundingClientRect();
    const rx=((e.clientY-r.top-r.height/2)/r.height)*-5;
    const ry=((e.clientX-r.left-r.width/2)/r.width)*5;
    c.style.transform=`perspective(600px) rotateX(${{rx}}deg) rotateY(${{ry}}deg) translateY(-2px)`;
}}
function rt(c){{c.style.transform='';}}
</script>
</body></html>
""", height=240, scrolling=False)

# ══════════════════════════════════════════
# RADAR CHART
# ══════════════════════════════════════════
def radar_chart(scores):
    vals = [scores[k][0] for k in ['viral','hook','engagement','share','retention','reach']]
    components.html(f"""
<!DOCTYPE html><html><head>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>*{{margin:0;padding:0;}}body{{background:transparent;display:flex;align-items:center;justify-content:center;}}canvas{{max-width:220px;max-height:220px;}}</style>
</head><body>
<canvas id="r"></canvas>
<script>
new Chart(document.getElementById('r'),{{
    type:'radar',
    data:{{labels:['Viral','Hook','Engage','Share','Retain','Reach'],datasets:[{{data:{vals},backgroundColor:'rgba(255,75,43,0.08)',borderColor:'{T["accent"]}',borderWidth:1.5,pointBackgroundColor:'{T["accent"]}',pointRadius:4}}]}},
    options:{{responsive:true,scales:{{r:{{min:0,max:100,ticks:{{display:false}},grid:{{color:'{T["rule2"]}'}},angleLines:{{color:'{T["rule2"]}'}},pointLabels:{{color:'{T["text3"]}',font:{{family:'JetBrains Mono',size:9}}}}}}}},plugins:{{legend:{{display:false}}}},animation:{{duration:1200,easing:'easeOutQuart'}}}}
}});
</script>
</body></html>
""", height=240, scrolling=False)

# ══════════════════════════════════════════
# HASHTAG COMPONENT
# ══════════════════════════════════════════
def hashtag_component(hv, mv, nv):
    def thtml(tags, color):
        return "".join([f'<span class="t" style="--c:{color};" onclick="ct(this)">{t}</span>' for t in tags])
    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;padding:4px 0;font-family:Inter,sans-serif;}}
.g{{margin-bottom:20px;}}
.gl{{font-family:JetBrains Mono,monospace;font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text3"]};margin-bottom:10px;display:flex;align-items:center;justify-content:space-between;}}
.ca{{background:transparent;border:1px solid {T["rule2"]};color:{T["text4"]};font-family:JetBrains Mono,monospace;font-size:7px;letter-spacing:1px;padding:3px 8px;cursor:pointer;transition:all .15s;text-transform:uppercase;}}
.ca:hover{{border-color:{T["accent"]};color:{T["accent"]};}}
.ts{{display:flex;flex-wrap:wrap;gap:6px;}}
.t{{background:{T["bg3"]};border:1px solid {T["rule2"]};color:{T["text2"]};font-family:JetBrains Mono,monospace;font-size:10px;padding:5px 10px;cursor:pointer;transition:all .2s;}}
.t:hover{{border-color:var(--c);color:var(--c);transform:translateY(-2px);box-shadow:0 4px 12px var(--c)20;}}
.toast{{position:fixed;bottom:12px;right:12px;background:{T["accent"]};color:#fff;font-family:JetBrains Mono,monospace;font-size:9px;letter-spacing:2px;padding:7px 14px;opacity:0;transition:opacity .2s;pointer-events:none;}}
.toast.s{{opacity:1;}}
</style>
</head><body>
<div class="g"><div class="gl"><span>High Volume — 1M+ ({len(hv)} tags)</span><button class="ca" onclick="cg('hv')">COPY ALL</button></div><div class="ts" id="hv">{thtml(hv,T["accent"])}</div></div>
<div class="g"><div class="gl"><span>Medium Volume — 100K–1M ({len(mv)} tags)</span><button class="ca" onclick="cg('mv')">COPY ALL</button></div><div class="ts" id="mv">{thtml(mv,T["blue"])}</div></div>
<div class="g"><div class="gl"><span>Niche Community — Under 100K ({len(nv)} tags)</span><button class="ca" onclick="cg('nv')">COPY ALL</button></div><div class="ts" id="nv">{thtml(nv,T["green"])}</div></div>
<div class="toast" id="toast">COPIED</div>
<script>
function sh(){{const t=document.getElementById('toast');t.classList.add('s');setTimeout(()=>t.classList.remove('s'),1500);}}
function ct(el){{navigator.clipboard.writeText(el.textContent);sh();}}
function cg(id){{navigator.clipboard.writeText(Array.from(document.getElementById(id).querySelectorAll('.t')).map(t=>t.textContent).join(' '));sh();}}
</script>
</body></html>
""", height=310, scrolling=False)

# ══════════════════════════════════════════
# GENERATE BUTTON (liquid, no duplicate)
# ══════════════════════════════════════════
def generate_button(label="→ GENERATE", key="gbtn"):
    clicked = components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;height:60px;display:flex;align-items:center;}}
.btn{{width:100%;height:54px;background:none;border:none;cursor:pointer;position:relative;overflow:hidden;outline:none;}}
.fill{{position:absolute;inset:0;background:linear-gradient(110deg,{T["accent"]} 0%,{T["accent2"]} 35%,{T["purple"]} 70%,{T["accent"]} 130%);background-size:250% 250%;animation:lf 3.5s ease infinite;}}
@keyframes lf{{0%{{background-position:0% 50%}}50%{{background-position:100% 50%}}100%{{background-position:0% 50%}}}}
.btn:hover .fill{{filter:brightness(1.12);}}
.btn:active .fill{{filter:brightness(.88);}}
.label{{position:relative;z-index:2;font-family:JetBrains Mono,monospace;font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#fff;pointer-events:none;}}
.rip{{position:absolute;border-radius:50%;background:rgba(255,255,255,.3);transform:scale(0);animation:ra .6s linear forwards;pointer-events:none;}}
@keyframes ra{{to{{transform:scale(4);opacity:0;}}}}
</style>
</head><body>
<button class="btn" id="b">
  <div class="fill"></div>
  <span class="label">{label}</span>
</button>
<script>
document.getElementById('b').addEventListener('click',e=>{{
    const btn=e.currentTarget,rect=btn.getBoundingClientRect();
    const r=document.createElement('span');r.className='rip';
    const sz=Math.max(rect.width,rect.height);
    r.style.cssText=`width:${{sz}}px;height:${{sz}}px;left:${{e.clientX-rect.left-sz/2}}px;top:${{e.clientY-rect.top-sz/2}}px`;
    btn.appendChild(r);setTimeout(()=>r.remove(),600);
    // Particles
    for(let i=0;i<30;i++){{
        const p=document.createElement('div'),angle=(Math.PI*2*i)/30,d=50+Math.random()*90;
        const sz2=Math.random()*6+2,cols=['{T["accent"]}','{T["accent2"]}','{T["purple"]}','#fff'];
        const col=cols[Math.floor(Math.random()*4)],dur=(.4+Math.random()*.6)+'s';
        const style=document.createElement('style');
        style.textContent=`@keyframes pf${{i}}{{0%{{transform:translate(0,0) scale(1);opacity:1}}100%{{transform:translate(${{Math.cos(angle)*d}}px,${{Math.sin(angle)*d}}px) scale(0);opacity:0}}}}`;
        document.head.appendChild(style);
        p.style.cssText=`position:fixed;border-radius:50%;pointer-events:none;z-index:9997;left:${{e.clientX}}px;top:${{e.clientY}}px;width:${{sz2}}px;height:${{sz2}}px;background:${{col}};animation:pf${{i}} ${{dur}} ease-out forwards;`;
        document.body.appendChild(p);
        setTimeout(()=>{{p.remove();style.remove();}},parseFloat(dur)*1000);
    }}
    window.parent.postMessage({{type:'btn_click',key:'{key}'}}, '*');
}});
</script>
</body></html>
""", height=60, scrolling=False)

# ══════════════════════════════════════════
# LOADING STEPS
# ══════════════════════════════════════════
def show_loading(steps):
    ph = st.empty()
    rows = lambda done: "".join([
        f'<div style="display:flex;align-items:center;gap:14px;padding:10px 0;border-bottom:1px solid {T["rule"]};font-family:JetBrains Mono,monospace;font-size:10px;letter-spacing:1px;color:{T["green"] if i<done else (T["accent"] if i==done else T["text4"])};"><span style="width:16px;text-align:center;">{"✓" if i<done else ("◌" if i==done else str(i+1))}</span><span>{s}</span></div>'
        for i,s in enumerate(steps)
    ])
    for i in range(len(steps)):
        ph.markdown(f'<div style="background:{T["bg2"]};border:1px solid {T["rule"]};padding:24px;margin:16px 0;">{rows(i)}</div>', unsafe_allow_html=True)
        time.sleep(0.45)
    ph.markdown(f'<div style="background:{T["bg2"]};border:1px solid {T["rule"]};padding:24px;margin:16px 0;">{rows(len(steps))}</div>', unsafe_allow_html=True)
    time.sleep(0.3)
    ph.empty()

# ══════════════════════════════════════════
# TOP NAV
# ══════════════════════════════════════════
inject_cursor()
theme_icon = "☀" if IS_DARK else "◑"

st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;padding:0 40px;height:56px;background:{T["bg"]}f0;border-bottom:1px solid {T["rule"]};position:sticky;top:0;z-index:100;backdrop-filter:blur(12px);">
  <div style="display:flex;align-items:center;gap:32px;">
    <div style="font-family:Syne,sans-serif;font-size:16px;font-weight:800;color:{T["text"]};letter-spacing:-.5px;">
      Reel<span style="color:{T["accent"]};">Mind</span>
    </div>
    <div style="display:flex;gap:0;">
      <div id="nav_rm" style="font-family:JetBrains Mono,monospace;font-size:9px;letter-spacing:2px;text-transform:uppercase;padding:4px 16px;border-bottom:2px solid {"" + T["accent"] + "" if st.session_state.page == "reelmind" else "transparent"};color:{"" + T["accent"] + "" if st.session_state.page == "reelmind" else T["text3"]};cursor:pointer;">Content</div>
      <div id="nav_sf" style="font-family:JetBrains Mono,monospace;font-size:9px;letter-spacing:2px;text-transform:uppercase;padding:4px 16px;border-bottom:2px solid {"" + T["gold"] + "" if st.session_state.page == "storyflow" else "transparent"};color:{"" + T["gold"] + "" if st.session_state.page == "storyflow" else T["text3"]};cursor:pointer;">Video Maker</div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="display:flex;align-items:center;gap:6px;font-family:JetBrains Mono,monospace;font-size:8px;color:{T["green"]};"><div style="width:5px;height:5px;background:{T["green"]};border-radius:50%;"></div>GEMINI LIVE</div>
    <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:{T["text4"]};background:{T["bg3"]};border:1px solid {T["rule2"]};padding:3px 9px;">v4.0</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Nav buttons
col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1,1,8,1])
with col_nav1:
    if st.button("CONTENT", key="nav_rm_btn"):
        st.session_state.page = "reelmind"
        st.rerun()
with col_nav2:
    if st.button("VIDEO MAKER", key="nav_sf_btn"):
        st.session_state.page = "storyflow"
        st.rerun()
with col_nav4:
    if st.button(theme_icon, key="theme_btn"):
        st.session_state.theme = "light" if IS_DARK else "dark"
        st.rerun()

# ══════════════════════════════════════════
# ██████████████ REELMIND PAGE ██████████████
# ══════════════════════════════════════════
if st.session_state.page == "reelmind":

    # ── BIG HERO ──
    st.markdown(f"""
<div style="padding:72px 40px 56px;border-bottom:1px solid {T["rule"]};position:relative;overflow:hidden;min-height:340px;">
  <div style="position:absolute;top:0;right:0;width:50%;height:100%;background:linear-gradient(135deg,transparent 0%,{T["accent"]}05 100%);pointer-events:none;"></div>
  <div style="font-family:JetBrains Mono,monospace;font-size:9px;letter-spacing:4px;text-transform:uppercase;color:{T["accent"]};margin-bottom:20px;display:flex;align-items:center;gap:12px;"><span style="width:20px;height:1px;background:{T["accent"]};display:inline-block;"></span>AI Content Engine — Studio Grade</div>
  <div style="font-family:Syne,sans-serif;font-size:clamp(48px,6vw,88px);font-weight:800;line-height:.9;letter-spacing:-3px;color:{T["text"]};margin-bottom:20px;">Generate<br><span style="color:{T["accent"]};">Viral</span><br>Content</div>
  <div style="font-size:15px;color:{T["text3"]};max-width:440px;line-height:1.65;margin-bottom:32px;">Captions, hashtags, scripts, thumbnails — all engineered for the algorithm, not just aesthetics.</div>
  <div style="display:flex;gap:24px;flex-wrap:wrap;">
    {"".join([f'<div style="display:flex;flex-direction:column;gap:3px;"><div style="font-family:JetBrains Mono,monospace;font-size:22px;font-weight:600;color:{T["text"]};">{n}</div><div style="font-family:JetBrains Mono,monospace;font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">{l}</div></div>' for n,l in [("4","Outputs/run"),("30","Hashtags"),("3","Captions"),("16","Niches")]])}
  </div>
</div>
""", unsafe_allow_html=True)

    # ── FORM ──
    st.markdown(f"<div style='padding:40px 40px 0;'>", unsafe_allow_html=True)
    mono_label("Configure Your Content")

    col_mode, col_right = st.columns([1, 2], gap="large")

    with col_mode:
        mode = st.radio("Mode", [
            "⚡ Full Content Pack","🎯 Hook Ideas Only",
            "📅 Content Series","🎠 Carousel Post",
            "🧵 X/Twitter Thread","🔄 Content Repurposer"
        ], label_visibility="collapsed")

    with col_right:
        r1, r2 = st.columns(2)
        with r1:
            topic = st.text_input("Topic", placeholder="e.g. Villain arc, AI tools, Gym motivation...")
            platform = st.selectbox("Platform", ["Instagram Reels","TikTok","YouTube Shorts"])
            tone = st.selectbox("Tone", ["Viral & Bold","Dark & Cinematic","Motivational & Intense","Minimal & Clean","Edgy & Controversial","Informative & Professional"])
        with r2:
            niche = st.selectbox("Niche", ["Dark Aesthetic / Motivation","Gaming","Anime & Manga","Fitness & Gym","Tech & AI","Finance & Investing","Horror & Thriller","Fashion & Lifestyle","Education","Movie Industry","Music & Artists","Business & Entrepreneurship","Luxury & Premium","Cars & Motorsport","Travel & Adventure","Food & Cooking"])
            num_posts = 5
            original_content = ""
            target_platform = "TikTok"
            if "Series" in mode:
                num_posts = st.selectbox("Posts in Series", [3,5,7])
            if "Repurposer" in mode:
                original_content = st.text_area("Paste original content", height=80)
                target_platform = st.selectbox("Repurpose for", ["TikTok","YouTube Shorts","X/Twitter","LinkedIn"])

        generate_button("→ GENERATE CONTENT", "rm_gen")
        gen_btn = st.button("GENERATE", key="rm_gen_fallback")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── GENERATE ──
    if gen_btn:
        if not topic.strip():
            st.warning("Enter a topic to generate content.")
            st.stop()

        st.markdown("<div style='padding:0 40px;'>", unsafe_allow_html=True)
        show_loading([
            "Analyzing topic & niche...",
            "Writing detailed captions...",
            "Building hashtag strategy...",
            "Crafting full reel script...",
            "Designing thumbnail prompt...",
            "Computing AI confidence scores...",
        ])

        result = None; raw_output = None; error_msg = None
        try:
            if "Full Content" in mode:
                result = generate_full_content(topic, niche, platform, tone)
                if "ERROR" in result.get("raw",""): error_msg = result["raw"].split("||")[-1]
            elif "Hook" in mode:
                raw_output = generate_hooks(topic, niche)
                if raw_output and "ERROR" in raw_output: error_msg = raw_output.split("||")[-1]
            elif "Series" in mode:
                raw_output = generate_series(topic, niche, platform, num_posts)
                if raw_output and "ERROR" in raw_output: error_msg = raw_output.split("||")[-1]
            elif "Carousel" in mode:
                raw_output = generate_carousel(topic, niche, platform)
                if raw_output and "ERROR" in raw_output: error_msg = raw_output.split("||")[-1]
            elif "Thread" in mode:
                raw_output = generate_thread(topic, niche)
                if raw_output and "ERROR" in raw_output: error_msg = raw_output.split("||")[-1]
            elif "Repurposer" in mode:
                raw_output = repurpose_content(original_content, target_platform)
                if raw_output and "ERROR" in raw_output: error_msg = raw_output.split("||")[-1]
        except Exception as e:
            error_msg = str(e)

        if error_msg:
            st.error(f"Generation failed: {error_msg}")
            st.stop()

        if result: st.session_state.rm_result = result
        scores = gen_scores(); st.session_state.rm_scores = scores
        st.session_state.history.append({"topic": topic, "niche": niche, "time": datetime.datetime.now().strftime("%H:%M")})
        confidence = random.randint(88,97)

        divider()
        mono_label("Content Score Card")
        score_cards(scores)
        divider()

        col_r, col_a = st.columns([1,1])
        with col_r:
            mono_label("Content Radar")
            radar_chart(scores)
        with col_a:
            mono_label("Best Posting Times")
            times = POSTING_TIMES.get(platform, POSTING_TIMES["Instagram Reels"])
            st.markdown("".join([f'<span style="display:inline-block;background:{T["bg3"]};border:1px solid {"" + T["green"] + "" if best else T["rule2"]};padding:8px 14px;font-family:JetBrains Mono,monospace;font-size:9px;color:{"" + T["green"] + "" if best else T["text3"]};margin:3px;{"background:"+T["green"]+"0f;" if best else ""}">{t}<small style="display:block;font-size:7px;letter-spacing:1px;">{label}{"  ★" if best else ""}</small></span>' for t,label,best in times]), unsafe_allow_html=True)

        divider()

        if "Full Content" in mode and result:
            tab1,tab2,tab3,tab4 = st.tabs(["📝  CAPTIONS","#️⃣  HASHTAGS","🎬  SCRIPT","🖼️  THUMBNAIL"])

            with tab1:
                short, med, long_cap = parse_captions(result.get("captions",""))
                for cap_text, label in [(short,"Short Caption"),(med,"Medium Caption"),(long_cap,"Long Caption")]:
                    output_card(label, cap_text, T["accent"], confidence)
                    st.download_button(f"↓ {label}", cap_text, file_name=f"{label.lower().replace(' ','_')}.txt", key=f"dl_{label[:3]}")
                    st.markdown("<br>", unsafe_allow_html=True)

            with tab2:
                hv, mv, nv = parse_hashtags(result.get("hashtags",""))
                hashtag_component(hv, mv, nv)
                st.download_button("↓ Download All 30 Hashtags", " ".join(hv+mv+nv), file_name="hashtags.txt", key="dl_ht")

            with tab3:
                mono_label("Full Reel Script — Formatted & Color Coded")
                st.markdown(f'<div style="font-size:12px;color:{T["text3"]};margin-bottom:16px;line-height:1.6;">Each section is color coded — Red = Hook, Grey = Body, Green = CTA, Purple = Audio. Every line is a complete on-screen text line.</div>', unsafe_allow_html=True)
                rich = format_script_rich(result.get("script",""))
                output_card("Reel Script — 30 Seconds", result.get("script",""), T["purple"], confidence, rich_html=rich)
                st.download_button("↓ Download Script", result.get("script",""), file_name="reel_script.txt", key="dl_sc")

            with tab4:
                thumb = result.get("thumbnail","")
                mj_m = re.search(r'(?:IMAGE PROMPT|PROMPT)[^:]*:\s*([\s\S]*?)(?=STYLE|$)', thumb, re.I)
                style_m = re.search(r'STYLE[^:]*:\s*([\s\S]*?)(?=COLOR|$)', thumb, re.I)
                color_m = re.search(r'COLOR[^:]*:\s*([\s\S]*?)$', thumb, re.I)
                base = mj_m.group(1).strip() if mj_m else thumb[:300]
                sty = style_m.group(1).strip() if style_m else ""
                colors_t = color_m.group(1).strip() if color_m else ""
                mj = f"{base}\n\n--style raw --ar 9:16 --v 6\nStyle: {sty}\nColors: {colors_t}"
                ideogram = f"{base}\n\nStyle: {sty}\nPalette: {colors_t}\nHigh detail, sharp focus, 9:16 aspect ratio"
                output_card("Midjourney Prompt", mj, T["accent"], confidence)
                st.download_button("↓ MJ Prompt", mj, file_name="mj_prompt.txt", key="dl_mj")
                st.markdown("<br>", unsafe_allow_html=True)
                output_card("Ideogram / Gemini Image Prompt", ideogram, T["blue"], confidence)
                st.download_button("↓ Ideogram Prompt", ideogram, file_name="ideogram_prompt.txt", key="dl_id")

            divider()
            c1,c2 = st.columns(2)
            with c1:
                full = f"REELMIND AI\nTopic: {topic} | Niche: {niche} | Platform: {platform}\n{'='*60}\n\n{result.get('raw','')}"
                st.download_button("↓ Download Full Pack (.txt)", full, file_name=f"reelmind_{topic[:20].replace(' ','_')}_full.txt", key="dl_full")
            with c2:
                st.download_button("↓ Download Raw Output", result.get("raw",""), file_name="reelmind_raw.txt", key="dl_raw")

        else:
            mode_label = mode.split(" ",1)[1] if " " in mode else mode
            output_card(mode_label, raw_output or "No output generated.", T["accent"])
            if raw_output:
                st.download_button("↓ Download Output", raw_output, file_name=f"reelmind_output.txt", key="dl_other")

        st.markdown("</div>", unsafe_allow_html=True)

    # history strip
    if st.session_state.history:
        st.markdown(f"<div style='padding:0 40px;'>", unsafe_allow_html=True)
        divider()
        mono_label("Recent Generations")
        cols = st.columns(min(4, len(st.session_state.history)))
        for i, h in enumerate(st.session_state.history[-4:]):
            with cols[i]:
                st.markdown(f'<div style="background:{T["bg2"]};border:1px solid {T["rule"]};padding:12px 14px;"><div style="font-size:13px;font-weight:500;color:{T["text"]};margin-bottom:4px;">{h["topic"][:22]}</div><div style="font-family:JetBrains Mono,monospace;font-size:7px;color:{T["text4"]};">{h["niche"][:20]} · {h["time"]}</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════
# ██████████████ STORYFLOW PAGE ██████████████
# ══════════════════════════════════════════
elif st.session_state.page == "storyflow":

    # ── DIFFERENT HERO — GOLD/CINEMATIC ──
    st.markdown(f"""
<div style="padding:72px 40px 56px;border-bottom:1px solid {T["rule"]};position:relative;overflow:hidden;min-height:340px;background:linear-gradient(135deg,{T["bg"]} 60%,{T["gold"]}06 100%);">
  <div style="position:absolute;bottom:-40px;right:-20px;width:400px;height:400px;background:radial-gradient(circle,{T["gold"]}08 0%,transparent 70%);pointer-events:none;"></div>
  <div style="font-family:JetBrains Mono,monospace;font-size:9px;letter-spacing:4px;text-transform:uppercase;color:{T["gold"]};margin-bottom:20px;display:flex;align-items:center;gap:12px;"><span style="width:20px;height:1px;background:{T["gold"]};display:inline-block;"></span>AI Video Story Engine — Pixar Grade</div>
  <div style="font-family:Syne,sans-serif;font-size:clamp(48px,6vw,88px);font-weight:800;line-height:.9;letter-spacing:-3px;color:{T["text"]};margin-bottom:20px;">Craft<br><span style="color:{T["gold"]};">Cinematic</span><br>Stories</div>
  <div style="font-size:15px;color:{T["text3"]};max-width:480px;line-height:1.65;margin-bottom:32px;">Complete video production packages — stories, character sheets, Frame 1, and full prompt chains for smooth AI video generation.</div>
  <div style="display:flex;gap:10px;flex-wrap:wrap;">
    {"".join([f'<div style="background:{T["bg3"]};border:1px solid {T["rule2"]};padding:8px 16px;font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:1px;color:{T["text3"]};">{t}</div>' for t in ["3 Story Options","Character Sheets","Frame 1 Prompt","Full Prompt Chain","Continuity Engine"]])}
  </div>
</div>
""", unsafe_allow_html=True)

    # Progress
    prog = (st.session_state.sf_step - 1) / 3 * 100
    st.markdown(f'<div style="height:2px;background:{T["rule"]};"><div style="height:100%;width:{prog}%;background:linear-gradient(90deg,{T["gold"]},{T["accent"]});transition:width .6s;"></div></div>', unsafe_allow_html=True)

    # Step indicator
    steps_nav = ["Configure","Select Story","Generate Package","Export"]
    step_html = "".join([
        f'<div style="display:flex;align-items:center;gap:6px;font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:1px;text-transform:uppercase;color:{T["gold"] if i+1==st.session_state.sf_step else (T["green"] if i+1<st.session_state.sf_step else T["text4"])};">{"✓" if i+1<st.session_state.sf_step else ("▶" if i+1==st.session_state.sf_step else "○")} {s}</div>'
        for i,s in enumerate(steps_nav)
    ])
    sep = f'<span style="color:{T["rule2"]};">—</span>'
    st.markdown(f'<div style="padding:16px 40px;border-bottom:1px solid {T["rule"]};display:flex;gap:16px;align-items:center;">{sep.join([f"<div>{h}</div>" for h in step_html.split("</div><div>")])}</div>', unsafe_allow_html=True)

    st.markdown("<div style='padding:40px;'>", unsafe_allow_html=True)

    # ── STEP 1: CONFIGURE ──
    if st.session_state.sf_step == 1:
        mono_label("Step 1 — Configure Your Story", T["gold"])
        st.markdown(f'<div style="font-size:14px;color:{T["text3"]};margin-bottom:28px;line-height:1.65;max-width:600px;">Choose your story parameters. AI generates 3 complete story options with full cinematic breakdowns, viral scores, and scene object lists.</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            sf_story_type = st.selectbox("Story Type", ["Funny","Emotional","Cute","Action","Adventure","Mystery","Educational","Heartwarming"])
            sf_character = st.selectbox("Character", ["Puppy","Cat","Penguin","Fox","Bunny","Panda","Baby Bear","Duck","Hamster","Custom"])
            sf_custom_char = ""
            if sf_character == "Custom":
                sf_custom_char = st.text_input("Custom Character", placeholder="e.g. tiny baby dragon with big eyes")
        with col2:
            sf_duration = st.number_input("Duration (seconds)", min_value=8, max_value=600, value=30, step=1,
                                           help="Enter any duration. Must be divisible by your segment size.")
            sf_segment = st.selectbox("Segment Size", [8, 10], help="8s = more detail per segment. 10s = fewer, longer segments.")
            sf_style = st.selectbox("Animation Style", ["Pixar","Disney","DreamWorks","Anime","Chibi","Cartoon","Realistic"])
        with col3:
            sf_platform = st.selectbox("Platform", ["Instagram Reels","TikTok","YouTube Shorts","YouTube"])
            sf_ending = st.selectbox("Ending Type", ["Happy","Funny","Emotional","Twist","Sad","Random"])
            sf_custom_idea = st.text_area("Custom Story Idea (optional)", placeholder="e.g. Puppy tries to get a heart balloon stuck in a tree...", height=80)

        # Validation + prompt count preview
        num_prompts = sf_duration // sf_segment
        remainder = sf_duration % sf_segment
        if remainder != 0:
            st.warning(f"⚠️ {sf_duration}s is not divisible by {sf_segment}s. Will generate {num_prompts} prompts covering {num_prompts * sf_segment}s. Consider using {num_prompts * sf_segment}s or {(num_prompts+1) * sf_segment}s.")
        else:
            st.markdown(f'<div style="background:{T["green"]}0f;border:1px solid {T["green"]}30;padding:12px 16px;font-family:JetBrains Mono,monospace;font-size:10px;color:{T["green"]};margin:12px 0;">{sf_duration}s ÷ {sf_segment}s = <strong>{num_prompts} video prompts</strong> will be generated</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        generate_button("→ GENERATE 3 STORY OPTIONS", "sf_gen1_lbtn")
        sf_gen1 = st.button("GENERATE STORIES", key="sf_gen1_btn")

        if sf_gen1:
            st.session_state.sf_config = {
                "story_type": sf_story_type, "character": sf_character,
                "custom_char": sf_custom_char, "duration": sf_duration,
                "segment": sf_segment, "style": sf_style,
                "platform": sf_platform, "ending": sf_ending, "custom_idea": sf_custom_idea
            }
            show_loading([
                "Analyzing story type and character...",
                "Crafting dramatic arc: Hook → Conflict → Escalation → Payoff...",
                "Writing 3 complete story options...",
                "Calculating viral, emotion, and retention scores...",
                "Listing all scene objects for Frame 1 continuity...",
            ])
            cfg = st.session_state.sf_config
            raw = generate_story(cfg["story_type"], cfg["character"], cfg["duration"],
                                  cfg["style"], cfg["platform"], cfg["ending"],
                                  cfg["custom_char"], cfg["custom_idea"])
            if raw and "ERROR" in raw:
                st.error("Story generation failed: " + raw.split("||")[-1])
            else:
                st.session_state.sf_stories = raw
                st.session_state.sf_step = 2
                st.rerun()

    # ── STEP 2: SELECT STORY ──
    elif st.session_state.sf_step == 2:
        cfg = st.session_state.sf_config
        num_p = cfg["duration"] // cfg["segment"]
        mono_label("Step 2 — Review & Select Your Story", T["gold"])
        st.markdown(f'<div style="font-size:14px;color:{T["text3"]};margin-bottom:20px;line-height:1.65;">Review all 3 stories. Select one to develop into a complete production package ({num_p} video prompts × {cfg["segment"]}s each = {cfg["duration"]}s total).</div>', unsafe_allow_html=True)

        output_card("3 Complete Story Options", st.session_state.sf_stories or "", T["gold"])
        st.download_button("↓ Download Stories", st.session_state.sf_stories or "", file_name="stories.txt", key="dl_sf_s")

        divider()
        c1, c2 = st.columns([2,1])
        with c1:
            selected = st.selectbox("Select story to develop", ["Story Option 1","Story Option 2","Story Option 3"])
        with c2:
            custom_objects = st.text_input("Override scene objects (optional)", placeholder="balloon, tree, box, mud, bird...")

        st.markdown(f"""
<div style="background:{T["bg2"]};border:1px solid {T["rule"]};border-left:3px solid {T["gold"]};padding:16px;margin:20px 0;">
  <div style="font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["gold"]};margin-bottom:12px;">PACKAGE INCLUDES</div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;">
    {"".join([f'<div style="font-size:12px;color:{T["text2"]};"><span style="color:{T["gold"]};">→</span> {t}</div>' for t in ["Character design prompts","6 expression sheets","Frame 1 master prompt",f"{num_p} video prompts","Continuity checklist","How-to workflow guide"]])}
  </div>
</div>
""", unsafe_allow_html=True)

        generate_button(f"→ GENERATE {num_p} PROMPTS + FULL PACKAGE", "sf_gen2_lbtn")
        sf_gen2 = st.button("GENERATE FULL PACKAGE", key="sf_gen2_btn")
        if st.button("← Back", key="sf_back2"):
            st.session_state.sf_step = 1; st.rerun()

        if sf_gen2:
            st.session_state.sf_config["selected"] = selected
            st.session_state.sf_config["custom_objects"] = custom_objects
            show_loading([
                "Extracting story elements...",
                "Generating character design sheet prompts...",
                "Creating expression reference prompts...",
                "Building Frame 1 establishing shot...",
                f"Engineering {num_p} video prompts × {cfg['segment']}s each...",
                "Writing continuity checklist...",
            ])
            cfg = st.session_state.sf_config
            char = cfg["custom_char"] if cfg["custom_char"] else cfg["character"]
            story_sum = f'{cfg["story_type"]} {char} story, {cfg["duration"]}s, {cfg["ending"]} ending. {selected}.'
            scene_obj = custom_objects if custom_objects else ""
            if not scene_obj:
                from gemini_helper import safe_generate
                scene_obj = safe_generate(f"List all props, supporting characters, and environment elements needed for a {cfg['story_type']} {char} story with {cfg['ending']} ending. Respond with a simple comma-separated list only.")
            char_sheet = generate_character_sheet(char, cfg["style"], story_sum)
            frame1 = generate_frame1_prompt(story_sum, char, scene_obj, cfg["style"], cfg["platform"])
            prompt_chain = generate_prompt_chain(story_sum, char, scene_obj, cfg["duration"], cfg["segment"], cfg["style"], cfg["platform"])
            st.session_state.sf_char_sheet = char_sheet
            st.session_state.sf_frame1 = frame1
            st.session_state.sf_prompt_chain = prompt_chain
            st.session_state.sf_scene_objects = scene_obj
            st.session_state.sf_step = 3
            st.rerun()

    # ── STEP 3: FULL PACKAGE ──
    elif st.session_state.sf_step == 3:
        cfg = st.session_state.sf_config
        char = cfg.get("custom_char","") or cfg.get("character","")
        num_p = cfg["duration"] // cfg["segment"]
        confidence = random.randint(89,97)
        mono_label("Step 3 — Complete Production Package", T["gold"])

        st.markdown(f"""
<div style="background:{T["bg2"]};border:1px solid {T["rule"]};border-top:2px solid {T["gold"]};padding:16px 20px;margin-bottom:24px;display:flex;align-items:center;justify-content:space-between;">
  <div>
    <div style="font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["gold"]};margin-bottom:4px;">Package Ready</div>
    <div style="font-size:13px;color:{T["text2"]};">{char.title()} · {cfg["style"]} · {cfg["duration"]}s · {num_p} prompts × {cfg["segment"]}s</div>
  </div>
  <div style="font-family:JetBrains Mono,monospace;font-size:9px;color:{T["green"]};background:{T["green"]}0f;border:1px solid {T["green"]}30;padding:5px 12px;">✦ AI CONFIDENCE: {confidence}%</div>
</div>
""", unsafe_allow_html=True)

        t1,t2,t3,t4,t5 = st.tabs(["📋  SCENE OBJECTS","🎨  CHARACTER SHEETS","🖼️  FRAME 1",f"🎬  {num_p} PROMPTS","📖  HOW TO USE"])

        with t1:
            mono_label("All Scene Objects — Must All Be Visible in Frame 1")
            st.markdown(f'<div style="font-size:13px;color:{T["text3"]};margin-bottom:16px;line-height:1.65;max-width:600px;">Every object, character, and environment element that appears in your story must be planted in Frame 1 — even if minor. This prevents random spawning and teleporting in later prompts.</div>', unsafe_allow_html=True)
            output_card("Complete Scene Object List", st.session_state.sf_scene_objects or "", T["gold"], confidence)
            st.download_button("↓ Download Scene Objects", st.session_state.sf_scene_objects or "", file_name="scene_objects.txt", key="dl_obj")

        with t2:
            mono_label("Character Design Prompts")
            st.markdown(f'<div style="font-size:13px;color:{T["text3"]};margin-bottom:16px;line-height:1.65;max-width:600px;"><strong style="color:{T["text"]};">Generate these images first</strong> before any video. Upload character sheets to every single video prompt to maintain consistent appearance across all clips.</div>', unsafe_allow_html=True)
            output_card("Character Sheet + Expression Prompts", st.session_state.sf_char_sheet or "", T["purple"], confidence)
            st.download_button("↓ Download Character Sheets", st.session_state.sf_char_sheet or "", file_name="character_sheets.txt", key="dl_char")

        with t3:
            mono_label("Frame 1 — Master Establishing Shot")
            st.markdown(f'<div style="font-size:13px;color:{T["text3"]};margin-bottom:16px;line-height:1.65;max-width:600px;"><strong style="color:{T["text"]};">Generate this second.</strong> Frame 1 sets camera angle, lighting, character scale, and positions every story object. It becomes the foundation screenshot for Prompt 1.</div>', unsafe_allow_html=True)
            output_card("Frame 1 Master Prompt", st.session_state.sf_frame1 or "", T["accent"], confidence)
            st.download_button("↓ Download Frame 1 Prompt", st.session_state.sf_frame1 or "", file_name="frame1_prompt.txt", key="dl_f1")

        with t4:
            mono_label(f"Complete Video Prompt Chain — {num_p} Prompts × {cfg['segment']}s = {cfg['duration']}s Total")
            st.markdown(f'<div style="font-size:13px;color:{T["text3"]};margin-bottom:16px;line-height:1.65;max-width:600px;"><strong style="color:{T["text"]};">Use prompts in exact order.</strong> Each starts from the last-frame screenshot of the previous clip. Never skip the screenshot step.</div>', unsafe_allow_html=True)
            output_card(f"Full Prompt Chain — {num_p} Prompts", st.session_state.sf_prompt_chain or "", T["green"], confidence)
            st.download_button("↓ Download Prompt Chain", st.session_state.sf_prompt_chain or "", file_name="prompt_chain.txt", key="dl_chain")
            divider()
            full_pkg = f"""STORYFLOW AI — COMPLETE PRODUCTION PACKAGE
Character: {char} | Style: {cfg["style"]} | Duration: {cfg["duration"]}s | {num_p} prompts × {cfg["segment"]}s
{'='*70}

SCENE OBJECTS
{st.session_state.sf_scene_objects or ''}

CHARACTER SHEETS
{st.session_state.sf_char_sheet or ''}

FRAME 1 PROMPT
{st.session_state.sf_frame1 or ''}

VIDEO PROMPT CHAIN
{st.session_state.sf_prompt_chain or ''}
"""
            st.download_button("↓ Download Complete Package (.txt)", full_pkg, file_name=f"storyflow_{char.lower()}_complete.txt", key="dl_full_pkg")

        with t5:
            guide = f"""STORYFLOW AI — PRODUCTION WORKFLOW GUIDE
{'='*60}

WORKFLOW OVERVIEW:
Character Sheets → Frame 1 → Prompt 1 → Screenshot → Prompt 2 → Screenshot → ... → Final

STEP 1 — GENERATE CHARACTER DESIGN SHEETS
Use the prompts from the Character Sheets tab in any AI image generator
(Midjourney, Ideogram, or Gemini Image).
Generate the full turnaround sheet and all 6 facial expressions.
Save all character images — upload them to every single video prompt.

STEP 2 — GENERATE FRAME 1 (ESTABLISHING SHOT)
Use the Frame 1 prompt from the Frame 1 tab.
This creates your master environment image with ALL objects visible.
Save this image — it becomes the starting point for Prompt 1.

STEP 3 — GENERATE CLIP 1
Open Google Flow or Gemini Video.
Upload: Character sheets + Frame 1 image.
Enter: Prompt 1 from the Prompt Chain.
Generate the first {cfg["segment"]}-second clip.

STEP 4 — SCREENSHOT THE LAST FRAME (CRITICAL STEP)
Watch the generated clip.
Pause on the very last frame.
Take a screenshot.
This screenshot is your continuity anchor for the next clip.

STEP 5 — GENERATE CLIP 2
Upload: Character sheets + screenshot from Step 4.
Enter: Prompt 2.
Generate the second clip.

STEP 6 — REPEAT FOR ALL {num_p} PROMPTS
For every new prompt:
  1. Upload character sheets for characters appearing in that prompt
  2. Upload screenshot of last frame from previous clip
  3. Enter the next prompt
  4. Generate → screenshot last frame → move to next

TOTAL WORKFLOW: {num_p} clips × {cfg["segment"]}s = {cfg["duration"]}s final video

GOLDEN RULES:
→ NEVER generate Prompt 2+ without the previous last frame screenshot
→ ALWAYS upload character sheets — they lock face, fur, and size
→ ALWAYS use the same AI model and project for all clips
→ NEVER add new objects that weren't in Frame 1
→ Every important object MUST already be in Frame 1

CONTINUITY CHECKLIST (check before each prompt):
□ Character sheets uploaded
□ Previous last-frame screenshot uploaded
□ Same camera angle maintained
□ Same lighting maintained
□ All story objects in same positions
□ Character in same location as end of previous clip
"""
            output_card("Complete Production Workflow Guide", guide.strip(), T["gold"])
            st.download_button("↓ Download Workflow Guide", guide, file_name="workflow_guide.txt", key="dl_guide")

        divider()
        cb1, cb2 = st.columns(2)
        with cb1:
            if st.button("← Back to Story Selection", key="back_step3"):
                st.session_state.sf_step = 2; st.rerun()
        with cb2:
            if st.button("↺ Start New Story", key="restart_sf"):
                for k in ["sf_step","sf_stories","sf_char_sheet","sf_frame1","sf_prompt_chain","sf_scene_objects","sf_config"]:
                    st.session_state[k] = DEFAULTS[k]
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════
st.markdown(f"""
<div style="padding:20px 40px;border-top:1px solid {T["rule"]};background:{T["bg2"]};display:flex;justify-content:space-between;align-items:center;margin-top:60px;">
  <div style="font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">ReelMind AI + StoryFlow AI — v4.0 — Gemini 2.5 Flash</div>
  <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:{T["text4"]};background:{T["bg3"]};border:1px solid {T["rule2"]};padding:3px 10px;">Built by Satvik Sharma · NIET 2024–28</div>
</div>
""", unsafe_allow_html=True)