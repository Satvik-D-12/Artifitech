import streamlit as st
from gemini_helper import (
    generate_all_content,
    generate_hooks,
    generate_series
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
# PREMIUM CSS — Studio-Grade Dark UI
# =====================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&family=Fraunces:ital,wght@0,900;1,900&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0a0a !important;
    color: #e8e6e1 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

[data-testid="stAppViewContainer"] > .main {
    background: #0a0a0a !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
    display: none;
}

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── HERO HEADER ── */
.rm-hero {
    position: relative;
    padding: 80px 60px 60px;
    border-bottom: 1px solid #1e1e1e;
    overflow: hidden;
}

.rm-hero::before {
    content: '';
    position: absolute;
    top: -120px; right: -120px;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(255, 75, 43, 0.08) 0%, transparent 70%);
    pointer-events: none;
}

.rm-hero::after {
    content: '';
    position: absolute;
    bottom: -80px; left: 200px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(100, 60, 255, 0.06) 0%, transparent 70%);
    pointer-events: none;
}

.rm-eyebrow {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #ff4b2b;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.rm-eyebrow::before {
    content: '';
    display: inline-block;
    width: 24px; height: 1px;
    background: #ff4b2b;
}

.rm-title {
    font-family: 'Fraunces', serif;
    font-size: clamp(52px, 6vw, 88px);
    font-weight: 900;
    font-style: italic;
    line-height: 0.92;
    letter-spacing: -3px;
    color: #f0ede6;
    margin-bottom: 20px;
}

.rm-title .accent {
    color: #ff4b2b;
}

.rm-title .dim {
    color: #3a3a3a;
}

.rm-subtitle {
    font-size: 15px;
    color: #666;
    font-weight: 300;
    max-width: 480px;
    line-height: 1.6;
    margin-bottom: 32px;
}

.rm-stats {
    display: flex;
    gap: 40px;
    flex-wrap: wrap;
}

