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
    prompt = f"""You are a world-class viral content strategist and professional scriptwriter.

Generate complete social media content for:
TOPIC: {topic}
NICHE: {niche}
PLATFORM: {platform}
TONE: {tone}

Return EXACTLY in this format:

==CAPTIONS==

SHORT (under 50 words):
[Write a complete punchy caption under 50 words. Use emojis naturally. End with a hook question or CTA. Make it feel human, not AI-generated.]

MEDIUM (50-100 words):
[Write a complete 50-100 word caption. Tell a mini story or share a real insight. Use emojis. Include a tension-building middle and a strong CTA at the end.]

LONG (100-150 words):
[Write a complete 100-150 word caption. Full narrative arc: hook opening, value delivery, emotional connection, and strong CTA. Use emojis strategically, not excessively.]

==HASHTAGS==

HIGH VOLUME (1M+ posts):
[10 hashtags on one line separated by spaces]

MEDIUM VOLUME (100K-1M posts):
[10 hashtags on one line separated by spaces]

NICHE COMMUNITY (under 100K posts):
[10 hashtags on one line separated by spaces]

==SCRIPT==

HOOK (0-3 seconds):
[Write ONE complete, powerful sentence spoken or shown on screen. This must create immediate curiosity, shock, or emotional pull that makes someone stop scrolling. Write it as actual dialogue or an on-screen statement — not a keyword or topic description. Example: "Nobody told me this would change my life in 30 days."]

BODY (3-25 seconds):
[Write 6-8 complete on-screen text lines. Each line is a full sentence under 10 words. Write them as a flowing spoken narrative where each line builds on the previous. Format each on its own line with a number:
1. [full sentence line]
2. [full sentence line]
3. [full sentence line]
4. [full sentence line]
5. [full sentence line]
6. [full sentence line]
7. [full sentence line]
8. [full sentence line]]

CTA (25-30 seconds):
[Write one complete, urgent call-to-action sentence. Tell viewers exactly what to do and why — follow, save, comment, share. Make it feel personal and time-sensitive, not generic.]

SUGGESTED AUDIO:
[Write 2-3 complete sentences describing the perfect music. Include genre, BPM range, mood, energy level, and why this specific sound profile matches the content and keeps viewers watching.]

==THUMBNAIL==

IMAGE PROMPT:
[Write a 65-85 word hyper-specific image generation prompt. Include: exact subject description with physical details, lighting style and direction, color palette, mood and emotion, composition and framing, camera angle, background detail, and rendering/art style. Be cinematic and specific enough to paste directly into Midjourney or Ideogram.]

STYLE KEYWORDS:
[8 specific visual style descriptors separated by commas]

COLOR PALETTE:
[4 hex color codes with descriptive names. Example: #ff4b2b Volcanic Red, #1a1a2e Midnight Navy, #f0b429 Molten Gold, #0f0f0f Deep Void]

Rules:
- Match {tone} tone throughout every single section
- Optimize specifically for {platform} algorithm behavior and viewer psychology
- Every caption must feel human and natural — no AI-sounding phrases
- Script hook must create immediate pattern interruption, not describe the topic
- Script body lines must be complete spoken thoughts, never fragments or keywords
- Hashtag strategy: spread across all three tiers for maximum algorithmic reach"""

    raw = safe_generate(prompt)
    return parse_sections(raw)

# ══════════════════════════════════════════
# HOOK IDEAS
# ══════════════════════════════════════════
def generate_hooks(topic: str, niche: str, count: int = 5) -> str:
    prompt = f"""You are a viral content hook specialist with deep expertise in scroll psychology.

Generate {count} different powerful opening hooks for a {niche} reel about: {topic}

Each hook must be under 12 words and use a distinctly different psychological trigger.
Write each as a complete spoken sentence or on-screen statement — not a fragment or keyword.

Format exactly:

HOOK 1 (Question):
[complete hook sentence]
WHY IT WORKS: [one sentence psychological explanation]
BEST PLATFORM: [where this hook style performs strongest]

HOOK 2 (Shock/Controversy):
[complete hook sentence]
WHY IT WORKS: [one sentence explanation]
BEST PLATFORM: [platform]

HOOK 3 (Bold Claim):
[complete hook sentence]
WHY IT WORKS: [one sentence explanation]
BEST PLATFORM: [platform]

HOOK 4 (Story/Personal):
[complete hook sentence]
WHY IT WORKS: [one sentence explanation]
BEST PLATFORM: [platform]

HOOK 5 (Number/Specificity):
[complete hook sentence]
WHY IT WORKS: [one sentence explanation]
BEST PLATFORM: [platform]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# CONTENT SERIES
# ══════════════════════════════════════════
def generate_series(topic: str, niche: str, platform: str, num_posts: int = 5) -> str:
    prompt = f"""You are a viral content strategist who creates series that build audiences.

