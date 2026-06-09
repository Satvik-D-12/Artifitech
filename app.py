import streamlit as st
import re
from gemini_helper import generate_all_content

# =====================================
# PREMIUM THEME CONFIGURATION
# =====================================
st.set_page_config(
    page_title="ReelMind AI Ultra",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS injection for Studio Level UI (Dark Mode, Sky Blue Accents)
st.markdown("""
<style>
    /* Main Layout Tweaks */
    .stApp {
        background-color: #0E1117;
        color: #F0F2F6;
    }
    
    /* Input Boxes Customization */
    div.stTextInput > div > div > input {
        background-color: #1A1F2C !important;
        color: #FFFFFF !important;
        border: 1px solid #2D3748 !important;
        border-radius: 8px !important;
    }
    div.stSelectbox > div > div > div {
        background-color: #1A1F2C !important;
        color: #FFFFFF !important;
        border: 1px solid #2D3748 !important;
        border-radius: 8px !important;
    }

    /* Core CTA Button - Premium Sky Blue Glow */
    .stButton > button {
        background: linear-gradient(135deg, #00A3FF 0%, #0066FF 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 4px 15px rgba(0, 163, 255, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 163, 255, 0.5) !important;
    }

    /* Custom Design Output Container cards */
    .content-card {
        background-color: #161B22;
        padding: 24px;
        border-radius: 12px;
        border-left: 5px solid #00A3FF;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================
# HELPER PARSING UTILITY
# =====================================
def parse_section(text, section_name):
    pattern = rf"\[SECTION_START:{section_name}\](.*?)\[SECTION_END:{section_name}\]"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return "Generation failed or format mismatched for this segment."

# =====================================
# SIDEBAR NAVIGATION & INFO
# =====================================
with st.sidebar:
    st.markdown("<h1 style='color: #00A3FF; font-size: 2.2rem;'>🎬 ReelMind</h1>", unsafe_allow_html=True)
    st.markdown("🌐 **Studio Edition v3.0**")
    st.write("---")
    
    st.subheader("⚡ Core Modules Active")
    st.markdown("""
    - 🟢 **Gemini 2.5 Flash Engine**
    - 🟢 **Cross-Platform Targeter**
    - 🟢 **Automated Component Parser**
    - 🟢 **Midjourney Prompt Generator**
    """)
    st.write("---")
    st.caption("Designed for High-Retention Short Form Creators.")

# =====================================
# MAIN USER INTERFACE
# =====================================
st.title("⚡ AI Content Co-Pilot")
st.write("Generate high-retention structural content layouts for your brand assets instantly.")
st.write("---")

# Main Input Controls arranged in clean Columns
row1_col1, row1_col2, row1_col3 = st.columns(3)

with row1_col1:
    niche = st.selectbox(
        "Brand Niche",
        ["Anime", "Gaming", "Motivation", "Tech & AI", "Fitness", "Finance", "Horror", "Movie Industry", "Education"]
    )

with row1_col2:
    platform = st.selectbox(
        "Target Platform",
        ["Instagram Reels", "YouTube Shorts", "TikTok"]
    )

with row1_col3:
    tone = st.selectbox(
        "Vibe / Tone Profile",
        ["Cinematic Aesthetic", "Aggressive / Hype", "Dark Minimalist", "Informative / Clean", "Gen-Z Trendsetter"]
    )

topic = st.text_input("Enter Topic / Concept Hook", placeholder="e.g., The Rise of Dark AI, Hidden Anime Lore, 3 AM Gym Routine...")

st.write("")

# Execution Trigger
if st.button("🚀 Construct Campaign Assets"):
    if not topic.strip():
        st.warning("Please specify a topic or core idea before generating assets.")
    else:
        with st.spinner("🧠 Orchestrating viral patterns via Gemini Engine..."):
            raw_output = generate_all_content(topic, niche, platform, tone)
        
        # Check for operational level exceptions handled by the helper script
        if "ERROR_" in raw_output:
            st.error(raw_output)
        else:
            st.success("✨ Campaign Assets Fully Rendered!")
            
            # Unpacking raw generation using structural tags
            captions_data = parse_section(raw_output, "CAPTIONS")
            hashtags_data = parse_section(raw_output, "HASHTAGS")
            script_data = parse_section(raw_output, "SCRIPT")
            thumbnail_data = parse_section(raw_output, "THUMBNAIL")
            
            # Tabbed Display Layout Interface
            tab_caption, tab_script, tab_tags, tab_thumb = st.tabs([
                "📝 Dynamic Captions", 
                "🎬 Production Script", 
                "#️⃣ Growth Hashtags", 
                "🖼️ Thumbnail Framework"
            ])
            
            with tab_caption:
                st.markdown(f"<div class='content-card'><h3>📝 Algorithmic Captions ({tone})</h3><p style='white-space: pre-wrap;'>{captions_data}</p></div>", unsafe_allow_html=True)
                
            with tab_script:
                st.markdown(f"<div class='content-card'><h3>🎬 Retention Script Structure</h3><p style='white-space: pre-wrap;'>{script_data}</p></div>", unsafe_allow_html=True)
                
            with tab_tags:
                st.markdown(f"<div class='content-card'><h3>#️⃣ Sorted Distribution Tags</h3><p style='white-space: pre-wrap;'>{hashtags_data}</p></div>", unsafe_allow_html=True)
                
            with tab_thumb:
                st.markdown(f"<div class='content-card'><h3>🖼️ Creative Image Prompts</h3><p style='white-space: pre-wrap;'>{thumbnail_data}</p></div>", unsafe_allow_html=True)

            # Master Backup Download Node
            st.write("---")
            st.download_button(
                label="📥 Export Complete Raw Package (.txt)",
                data=raw_output,
                file_name=f"reelmind_{topic.lower().replace(' ', '_')}_package.txt",
                mime="text/plain"
            )