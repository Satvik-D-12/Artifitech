from google import genai
from dotenv import load_dotenv
import os, time

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ══════════════════════════════════════════
# SAFE GENERATE
# ══════════════════════════════════════════
def safe_generate(prompt: str) -> str:
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
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
[Write a complete punchy caption under 50 words. Use emojis naturally. End with a question or CTA.]

MEDIUM (50-100 words):
[Write a complete 50-100 word caption. Tell a mini story or share insight. Use emojis. Strong CTA at the end.]

LONG (100-150 words):
[Write a complete 100-150 word caption. Full narrative arc with hook, value delivery, and strong CTA. Use emojis strategically.]

==HASHTAGS==

HIGH VOLUME (1M+ posts):
[10 hashtags on one line separated by spaces]

MEDIUM VOLUME (100K-1M posts):
[10 hashtags on one line separated by spaces]

NICHE COMMUNITY (under 100K posts):
[10 hashtags on one line separated by spaces]

==SCRIPT==

HOOK (0-3 seconds):
[Write one complete, powerful sentence that will stop someone mid-scroll. It must create immediate curiosity, shock, or emotional pull. This is spoken or shown on screen as the very first thing viewers see. Make it impossible to ignore.]

BODY (3-25 seconds):
[Write 6-8 complete on-screen text lines. Each line should be a complete thought under 8 words. Write them as a flowing narrative — each line builds on the previous one. Together they should deliver real value, tell a story, or build tension. Format each line on its own line with a dash: - line one here]

CTA (25-30 seconds):
[Write one specific, compelling call to action. Tell viewers exactly what to do and why — follow, save, comment, share. Make it feel urgent and personal, not generic.]

SUGGESTED AUDIO:
[Describe the perfect music in detail — genre, tempo (BPM range), mood, energy level, and why it matches this content. Example: "Lo-fi hip hop, 75-85 BPM, melancholic but hopeful, minimal beats with subtle piano — matches the reflective tone of the content and keeps viewers watching without distraction."]

==THUMBNAIL==

IMAGE PROMPT:
[Write a 60-80 word hyper-specific image generation prompt. Include: exact subject description, lighting style, color palette, mood, composition, camera angle, background detail, and rendering style. Be cinematic and specific.]

STYLE KEYWORDS:
[8 specific visual style descriptors separated by commas]