Create a {num_posts}-post content series for {niche} on {platform} about: {topic}

Each post must build on the previous one — design this like a Netflix series where viewers need to see the next episode.

For each post provide:

POST [N]:
ANGLE: [unique sub-angle not covered in previous posts]
HOOK: [complete opening line under 12 words — written as a spoken sentence]
CAPTION PREVIEW: [first 2-3 complete sentences that draw viewers in immediately]
KEY VALUE: [what viewers learn, feel, or gain from this post]
HASHTAG THEME: [4 core hashtags most relevant to this specific post's angle]
BEST DAY TO POST: [specific day and brief reason why]
CLIFFHANGER: [one sentence that makes viewers need to see the next post in the series]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# CAROUSEL
# ══════════════════════════════════════════
def generate_carousel(topic: str, niche: str, platform: str) -> str:
    prompt = f"""You are a carousel content specialist. Create a high-save, high-share 7-slide carousel for {platform} about: {topic} in the {niche} niche.

SLIDE [N]:
HEADLINE: [bold headline under 6 words — direct and punchy]
BODY TEXT: [2-3 complete value-packed sentences. Real sentences, no fragments.]
VISUAL DIRECTION: [specific design instruction with layout and color]
EMOTION TARGET: [what this slide should make the viewer feel]

Slide 1 = pattern interrupt hook that stops the scroll.
Slide 7 = strong save/share/follow CTA.

After all slides add:
COVER DESIGN: [detailed visual description of the cover image]
POST CAPTION: [full 3-sentence caption for the carousel post itself]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# THREAD
# ══════════════════════════════════════════
def generate_thread(topic: str, niche: str) -> str:
    prompt = f"""You are a viral X/Twitter thread writer who consistently hits 1M+ impressions.

Write a viral 8-tweet thread about: {topic} in the {niche} niche.

Rules:
- Every tweet is a complete thought under 280 characters
- Tweet 1 must stop someone mid-scroll with a bold claim or pattern interrupt
- Tweets 2-7 must deliver specific, actionable value
- Each tweet naturally leads to the next
- Tweet 8 drives follows, bookmarks, or replies

TWEET 1 (Hook): [complete tweet — under 280 chars]
TWEET 2: [complete tweet]
TWEET 3: [complete tweet]
TWEET 4: [complete tweet]
TWEET 5: [complete tweet]
TWEET 6: [complete tweet]
TWEET 7: [complete tweet]
TWEET 8 (CTA): [engagement CTA tweet]

After the thread:
THREAD TITLE: [what to save this thread as]
BEST TIME TO POST: [day and time with reason]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# REPURPOSE
# ══════════════════════════════════════════
def repurpose_content(original: str, target_platform: str) -> str:
    prompt = f"""You are a content repurposing expert who understands each platform's unique culture and algorithm.

Repurpose this content for {target_platform}:

ORIGINAL CONTENT:
{original}

Analyze the core message and completely rewrite it natively for {target_platform} — not just an edit, a full transformation.

REPURPOSED CAPTION:
[Fully rewritten caption native to {target_platform}. Match the platform's tone, format, and character expectations completely.]

REPURPOSED HASHTAGS:
[10 hashtags optimized specifically for {target_platform}'s tagging culture and discovery system]

REPURPOSED HOOK:
[Opening line rewritten specifically for {target_platform}'s viewer scroll behavior and attention patterns]

REPURPOSED CTA:
[Call to action that fits {target_platform}'s specific engagement mechanics and what users naturally do on that platform]

ADAPTATION NOTES:
[3 specific observations about what changed and exactly why those changes improve performance on {target_platform}]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# STORYFLOW — STORY GENERATION
# ══════════════════════════════════════════
def generate_story(story_type: str, character: str, duration: int, style: str,
                   platform: str, ending_type: str,
                   custom_character: str = "", custom_story_idea: str = "") -> str:
    char = custom_character if custom_character else character
    idea_ctx = f"\nCustom story idea to incorporate: {custom_story_idea}" if custom_story_idea else ""

    prompt = f"""You are a master viral AI animal story writer specializing in {style}-style animated {platform} videos.

Create 3 COMPLETELY DIFFERENT story options for a {duration}-second {story_type} animated video.
Character: {char}
Ending style: {ending_type}{idea_ctx}

For EACH story follow this EXACT structure:

═══════════════════════════════════════════════════════
STORY OPTION [N]
═══════════════════════════════════════════════════════

TITLE: [Catchy viral title]

VIRALITY SCORE: [X/100]
EMOTION SCORE: [X/100]
RETENTION SCORE: [X/100]
HOOK STRENGTH: [X/100]
ESTIMATED WATCH %: [X%]
AI CONFIDENCE: [X%]

LOGLINE: [One sentence that makes someone need to watch this video immediately. No spoilers.]

FULL STORY BREAKDOWN:

HOOK (0-3 seconds):
[Describe the exact opening shot in cinematic detail. What is the camera angle? What is the character doing? What is their expression? What in the environment immediately creates curiosity or emotion? What makes someone stop scrolling?]

GOAL/CURIOSITY (3-8 seconds):
[What does the character want more than anything? Show the moment they see it or decide to pursue it. Describe the visual that makes viewers immediately root for them. What is the camera doing?]

FIRST CONFLICT (8-{duration//3} seconds):
[Describe in cinematic detail what goes wrong in the first attempt. Character reaction shot — what does their face do? Body language? How does the environment interact with them? What makes viewers laugh or feel bad for the character?]

ESCALATION ({duration//3}-{2*duration//3} seconds):
[How does it get worse? Describe the full cause-and-effect chain. Each failure leads naturally to the next. Include the peak funny or emotional moment. Describe character expressions and reactions in full detail.]

TWIST/HELP ({2*duration//3}-{duration-5} seconds):
[The unexpected turn. Who or what helps? What surprising element appears? How does the character react to this unexpected help? Describe the hope and anticipation building.]

PAYOFF ({duration-5}-{duration} seconds):
[The complete {ending_type} ending. Describe the final 5 seconds in full cinematic detail — character expression, body language, environment, lighting, camera pull-back or close-up, the specific emotional peak. What makes viewers say "aww" or burst out laughing?]

ALL SCENE OBJECTS (must ALL be visible in Frame 1):
[List every prop, supporting character, and environment element that appears anywhere in the story. This list is used to plant them all in Frame 1.]

VIRALITY HOOK:
[Why will people share this? What specific emotion does it trigger? What makes someone tag their friend?]

═══════════════════════════════════════════════════════

All 3 stories must have completely different dramatic structures and emotional arcs. Do not repeat similar plots."""

    return safe_generate(prompt)

# ══════════════════════════════════════════
# STORYFLOW — CHARACTER SHEET
# ══════════════════════════════════════════
def generate_character_sheet(character: str, style: str, story_context: str = "") -> str:
    prompt = f"""You are a professional character designer for {style} 3D animation productions.

Create a complete character design package for: {character}
Animation style: {style}
Story context: {story_context if story_context else "Animated short film for social media"}

1. MASTER CHARACTER SHEET PROMPT:
[Write a 180-220 word image generation prompt for a professional character turnaround sheet.
Include highly specific physical features: exact fur/skin color codes if possible, eye shape and color, size proportions, distinguishing features, accessories, and how the design conveys personality.
Structure it as:
"{character} character model sheet, professional animation turnaround, multiple angles.
Top Row (Turnaround Views): Full body, neutral standing pose repeated from: front view, side view left, back view, side view right, three-quarter view.
Bottom Row (Reference Details): A Character Details grid with close-up macro shots of eyes, hands/paws, and key features. A Color Palette box with labeled swatches and specific descriptions. An Expression Reference grid showing 6 distinct facial expressions: Happy, Excited, Sad, Curious, Determined, Surprised.
Art style: {style} 3D animation quality, clean white studio background, warm professional lighting, 4K render quality, high detail, smooth shading.
[Then add all specific character description details here]"]

2. INDIVIDUAL EXPRESSION PROMPTS (for generating separate close-up expression images):
HAPPY: [specific close-up face prompt]
EXCITED: [specific close-up face prompt]
SAD: [specific close-up face prompt]
CURIOUS: [specific close-up face prompt]
DETERMINED: [specific close-up face prompt]
SURPRISED: [specific close-up face prompt]

3. CHARACTER BIBLE:
[200-word description covering: personality traits and how they show physically, signature movement patterns and quirks, what makes them visually memorable and distinct, color theory behind their design, and how their appearance serves the {story_context} story.]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# STORYFLOW — FRAME 1
# ══════════════════════════════════════════
def generate_frame1_prompt(story_summary: str, character: str,
                            scene_objects: str, style: str, platform: str) -> str:
    aspect = "vertical 9:16" if platform in ["Instagram Reels","TikTok","YouTube Shorts"] else "horizontal 16:9"
    prompt = f"""You are a master cinematographer and visual director for {style} animated films.

Create the perfect Frame 1 establishing shot for this story:
STORY: {story_summary}
MAIN CHARACTER: {character}
ALL STORY OBJECTS TO PLANT: {scene_objects}
ANIMATION STYLE: {style}
ASPECT RATIO: {aspect}

FRAME 1 MASTER PROMPT:
[Write a complete 220-260 word image generation prompt.

Start with the character in the foreground — describe their exact position, pose, and starting expression.
Plant EVERY story object from the list somewhere logically in the scene — even background objects.
Establish the camera angle and height that will work for all future story moments.
Set the lighting, time of day, and overall mood.
Describe the full environment in detail.

The prompt must end with: "{style} 3D animation, 4K cinematic quality, {aspect}, professional studio lighting, high detail, sharp focus, clean render"

Structure: [character description and position] [environment description] [object placements and positions] [lighting and mood] [technical specs]]

OBJECT PLACEMENT GUIDE:
[For each story object, describe exactly where it is in the scene and why that placement makes visual sense for the story]

CAMERA SPECIFICATION:
[Camera height: eye-level / low angle / high angle — and why this choice works for the entire story]
[Focal length feel: wide / medium / close — and what this establishes]
[Framing: what the character occupies in frame and how much negative space exists for action]

CONTINUITY ANCHOR LIST:
[List every specific visual element that MUST remain identical across ALL future prompts:
- Camera angle and height
- Character physical appearance
- Each object's exact position
- Light direction and color
- Environment specific details]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# STORYFLOW — PROMPT CHAIN
# Fully flexible: any duration, any segment size
# ══════════════════════════════════════════
def generate_prompt_chain(story_breakdown: str, character: str, scene_objects: str,
                           duration: int, segment_size: int,
                           style: str, platform: str) -> str:
    num_prompts = duration // segment_size
    aspect = "vertical 9:16" if platform in ["Instagram Reels","TikTok","YouTube Shorts"] else "horizontal 16:9"

    prompt = f"""You are a master AI video prompt engineer specializing in {style} animated story continuity.

Create a COMPLETE {num_prompts}-prompt video chain for this story.

STORY: {story_breakdown}
CHARACTER: {character}
ALL SCENE OBJECTS: {scene_objects}
TOTAL DURATION: {duration} seconds
SEGMENTS: {num_prompts} prompts × {segment_size} seconds each
STYLE: {style}
ASPECT RATIO: {aspect}

Generate ALL {num_prompts} prompts. Each prompt must be 200-260 words and describe physical motion in extreme detail — not keywords.

Use EXACTLY this format for each:

═══════════════════════════════════════════════════════
PROMPT [N] of {num_prompts} — [SCENE NAME] ({segment_size} SECONDS)
═══════════════════════════════════════════════════════

STORY BEAT: [What narrative moment does this segment accomplish?]

CONTINUITY LOCK (must match end of previous prompt):
Character position: [exact location in frame]
Character expression: [emotion at start of this clip]
Camera: [angle and height — must match established shot]
Key objects: [where each story object sits]
Lighting: [matches established lighting]

FULL VIDEO PROMPT:
[For PROMPT 1: Begin with "Ultra-cute {style}-quality 3D animated {character}. 4K cinematic quality. {aspect}. One continuous camera shot. No scene changes. No cuts. Same environment throughout. No teleporting. No object spawning."
For PROMPT 2 through {num_prompts}: Begin with "IMPORTANT: Start from the EXACT frame shown in the attached screenshot. Match everything precisely — character appearance, fur color, eye shape, accessories, exact position in frame, expression, camera angle and height, lighting direction and color, all object positions. Continue seamlessly. No cuts. No new objects. No environment changes. Same shot."

Then describe second-by-second physical action in cinematic detail:
0-{segment_size//4}s: [Exact physical action — describe movement, expression change, body language shift, environment interaction. Not "puppy jumps" but "puppy crouches low, hind legs tensing, ears flattening, eyes wide with determination, then pushes off with full force toward the balloon..."]
{segment_size//4}-{segment_size//2}s: [Continue with same specificity]
{segment_size//2}-{3*segment_size//4}s: [Continue with same specificity]
{3*segment_size//4}-{segment_size}s: [Action leading into stable end frame, describe final freeze position clearly]]

END FRAME (for screenshot):
[Describe the exact last frame: character pose, expression, position in frame, all objects visible, stable composition — this is what gets screenshotted for the next prompt]

MOTION PHYSICS:
[Cause → Effect chain for this segment's key actions]

═══════════════════════════════════════════════════════

Generate all {num_prompts} prompts completely. Every prompt ends on a STABLE FRAME.
The final prompt must deliver the complete story payoff in full cinematic detail.
Make each segment feel like a natural continuation — no jarring story jumps."""

    return safe_generate(prompt)