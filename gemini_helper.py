"""
gemini_helper.py — ReelMind AI v6.1
All Gemini API calls, input validation, mode descriptions,
story parsing, and safe content assembly.
"""
from google import genai
from dotenv import load_dotenv
import os, re, time

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ── MODE DESCRIPTIONS (used for tooltips) ──────────────────
MODE_DESCRIPTIONS = {
    "⚡ Full Content Pack": {
        "short":   "Everything in one run — captions, hashtags, script, thumbnail.",
        "detail":  "Generates 3 caption lengths, 30 hashtags across 3 tiers, a fully readable reel script (Hook→Body→CTA) and a Midjourney/Ideogram thumbnail prompt.",
        "time":    "~15–25 sec",
        "best_for":"Full content drops, batch planning",
    },
    "🎯 Hook Ideas Only": {
        "short":   "5 scroll-stopping openers, each with a psychology breakdown.",
        "detail":  "Creates 5 distinct hook styles (Question, Shock, Controversy, Story, Number) with a plain-English explanation of why each one works.",
        "time":    "~8–12 sec",
        "best_for":"A/B testing your first 3 seconds",
    },
    "📅 Content Series": {
        "short":   "A Netflix-style multi-post series with cliffhangers.",
        "detail":  "Plans 3–7 connected posts, each with a unique angle, hook, caption preview, hashtag theme, best posting day, and a cliffhanger line.",
        "time":    "~12–18 sec",
        "best_for":"Building an audience over multiple posts",
    },
    "🎠 Carousel Post": {
        "short":   "A 7-slide save-worthy carousel with visual design notes.",
        "detail":  "Writes each slide's headline, body copy, visual layout suggestion, and a micro-CTA. Slide 1 stops the scroll; slide 7 converts viewers to followers.",
        "time":    "~12–18 sec",
        "best_for":"High-save educational or value posts",
    },
    "🧵 X/Twitter Thread": {
        "short":   "An 8-tweet viral thread built to hit 1M+ impressions.",
        "detail":  "Writes a hook tweet, 6 value-packed body tweets, and a CTA tweet — each under 280 characters and engineered to pull the reader to the next.",
        "time":    "~10–15 sec",
        "best_for":"Cross-posting reel content to X/Twitter",
    },
    "🔄 Content Repurposer": {
        "short":   "Takes your existing content and rewrites it natively for a new platform.",
        "detail":  "Paste any caption, script, or idea. The AI rewrites it for TikTok, YouTube Shorts, X, or LinkedIn — matching that platform's culture and mechanics.",
        "time":    "~10–15 sec",
        "best_for":"Maximising reach from one piece of content",
    },
}

def get_all_mode_descriptions() -> dict:
    return MODE_DESCRIPTIONS

# ── INPUT VALIDATION ───────────────────────────────────────
def validate_inputs(topic="", original_content="", mode=""):
    if "Repurposer" in mode:
        if not original_content or not original_content.strip():
            return False, "Please paste your original content before repurposing."
        if len(original_content.strip()) < 20:
            return False, "Content too short — paste at least a sentence or two."
        return True, ""
    if not topic or not topic.strip():
        return False, "Please enter a topic before generating."
    if len(topic.strip()) < 3:
        return False, "Topic is too short — be a bit more specific."
    if len(topic) > 300:
        return False, "Topic too long — keep it under 300 characters."
    return True, ""

# ── SAFE GENERATE ──────────────────────────────────────────
def safe_generate(prompt: str) -> str:
    for attempt in range(3):
        try:
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            return response.text
        except Exception as e:
            err = str(e)
            if "RESOURCE_EXHAUSTED" in err:
                return "QUOTA_ERROR||Daily Gemini quota exceeded. Wait for reset or use another API key."
            if "API_KEY_INVALID" in err:
                return "KEY_ERROR||Invalid API key. Check your .env file."
            print(f"[ReelMind] Attempt {attempt+1} failed: {err}")
            if attempt < 2: time.sleep(5)
            else: return f"GENERATION_ERROR||{err}"

# ── PARSE SECTIONS ─────────────────────────────────────────
def parse_sections(raw: str) -> dict:
    sections = {"captions":"","hashtags":"","script":"","thumbnail":"","raw":raw}
    markers = {
        "captions": ("==CAPTIONS==","==HASHTAGS=="),
        "hashtags":  ("==HASHTAGS==","==SCRIPT=="),
        "script":    ("==SCRIPT==","==THUMBNAIL=="),
        "thumbnail": ("==THUMBNAIL==",None),
    }
    for key,(start,end) in markers.items():
        si = raw.find(start)
        if si == -1: continue
        si += len(start)
        if end:
            ei = raw.find(end, si)
            sections[key] = raw[si:ei].strip() if ei != -1 else raw[si:].strip()
        else:
            sections[key] = raw[si:].strip()
    return sections

