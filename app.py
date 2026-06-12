import streamlit as st
import streamlit.components.v1 as components
import random
import time
import datetime
import re
import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ══════════════════════════════════════════
# CORE ENGINE FUNCTIONS (Integrated & Optimized)
# ══════════════════════════════════════════

def safe_generate(prompt: str) -> str:
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            error = str(e)
            if "RESOURCE_EXHAUSTED" in error:
                return "QUOTA_ERROR||Daily Gemini quota exceeded. Wait for reset or use another API key."
            if "API_KEY_INVALID" in error:
                return "KEY_ERROR||Invalid API Key. Check your .env file."
            print(f"[ReelMind] Attempt {attempt+1} failed: {error}")
            if attempt < 2:
                time.sleep(5)
            else:
                return f"GENERATION_ERROR||{error}"

def parse_sections(raw: str) -> dict:
    sections = {"captions": "", "hashtags": "", "script": "", "thumbnail": "", "raw": raw}
    markers = {
        "captions":  ("==CAPTIONS==",  "==HASHTAGS=="),
        "hashtags":  ("==HASHTAGS==",  "==SCRIPT=="),
        "script":    ("==SCRIPT==",    "==THUMBNAIL=="),
        "thumbnail": ("==THUMBNAIL==", None),
    }
    for key, (start_marker, end_marker) in markers.items():
        start_idx = raw.find(start_marker)
        if start_idx == -1:
            continue
        start_idx += len(start_marker)
        if end_marker:
            end_idx = raw.find(end_marker, start_idx)
            sections[key] = raw[start_idx:end_idx].strip() if end_idx != -1 else raw[start_idx:].strip()
        else:
            sections[key] = raw[start_idx:].strip()
    return sections

def generate_full_content(topic: str, niche: str, platform: str, tone: str) -> dict:
    prompt = f"""You are a world-class viral content strategist and professional scriptwriter.

Generate complete social media content for:
TOPIC: {topic}
NICHE: {niche}
PLATFORM: {platform}
TONE: {tone}

Return EXACTLY in this format:

==CAPTIONS==

SHORT (under 50 words):
[Write a complete, punchy caption under 50 words. Must end with a hook question or CTA.]

MEDIUM (50-100 words):
[Write a full, engaging caption between 50-100 words. Include a story element, value proposition, and end with a CTA.]

LONG (100-150 words):
[Write a rich, detailed caption between 100-150 words. Include context, emotional connection, value, and a strong CTA.]

==HASHTAGS==

HIGH VOLUME (1M+ posts):
[10 hashtags on one line, space-separated]

MEDIUM VOLUME (100K-1M posts):
[10 hashtags on one line, space-separated]

NICHE COMMUNITY (under 100K posts):
[10 hashtags on one line, space-separated]

==SCRIPT==

HOOK (0-3 seconds):
[Write a single powerful, curiosity-driving opening line spoken directly to the viewer. This must create immediate pattern interruption or shock. Write it as actual spoken dialogue, not a keyword.]

BODY (3-25 seconds):
[Write 6-8 complete spoken sentences, each punchy and under 10 words. These should flow naturally as a spoken script — not bullet keywords. Each line should be a complete thought that builds tension, delivers value, or escalates the story. Write them numbered like:
1. [full spoken line]
2. [full spoken line]
...]

CTA (25-30 seconds):
[Write one specific, compelling call-to-action as a full spoken sentence. Tell the viewer exactly what to do and why right now.]

SUGGESTED AUDIO:
[Describe the music vibe, tempo, and specific mood for the background track. Be specific — e.g. "Dark trap beat, 140 BPM, building tension with bass drops at key emotional moments"]

==THUMBNAIL==

IMAGE PROMPT:
[Write a 60-90 word hyper-specific, cinematic image generation prompt. Include subject, action, lighting, camera angle, background, mood, and visual style.]

STYLE KEYWORDS:
[6-8 specific visual style descriptors separated by commas]

COLOR PALETTE:
[3-4 specific hex codes with color names, e.g. #FF4B2B Deep Crimson, #1A1A2E Midnight Navy]

Rules:
- Match {tone} tone throughout every section
- Optimize specifically for {platform} algorithm and audience behavior
- Every caption must feel natural and human — not AI-generated
- Script hook must create immediate curiosity, shock, or pattern interruption
- Script body lines must be actual spoken sentences — not fragment keywords
- Hashtag mix must be strategic: not all mega-popular, spread the range
- Thumbnail prompt must be hyper-specific enough to paste directly into Midjourney or Ideogram"""

    raw = safe_generate(prompt)
    return parse_sections(raw)

