import streamlit as st
import streamlit.components.v1 as components
import random
import time
import datetime
import re
from gemini_helper import (
    generate_full_content, generate_hooks,
    generate_series, generate_carousel,
    generate_thread, repurpose_content
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
    ("generated", False)
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
    "glass":   "rgba(255,255,255,0.04)" if IS_DARK else "rgba(0,0,0,0.04)",
    "glassborder": "rgba(255,255,255,0.08)" if IS_DARK else "rgba(0,0,0,0.08)",
}

# ══════════════════════════════════════════
# PREMIUM EFFECTS COMPONENT
# ══════════════════════════════════════════
def inject_premium_effects():
    components.html(f"""
<!DOCTYPE html>
<html>
<head>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ overflow:hidden; background:transparent; }}
#canvas {{ position:fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none; z-index:0; }}
#aurora {{ position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:0; overflow:hidden; }}
.aurora-layer {{
    position:absolute; width:200%; height:200%;
    background: conic-gradient(from var(--angle, 0deg) at 50% 50%,
        transparent 0deg,
        {T["accent"]}08 60deg,
        {T["purple"]}06 120deg,
        transparent 180deg,
        {T["blue"]}05 240deg,
        {T["accent"]}08 300deg,
        transparent 360deg
    );
    animation: auroraRotate 12s linear infinite;
    top:-50%; left:-50%;
}}
.aurora-layer-2 {{
    position:absolute; width:150%; height:150%;
    background: radial-gradient(ellipse at 20% 50%, {T["accent"]}07 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, {T["purple"]}06 0%, transparent 50%),
                radial-gradient(ellipse at 60% 80%, {T["blue"]}05 0%, transparent 50%);
    animation: auroraFloat 8s ease-in-out infinite alternate;
    top:-25%; left:-25%;
}}
@keyframes auroraRotate {{
    from {{ transform: rotate(0deg); }}
    to {{ transform: rotate(360deg); }}
}}
@keyframes auroraFloat {{
    from {{ transform: translate(0px, 0px) scale(1); }}
    to {{ transform: translate(30px, -20px) scale(1.05); }}
}}
#cursor-dot {{
    position:fixed; width:8px; height:8px;
    background:{T["accent"]}; border-radius:50%;
    pointer-events:none; z-index:9999;
    transform:translate(-50%,-50%);
    transition:transform 0.05s;
    box-shadow: 0 0 10px {T["accent"]}, 0 0 20px {T["accent"]}80;
}}
#cursor-ring {{
    position:fixed; width:36px; height:36px;
    border:1.5px solid {T["accent"]}80; border-radius:50%;
    pointer-events:none; z-index:9998;
    transform:translate(-50%,-50%);
    transition:width 0.25s, height 0.25s, border-color 0.25s, background 0.25s;
}}
#cursor-ring.hovering {{
    width:52px; height:52px;
    border-color:{T["accent"]};
    background:{T["accent"]}10;
}}
.particle {{
    position:fixed; border-radius:50%;
    pointer-events:none; z-index:9997;
    animation: particleFade var(--dur) ease-out forwards;
}}
@keyframes particleFade {{
    0% {{ transform: translate(0,0) scale(1); opacity:1; }}
    100% {{ transform: translate(var(--tx), var(--ty)) scale(0); opacity:0; }}
}}
.trail-particle {{
    position:fixed; width:4px; height:4px;
    border-radius:50%; pointer-events:none; z-index:9996;
    animation: trailFade 0.6s ease-out forwards;
}}
@keyframes trailFade {{
    0% {{ opacity:0.8; transform:translate(-50%,-50%) scale(1); }}
    100% {{ opacity:0; transform:translate(-50%,-50%) scale(0.1); }}
}}
</style>
</head>
<body>
<div id="aurora">
    <div class="aurora-layer"></div>
    <div class="aurora-layer-2"></div>
</div>
<canvas id="canvas"></canvas>
<div id="cursor-dot"></div>
<div id="cursor-ring"></div>
<script>
// ── NEURAL NETWORK CANVAS ──
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const NODES = 55;
const nodes = Array.from({{length: NODES}}, () => ({{
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    vx: (Math.random() - 0.5) * 0.4,
    vy: (Math.random() - 0.5) * 0.4,
    r: Math.random() * 2 + 1,
    pulse: Math.random() * Math.PI * 2
}}));

let mouseX = canvas.width / 2, mouseY = canvas.height / 2;

function drawNetwork() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Mouse influence
    nodes.forEach(n => {{
        const dx = mouseX - n.x, dy = mouseY - n.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 120) {{
            n.vx += dx / dist * 0.015;
            n.vy += dy / dist * 0.015;
        }}
        n.vx *= 0.99; n.vy *= 0.99;
        n.x += n.vx; n.y += n.vy;
        n.pulse += 0.02;
        if (n.x < 0 || n.x > canvas.width) n.vx *= -1;
        if (n.y < 0 || n.y > canvas.height) n.vy *= -1;
        n.x = Math.max(0, Math.min(canvas.width, n.x));
        n.y = Math.max(0, Math.min(canvas.height, n.y));
    }});

    // Draw connections
    for (let i = 0; i < nodes.length; i++) {{
        for (let j = i+1; j < nodes.length; j++) {{
            const dx = nodes[i].x - nodes[j].x;
            const dy = nodes[i].y - nodes[j].y;
            const dist = Math.sqrt(dx*dx + dy*dy);
            if (dist < 110) {{
                const alpha = (1 - dist/110) * 0.18;
                ctx.beginPath();
                ctx.strokeStyle = `rgba(255,75,43,${{alpha}})`;
                ctx.lineWidth = 0.6;
                ctx.moveTo(nodes[i].x, nodes[i].y);
                ctx.lineTo(nodes[j].x, nodes[j].y);
                ctx.stroke();
            }}
        }}
    }}

    // Draw nodes
    nodes.forEach(n => {{
        const pulse = Math.sin(n.pulse) * 0.5 + 0.5;
        const alpha = 0.25 + pulse * 0.35;
        const radius = n.r + pulse * 0.8;
        ctx.beginPath();
        ctx.arc(n.x, n.y, radius, 0, Math.PI*2);
        ctx.fillStyle = `rgba(255,75,43,${{alpha}})`;
        ctx.fill();
        // Glow
        ctx.beginPath();
        ctx.arc(n.x, n.y, radius * 2.5, 0, Math.PI*2);
        ctx.fillStyle = `rgba(255,75,43,${{alpha * 0.1}})`;
        ctx.fill();
    }});

    requestAnimationFrame(drawNetwork);
}}
drawNetwork();

window.addEventListener('resize', () => {{
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}});

// ── CURSOR ──
const dot = document.getElementById('cursor-dot');
const ring = document.getElementById('cursor-ring');
let rx = 0, ry = 0, mx = 0, my = 0;

window.addEventListener('mousemove', e => {{
    mx = e.clientX; my = e.clientY;
    dot.style.left = mx + 'px';
    dot.style.top = my + 'px';
    mouseX = mx; mouseY = my;
    spawnTrail(mx, my);
}});

function animRing() {{
    rx += (mx - rx) * 0.13;
    ry += (my - ry) * 0.13;
    ring.style.left = rx + 'px';
    ring.style.top = ry + 'px';
    requestAnimationFrame(animRing);
}}
animRing();

// ── CURSOR GLOW TRAIL ──
let trailCount = 0;
function spawnTrail(x, y) {{
    if (trailCount++ % 2 !== 0) return;
    const p = document.createElement('div');
    p.className = 'trail-particle';
    const colors = ['{T["accent"]}', '{T["purple"]}', '{T["accent2"]}'];
    const col = colors[Math.floor(Math.random()*colors.length)];
    const size = Math.random()*5 + 2;
    p.style.cssText = `
        left:${{x}}px; top:${{y}}px; width:${{size}}px; height:${{size}}px;
        background:${{col}}; box-shadow: 0 0 6px ${{col}};
    `;
    document.body.appendChild(p);
    setTimeout(() => p.remove(), 600);
}}

// ── PARTICLE EXPLOSION (triggered from parent) ──
window.explodeParticles = function(x, y) {{
    const colors = ['{T["accent"]}', '{T["accent2"]}', '{T["purple"]}', '#fff', '{T["yellow"]}'];
    for (let i = 0; i < 40; i++) {{
        const p = document.createElement('div');
        p.className = 'particle';
        const angle = (Math.PI * 2 * i) / 40;
        const dist = 60 + Math.random() * 120;
        const size = Math.random()*8 + 3;
        const col = colors[Math.floor(Math.random()*colors.length)];
        const dur = (0.6 + Math.random()*0.8) + 's';
        p.style.cssText = `
            left:${{x}}px; top:${{y}}px;
            width:${{size}}px; height:${{size}}px;
            background:${{col}};
            box-shadow: 0 0 ${{size*2}}px ${{col}};
            --tx:${{Math.cos(angle)*dist}}px;
            --ty:${{Math.sin(angle)*dist}}px;
            --dur:${{dur}};
        `;
        document.body.appendChild(p);
        setTimeout(() => p.remove(), parseFloat(dur)*1000);
    }}
}};

// ── HOVER DETECTION ──
document.addEventListener('mouseover', e => {{
    if (e.target.matches('button,a,input,select,[role="button"]')) {{
        ring.classList.add('hovering');
    }}
}});
document.addEventListener('mouseout', e => {{
    if (e.target.matches('button,a,input,select,[role="button"]')) {{
        ring.classList.remove('hovering');
    }}
}});
</script>
</body>
</html>
""", height=0, scrolling=False)