# ── PARSE STORY BLOCKS ─────────────────────────────────────
def parse_story_blocks(raw: str) -> list:
    """Parse 3-story AI response into list of dicts for story cards."""
    stories = []
    blocks = re.split(r'\bSTORY\s*\[?(\d)\]?\s*:', raw, flags=re.I)
    i = 1
    while i < len(blocks) - 1:
        num_str = blocks[i].strip()
        content = blocks[i+1].strip() if i+1 < len(blocks) else ""
        def g(pat): m=re.search(pat,content,re.I); return m.group(1).strip() if m else ""
        title   = g(r'TITLE\s*:\s*(.+)') or f"Story {num_str}"
        logline = g(r'LOGLINE\s*:\s*(.+)')
        hook    = g(r'HOOK[^:]*:\s*(.+)')
        viral   = g(r'VIRALITY SCORE\s*:\s*(.+)')
        emotion = g(r'EMOTION SCORE\s*:\s*(.+)')
        why_m   = re.search(r'WHY IT WORKS\s*:\s*([\s\S]*?)(?=\n[A-Z]|$)',content,re.I)
        why     = why_m.group(1).strip()[:200] if why_m else ""
        stories.append({
            "number": int(num_str) if num_str.isdigit() else len(stories)+1,
            "title": title, "logline": logline,
            "hook_preview": hook[:120]+("..." if len(hook)>120 else ""),
            "virality": viral or "—", "emotion": emotion or "—",
            "why": why,
            "full_text": f"STORY {num_str}:\n{content}".strip()
        })
        i += 2
    if not stories:
        stories.append({"number":1,"title":"Generated Story","logline":"See full text below.",
                        "hook_preview":"","virality":"—","emotion":"—","why":"","full_text":raw})
    return stories[:3]

# ── CONTENT GENERATORS ─────────────────────────────────────
def generate_full_content(topic, niche, platform, tone):
    prompt = f"""You are a world-class viral content strategist and professional scriptwriter.
Generate complete social media content for:
TOPIC: {topic} | NICHE: {niche} | PLATFORM: {platform} | TONE: {tone}

Return EXACTLY in this format:

==CAPTIONS==
SHORT (under 50 words):
[punchy caption under 50 words ending with a hook question or CTA]

MEDIUM (50-100 words):
[engaging 50-100 word caption with story element, value proposition, CTA]

LONG (100-150 words):
[rich 100-150 word caption with context, emotional connection, value, strong CTA]

==HASHTAGS==
HIGH VOLUME (1M+ posts):
[10 hashtags space-separated]
MEDIUM VOLUME (100K-1M posts):
[10 hashtags space-separated]
NICHE COMMUNITY (under 100K posts):
[10 hashtags space-separated]

==SCRIPT==
Write every line as a complete natural spoken sentence — NEVER keywords or fragments.
This will be read aloud on camera word-for-word.

HOOK (0-3 seconds):
[ONE complete spoken sentence — the exact words to say to stop the scroll]

VISUAL DIRECTION FOR HOOK:
[One sentence: what to show on screen during the hook]

BODY (3-25 seconds):
[6-8 numbered complete spoken sentences, each under 12 words, building the story]
1. [sentence]
2. [sentence]
...

CTA (25-30 seconds):
[ONE complete spoken sentence — tell the viewer exactly what to do and why]

SUGGESTED AUDIO:
[1-2 sentences: music vibe, tempo (BPM), mood]

PRODUCTION NOTES:
[2-3 sentences: practical filming tips — pacing, energy, pauses]

==THUMBNAIL==
IMAGE PROMPT:
[60-90 word cinematic image prompt: subject, action, lighting, camera angle, background, mood, style]
STYLE KEYWORDS:
[6-8 visual style descriptors, comma-separated]
COLOR PALETTE:
[3-4 hex codes with names, e.g. #FF4B2B Deep Crimson]

Rules: match {tone} throughout; optimise for {platform}; every caption must feel human; script must be performable immediately."""
    return parse_sections(safe_generate(prompt))