COLOR PALETTE:
[4 hex color codes with descriptive names, e.g. #ff4b2b Volcanic Red, #1a1a2e Midnight Navy]"""

    raw = safe_generate(prompt)
    return parse_sections(raw)

# ══════════════════════════════════════════
# HOOK IDEAS
# ══════════════════════════════════════════
def generate_hooks(topic: str, niche: str, count: int = 5) -> str:
    prompt = f"""You are a viral content hook specialist.

Generate {count} different powerful hooks for a {niche} reel about: {topic}

Each hook must be under 10 words and use a different psychological trigger.

Format exactly:
HOOK 1 (Question): [hook]
WHY IT WORKS: [one sentence psychological explanation]
BEST PLATFORM: [where this hook style dominates]

HOOK 2 (Shock): [hook]
WHY IT WORKS: [explanation]
BEST PLATFORM: [platform]

HOOK 3 (Controversy): [hook]
WHY IT WORKS: [explanation]
BEST PLATFORM: [platform]

HOOK 4 (Story): [hook]
WHY IT WORKS: [explanation]
BEST PLATFORM: [platform]

HOOK 5 (Number): [hook]
WHY IT WORKS: [explanation]
BEST PLATFORM: [platform]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# CONTENT SERIES
# ══════════════════════════════════════════
def generate_series(topic: str, niche: str, platform: str, num_posts: int = 5) -> str:
    prompt = f"""You are a viral content strategist.

Create a {num_posts}-post content series for {niche} on {platform} about: {topic}

Each post builds on the previous — create a journey viewers NEED to follow.

For each post:

POST [N]:
ANGLE: [unique angle not covered in previous posts]
HOOK: [opening hook under 10 words]
CAPTION PREVIEW: [first 2 complete sentences that pull viewers in]
KEY VALUE: [what viewers learn or feel]
HASHTAG THEME: [4 core hashtags]
BEST DAY TO POST: [day]
CLIFFHANGER: [how this post makes viewers need the next one]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# CAROUSEL
# ══════════════════════════════════════════
def generate_carousel(topic: str, niche: str, platform: str) -> str:
    prompt = f"""Create a 7-slide carousel for {platform} about: {topic} in the {niche} niche.

SLIDE [N]:
HEADLINE: [bold headline under 6 words]
BODY TEXT: [2-3 complete sentences of value]
VISUAL DIRECTION: [specific design instruction]
EMOTION: [what this slide should make the viewer feel]

Slide 1 = pattern interrupt hook. Slide 7 = strong save/share CTA."""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# THREAD
# ══════════════════════════════════════════
def generate_thread(topic: str, niche: str) -> str:
    prompt = f"""Write a viral 8-tweet X/Twitter thread about: {topic} in the {niche} niche.

TWEET 1 (Hook): [complete tweet under 280 chars — bold claim or pattern interrupt]
TWEET 2: [complete tweet]
TWEET 3: [complete tweet]
TWEET 4: [complete tweet]
TWEET 5: [complete tweet]
TWEET 6: [complete tweet]
TWEET 7: [complete tweet]
TWEET 8 (CTA): [engagement CTA tweet]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# REPURPOSE
# ══════════════════════════════════════════
def repurpose_content(original: str, target_platform: str) -> str:
    prompt = f"""Repurpose this content for {target_platform}:

ORIGINAL:
{original}

REPURPOSED CAPTION:
[fully adapted caption native to {target_platform}]

REPURPOSED HASHTAGS:
[platform-specific hashtags]

REPURPOSED HOOK:
[platform-optimized opening]

REPURPOSED CTA:
[platform-appropriate call to action]

ADAPTATION NOTES:
[2-3 sentences on what changed and why]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# STORYFLOW — STORY GENERATION
# ══════════════════════════════════════════
def generate_story(story_type, character, duration, style, platform, ending_type,
                   custom_character="", custom_story_idea="") -> str:
    char = custom_character if custom_character else character
    idea_ctx = f"\nCustom idea: {custom_story_idea}" if custom_story_idea else ""

    prompt = f"""You are a master viral AI animal story writer for {style}-style animated {platform} videos.

Create 3 complete story options for a {duration}-second {story_type} animated video featuring: {char}
Ending: {ending_type}{idea_ctx}

For EACH story follow this EXACT structure:

═══════════════════════════════════
STORY OPTION [N]
═══════════════════════════════════

TITLE: [Catchy viral title]

VIRALITY SCORE: [X/100]
EMOTION SCORE: [X/100]
RETENTION SCORE: [X/100]
HOOK STRENGTH: [X/100]
ESTIMATED WATCH %: [X%]
AI CONFIDENCE: [X%]

LOGLINE: [One sentence that makes someone need to watch this immediately]

FULL STORY BREAKDOWN:

HOOK (0-3 seconds):
[Describe exactly what happens — camera angle, character action, expression, environment. What makes someone stop scrolling instantly?]

GOAL/CURIOSITY (3-8 seconds):
[What does the character want? Why do viewers immediately root for them? Describe the visual that creates investment.]

FIRST CONFLICT (8-{duration//3} seconds):
[What goes wrong? Describe the problem in cinematic detail — character reaction, facial expression, body language, environment interaction.]

ESCALATION ({duration//3}-{2*duration//3} seconds):
[How does it get worse? Describe the cause-and-effect chain. Each failure leads naturally to the next. Include the funny or emotional peak moment.]

TWIST/HELP ({2*duration//3}-{duration-5} seconds):
[The unexpected turn. Who helps? What clever solution appears? What surprises the viewer?]

PAYOFF ({duration-5}-{duration} seconds):
[The {ending_type} ending in full detail. Exact visuals, character expressions, the emotional peak. What makes viewers say "aww" or laugh out loud?]

ALL SCENE OBJECTS (must all appear in Frame 1):
[Comma-separated list of every prop, character, and environment element]

VIRALITY HOOK:
[Why will people share this? What specific emotion does it trigger?]

═══════════════════════════════════

Generate all 3 stories. Make each completely different in approach."""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# STORYFLOW — CHARACTER SHEET
# ══════════════════════════════════════════
def generate_character_sheet(character: str, style: str, story_context: str = "") -> str:
    prompt = f"""You are a professional character designer for {style} 3D animation.

Generate a complete character design package for: {character}
Style: {style}
Context: {story_context if story_context else "Animated short film"}

1. MASTER CHARACTER SHEET PROMPT:
[150-200 word image generation prompt for a professional character turnaround sheet.
Include: specific physical features, fur/skin texture, eye details, colors, accessories, personality in design.
Format: "[Character] character model sheet, animation turnaround, multiple angles.
Top Row: Front, left side, back, right side, 3/4 view — all neutral standing pose.
Bottom Row: Close-up details grid, color palette with hex codes, expressions grid (Happy, Excited, Sad, Curious, Determined, Surprised).
{style} 3D animation, clean white background, warm studio lighting, 4K quality."]

2. INDIVIDUAL EXPRESSION PROMPTS:
HAPPY: [specific expression prompt]
EXCITED: [specific expression prompt]
SAD: [specific expression prompt]
CURIOUS: [specific expression prompt]
DETERMINED: [specific expression prompt]
SURPRISED: [specific expression prompt]

3. CHARACTER BIBLE:
[150-word description of personality, movement style, quirks, and what makes them visually memorable]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# STORYFLOW — FRAME 1
# ══════════════════════════════════════════
def generate_frame1_prompt(story_summary, character, scene_objects, style, platform) -> str:
    aspect = "vertical 9:16" if platform in ["Instagram Reels","TikTok","YouTube Shorts"] else "horizontal 16:9"
    prompt = f"""You are a master cinematographer for {style} animated films.

Create the perfect Frame 1 establishing shot for:
STORY: {story_summary}
CHARACTER: {character}
ALL OBJECTS: {scene_objects}
STYLE: {style}
ASPECT: {aspect}

FRAME 1 MASTER PROMPT:
[Write a complete 200-250 word image generation prompt.
Start with the character in foreground. Plant ALL story objects visibly even if minor.
Set the camera angle that works for the entire story.
Establish lighting and mood.
End with: "{style} 3D animation, 4K cinematic quality, {aspect}, professional studio lighting, high detail"]

OBJECT PLACEMENT GUIDE:
[Where each object sits and why it makes visual sense]

CAMERA NOTES:
[Height, angle, focal length, and why this works for the full story]

CONTINUITY CHECKLIST:
[Every element that must stay consistent across ALL future prompts]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# STORYFLOW — PROMPT CHAIN
# (Fully flexible: user picks duration + segment size)
# ══════════════════════════════════════════
def generate_prompt_chain(story_breakdown, character, scene_objects,
                           duration: int, segment_size: int, style, platform) -> str:
    num_prompts = duration // segment_size
    aspect = "vertical 9:16" if platform in ["Instagram Reels","TikTok","YouTube Shorts"] else "horizontal 16:9"

    prompt = f"""You are a master AI video prompt engineer for {style} animated story continuity.

Create a COMPLETE {num_prompts}-prompt video chain.

STORY: {story_breakdown}
CHARACTER: {character}
ALL SCENE OBJECTS: {scene_objects}
TOTAL DURATION: {duration} seconds
SEGMENTS: {num_prompts} prompts × {segment_size} seconds each
STYLE: {style}
ASPECT: {aspect}

Generate ALL {num_prompts} prompts in this EXACT format:

═══════════════════════════════════════════════
PROMPT [N] — [SCENE NAME] ({segment_size} SECONDS)
═══════════════════════════════════════════════

SCENE GOAL: [What story beat does this segment accomplish?]

CONTINUITY LOCK:
- Character: [exact appearance description]
- Position: [where in frame]
- Expression: [emotion at start]
- Camera: [angle and height]
- All objects: [list with positions]
- Lighting: [description]

FULL VIDEO PROMPT:
[Write 200-250 words. 
Start PROMPT 1 with: "Ultra-cute {style}-quality 3D animated {character}. 4K cinematic quality. {aspect}. One continuous camera shot. No scene changes. No cuts. No teleporting. Same environment throughout."
Start PROMPTS 2+ with: "IMPORTANT: Start from the EXACT frame shown in the attached screenshot. Match everything exactly — character appearance, expression, camera angle, lighting, all object positions. Continue seamlessly. No cuts. No new objects. Same environment. Same shot."
Then write second-by-second action:
0-{segment_size//4} sec: [exact visual action]
{segment_size//4}-{segment_size//2} sec: [exact visual action]
{segment_size//2}-{3*segment_size//4} sec: [exact visual action]
{3*segment_size//4}-{segment_size} sec: [exact visual action with end frame freeze description]]

END FRAME:
[Describe the exact last frame — character pose, expression, position, all objects visible, stable and ready for screenshot]

MOTION PHYSICS:
[Cause → Effect chain for this segment]

═══════════════════════════════════════════════

Generate all {num_prompts} prompts. Every prompt ends on a STABLE FRAME.
The final prompt delivers the complete story payoff."""
    return safe_generate(prompt)