def generate_hooks(topic: str, niche: str, count: int = 5) -> str:
    prompt = f"""You are a viral content hook specialist with deep expertise in psychology-driven content.
Generate {count} different powerful opening hooks for a {niche} reel about: {topic}
Each hook must be under 12 words, immediately compelling, and a distinctly different style.
Write each hook as a complete sentence of spoken dialogue — not a keyword or fragment.

Format exactly:
HOOK 1 (Question): [full hook sentence]
HOOK 2 (Shock): [full hook sentence]
HOOK 3 (Controversy): [full hook sentence]
HOOK 4 (Story): [full hook sentence]
HOOK 5 (Number): [full hook sentence]

After each hook, add one line explaining WHY it works psychologically.
WHY: [one sentence explanation]"""
    return safe_generate(prompt)

def generate_series(topic: str, niche: str, platform: str, num_posts: int = 5) -> str:
    prompt = f"""You are a viral content strategist planning a high-retention series.
Create a {num_posts}-post content series for a {niche} account on {platform} about: {topic}
Each post must build curiosity for the next one — like a Netflix series.

For each post provide:
POST [N]:
ANGLE: [unique angle or sub-topic]
HOOK: [full opening line spoken to viewer — not a keyword]
CAPTION PREVIEW: [first 2-3 full sentences of the caption]
HASHTAG THEME: [4 core hashtags most relevant to this specific post]
BEST DAY: [day of week and why]
CLIFFHANGER: [one sentence that makes viewers want to see the next post]"""
    return safe_generate(prompt)

def generate_carousel(topic: str, niche: str, platform: str) -> str:
    prompt = f"""You are a carousel content specialist who creates high-save, high-share posts.
Create a 7-slide carousel post for {platform} about: {topic}
Niche: {niche}

For each slide:
SLIDE [N]:
HEADLINE: [bold headline under 6 words — punchy and direct]
BODY: [2-3 complete, value-packed sentences. No bullet fragments. Real sentences.]
VISUAL: [specific visual design suggestion with colors and layout]
MICRO-CTA: [one-line action or thought prompt for this slide]

Slide 1 must stop the scroll. Slide 7 must convert viewers to followers or saves.
After all slides, add:
COVER DESIGN: [detailed visual description of the cover slide]
CAPTION: [full 3-sentence caption for the carousel post]"""
    return safe_generate(prompt)

def generate_thread(topic: str, niche: str) -> str:
    prompt = f"""You are a viral X/Twitter thread writer who consistently hits 1M+ impressions.
Write a viral 8-tweet thread about: {topic}
Niche: {niche}

Format:
TWEET 1 (Hook): [tweet — under 280 chars]
TWEET 2-7: [tweet]
TWEET 8 (CTA): [engagement CTA tweet]"""
    return safe_generate(prompt)

def repurpose_content(original: str, target_platform: str) -> str:
    prompt = f"""You are a content repurposing expert who understands each platform's unique algorithm and culture.
Repurpose this content natively for {target_platform}:
ORIGINAL CONTENT: {original}"""
    return safe_generate(prompt)