# ══════════════════════════════════════════
# GLASSMORPHISM CARD COMPONENT
# ══════════════════════════════════════════
def glass_card(title, content, accent_color=None, height=None):
    color = accent_color or T["accent"]
    h = f"max-height:{height}px;overflow-y:auto;" if height else ""
    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:transparent; font-family:'Space Grotesk',sans-serif; padding:2px; }}
.card {{
    background: {T["glass"]};
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid {T["glassborder"]};
    border-left: 2px solid {color};
    padding: 16px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    cursor: default;
    {h}
}}
.card::before {{
    content:''; position:absolute; inset:0;
    background: radial-gradient(circle at var(--mx,50%) var(--my,50%), {color}12 0%, transparent 60%);
    opacity:0; transition:opacity 0.3s;
    pointer-events:none;
}}
.card:hover::before {{ opacity:1; }}
.card:hover {{
    border-color: {color}80;
    box-shadow: 0 0 30px {color}15, 0 8px 32px rgba(0,0,0,0.3);
    transform: translateY(-2px) perspective(600px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg));
}}
.electric {{
    position:absolute; inset:-1px;
    background:transparent;
    pointer-events:none;
    border-radius:inherit;
}}
.electric::after {{
    content:'';
    position:absolute; inset:0;
    border: 1px solid transparent;
    border-image: linear-gradient(var(--angle,0deg), {color}, transparent, {color}, transparent) 1;
    animation: electricRotate 2s linear infinite;
    opacity:0;
    transition:opacity 0.3s;
}}
.card:hover .electric::after {{ opacity:1; }}
@keyframes electricRotate {{
    from {{ --angle:0deg; }}
    to {{ --angle:360deg; }}
}}
@property --angle {{
    syntax:'<angle>'; initial-value:0deg; inherits:false;
}}
.card-title {{
    font-family:'Space Mono',monospace;
    font-size:8px; letter-spacing:3px;
    text-transform:uppercase;
    color:{color}; margin-bottom:10px;
}}
.card-body {{
    font-size:13px; line-height:1.8;
    color:{T["text2"]}; white-space:pre-wrap;
}}
</style>
</head><body>
<div class="card" id="card">
    <div class="electric"></div>
    <div class="card-title">{title}</div>
    <div class="card-body">{content}</div>
