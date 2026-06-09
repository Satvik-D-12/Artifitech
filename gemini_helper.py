from google import genai
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Initializing the modern Google GenAI Client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# =====================================
# SAFE GENERATE WITH RETRIES
# =====================================
def safe_generate(prompt):
    for attempt in range(3):
        try:
            # Utilizing the latest fast reasoning model
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            error = str(e)
            if "RESOURCE_EXHAUSTED" in error:
                return "ERROR_QUOTA: Daily Gemini quota exceeded."
            if "API_KEY_INVALID" in error:
                return "ERROR_KEY: Invalid API Key detected."
            
            print(f"Attempt {attempt+1} failed: {error}")
            if attempt < 2:
                time.sleep(3)
            else:
                return f"ERROR_FINAL: {error}"

# =====================================
# CORE GENERATION ENGINE
# =====================================
def generate_all_content(topic, niche, platform, tone):
    prompt = f"""
You are an elite, multi-platform viral growth strategist and expert copywriter.
Generate high-retaining short-form content optimized for:
TOPIC: {topic}
NICHE: {niche}
PLATFORM: {platform}
TONE/VIBE: {tone}

Your response must strictly use the designated structural tags [SECTION_START:NAME] and [SECTION_END:NAME] so the backend engine can parse it cleanly. Do not skip any section.

[SECTION_START:CAPTIONS]
Provide three variations optimized for the {platform} algorithm matching a {tone} vibe.
SHORT (Punchy, under 50 words):
[Insert short caption here + emojis]

MEDIUM (Engaging story/value hook, 50-100 words):
[Insert medium caption here]

LONG (Deep-dive, high interaction, 100-150 words):
[Insert long caption here]
[SECTION_END:CAPTIONS]

[SECTION_START:HASHTAGS]
Provide exactly 30 platform-specific tags separated cleanly by spaces.
HIGH VOLUME (Broad reach):
[10 tags]
MEDIUM VOLUME (Targeted):
[10 tags]
NICHE (Community specific):
[10 tags]
[SECTION_END:HASHTAGS]

[SECTION_START:SCRIPT]
Write a highly engaging 30-60 second retention-optimized video script.
HOOK (0-3s): [Extreme hook matching {tone}]
BODY (3-25s): [Fast-paced, high value delivery lines]
CTA (25-30s): [Strong psychological call to action tailored to {platform}]
AUDIO: [Specific trending audio style or sound design cue]
[SECTION_END:SCRIPT]

[SECTION_START:THUMBNAIL]
PROMPT: [Ultra-detailed text-to-image prompt for Midjourney/Ideogram reflecting the {niche} aesthetic, composition, lighting and layout]
STYLE: [5 cinematic keywords]
COLORS: [Hex codes or clear aesthetic color palette description]
[SECTION_END:THUMBNAIL]

Rules:
- Strictly adhere to the requested format tags.
- Maximize watch time indicators (loops, open loops, curiosity gaps).
- Infuse the selected tone profile explicitly throughout.
"""
    return safe_generate(prompt)