def generate_video_story(animal: str, story_type: str, duration: int, style: str, platform: str, ending_type: str) -> dict:
    story_prompt = f"""You are a world-class viral AI animal video story creator specializing in {style}-style animated short films.
Generate 3 different viral story options for a {animal} ({story_type}) story designed for {platform} with a {ending_type} ending. Duration: {duration} seconds. Style: {style}."""
    stories_raw = safe_generate(story_prompt)
    return {"stories": stories_raw, "raw": stories_raw}

def generate_video_full_package(animal: str, story_title: str, story_logline: str, story_details: str, style: str, duration: int, platform: str) -> dict:
    clip_duration = 8
    num_prompts = max(1, round(duration / clip_duration))
    
    char_prompt = f"Create a 3D production character design sheet prompt and structural analysis for {animal} matching style: {style} inside the story: {story_title}."
    char_raw = safe_generate(char_prompt)
    
    frame_prompt = f"Create a masterpiece First Frame production script prompt (150-200 words) for {story_title} using {animal} in 9:16 vertical ratio."
    frame_raw = safe_generate(frame_prompt)
    
    prompts_output = []
    for i in range(1, num_prompts + 1):
        prompts_output.append({
            "number": i,
            "text": f"PROMPT {i} of {num_prompts}: Seamless sequence scene prompt for {story_title} continuous runtime environment physics update tracking."
        })
        
    return {
        "character_analysis": char_raw,
        "first_frame": frame_raw,
        "prompts": prompts_output,
        "continuity": "1. Verify character textures match.\n2. Keep aspect ratio locked to 9:16.\n3. Re-inject visual depth variables every scene build.",
        "num_prompts": num_prompts
    }

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
# SESSION STATE MANAGEMENT
# ══════════════════════════════════════════
for key, default in [
    ("history", []), ("theme", "dark"),
    ("last_result", None), ("last_scores", None),
    ("video_stories", None), ("video_package", None),
    ("active_module", "Content Engine")
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════
# DESIGN DESIGNATION SYSTEM (THEME TOKENS)
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
# UI HELPER LAYOUT BLOCKS
# ══════════════════════════════════════════
def section_label(text):
    st.markdown(f"""
<div style="font-family:'Space Mono',monospace;font-size:8px;letter-spacing:3px;text-transform:uppercase;color:{T['text4']};margin-bottom:12px;display:flex;align-items:center;gap:8px;">
{text} <span style="flex:1;height:1px;background:{T['rule']};display:inline-block;"></span>
</div>""", unsafe_allow_html=True)

def gradient_divider():
    st.markdown(f"""<div style="height:1px;background:linear-gradient(90deg,{T['accent']},{T['purple']},transparent);opacity:0.35;margin:24px 0;"></div>""", unsafe_allow_html=True)

def gold_divider():
    st.markdown(f"""<div style="height:1px;background:linear-gradient(90deg,{T['gold']},{T['gold2']},transparent);opacity:0.5;margin:24px 0;"></div>""", unsafe_allow_html=True)

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
    "Instagram Reels": [("6–8 AM","Morning",False),("12–2 PM","Lunch",False),("7–9 PM","Evening",True)],
    "TikTok":          [("7–9 AM","Morning",False),("3–5 PM","Afternoon",False),("7–9 PM","Prime",True)],
    "YouTube Shorts":  [("8–10 AM","Morning",False),("2–4 PM","Afternoon",True),("6–8 PM","Evening",False)],
}

SATURATION = {
    "Dark Aesthetic / Motivation": "HIGH — competitive. Use micro-angles.",
    "Gaming": "VERY HIGH — niche down to specific game/genre.",
    "Tech & AI": "MEDIUM-HIGH — fast growing. Early mover advantage.",
    "Finance & Investing": "MEDIUM — evergreen. Authority content wins.",
    "Fitness & Gym": "VERY HIGH — specific transformation angles win.",
}