def generate_hooks(topic, niche, count=5):
    return safe_generate(f"""You are a viral content hook specialist.
Generate {count} powerful opening hooks for a {niche} reel about: {topic}
Each hook: under 12 words, complete spoken sentence, distinctly different style.
Format exactly:
HOOK 1 (Question): [sentence]
WHY: [plain-English explanation]
HOOK 2 (Shock): [sentence]
WHY: [plain-English explanation]
HOOK 3 (Controversy): [sentence]
WHY: [plain-English explanation]
HOOK 4 (Story): [sentence]
WHY: [plain-English explanation]
HOOK 5 (Number): [sentence]
WHY: [plain-English explanation]""")

def generate_series(topic, niche, platform, num_posts=5):
    return safe_generate(f"""You are a viral content strategist planning a high-retention series.
Create a {num_posts}-post content series for a {niche} account on {platform} about: {topic}
Each post builds curiosity for the next — like a Netflix series. Write in plain English.
For each post:
POST [N]:
ANGLE: [unique sub-topic in plain language]
HOOK: [full opening line — complete spoken sentence]
CAPTION PREVIEW: [first 2-3 full sentences]
HASHTAG THEME: [4 core hashtags]
BEST DAY: [day and one-sentence reason]
CLIFFHANGER: [one sentence pulling viewers to next post]""")

def generate_carousel(topic, niche, platform):
    return safe_generate(f"""You are a carousel content specialist.
Create a 7-slide carousel for {platform} about: {topic} | Niche: {niche}
For each slide:
SLIDE [N]:
HEADLINE: [bold headline under 6 words]
BODY: [2-3 complete value-packed sentences]
VISUAL: [specific visual design suggestion with colors and layout]
MICRO-CTA: [one-line action prompt]
Slide 1 stops the scroll. Slide 7 converts viewers to followers.
End with:
COVER DESIGN: [detailed cover visual description]
CAPTION: [3-sentence post caption]""")

def generate_thread(topic, niche):
    return safe_generate(f"""You are a viral X/Twitter thread writer.
Write a viral 8-tweet thread about: {topic} | Niche: {niche}
Rules: every tweet under 280 chars, complete thought, natural flow, plain English.
TWEET 1 (Hook): [tweet]
TWEET 2: [tweet]
TWEET 3: [tweet]
TWEET 4: [tweet]
TWEET 5: [tweet]
TWEET 6: [tweet]
TWEET 7: [tweet]
TWEET 8 (CTA): [tweet]
THREAD TITLE: [name for saving]
BEST TIME TO POST: [day/time + one-sentence reason]""")

def repurpose_content(original, target_platform):
    return safe_generate(f"""You are a content repurposing expert.
Repurpose this content for {target_platform}:
ORIGINAL CONTENT:
{original}
Rewrite it natively for {target_platform}. Plain, easy-to-understand language throughout.
REPURPOSED CAPTION:
[complete native rewrite for {target_platform}'s culture and limits]
REPURPOSED HASHTAGS:
[10 hashtags optimised for {target_platform}]
REPURPOSED HOOK:
[opening line for {target_platform}'s scroll behaviour]
REPURPOSED CTA:
[platform-appropriate call to action]
PLATFORM NOTES:
[3 plain-English observations explaining what changed and why]""")

# ── VIDEO STORY GENERATOR ──────────────────────────────────
def generate_video_story(animal, story_type, duration, style, platform, ending_type):
    raw = safe_generate(f"""You are a world-class viral AI animal video story creator.
Generate 3 viral story options for:
- Character: {animal} | Type: {story_type} | Duration: {duration}s
- Style: {style} | Platform: {platform} | Ending: {ending_type}

Use EXACTLY this format for each:

STORY [N]:
TITLE: [catchy title]
LOGLINE: [one sentence summary]
HOOK (0-3 sec): [exactly what happens in first 3 seconds]
GOAL: [what the character wants — one sentence]
CONFLICT: [the obstacle — one sentence]
ESCALATION: [how it gets worse — one sentence]
PAYOFF: [the resolution — one sentence]
ENDING: [the final {ending_type} moment — be specific]
VIRALITY SCORE: [1-100]
EMOTION SCORE: [1-100]
RETENTION SCORE: [1-100]
ESTIMATED WATCH %: [percentage]
WHY IT WORKS: [2 sentences on the psychological hooks]

Make each story distinctly different in structure and emotional arc.
Ensure enough plot material for a {duration}-second video.""")
    return {"stories": raw, "parsed": parse_story_blocks(raw), "raw": raw}