.rm-stat {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.rm-stat-num {
    font-family: 'Space Mono', monospace;
    font-size: 22px;
    font-weight: 700;
    color: #f0ede6;
}

.rm-stat-label {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #444;
}

/* ── NAV TABS ── */
.rm-nav {
    display: flex;
    gap: 0;
    border-bottom: 1px solid #1a1a1a;
    padding: 0 60px;
    background: #0a0a0a;
}

.rm-nav-item {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 16px 24px;
    color: #444;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;
}

.rm-nav-item.active {
    color: #ff4b2b;
    border-bottom-color: #ff4b2b;
}

/* ── MAIN CONTENT AREA ── */
.rm-content {
    padding: 48px 60px;
    display: grid;
    grid-template-columns: 340px 1fr;
    gap: 48px;
    align-items: start;
}

/* ── INPUT PANEL ── */
.rm-panel {
    background: #0f0f0f;
    border: 1px solid #1e1e1e;
    padding: 32px;
    position: sticky;
    top: 24px;
}

.rm-panel-label {
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #444;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 1px solid #1a1a1a;
}

/* ── STREAMLIT OVERRIDES ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #111 !important;
    border: 1px solid #222 !important;
    border-radius: 0 !important;
    color: #e8e6e1 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 14px !important;
    padding: 14px 16px !important;
    transition: border-color 0.2s !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #ff4b2b !important;
    box-shadow: 0 0 0 1px #ff4b2b20 !important;
}

.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #333 !important;
}

.stSelectbox > div > div {
    background: #111 !important;
    border: 1px solid #222 !important;
    border-radius: 0 !important;
    color: #e8e6e1 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

.stSelectbox > div > div > div {
    color: #e8e6e1 !important;
}

/* Selectbox dropdown */
[data-baseweb="select"] > div {
    background: #111 !important;
    border-color: #222 !important;
    border-radius: 0 !important;
}

[data-baseweb="popover"] {
    background: #111 !important;
}

[data-baseweb="menu"] {
    background: #111 !important;
    border: 1px solid #222 !important;
}

[data-baseweb="option"] {
    background: #111 !important;
    color: #e8e6e1 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

[data-baseweb="option"]:hover {
    background: #1e1e1e !important;
}

label, .stSelectbox label, .stTextInput label, .stTextArea label {
    color: #555 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    margin-bottom: 6px !important;
}

/* ── GENERATE BUTTON ── */
.stButton > button {
    background: #ff4b2b !important;
    color: #fff !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    padding: 16px 32px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    margin-top: 8px !important;
}

.stButton > button:hover {
    background: #e03a1a !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(255,75,43,0.25) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* Secondary buttons (download) */
.stDownloadButton > button {
    background: transparent !important;
    color: #555 !important;
    border: 1px solid #222 !important;
    border-radius: 0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
}

.stDownloadButton > button:hover {
    border-color: #ff4b2b !important;
    color: #ff4b2b !important;
    background: transparent !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1a1a1a !important;
    gap: 0 !important;
    padding: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #444 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 12px 20px !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
}

.stTabs [aria-selected="true"] {
    color: #ff4b2b !important;
    border-bottom-color: #ff4b2b !important;
    background: transparent !important;
}

.stTabs [data-baseweb="tab-panel"] {
    padding: 0 !important;
    background: transparent !important;
}

/* ── OUTPUT CARDS ── */
.rm-output-card {
    background: #0f0f0f;
    border: 1px solid #1a1a1a;
    padding: 28px;
    margin-bottom: 16px;
    position: relative;
}

.rm-output-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: #ff4b2b;
}

.rm-output-label {
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #ff4b2b;
    margin-bottom: 14px;
}

.rm-output-text {
    font-size: 13px;
    line-height: 1.8;
    color: #aaa;
    white-space: pre-wrap;
    font-family: 'Space Grotesk', sans-serif;
}

/* ── TEXT AREA OUTPUT ── */
.stTextArea > div > div > textarea {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important;
    line-height: 1.8 !important;
    color: #aaa !important;
    background: #0f0f0f !important;
    border: 1px solid #1a1a1a !important;
    border-left: 3px solid #ff4b2b !important;
}

/* ── SUCCESS / WARNING ── */
.stSuccess {
    background: rgba(255,75,43,0.06) !important;
    border: 1px solid rgba(255,75,43,0.2) !important;
    color: #ff4b2b !important;
    border-radius: 0 !important;
}

.stWarning {
    background: rgba(255,193,7,0.06) !important;
    border: 1px solid rgba(255,193,7,0.2) !important;
    border-radius: 0 !important;
}

.stSpinner > div {
    border-top-color: #ff4b2b !important;
}

/* ── DIVIDER ── */
hr {
    border-color: #1a1a1a !important;
    margin: 32px 0 !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0d0d0d !important;
    border-right: 1px solid #1a1a1a !important;
}

[data-testid="stSidebar"] * {
    color: #888 !important;
}

/* ── METRIC ── */
[data-testid="stMetric"] {
    background: #0f0f0f !important;
    border: 1px solid #1a1a1a !important;
    padding: 20px !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #444 !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Space Mono', monospace !important;
    color: #f0ede6 !important;
    font-size: 28px !important;
}

/* ── RADIO ── */
.stRadio > div {
    gap: 8px !important;
}

.stRadio > div > label {
    background: #0f0f0f !important;
    border: 1px solid #1e1e1e !important;
    padding: 10px 16px !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    color: #555 !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
}

.stRadio > div > label:hover {
    border-color: #ff4b2b !important;
    color: #ff4b2b !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0a0a0a; }
::-webkit-scrollbar-thumb { background: #222; border-radius: 0; }
::-webkit-scrollbar-thumb:hover { background: #ff4b2b; }

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: #0f0f0f !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 0 !important;
    color: #555 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
}

.streamlit-expanderContent {
    background: #0d0d0d !important;
    border: 1px solid #1a1a1a !important;
    border-top: none !important;
}

/* ── FOOTER LINE ── */
.rm-footer {
    padding: 24px 60px;
    border-top: 1px solid #111;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.rm-footer-left {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    color: #2a2a2a;
}

.rm-footer-right {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: #2a2a2a;
    letter-spacing: 1px;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# HERO HEADER
# =====================================

st.markdown("""
<div class="rm-hero">
    <div class="rm-eyebrow">AI Content Engine — v3.0</div>
    <div class="rm-title">
        Reel<span class="accent">Mind</span><br>
        <span class="dim">AI</span>
    </div>
    <div class="rm-subtitle">
        Generate scroll-stopping captions, hashtag stacks, reel scripts,
        and thumbnail prompts — in one shot.
    </div>
    <div class="rm-stats">
        <div class="rm-stat">
            <span class="rm-stat-num">4</span>
            <span class="rm-stat-label">Outputs per run</span>
        </div>
        <div class="rm-stat">
            <span class="rm-stat-num">30</span>
            <span class="rm-stat-label">Hashtags generated</span>
        </div>
        <div class="rm-stat">
            <span class="rm-stat-num">3</span>
            <span class="rm-stat-label">Caption lengths</span>
        </div>
        <div class="rm-stat">
            <span class="rm-stat-num">∞</span>
            <span class="rm-stat-label">Niches supported</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================
# MODE SELECTOR
# =====================================

st.markdown("<div style='padding: 24px 60px 0; border-bottom: 1px solid #1a1a1a;'>", unsafe_allow_html=True)

mode = st.radio(
    "",
    ["Full Content Pack", "Hook Ideas Only", "Content Series"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("</div>", unsafe_allow_html=True)

# =====================================
# MAIN CONTENT
# =====================================

st.markdown("<div style='padding: 40px 60px;'>", unsafe_allow_html=True)

col_input, col_output = st.columns([1, 1.8], gap="large")

# ── INPUT PANEL ──
with col_input:
    st.markdown('<div class="rm-panel-label">Configure Your Content</div>', unsafe_allow_html=True)

    topic = st.text_input(
        "Topic",
        placeholder="e.g. Super Villain, Morning Routine, AI Tools...",
        key="topic_input"
    )

    niche = st.selectbox(
        "Niche",
        [
            "Dark Aesthetic / Motivation",
            "Gaming",
            "Anime & Manga",
            "Fitness & Gym",
            "Tech & AI",
            "Finance & Investing",
            "Horror & Thriller",
            "Fashion & Lifestyle",
            "Education",
            "Movie Industry",
            "Music & Artists",
            "Business & Entrepreneurship"
        ]
    )

    platform = st.selectbox(
        "Platform",
        [
            "Instagram Reels",
            "TikTok",
            "YouTube Shorts"
        ]
    )

    tone = st.selectbox(
        "Tone",
        [
            "Viral & Bold",
            "Dark & Cinematic",
            "Motivational & Intense",
            "Minimal & Clean",
            "Edgy & Controversial",
            "Informative & Professional"
        ]
    )

    if mode == "Content Series":
        num_posts = st.selectbox("Posts in Series", [3, 5, 7, 10])

    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)

    generate_btn = st.button(
        "→ GENERATE" if mode == "Full Content Pack"
        else "→ GET HOOKS" if mode == "Hook Ideas Only"
        else "→ BUILD SERIES"
    )

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # Quick tips
    with st.expander("QUICK TIPS"):
        st.markdown("""
<div style='font-family: Space Grotesk, sans-serif; font-size: 12px; color: #555; line-height: 1.8;'>

→ Specific topics outperform generic ones<br>
→ <strong style='color: #888;'>"Villain arc workout" &gt; "gym"</strong><br>
→ Match tone to your existing content<br>
→ Use Hook Ideas to A/B test openings<br>
→ Build Series for consistent posting

</div>
""", unsafe_allow_html=True)

# ── OUTPUT PANEL ──
with col_output:

    if generate_btn:
        if not topic.strip():
            st.warning("Enter a topic to generate content.")
        else:
            # ── FULL CONTENT PACK ──
            if mode == "Full Content Pack":
                with st.spinner(""):
                    st.markdown("""
<div style='font-family: Space Mono, monospace; font-size: 10px;
letter-spacing: 2px; color: #ff4b2b; padding: 20px 0;'>
GENERATING CONTENT...
</div>""", unsafe_allow_html=True)
                    result = generate_all_content(topic, niche, platform, tone)

                if "ERROR" in result.get("raw", "") or not result["captions"]:
                    st.error(result.get("raw", "Generation failed. Try again."))
                else:
                    st.markdown("""
<div style='font-family: Space Mono, monospace; font-size: 9px;
letter-spacing: 3px; color: #ff4b2b; margin-bottom: 24px;'>
✓ CONTENT READY
</div>""", unsafe_allow_html=True)

                    tab1, tab2, tab3, tab4 = st.tabs([
                        "CAPTIONS", "HASHTAGS", "SCRIPT", "THUMBNAIL"
                    ])

                    with tab1:
                        st.markdown(f"""
<div class="rm-output-card">
<div class="rm-output-label">Caption Stack</div>
<div class="rm-output-text">{result['captions']}</div>
</div>""", unsafe_allow_html=True)
                        st.download_button(
                            "↓ DOWNLOAD CAPTIONS",
                            result["captions"],
                            file_name=f"captions_{topic[:20].replace(' ','_')}.txt",
                            mime="text/plain",
                            key="dl_captions"
                        )

                    with tab2:
                        st.markdown(f"""
<div class="rm-output-card">
<div class="rm-output-label">Hashtag Stack — 30 Tags</div>
<div class="rm-output-text">{result['hashtags']}</div>
</div>""", unsafe_allow_html=True)
                        st.download_button(
                            "↓ DOWNLOAD HASHTAGS",
                            result["hashtags"],
                            file_name=f"hashtags_{topic[:20].replace(' ','_')}.txt",
                            mime="text/plain",
                            key="dl_hashtags"
                        )

                    with tab3:
                        st.markdown(f"""
<div class="rm-output-card">
<div class="rm-output-label">Reel Script — 30 Seconds</div>
<div class="rm-output-text">{result['script']}</div>
</div>""", unsafe_allow_html=True)
                        st.download_button(
                            "↓ DOWNLOAD SCRIPT",
                            result["script"],
                            file_name=f"script_{topic[:20].replace(' ','_')}.txt",
                            mime="text/plain",
                            key="dl_script"
                        )

                    with tab4:
                        st.markdown(f"""
<div class="rm-output-card">
<div class="rm-output-label">Thumbnail Generation Prompt</div>
<div class="rm-output-text">{result['thumbnail']}</div>
</div>""", unsafe_allow_html=True)
                        st.download_button(
                            "↓ DOWNLOAD PROMPT",
                            result["thumbnail"],
                            file_name=f"thumbnail_{topic[:20].replace(' ','_')}.txt",
                            mime="text/plain",
                            key="dl_thumbnail"
                        )

                    # Full pack download
                    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
                    full_content = f"""REELMIND AI — FULL CONTENT PACK
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
"""
                    st.download_button(
                        "↓ DOWNLOAD FULL PACK",
                        full_content,
                        file_name=f"reelmind_{topic[:20].replace(' ','_')}_full.txt",
                        mime="text/plain",
                        key="dl_full"
                    )

            # ── HOOK IDEAS ──
            elif mode == "Hook Ideas Only":
                with st.spinner(""):
                    hooks = generate_hooks(topic, niche)

                if hooks and "ERROR" not in hooks:
                    st.markdown(f"""
<div class="rm-output-card">
<div class="rm-output-label">5 Hook Variations — {topic}</div>
<div class="rm-output-text">{hooks}</div>
</div>""", unsafe_allow_html=True)
                    st.download_button(
                        "↓ DOWNLOAD HOOKS",
                        hooks,
                        file_name=f"hooks_{topic[:20].replace(' ','_')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(hooks or "Generation failed.")

            # ── CONTENT SERIES ──
            elif mode == "Content Series":
                with st.spinner(""):
                    series = generate_series(topic, niche, platform, num_posts)

                if series and "ERROR" not in series:
                    st.markdown(f"""
<div class="rm-output-card">
<div class="rm-output-label">{num_posts}-Post Content Series — {topic}</div>
<div class="rm-output-text">{series}</div>
</div>""", unsafe_allow_html=True)
                    st.download_button(
                        "↓ DOWNLOAD SERIES PLAN",
                        series,
                        file_name=f"series_{topic[:20].replace(' ','_')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(series or "Generation failed.")

    else:
        # Empty state
        st.markdown("""
<div style='
    border: 1px dashed #1a1a1a;
    padding: 80px 40px;
    text-align: center;
    margin-top: 8px;
'>
    <div style='
        font-family: Space Mono, monospace;
        font-size: 9px;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #222;
        margin-bottom: 16px;
    '>Awaiting Input</div>
    <div style='
        font-size: 13px;
        color: #2a2a2a;
        line-height: 1.7;
        font-family: Space Grotesk, sans-serif;
    '>
        Configure your content parameters<br>
        on the left and hit Generate.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# =====================================
# FOOTER
# =====================================

st.markdown("""
<div class="rm-footer">
    <div class="rm-footer-left">REELMIND AI — v3.0 — POWERED BY GEMINI 2.5 FLASH</div>
    <div class="rm-footer-right">BUILT BY SATVIK SHARMA</div>
</div>
""", unsafe_allow_html=True)