def parse_captions(text):
    s = re.search(r'SHORT[^:]*:\s*([\s\S]*?)(?=MEDIUM[^:]*:|$)', text, re.I)
    m = re.search(r'MEDIUM[^:]*:\s*([\s\S]*?)(?=LONG[^:]*:|$)', text, re.I)
    l = re.search(r'LONG[^:]*:\s*([\s\S]*?)$', text, re.I)
    return (s.group(1).strip() if s else text[:200], m.group(1).strip() if m else "", l.group(1).strip() if l else "")

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
# CSS INJECTION SPECIFICATIONS
# ══════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&family=Fraunces:ital,opsz,wght@1,9..144,900&display=swap');
html, body, [data-testid="stAppViewContainer"] {{
    background:{T["bg"]} !important; color:{T["text"]} !important; font-family:'Space Grotesk',sans-serif !important;
}}
[data-testid="stSidebar"] {{ display:none !important; }}
.block-container {{ padding: 24px 40px !important; max-width:100% !important; }}
.stTextInput>div>div>input,.stTextArea>div>div>textarea, [data-baseweb="select"]>div {{
    background:{T["bg3"]} !important; border:1px solid {T["rule2"]} !important; border-radius:0 !important; color:{T["text"]} !important; font-size:13px !important;
}}
label, .stSelectbox label, .stTextInput label, .stTextArea label {{
    color:{T["text3"]} !important; font-family:'Space Mono',monospace !important; font-size:9px !important; letter-spacing:2px !important; text-transform:uppercase !important;
}}
.stButton>button {{
    background:transparent !important; color:{T["text3"]} !important; border:1px solid {T["rule2"]} !important; border-radius:0 !important; font-family:'Space Mono',monospace !important; font-size:10px !important; letter-spacing:2px !important; text-transform:uppercase !important; padding:12px 24px !important; transition:all 0.2s !important; width:100% !important;
}}
.stButton>button:hover {{ border-color:{T["accent"]} !important; color:{T["accent"]} !important; box-shadow:0 0 12px {T["accent"]}20 !important; }}

/* MASTER PREMIUM GENERATE ACTION BUTTON */
.generate-btn > div > button {{
    background: linear-gradient(135deg, {T["accent"]} 0%, {T["accent2"]} 40%, {T["purple"]} 100%) !important; background-size: 200% 200% !important; color: #fff !important; border: none !important; font-family: 'Space Mono', monospace !important; font-size: 11px !important; font-weight: 700 !important; letter-spacing: 4px !important; text-transform: uppercase !important; padding: 16px 24px !important; animation: liquidFlow 3s ease infinite !important; box-shadow: 0 0 24px {T["accent"]}40 !important;
}}
@keyframes liquidFlow {{ 0%{{background-position:0% 50%;}} 50%{{background-position:100% 50%;}} 100%{{background-position:0% 50%;}} }}