def generate_video_full_package(animal, story_title, story_logline, story_details,
                                 style, duration, platform, clip_length=8):
    """
    Full production package.
    duration: any positive integer (total seconds).
    clip_length: 8 or 10 seconds per clip.
    num_prompts = round(duration / clip_length), no upper cap.
    """
    if clip_length not in (8, 10): clip_length = 8
    num_prompts = max(1, round(duration / clip_length))

    char_raw = safe_generate(f"""You are a {style}-style 3D animation character designer.
STORY: {story_title} | CHARACTER: {animal}
DETAILS: {story_details}
Output:
CHARACTERS: [list each character, one per line]
STORY OBJECTS (props): [list each prop, one per line]
ENVIRONMENT ELEMENTS: [list each environment component, one per line]
CHARACTER SHEET PROMPT for {animal}:
[Complete character design prompt in {style} style. Include fur/skin color, eye shape/color,
distinguishing features, accessories. Format:
"{animal} character model sheet, animation turnaround, multiple angles.
Top Row: Full body front, side, back, top-down views.
Bottom Row: Feature close-ups, color palette swatches, 6 expression references (Happy, Excited, Sad, Curious, Determined, Surprised).
Style: {style}-style 3D render, 4K, warm studio lighting, clean neutral background. [description]"]""")

    frame_raw = safe_generate(f"""You are a {style}-style cinematic 3D animation director of photography.
TITLE: {story_title} | CHARACTER: {animal} | STYLE: {style} | PLATFORM: {platform} (9:16)
TOTAL: {duration}s across {num_prompts} clips of {clip_length}s each
STORY: {story_details}

Write a 150-200 word image generation prompt for the MASTER FIRST FRAME:
- All story-important objects already visible in the scene
- Camera angle that will be held across ALL clips
- Character's emotional starting state
- Complete environment, lighting, mood
- Technical: {style}-quality 3D, 4K, vertical 9:16, cinematic

FIRST FRAME PROMPT:
[full prompt here]

CONTINUITY NOTES:
[5-8 specific visual elements that MUST stay identical in every clip]""")

    beats_raw = safe_generate(f"""Story editor for {style} animation.
STORY: {story_details}
Break into exactly {num_prompts} sequential beats (one per clip of {clip_length}s).
Avoid filler. Each beat must be distinct and advance the story.
BEAT 1: [what happens]
BEAT 2: [what happens]
...
BEAT {num_prompts}: [what happens]""")

    beat_lines = []
    for line in beats_raw.splitlines():
        line = line.strip()
        if re.match(r'BEAT\s*\d+', line, re.I):
            ci = line.find(":")
            if ci != -1: beat_lines.append(line[ci+1:].strip())
    while len(beat_lines) < num_prompts: beat_lines.append("")

    prompts_output = []
    for i in range(1, num_prompts+1):
        is_first = (i == 1); is_last = (i == num_prompts)
        beat = beat_lines[i-1]
        clip_raw = safe_generate(f"""You are a {style}-style 3D animated video director.
Prompt {i} of {num_prompts} for: {story_title} | {animal} | {style} | {platform} | {clip_length}s
THIS CLIP'S BEAT: {beat if beat else "Continue story naturally."}
{"Start from the First Frame image." if is_first else "MUST open with: IMPORTANT: Start from the exact last frame of the previous clip. Match everything exactly: character, position, environment, camera angle, lighting, all objects."}
{"FINAL CLIP — deliver complete emotional payoff, end on perfect shareable frame." if is_last else ""}

Write a complete {clip_length}s video prompt:
1. OPENING: exact starting state
2. TIMELINE ({clip_length//4}s segments):
   0-{clip_length//4}s: [action]
   {clip_length//4}-{clip_length//2}s: [action]
   {clip_length//2}-{3*clip_length//4}s: [action]
   {3*clip_length//4}-{clip_length}s: [action]
3. MOTION PHYSICS: weight, speed, bounce, reaction
4. FACIAL EXPRESSIONS: specific emotions each moment
5. END FRAME: exact final state, stable pose, ready for next clip
6. TECHNICAL: {style} 3D, 4K cinematic, 9:16, one continuous shot, no cuts
Be extremely specific — not "puppy jumps" but precise physical description.

PROMPT {i}:
[full prompt here]""")
        prompts_output.append({"number":i,"beat":beat,"text":clip_raw})

    cont_raw = safe_generate(f"""Production continuity checklist for:
{story_title} | {animal} | {style} | {num_prompts} clips × {clip_length}s = {duration}s total
List 10 specific, actionable checks between every clip to maintain perfect visual continuity.
Write in plain, clear English. Number each item. Make each specific to this story.""")

    return {
        "character_analysis": char_raw,
        "first_frame": frame_raw,
        "beats": beats_raw,
        "prompts": prompts_output,
        "continuity": cont_raw,
        "num_prompts": num_prompts,
        "clip_length": clip_length,
        "duration": duration,
    }