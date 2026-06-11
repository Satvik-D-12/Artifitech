from google import genai
from dotenv import load_dotenv
import os
import time

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ══════════════════════════════════════════
# SAFE GENERATE
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


# ══════════════════════════════════════════
# PARSE SECTIONS
# ══════════════════════════════════════════

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


# ══════════════════════════════════════════
# FULL CONTENT PACK
# ══════════════════════════════════════════

def generate_full_content(topic: str, niche: str, platform: str, tone: str) -> dict:
    prompt = f"""You are a world-class viral content strategist.

Generate complete social media content for:
TOPIC: {topic}
NICHE: {niche}
PLATFORM: {platform}
TONE: {tone}

Return EXACTLY in this format:

==CAPTIONS==

SHORT (under 50 words):
[caption]

MEDIUM (50-100 words):
[caption]

LONG (100-150 words):
[caption]

==HASHTAGS==

HIGH VOLUME (1M+ posts):
[10 hashtags on one line]

MEDIUM VOLUME (100K-1M posts):
[10 hashtags on one line]

NICHE COMMUNITY (under 100K posts):
[10 hashtags on one line]

==SCRIPT==

HOOK (0-3 seconds):
[one powerful line]

BODY (3-25 seconds):
[5-7 short punchy lines, each under 8 words]

CTA (25-30 seconds):
[one specific call to action]

SUGGESTED AUDIO:
[music vibe description]

==THUMBNAIL==

IMAGE PROMPT:
[50-80 word detailed image generation prompt]

STYLE KEYWORDS:
[6-8 style descriptors]

COLOR PALETTE:
[3-4 specific hex codes with names]

Rules:
- Match {tone} tone throughout
- Optimize for {platform} algorithm specifically
- Every caption must end with a hook question or CTA
- Script hook must create immediate curiosity or shock
- Hashtag mix must be strategic not all mega-popular
- Thumbnail prompt must be hyper-specific and cinematic"""

    raw = safe_generate(prompt)
    return parse_sections(raw)


# ══════════════════════════════════════════
# HOOK IDEAS
# ══════════════════════════════════════════

def generate_hooks(topic: str, niche: str, count: int = 5) -> str:
    prompt = f"""You are a viral content hook specialist.

Generate {count} different powerful hooks for a {niche} reel about: {topic}

Each hook must be under 10 words and a different style.

Format exactly:
HOOK 1 (Question): [hook]
HOOK 2 (Shock): [hook]
HOOK 3 (Controversy): [hook]
HOOK 4 (Story): [hook]
HOOK 5 (Number): [hook]"""
    return safe_generate(prompt)


# ══════════════════════════════════════════
# CONTENT SERIES
# ══════════════════════════════════════════

def generate_series(topic: str, niche: str, platform: str, num_posts: int = 5) -> str:
    prompt = f"""You are a viral content strategist planning a series.

Create a {num_posts}-post content series for a {niche} account on {platform} about: {topic}

Each post builds on the previous one.

For each post:
POST [N]:
ANGLE: [unique angle]
HOOK: [opening hook under 10 words]
CAPTION PREVIEW: [first 2 sentences]
HASHTAG THEME: [4 core hashtags]
BEST DAY: [day of week]"""
    return safe_generate(prompt)


# ══════════════════════════════════════════
# CAROUSEL
# ══════════════════════════════════════════

def generate_carousel(topic: str, niche: str, platform: str) -> str:
    prompt = f"""You are a carousel content specialist.

Create a 7-slide carousel post for {platform} about: {topic}
Niche: {niche}

For each slide:
SLIDE [N]:
HEADLINE: [bold headline under 6 words]
BODY: [2-3 lines of value-packed content]
VISUAL: [specific visual suggestion]

Slide 1 = hook. Slide 7 = CTA."""
    return safe_generate(prompt)


# ══════════════════════════════════════════
# TWITTER/X THREAD
# ══════════════════════════════════════════

def generate_thread(topic: str, niche: str) -> str:
    prompt = f"""You are a viral X/Twitter thread writer.

Write a viral 8-tweet thread about: {topic}
Niche: {niche}

Format:
TWEET 1 (Hook): [tweet under 280 chars]
TWEET 2: [tweet]
...
TWEET 8 (CTA): [engagement CTA]

Each tweet stands alone but flows into the next."""
    return safe_generate(prompt)


# ══════════════════════════════════════════
# CONTENT REPURPOSER
# ══════════════════════════════════════════

def repurpose_content(original: str, target_platform: str) -> str:
    prompt = f"""You are a content repurposing expert.

Repurpose this content for {target_platform}:

ORIGINAL:
{original}

Output:
REPURPOSED CAPTION:
[adapted caption]

REPURPOSED HASHTAGS:
[platform-specific hashtags]

REPURPOSED CTA:
[platform-appropriate CTA]"""
    return safe_generate(prompt)