</div>
<script>
const card = document.getElementById('card');
card.addEventListener('mousemove', e => {{
    const r = card.getBoundingClientRect();
    const x = ((e.clientX - r.left) / r.width) * 100;
    const y = ((e.clientY - r.top) / r.height) * 100;
    card.style.setProperty('--mx', x + '%');
    card.style.setProperty('--my', y + '%');
    const rx = ((e.clientY - r.top - r.height/2) / r.height) * -6;
    const ry = ((e.clientX - r.left - r.width/2) / r.width) * 6;
    card.style.setProperty('--rx', rx + 'deg');
    card.style.setProperty('--ry', ry + 'deg');
}});
card.addEventListener('mouseleave', () => {{
    card.style.setProperty('--rx', '0deg');
    card.style.setProperty('--ry', '0deg');
}});
</script>
</body></html>
""", height=(height or 200) + 60, scrolling=False)

# ══════════════════════════════════════════
# LIQUID GENERATE BUTTON COMPONENT
# ══════════════════════════════════════════
def liquid_generate_button(label="→ GENERATE"):
    clicked = components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@700&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:transparent; display:flex; align-items:center; justify-content:center; height:60px; }}
.btn {{
    width:100%; height:52px; background:none; border:none; cursor:pointer;
    position:relative; overflow:hidden; outline:none;
}}
.btn-bg {{
    position:absolute; inset:0;
    background: linear-gradient(135deg, {T["accent"]} 0%, {T["accent2"]} 40%, {T["purple"]} 80%, {T["accent"]} 120%);
    background-size:300% 300%;
    animation: liquidFlow 3s ease infinite;
    transition: filter 0.2s;
}}
.btn:hover .btn-bg {{ filter:brightness(1.15); }}
.btn:active .btn-bg {{ filter:brightness(0.9); }}
@keyframes liquidFlow {{
    0%  {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100%{{ background-position: 0% 50%; }}
}}
.btn-text {{
    position:relative; z-index:2;
    font-family:'Space Mono',monospace;
    font-size:11px; font-weight:700;
    letter-spacing:4px; text-transform:uppercase;
    color:#fff; pointer-events:none;
}}
.ripple {{
    position:absolute; border-radius:50%;
    background:rgba(255,255,255,0.35);
    transform:scale(0);
    animation: rippleAnim 0.7s linear forwards;
    pointer-events:none;
}}
@keyframes rippleAnim {{
    to {{ transform:scale(4); opacity:0; }}
}}
</style>
</head><body>
<button class="btn" id="genBtn">
    <div class="btn-bg"></div>
    <span class="btn-text">{label}</span>
</button>
<script>
const btn = document.getElementById('genBtn');
btn.addEventListener('click', e => {{
    // Ripple
    const r = document.createElement('span');
    r.className = 'ripple';
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    r.style.cssText = `width:${{size}}px;height:${{size}}px;left:${{e.clientX-rect.left-size/2}}px;top:${{e.clientY-rect.top-size/2}}px`;
    btn.appendChild(r);
    setTimeout(()=>r.remove(), 700);

    // Particle explosion — communicate to parent
    window.parent.postMessage({{type:'GENERATE_CLICKED', x: e.clientX, y: e.clientY}}, '*');
    setTimeout(()=> window.parent.postMessage({{type:'STREAMLIT_RERUN'}}, '*'), 100);
}});
</script>
</body></html>
""", height=60, scrolling=False)