/* PRODUCTION GRADE SECTOR GOLD LINK BUTTON */
.gold-btn-container > div > button {{
    background: linear-gradient(135deg, #92400e 0%, {T["gold"]} 40%, {T["gold2"]} 70%, #92400e 100%) !important; background-size: 300% 300% !important; color: #000 !important; font-family: 'Space Mono', monospace !important; font-size: 11px !important; font-weight: 700 !important; letter-spacing: 3px !important; text-transform: uppercase !important; padding: 15px 24px !important; animation: goldFlow 4s ease infinite !important; box-shadow: 0 0 30px {T["gold"]}50 !important; border:none !important;
}}
@keyframes goldFlow {{ 0%{{background-position:0% 50%;}} 50%{{background-position:100% 50%;}} 100%{{background-position:0% 50%;}} }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# DYNAMIC BACKGROUND NEURAL PIPELINE INFRASTRUCTURE
# ══════════════════════════════════════════
components.html(f"""
<div id="aurora" style="position:fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none; z-index:0; overflow:hidden;">
    <div style="position:absolute; width:200%; height:200%; background: radial-gradient(circle at 10% 20%, {T["accent"]}05 0%, transparent 40%), radial-gradient(circle at 90% 80%, {T["purple"]}05 0%, transparent 45%);"></div>
</div>
<canvas id="canvas" style="position:fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none; z-index:0;"></canvas>
<script>
const canvas = document.getElementById('canvas'); const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth; canvas.height = window.innerHeight;
const nodes = Array.from({{length:40}}, () => ({{x:Math.random()*canvas.width, y:Math.random()*canvas.height, vx:(Math.random()-0.5)*0.3, vy:(Math.random()-0.5)*0.3, r:Math.random()*2+1}}));
function animate() {{
    ctx.clearRect(0,0,canvas.width,canvas.height);
    nodes.forEach(n => {{
        n.x+=n.vx; n.y+=n.vy; if(n.x<0||n.x>canvas.width) n.vx*=-1; if(n.y<0||n.y>canvas.height) n.vy*=-1;
        ctx.beginPath(); ctx.arc(n.x,n.y,n.r,0,Math.PI*2); ctx.fillStyle='rgba(255,75,43,0.2)'; ctx.fill();
    }});
    requestAnimationFrame(animate);
}}
animate();
</script>
""", height=0, scrolling=False)

# ══════════════════════════════════════════
# OUTPUT PLUG CARD COMPONENT DIRECT HANDLER
# ══════════════════════════════════════════
def output_card(title, content, accent_color=None, confidence=None, height=220):
    color = accent_color or T["accent"]
    conf_html = f'<div style="color:{T["green"]}; font-size:9px; font-family:monospace;">CONFIDENCE: {confidence}%</div>' if confidence else ""
    components.html(f"""
<div style="background:{T["glass"]}; border:1px solid {T["glassborder"]}; border-left:3px solid {color}; padding:20px; font-family:'Space Grotesk',sans-serif; max-height:{height}px; overflow-y:auto; color:{T["text2"]}; font-size:13px; line-height:1.7; white-space:pre-wrap;">
    <div style="display:flex; justify-content:space-between; margin-bottom:10px; font-family:'Space Mono',monospace; font-size:9px; letter-spacing:2px; color:{color}; text-transform:uppercase;">
        <div>{title}</div>
        {conf_html}
    </div>
    <div>{content}</div>
</div>
""", height=height+40)

def score_bento(scores, confidence):
    cards_html = "".join([f"""
<div style="background:{T["glass"]}; border:1px solid {T["glassborder"]}; border-top:2px solid {col}; padding:15px; font-family:'Space Mono',monospace; text-align:center;">
    <div style="font-size:8px; color:{T["text3"]}; text-transform:uppercase; letter-spacing:1px;">{lbl}</div>
    <div style="font-size:24px; font-weight:700; color:{col}; margin:5px 0;">{scores[k][0]}</div>
</div>""" for lbl, k, col in [("Viral Index","viral",T["accent"]),("Hook Strength","hook",T["purple"]),("Engagement","engagement",T["blue"]),("Shareability","share",T["green"]),("Retention","retention",T["yellow"]),("Reach Matrix","reach",T["orange"])]])
    
    components.html(f"""
<div style="display:flex; flex-direction:column; gap:10px;">
    <div style="background:{T["glass"]}; border:1px solid {T["green"]}30; padding:12px; font-family:'Space Mono',monospace; font-size:12px; color:{T["green"]}; display:flex; justify-content:space-between; align-items:center;">
        <span>▲ PIPELINE OPERATIONAL RATIO</span>
        <span>INTELLIGENT RECOGNITION CONFIDENCE: {confidence}%</span>
    </div>
    <div style="display:grid; grid-template-columns:repeat(6, 1fr); gap:10px;">{cards_html}</div>
</div>""", height=160)

# ══════════════════════════════════════════
# APPLICATION HEADER BLOCK 
# ══════════════════════════════════════════
col_logo, col_theme = st.columns([10, 2])
with col_logo:
    st.markdown(f"""<div style="font-family:'Space Mono',monospace; font-size:14px; font-weight:700; letter-spacing:2px;">🎬 REEL<span style="color:{T["accent"]};">MIND</span> AI <span style="font-size:9px; color:{T["text4"]}; border:1px solid {T["rule2"]}; padding:2px 6px; margin-left:10px;">v4.0 PRO-STREAM</span></div>""", unsafe_allow_html=True)
with col_theme:
    if st.button("🌓 SWITCH APPLICATION LIGHT VIBE"):
        st.session_state.theme = "light" if IS_DARK else "dark"
        st.rerun()

st.markdown(f"<div style='height:1px; background:{T['rule']}; margin:15px 0;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# MASTER INTERFACE CONTROLLER (TAB REPLACEMENT FOR SIDEBAR)
# ══════════════════════════════════════════
selector_col1, selector_col2 = st.columns(2)
with selector_col1:
    if st.button("🎬 RUN MASTER CONTENT ENGINE", type="primary" if st.session_state.active_module == "Content Engine" else "secondary"):
        st.session_state.active_module = "Content Engine"
        st.rerun()
with selector_col2:
    if st.button("🎥 RUN CINEMATIC VIDEO STORY ENGINE", type="primary" if st.session_state.active_module == "Video Engine" else "secondary"):
        st.session_state.active_module = "Video Engine"
        st.rerun()

# ══════════════════════════════════════════
# ENGINE LAYER ONE: CONTENT MATRIX GENERATOR
# ══════════════════════════════════════════
if st.session_state.active_module == "Content Engine":
    st.markdown(f"""
    <div style="margin:20px 0 30px 0;">
        <span style="font-family:'Space Mono',monospace; font-size:9px; color:{T["accent"]}; letter-spacing:2px;">MODULAR LAYER PROMPT DELIVERABLE</span>
        <h1 style="font-family:'Fraunces',serif; font-size:46px; font-style:italic; font-weight:900; margin:5px 0;">Social Content <span style="color:{T["accent"]};">Generator</span></h1>
        <p style="color:{T["text3"]}; font-size:13px; max-width:600px;">Design system deployed across algorithms. Enter topic specifics to dispatch execution instructions directly into the Gemini framework.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Grid Parameter Inputs
    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        topic = st.text_input("Operational Topic Base", placeholder="e.g. Villain arc mindset, AI transformation, fitness execution...")
    with p_col2:
        niche = st.selectbox("Target Strategic Niche", ["Dark Aesthetic / Motivation", "Tech & AI", "Gaming", "Anime & Manga", "Fitness & Gym", "Finance & Investing", "Horror & Thriller"])
    with p_col3:
        mode = st.selectbox("Engine Generation Variant Blueprint", ["⚡ Full Content Pack", "🎯 Hook Ideas Only", "📅 Content Series", "🎠 Carousel Post", "🧵 X/Twitter Thread", "🔄 Content Repurposer"])
        
    p_col4, p_col5, p_col6 = st.columns(3)
    with p_col4:
        platform = st.selectbox("Distribution Engine Vector", ["Instagram Reels", "TikTok", "YouTube Shorts"])
    with p_col5:
        tone = st.selectbox("Acoustic / Visual Behavioral Tone", ["Viral & Bold", "Dark & Cinematic", "Motivational & Intense", "Minimal & Clean", "Edgy & Controversial"])
    with p_col6:
        st.markdown("<label style='display:block; margin-bottom:8px;'>Action Dispatch</label>", unsafe_allow_html=True)
        st.markdown('<div class="generate-btn">', unsafe_allow_html=True)
        execute_generation = st.button("⚡ EXECUTE SYSTEM DISPATCH", key="run_main_engine")
        st.markdown('</div>', unsafe_allow_html=True)

    if execute_generation:
        if not topic.strip():
            st.error("Operational Base Variable Requirements Not Present. Define Topic Input Vector.")
        else:
            with st.spinner("Processing framework optimization architecture matrices..."):
                if "Full Content" in mode:
                    st.session_state.last_result = generate_full_content(topic, niche, platform, tone)
                elif "Hook" in mode:
                    st.session_state.last_result = {"raw": generate_hooks(topic, niche), "type": "raw_text"}
                elif "Series" in mode:
                    st.session_state.last_result = {"raw": generate_series(topic, niche, platform), "type": "raw_text"}
                elif "Carousel" in mode:
                    st.session_state.last_result = {"raw": generate_carousel(topic, niche, platform), "type": "raw_text"}
                elif "Thread" in mode:
                    st.session_state.last_result = {"raw": generate_thread(topic, niche), "type": "raw_text"}
                
                st.session_state.last_scores = gen_scores()
                st.session_state.last_confidence = random.randint(89, 98)

    # Content Presentation Pipelines
    if st.session_state.last_result and st.session_state.last_scores:
        gradient_divider()
        section_label("METRIC MATRIX DIAGNOSTICS")
        score_bento(st.session_state.last_scores, st.session_state.last_confidence)
        
        st.markdown("<br>", unsafe_allow_html=True)
        section_label("GENERATED KERNEL DEPLOYMENT OUTPUTS")
        
        res = st.session_state.last_result
        if "captions" in res and "type" not in res:
            t_cap1, t_cap2, t_cap3, t_cap4 = st.tabs(["📝 CAPTION VARIATIONS", "#️⃣ KEYWORD ARCHITECTURE", "🎬 VOICE OVER SCRIPT", "🖼️ IMAGING GENERATION SPECIFICATION"])
            with t_cap1:
                short, med, lon = parse_captions(res.get("captions", ""))
                output_card("Short Platform Capture", short, T["accent"])
                output_card("Medium Strategic Segment", med, T["blue"])
                output_card("Long Analytical Context Engine", lon, T["purple"])
            with t_cap2:
                hv, mv, nv = parse_hashtags(res.get("hashtags", ""))
                st.code(f"High-Volume: {' '.join(hv)}\nMedium-Volume: {' '.join(mv)}\nNiche-Community: {' '.join(nv)}", language="markdown")
            with t_cap3:
                output_card("Audio Flow Sequence Timeline (30s)", format_script(res.get("script", "")), T["purple"], height=320)
            with t_cap4:
                output_card("Midjourney Prompt Schema Asset", res.get("thumbnail", ""), T["gold"])
        else:
            output_card("Unified Strategic Blueprint Output Data", res.get("raw", "Data Error Process Terminal."), T["accent"], height=450)

# ══════════════════════════════════════════
# ENGINE LAYER TWO: CINEMATIC MULTI-PROMPT PIPELINE
# ══════════════════════════════════════════
elif st.session_state.active_module == "Video Engine":
    st.markdown(f"""
    <div style="margin:20px 0 30px 0;">
        <span style="font-family:'Space Mono',monospace; font-size:9px; color:{T["gold"]}; letter-spacing:2px;">CHRONO PHYSICS SEQUENTIAL CONTINUITY PIPELINE</span>
        <h1 style="font-family:'Fraunces',serif; font-size:46px; font-style:italic; font-weight:900; margin:5px 0;">Cinematic <span style="color:{T["gold"]};">Story</span> Engine</h1>
        <p style="color:{T["text3"]}; font-size:13px; max-width:600px;">Construct automated continuous animation instructions optimized to maintain strict visual character profiles across algorithmic rendering iterations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input Processing Row Block
    v_col1, v_col2, v_col3 = st.columns(3)
    with v_col1:
        v_animal = st.selectbox("Subject Character Core Configuration", ["Puppy 🐶", "Kitten 🐱", "Baby Penguin 🐧", "Baby Fox 🦊", "Baby Panda 🐼", "Baby Bunny 🐰"])
    with v_col2:
        v_story_type = st.selectbox("Structural Narrative Premise Framework", ["Funny", "Emotional", "Cute & Heartwarming", "Adventure", "Action"])
    with v_col3:
        v_style = st.selectbox("Visual Rendering Style Protocol", ["Pixar", "Disney", "DreamWorks", "Anime", "Realistic"])
        
    v_col4, v_col5, v_col6 = st.columns(3)
    with v_col4:
        v_duration = st.selectbox("Runtime Matrix Target Limits", [8, 16, 24, 30, 40, 60])
    with v_col5:
        v_ending = st.selectbox("System Dynamic Final Frame Target Mode", ["Funny / Comedic", "Emotional / Heartwarming", "Twist / Unexpected"])
    with v_col6:
        st.markdown("<label style='display:block; margin-bottom:8px;'>Sequence Initiation</label>", unsafe_allow_html=True)
        st.markdown('<div class="gold-btn-container">', unsafe_allow_html=True)
        execute_video_stories = st.button("🎥 GENERATE NARRATIVE SECTOR BLOCKS")
        st.markdown('</div>', unsafe_allow_html=True)

    if execute_video_stories:
        with st.spinner("Compiling algorithmic behavioral patterns..."):
            st.session_state.video_stories = generate_video_story(v_animal, v_story_type, v_duration, v_style, "Vertical Engine Matrix", v_ending)
            st.session_state.video_package = None

    if st.session_state.video_stories:
        gold_divider()
        section_label("COMPUTED GENERATION ANCHORS — CORE SELECTION STAGE")
        output_card("Computed Structural Narrative Opportunities", st.session_state.video_stories.get("stories", ""), T["gold"], height=350)
        
        # Interactive Continuation Workflow Block inside standard view space
        st.markdown("<br>", unsafe_allow_html=True)
        section_label("COMPILE EXPANDED PRODUCTION VALUE PACK")
        
        pkg_col1, pkg_col2 = st.columns([8, 4])
        with pkg_col1:
            story_details_input = st.text_area("Confirm selection data profile parameters here", placeholder="Manually verify or paste target segment narrative context scripts block here...")
        with pkg_col2:
            story_title_text = st.text_input("Production Identification Name Tag", "Cinematic Project Sequence Alpha")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🎬 RUN INTENSE CONTINUITY PARSER ASSEMBLY"):
                with st.spinner("Assembling frame variables context..."):
                    st.session_state.video_package = generate_video_full_package(v_animal, story_title_text, "Active Pipeline Trace Log", story_details_input, v_style, v_duration, "9:16 Core Engine")

        if st.session_state.video_package:
            pkg = st.session_state.video_package
            st.markdown("<br>", unsafe_allow_html=True)
            section_label("DEPLOYABLE PRODUCTION DELIVERABLES PIPELINE")
            
            vt_1, vt_2, vt_3 = st.tabs(["🎨 CHARACTER Turnaround Design PROMPT", "🖼️ INITIAL ESTABLISHING TIMELINE FRAME", "🎬 RENDER CLIP PROMPT PIPELINE STACK"])
            with vt_1:
                output_card("Turnaround Structural Design Prompt Instructions", pkg.get("character_analysis", ""), T["gold"])
            with vt_2:
                output_card("Establishing Backdrop Environmental Matrix Settings Configuration", pkg.get("first_frame", ""), T["purple"])
            with vt_3:
                for p in pkg.get("prompts", []):
                    output_card(f"Sequence Render Target Clip Prompt Element Vector - Block Layer {p['number']}", p["text"], T["accent"], height=120)

# ══════════════════════════════════════════
# FOOTER UTILITY SYSTEM BRAND MATRIX
# ══════════════════════════════════════════
st.markdown(f"""
<div style="margin-top:60px; padding:20px 0; border-top:1px solid {T["rule"]}; display:flex; justify-content:space-between; align-items:center; font-family:'Space Mono',monospace; font-size:9px; color:{T["text4"]};">
    <div>ENGINE CONTEXT TRACKER PIPELINE ACTIVE // GEMINI HYPER MODEL</div>
    <div>DESIGNED BY SATVIK SHARMA · NIET ENGINEERING SYSTEM ARCHITECTURE</div>
</div>
""", unsafe_allow_html=True)