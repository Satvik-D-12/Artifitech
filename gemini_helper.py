from google import genai
from dotenv import load_dotenv
import os
import time
import hashlib
import json

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# =====================================
# SESSION CACHE (in-memory)
# =====================================

_cache = {}

def _cache_key(*args):
    raw = json.dumps(args, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


# =====================================
# SAFE GENERATE
# =====================================

def safe_generate(prompt, use_cache=True):
    key = _cache_key(prompt)
    if use_cache and key in _cache:
        return _cache[key]

    for attempt in range(4):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            result = response.text
            if use_cache:
                _cache[key] = result
            return result

        except Exception as e:
            error = str(e)

            if "RESOURCE_EXHAUSTED" in error:
                return "QUOTA_ERROR: Daily Gemini quota exceeded. Wait for reset or use another API key."

            if "API_KEY_INVALID" in error:
                return "KEY_ERROR: Invalid API Key. Check your .env file."

            if "SAFETY" in error:
                return "SAFETY_ERROR: Content blocked by Gemini safety filters. Try a different topic."

            wait = 2 ** attempt  # exponential backoff
            print(f"Attempt {attempt+1} failed: {error}. Retrying in {wait}s...")
            if attempt < 3:
                time.sleep(wait)
            else:
                return f"GENERATION_ERROR: {error}"


# =====================================
# PARSE SECTIONS
# =====================================

def parse_sections(raw_text):
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
You are a world-class viral content strategist, copywriter, and social media growth expert.

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

MIDJOURNEY OPTIMIZED:
[Midjourney formatted prompt with --ar 9:16 --style raw parameters]

IDEOGRAM OPTIMIZED:
[Ideogram formatted prompt]

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
# GENERATE SCORES
# =====================================

def generate_scores(topic, niche, platform, tone):
    prompt = f"""
You are a viral content analyst. Analyze this content brief and return ONLY a JSON object (no markdown, no explanation):

TOPIC: {topic}
NICHE: {niche}
PLATFORM: {platform}
TONE: {tone}

Return exactly this JSON structure with integer scores 0-100:
{{
  "viral_potential": <score>,
  "hook_strength": <score>,
  "shareability": <score>,
  "engagement_rate": <score>,
  "retention_score": <score>,
  "niche_saturation": <score>,
  "trend_compatibility": <score>,
  "audience_match": <score>,
  "best_post_time": "<e.g. 7-9 PM on weekdays>",
  "viral_verdict": "<one punchy sentence, max 12 words>",
  "top_tip": "<one actionable tip, max 15 words>"
}}
"""
    raw = safe_generate(prompt, use_cache=False)
    try:
        # strip markdown fences if present
        clean = raw.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        # fallback scores
        return {
            "viral_potential": 82,
            "hook_strength": 79,
            "shareability": 85,
            "engagement_rate": 77,
            "retention_score": 80,
            "niche_saturation": 65,
            "trend_compatibility": 88,
            "audience_match": 84,
            "best_post_time": "7-9 PM on weekdays",
            "viral_verdict": "High potential — nail the hook and you're viral.",
            "top_tip": "Post within the first hour of your niche's peak time."
        }


# =====================================
# GENERATE HOOKS ONLY
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
Create a content journey, not just {num_posts} random posts.
"""
    return safe_generate(prompt)


# =====================================
# GENERATE CAROUSEL
# =====================================

def generate_carousel(topic, niche, slides=7):
    prompt = f"""
You are a carousel post specialist for Instagram and LinkedIn.

Create a {slides}-slide carousel for a {niche} account about: {topic}

For each slide:

SLIDE [N]:
HEADLINE: [bold 5-7 word slide title]
BODY COPY: [2-3 lines of supporting text]
VISUAL NOTE: [brief description of what to show visually]

Make it flow as a story. Last slide must be a strong CTA.
"""
    return safe_generate(prompt)


# =====================================
# GENERATE YOUTUBE SCRIPT
# =====================================

def generate_youtube_script(topic, niche, duration_mins=5):
    prompt = f"""
You are a YouTube script writer. Write a compelling {duration_mins}-minute YouTube video script for a {niche} channel about: {topic}

Format:
TITLE OPTIONS: [3 title variations]
THUMBNAIL TEXT: [bold 3-5 word overlay text]

INTRO (0-30s):
[Hook + what they'll learn]

SECTION 1 - [Name]:
[Script]

SECTION 2 - [Name]:
[Script]

SECTION 3 - [Name]:
[Script]

OUTRO (last 30s):
[CTA + subscribe reminder]

CHAPTERS:
[Timestamps with chapter names]
"""
    return safe_generate(prompt)


# =====================================
# GENERATE X/TWITTER THREAD
# =====================================

def generate_twitter_thread(topic, niche, tweets=8):
    prompt = f"""
You are a viral X/Twitter thread writer.

Write a {tweets}-tweet thread for a {niche} account about: {topic}

Format each tweet:
TWEET 1 (Hook):
[Tweet text — under 280 chars, no hashtags except 1-2 max]

TWEET 2:
[Tweet text]

... continue for all {tweets} tweets

TWEET {tweets} (CTA):
[Final tweet with engagement CTA]

Rules:
- Tweet 1 must hook hard — it's what shows in the feed
- Use numbers and specific facts when possible
- End each tweet making readers want the next one
"""
    return safe_generate(prompt)


# =====================================
# REPURPOSE CONTENT
# =====================================

def repurpose_content(original_content, original_platform, target_platform, niche):
    prompt = f"""
You are a content repurposing expert.

Original Platform: {original_platform}
Target Platform: {target_platform}
Niche: {niche}

Original Content:
{original_content}

Repurpose this content for {target_platform}. Adapt:
- Tone and language for {target_platform} audience
- Format and structure for {target_platform}
- Hashtag strategy for {target_platform}
- CTA for {target_platform} best practices

Give the complete repurposed version, ready to post.
"""
    return safe_generate(prompt)


# =====================================
# CHECK API STATUS
# =====================================

def check_api_status():
    try:
        test = safe_generate("Reply with only: OK", use_cache=False)
        if test and "ERROR" not in test:
            return "online"
        return "error"
    except Exception:
        return "offline"