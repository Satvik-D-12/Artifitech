from google import genai
from dotenv import load_dotenv
import os
import time

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# =====================================
# SAFE GENERATE
# =====================================

def safe_generate(prompt):
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
                return "QUOTA_ERROR: Daily Gemini quota exceeded. Wait for reset or use another API key."

            if "API_KEY_INVALID" in error:
                return "KEY_ERROR: Invalid API Key. Check your .env file."

            print(f"Attempt {attempt+1} failed: {error}")
            if attempt < 2:
                time.sleep(5)
            else:
                return f"GENERATION_ERROR: {error}"


# =====================================
# PARSE SECTIONS
# =====================================

def parse_sections(raw_text):
    """
    Parse the structured response into a clean dict
    with keys: captions, hashtags, script, thumbnail
    """
    sections = {
        "captions": "",
        "hashtags": "",
        "script": "",
        "thumbnail": "",
        "raw": raw_text
    }

    try:
        markers = {
            "captions":  ("==CAPTIONS==",  "==HASHTAGS=="),
            "hashtags":  ("==HASHTAGS==",  "==SCRIPT=="),
            "script":    ("==SCRIPT==",    "==THUMBNAIL=="),
            "thumbnail": ("==THUMBNAIL==", None),
        }

        for key, (start_marker, end_marker) in markers.items():
            start_idx = raw_text.find(start_marker)
            if start_idx == -1:
                continue
            start_idx += len(start_marker)

            if end_marker:
                end_idx = raw_text.find(end_marker)
                sections[key] = raw_text[start_idx:end_idx].strip() if end_idx != -1 else raw_text[start_idx:].strip()
            else:
                sections[key] = raw_text[start_idx:].strip()

    except Exception:
        pass

    return sections


# =====================================
# GENERATE ALL CONTENT
# =====================================

def generate_all_content(topic, niche, platform, tone="Viral & Bold"):

    prompt = f"""
You are a world-class viral content strategist and copywriter.

Generate complete social media content for:

TOPIC: {topic}
NICHE: {niche}
PLATFORM: {platform}
TONE: {tone}

Return EXACTLY in this format with these EXACT markers:

==CAPTIONS==

SHORT (under 50 words):
[caption here]

MEDIUM (50-100 words):
[caption here]

LONG (100-150 words):
[caption here]

==HASHTAGS==

HIGH VOLUME (1M+ posts):
[10 hashtags]

MEDIUM VOLUME (100K-1M posts):
[10 hashtags]

NICHE COMMUNITY (under 100K posts):
[10 hashtags]

==SCRIPT==

HOOK (0-3 seconds):
[one powerful scroll-stopping line]

BODY (3-25 seconds):
[5-7 punchy lines, each under 8 words, for on-screen text]

CTA (25-30 seconds):
[one specific call to action]

SUGGESTED AUDIO:
[describe the vibe/genre of music that fits]

==THUMBNAIL==

IMAGE PROMPT:
[50-80 word detailed prompt for Midjourney or Ideogram]

STYLE KEYWORDS:
[6-8 style descriptors separated by commas]

COLOR PALETTE:
[3-4 specific hex color codes with names]

Rules:
- Match the {tone} tone throughout
- Optimize specifically for {platform} algorithm
- Every caption must end with a hook question or CTA
- Script hook must create immediate curiosity or shock
- Hashtag mix must be strategic (not all mega-popular)
- Thumbnail prompt must be hyper-specific and visual
"""

    raw = safe_generate(prompt)
    return parse_sections(raw)


# =====================================
# GENERATE HOOK IDEAS ONLY
# =====================================

def generate_hooks(topic, niche, count=5):
    prompt = f"""
You are a viral content hook specialist.

Generate {count} different powerful hooks for a {niche} reel about: {topic}

Each hook should be:
- Under 10 words
- Immediately curiosity-triggering
- Different style (question, shock, controversy, story, number)

Format:
HOOK 1 (Question): ...
HOOK 2 (Shock): ...
HOOK 3 (Controversy): ...
HOOK 4 (Story): ...
HOOK 5 (Number): ...
"""
    return safe_generate(prompt)


# =====================================
# GENERATE CONTENT SERIES
# =====================================

def generate_series(topic, niche, platform, num_posts=5):
    prompt = f"""
You are a viral content strategist planning a content series.

Create a {num_posts}-post content series for a {niche} account on {platform} about: {topic}

For each post provide:

POST [N]:
ANGLE: [unique angle/perspective for this post]
HOOK: [opening hook line]
CAPTION PREVIEW: [first 2 sentences of caption]
HASHTAG THEME: [3-4 core hashtags]

Make each post build on the previous one.
Create a content journey, not just 5 random posts.
"""
    return safe_generate(prompt)