# ══════════════════════════════════════════
# SCORE BENTO COMPONENT
# ══════════════════════════════════════════
def score_bento(scores):
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
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:transparent; font-family:'Space Mono',monospace; padding:4px 2px; }}
.grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }}
.score-card {{
    background: {T["glass"]};
    backdrop-filter:blur(20px);
    border:1px solid {T["glassborder"]};
    border-top: 2px solid var(--accent);
    padding:14px; position:relative; overflow:hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    cursor:default;
}}
.card-glow {{
    position:absolute; inset:0;
    background: radial-gradient(circle at 50% 0%, var(--accent)15 0%, transparent 70%);
    opacity:0; transition:opacity 0.3s; pointer-events:none;
}}
.score-card:hover .card-glow {{ opacity:1; }}
.score-card:hover {{
    box-shadow: 0 0 20px var(--accent)20, 0 4px 20px rgba(0,0,0,0.4);
}}
.score-label {{
    font-size:7px; letter-spacing:2px;
    text-transform:uppercase; color:{T["text3"]};
    margin-bottom:6px;
}}
.score-value {{
    font-size:28px; font-weight:700;
    color:var(--accent); line-height:1; margin-bottom:8px;
}}
.score-bar {{ height:2px; background:{T["rule2"]}; overflow:hidden; }}
.score-fill {{ height:100%; background:var(--accent); width:0%; transition:width 1.4s cubic-bezier(0.4,0,0.2,1); }}
</style>
</head><body>
<div class="grid">{cards_html}</div>
<script>
// Count-up animation
document.querySelectorAll('.score-value').forEach(el => {{
    const target = parseInt(el.dataset.target);
    let cur = 0;
    const step = Math.ceil(target / 50);
    const timer = setInterval(() => {{
        cur = Math.min(cur + step, target);
        el.textContent = cur;
        if (cur >= target) clearInterval(timer);
    }}, 25);
}});
// Fill bars
setTimeout(() => {{
    document.querySelectorAll('.score-fill').forEach(el => {{
        el.style.width = el.dataset.width + '%';
    }});
}}, 100);
// 3D tilt
function tilt(card, e) {{
    const r = card.getBoundingClientRect();
    const rx = ((e.clientY - r.top - r.height/2) / r.height) * -8;
    const ry = ((e.clientX - r.left - r.width/2) / r.width) * 8;
    card.style.transform = `perspective(400px) rotateX(${{rx}}deg) rotateY(${{ry}}deg) translateY(-2px)`;
}}
function resetTilt(card) {{
    card.style.transform = '';
}}
</script>
</body></html>
""", height=220, scrolling=False)

# ══════════════════════════════════════════
# RADAR CHART COMPONENT
# ══════════════════════════════════════════
def radar_component(scores):
    vals = [scores[k][0] for k in ['viral','hook','engagement','share','retention','reach']]
    labels = ['Viral','Hook','Engage','Share','Retain','Reach']
    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:transparent; display:flex; align-items:center; justify-content:center; }}
canvas {{ max-width:220px; max-height:220px; }}
</style>
</head><body>
<canvas id="rc"></canvas>
<script>
new Chart(document.getElementById('rc'), {{
    type:'radar',
    data:{{
        labels:{labels},
        datasets:[{{
            data:{vals},
            backgroundColor:'rgba(255,75,43,0.1)',
            borderColor:'{T["accent"]}',
            borderWidth:1.5,
            pointBackgroundColor:'{T["accent"]}',
            pointRadius:4,
            pointHoverRadius:6
        }}]
    }},
    options:{{
        responsive:true,
        scales:{{
            r:{{
                min:0, max:100,
                ticks:{{ display:false }},
                grid:{{ color:'rgba(255,75,43,0.08)' }},
                angleLines:{{ color:'rgba(255,75,43,0.08)' }},
                pointLabels:{{
                    color:'{T["text3"]}',
                    font:{{ family:'Space Mono', size:9 }}
                }}
            }}
        }},
        plugins:{{ legend:{{ display:false }} }},
        animation:{{ duration:1200, easing:'easeOutQuart' }}
    }}
}});
</script>
</body></html>
""", height=240, scrolling=False)

# ══════════════════════════════════════════
# HASHTAG TAG COMPONENT
# ══════════════════════════════════════════
def hashtag_component(hv, mv, nv):
    def tags_html(tags, color):
        return "".join([f'<span class="tag" style="--c:{color};" onclick="copyTag(this)">{t}</span>' for t in tags])

    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Space+Grotesk:wght@400&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:transparent; font-family:'Space Grotesk',sans-serif; padding:4px 2px; }}
.group {{ margin-bottom:16px; }}
.group-label {{
    font-family:'Space Mono',monospace; font-size:7px;
    letter-spacing:2px; text-transform:uppercase;
    color:{T["text3"]}; margin-bottom:8px;
    display:flex; align-items:center; justify-content:space-between;
}}
.copy-all {{
    background:transparent; border:1px solid {T["rule2"]};
    color:{T["text4"]}; font-family:'Space Mono',monospace;
    font-size:7px; letter-spacing:1px; padding:2px 7px;
    cursor:pointer; transition:all 0.15s; text-transform:uppercase;
}}
.copy-all:hover {{ border-color:{T["accent"]}; color:{T["accent"]}; }}
.tags {{ display:flex; flex-wrap:wrap; gap:5px; }}
.tag {{
    background:{T["bg3"]}; border:1px solid {T["rule2"]};
    color:{T["text2"]}; font-family:'Space Mono',monospace;
    font-size:10px; padding:4px 9px; cursor:pointer;
    transition:all 0.2s; display:inline-block;
    position:relative; overflow:hidden;
}}
.tag::before {{
    content:''; position:absolute; inset:0;
    background:var(--c); opacity:0; transition:opacity 0.2s;
}}
.tag:hover::before {{ opacity:0.1; }}
.tag:hover {{ border-color:var(--c); color:var(--c); transform:translateY(-1px); }}
.copied-toast {{
    position:fixed; bottom:10px; right:10px;
    background:{T["accent"]}; color:#fff;
    font-family:'Space Mono',monospace; font-size:9px;
    letter-spacing:2px; padding:6px 12px;
    opacity:0; transition:opacity 0.2s; pointer-events:none;
}}
.copied-toast.show {{ opacity:1; }}
</style>
</head><body>
<div class="group">
    <div class="group-label">
        <span>High Volume — 1M+ posts ({len(hv)} tags)</span>
        <button class="copy-all" onclick="copyGroup('hv')">COPY ALL</button>
    </div>
    <div class="tags" id="hv">{tags_html(hv, T["accent"])}</div>
</div>
<div class="group">
    <div class="group-label">
        <span>Medium Volume — 100K–1M ({len(mv)} tags)</span>
        <button class="copy-all" onclick="copyGroup('mv')">COPY ALL</button>
    </div>
    <div class="tags" id="mv">{tags_html(mv, T["blue"])}</div>
</div>
<div class="group">
    <div class="group-label">
        <span>Niche Community — Under 100K ({len(nv)} tags)</span>
        <button class="copy-all" onclick="copyGroup('nv')">COPY ALL</button>
    </div>
    <div class="tags" id="nv">{tags_html(nv, T["green"])}</div>
</div>
<div class="copied-toast" id="toast">COPIED</div>
<script>
function showToast() {{
    const t = document.getElementById('toast');
    t.classList.add('show');
    setTimeout(()=>t.classList.remove('show'), 1500);
}}
function copyTag(el) {{
    navigator.clipboard.writeText(el.textContent);
    showToast();
}}
function copyGroup(id) {{
    const tags = Array.from(document.getElementById(id).querySelectorAll('.tag')).map(t=>t.textContent).join(' ');
    navigator.clipboard.writeText(tags);
    showToast();
}}
</script>
</body></html>
""", height=280, scrolling=False)

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

def gen_scores():
    return {
        "viral":      (random.randint(82,97), T["accent"]),
        "hook":       (random.randint(80,96), T["purple"]),
        "engagement": (random.randint(83,95), T["blue"]),
        "share":      (random.randint(81,94), T["green"]),
        "retention":  (random.randint(82,95), T["yellow"]),
        "reach":      (random.randint(80,93), T["orange"]),
    }

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
.block-container {{ padding:0 !important; max-width:100% !important; }}
[data-testid="stSidebar"] {{
    background:{T["bg2"]} !important;
    border-right:1px solid {T["rule"]} !important;
}}
[data-testid="stSidebar"] * {{ color:{T["text"]} !important; }}
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
.stRadio>div {{ gap:3px !important; flex-direction:column !important; }}
.stRadio>div>label {{
    background:{T["bg3"]} !important; border:1px solid {T["rule2"]} !important;
    padding:9px 14px !important; transition:all 0.15s !important;
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
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# INJECT PREMIUM EFFECTS (background layer)
# ══════════════════════════════════════════
inject_premium_effects()

# ══════════════════════════════════════════
# TOPBAR
# ══════════════════════════════════════════
theme_icon = "🌙" if IS_DARK else "🌕"
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
padding:0 40px;height:52px;background:{T["bg2"]}ee;
border-bottom:1px solid {T["rule"]};backdrop-filter:blur(20px);">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:26px;height:26px;background:{T["accent"]};
    display:flex;align-items:center;justify-content:center;font-size:13px;
    box-shadow:0 0 16px {T["accent"]}60;">🎬</div>
    <div style="font-family:'Space Mono',monospace;font-size:13px;
    font-weight:700;color:{T["text"]};letter-spacing:1px;">
        Reel<span style="color:{T["accent"]};">Mind</span> AI</div>
  </div>
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="display:flex;align-items:center;gap:6px;
    font-family:'Space Mono',monospace;font-size:8px;color:{T["green"]};">
        <div style="width:5px;height:5px;background:{T["green"]};border-radius:50%;
        animation:pulse 2s infinite;"></div>GEMINI LIVE</div>
    <div style="font-family:'Space Mono',monospace;font-size:8px;
    color:{T["text4"]};background:{T["bg3"]};border:1px solid {T["rule2"]};padding:3px 8px;">v3.0</div>
  </div>
</div>
<style>@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# HERO
# ══════════════════════════════════════════
st.markdown(f"""
<div style="padding:40px 40px 28px;border-bottom:1px solid {T["rule"]};position:relative;overflow:hidden;">
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:4px;
  text-transform:uppercase;color:{T["accent"]};margin-bottom:10px;
  display:flex;align-items:center;gap:10px;">
    <span style="width:18px;height:1px;background:{T["accent"]};display:inline-block;"></span>
    AI Content Engine — Studio Grade
  </div>
  <div style="font-family:'Fraunces',serif;font-size:58px;font-weight:900;font-style:italic;
  line-height:0.92;letter-spacing:-2px;color:{T["text"]};margin-bottom:14px;">
    Reel<span style="color:{T["accent"]};">Mind</span>
    <span style="color:{T["text4"]};">AI</span>
  </div>
  <div style="font-size:13px;color:{T["text3"]};max-width:420px;line-height:1.6;margin-bottom:24px;">
    Generate scroll-stopping captions, hashtag stacks, viral scripts,
    and thumbnail prompts — powered by Gemini 2.5 Flash.
  </div>
  <div style="display:flex;gap:32px;flex-wrap:wrap;">
    {"".join([f'<div style="display:flex;flex-direction:column;gap:2px;"><div style="font-family:Space Mono,monospace;font-size:20px;font-weight:700;color:{T["text"]};">{n}</div><div style="font-family:Space Mono,monospace;font-size:7px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">{l}</div></div>' for n,l in [("4","Outputs/run"),("30","Hashtags"),("3","Captions"),("16","Niches")]])}
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:8px;letter-spacing:3px;text-transform:uppercase;color:{T["text4"]};padding:16px 16px 10px;border-bottom:1px solid {T["rule"]};">⚡ Content Engine</div>', unsafe_allow_html=True)

    col_t1, col_t2 = st.columns([3,1])
    with col_t2:
        if st.button(theme_icon):
            st.session_state.theme = "light" if IS_DARK else "dark"
            st.rerun()

    st.markdown("---")
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
    if "Series" in mode:
        num_posts = st.selectbox("Posts in Series", [3,5,7])

    original_content = ""
    target_platform = "TikTok"
    if "Repurposer" in mode:
        original_content = st.text_area("Paste original content", height=80)
        target_platform = st.selectbox("Repurpose for", ["TikTok","YouTube Shorts","X/Twitter","LinkedIn"])

    st.markdown("---")

    # Liquid generate button via component
    liquid_generate_button("→ GENERATE")
    # Fallback standard button
    generate_btn = st.button("GENERATE", key="gen_fallback")

    with st.expander("QUICK TIPS"):
        st.markdown(f'<div style="font-family:Space Grotesk,sans-serif;font-size:12px;color:{T["text3"]};line-height:1.8;">→ Specific topics outperform generic<br>→ <strong style="color:{T["text2"]};">"Villain arc workout" > "gym"</strong><br>→ Match tone to your content style<br>→ Use Hook mode to A/B test openings</div>', unsafe_allow_html=True)

    if st.session_state.history:
        st.markdown("---")
        st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};margin-bottom:8px;">Recent</div>', unsafe_allow_html=True)
        for h in st.session_state.history[-4:]:
            st.markdown(f'<div style="background:{T["bg3"]};border:1px solid {T["rule"]};padding:8px 10px;margin-bottom:3px;"><div style="font-size:12px;font-weight:500;color:{T["text"]};">{h["topic"][:24]}</div><div style="font-family:Space Mono,monospace;font-size:7px;color:{T["text4"]};">{h["niche"][:22]} · {h["time"]}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# MAIN OUTPUT
# ══════════════════════════════════════════
if not generate_btn:
    if not st.session_state.last_result:
        st.markdown(f"""
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
min-height:420px;border:1px dashed {T["rule2"]};margin:32px 40px;gap:14px;">
  <div style="font-size:38px;filter:grayscale(1);opacity:0.15;">🎬</div>
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:3px;
  text-transform:uppercase;color:{T["text4"]};">Configure & Generate</div>
  <div style="font-size:12px;color:{T["text4"]};font-family:'Space Mono',monospace;">
  Your content will appear here</div>
</div>""", unsafe_allow_html=True)

if generate_btn:
    if not topic.strip():
        st.warning("Please enter a topic first.")
        st.stop()

    # ── LOADING STEPS ──
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
            if i < done:
                col, icon = T["green"], "✓"
            elif i == done:
                col, icon = T["accent"], "◌"
            else:
                col, icon = T["text4"], str(i+1)
            rows += f'<div style="display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid {T["rule"]};font-family:Space Mono,monospace;font-size:10px;letter-spacing:1px;color:{col};"><span style="width:18px;text-align:center;">{icon}</span><span>{name}</span></div>'
        return f'<div style="background:{T["bg2"]};border:1px solid {T["rule"]};padding:24px;margin:20px 40px;">{rows}</div>'

    for i in range(len(step_names)):
        steps_ph.markdown(render_steps(i), unsafe_allow_html=True)
        time.sleep(0.45)

    # ── API CALL ──
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
    st.session_state.last_scores = scores
    st.session_state.history.append({
        "topic": topic, "niche": niche,
        "time": datetime.datetime.now().strftime("%H:%M")
    })

    # ── SCORE BENTO ──
    st.markdown("<div style='padding:0 40px;'>", unsafe_allow_html=True)
    section_label("Content Score Card")
    score_bento(scores)
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

    # ══════════════════════════════════════
    # FULL CONTENT TABS
    # ══════════════════════════════════════
    if "Full Content" in mode and result:
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Captions","#️⃣ Hashtags","🎬 Script","🖼️ Thumbnail"])

        with tab1:
            short, med, long_cap = parse_captions(result.get("captions",""))
            for cap_text, label, key in [(short,"Short Caption","s"),(med,"Medium Caption","m"),(long_cap,"Long Caption","l")]:
                wc = len(cap_text.split())
                glass_card(f"{label} — {wc} words", cap_text, T["accent"], 160)
                st.download_button(f"↓ COPY {label.split()[0].upper()}", cap_text,
                    file_name=f"{label.lower().replace(' ','_')}.txt", key=f"dl_{key}")

        with tab2:
            hv, mv, nv = parse_hashtags(result.get("hashtags",""))
            hashtag_component(hv, mv, nv)
            all_tags = " ".join(hv+mv+nv)
            st.download_button("↓ DOWNLOAD ALL HASHTAGS", all_tags,
                file_name="hashtags.txt", key="dl_ht")

        with tab3:
            formatted = format_script(result.get("script",""))
            glass_card("Reel Script — 30 Seconds", formatted, T["purple"], 300)
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
            glass_card("Midjourney Prompt", mj, T["accent"], 180)
            st.download_button("↓ MJ PROMPT", mj, file_name="mj_prompt.txt", key="dl_mj")
            glass_card("Ideogram / Gemini Image Prompt", ideogram, T["blue"], 180)
            st.download_button("↓ IDEOGRAM PROMPT", ideogram, file_name="ideogram_prompt.txt", key="dl_id")

        gradient_divider()
        full = f"REELMIND AI\nTopic:{topic} | Niche:{niche} | Platform:{platform}\n{'='*60}\n\n{result.get('raw','')}"
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("↓ DOWNLOAD FULL PACK", full,
                file_name=f"reelmind_{topic[:20].replace(' ','_')}_full.txt", key="dl_full")
        with c2:
            st.download_button("↓ DOWNLOAD RAW", result.get("raw",""),
                file_name="reelmind_raw.txt", key="dl_raw")

    else:
        mode_label = mode.split(" ",1)[1] if " " in mode else mode
        glass_card(mode_label, raw_output or "No output generated.", T["accent"], 400)
        if raw_output:
            st.download_button("↓ DOWNLOAD OUTPUT", raw_output,
                file_name=f"reelmind_{topic[:20].replace(' ','_')}.txt", key="dl_other")

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════
st.markdown(f"""
<div style="padding:16px 40px;border-top:1px solid {T["rule"]};background:{T["bg2"]};
display:flex;justify-content:space-between;align-items:center;margin-top:40px;">
  <div style="font-family:'Space Mono',monospace;font-size:8px;
  letter-spacing:2px;text-transform:uppercase;color:{T["text4"]};">
    REELMIND AI — v3.0 — GEMINI 2.5 FLASH</div>
  <div style="font-family:'Space Mono',monospace;font-size:8px;
  color:{T["text4"]};background:{T["bg3"]};border:1px solid {T["rule2"]};padding:3px 8px;">
    BUILT BY SATVIK SHARMA · NIET 2024–28</div>
</div>
""", unsafe_allow_html=True)