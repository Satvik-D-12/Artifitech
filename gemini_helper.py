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

Return EXACTLY in this format with NO extra commentary:

==CAPTIONS==

SHORT (under 50 words):
[Write a complete, engaging caption under 50 words with emojis and a CTA question at the end]

MEDIUM (50-100 words):
[Write a complete, engaging caption 50-100 words with emojis, storytelling, and a CTA]

LONG (100-150 words):
[Write a complete, engaging caption 100-150 words with full narrative, emojis, and strong CTA]

==HASHTAGS==

HIGH VOLUME (1M+ posts):
[exactly 10 hashtags separated by spaces]

MEDIUM VOLUME (100K-1M posts):
[exactly 10 hashtags separated by spaces]

NICHE COMMUNITY (under 100K posts):
[exactly 10 hashtags separated by spaces]

==SCRIPT==

HOOK (0-3 seconds):
[Write one powerful, scroll-stopping opening line that creates immediate curiosity or shock]

BODY (3-25 seconds):
[Write 6-8 punchy on-screen text lines, each under 8 words. Each line on its own line. Make them flow as a narrative that builds tension and delivers value.]

CTA (25-30 seconds):
[Write one specific, compelling call to action that drives engagement]

SUGGESTED AUDIO:
[Describe the specific music genre, tempo, mood, and energy that perfectly matches this content]

==THUMBNAIL==

IMAGE PROMPT:
[Write a 60-80 word hyper-specific image generation prompt with lighting, mood, composition, style, and visual details]

STYLE KEYWORDS:
[8 specific style descriptors separated by commas]

COLOR PALETTE:
[4 specific hex color codes with descriptive names, e.g. #ff4b2b Volcanic Red]

Rules:
- Match {tone} tone throughout every section
- Optimize specifically for {platform} algorithm
- Every caption must end with an engaging question or strong CTA
- Script hook must create immediate pattern interrupt
- Hashtag strategy must be layered not all mega-popular
- Be specific, detailed, and professional throughout"""

    raw = safe_generate(prompt)
    return parse_sections(raw)

# ══════════════════════════════════════════
# HOOK IDEAS
# ══════════════════════════════════════════
def generate_hooks(topic: str, niche: str, count: int = 5) -> str:
    prompt = f"""You are a viral content hook specialist with deep knowledge of {niche} content.

Generate {count} different powerful hooks for a {niche} reel about: {topic}

Each hook must be:
- Under 10 words
- Immediately curiosity-triggering
- A completely different psychological style

Format exactly like this with NO extra text:
HOOK 1 (Question): [hook — creates immediate curiosity through a question]
HOOK 2 (Shock): [hook — delivers a shocking or surprising statement]
HOOK 3 (Controversy): [hook — challenges a common belief]
HOOK 4 (Story): [hook — opens a personal story loop]
HOOK 5 (Number): [hook — uses a specific number or statistic]

After each hook add:
WHY IT WORKS: [one sentence explaining the psychological trigger]
BEST FOR: [which platform/audience this hook style dominates]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# CONTENT SERIES
# ══════════════════════════════════════════
def generate_series(topic: str, niche: str, platform: str, num_posts: int = 5) -> str:
    prompt = f"""You are a viral content strategist planning a {num_posts}-post series.

Create a {num_posts}-post content series for a {niche} account on {platform} about: {topic}

Each post builds on the previous — create a journey not random posts.
Make it so viewers NEED to see the next post.

For each post provide:

POST [N]:
ANGLE: [unique angle/perspective that hasn't been covered yet]
HOOK: [opening hook line under 10 words]
CAPTION PREVIEW: [first 2 engaging sentences that pull viewers in]
KEY VALUE: [the main thing viewers learn or feel from this post]
HASHTAG THEME: [4 core hashtags]
BEST DAY: [optimal day to post]
CLIFFHANGER: [how this post teases the next one]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# CAROUSEL
# ══════════════════════════════════════════
def generate_carousel(topic: str, niche: str, platform: str) -> str:
    prompt = f"""You are a carousel content specialist for {platform}.

Create a 7-slide carousel post about: {topic}
Niche: {niche}

For each slide provide full detail:

SLIDE [N]:
HEADLINE: [bold headline under 6 words — make it punch]
BODY TEXT: [2-3 complete sentences of value-packed content that educates or entertains]
VISUAL DIRECTION: [specific design instruction — colors, layout, imagery style]
EMOTION TARGET: [what feeling this slide should create in the viewer]

Rules:
- Slide 1 = pattern interrupt hook that stops the scroll
- Slides 2-6 = escalating value delivery
- Slide 7 = strong CTA with save/share incentive"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# TWITTER/X THREAD
# ══════════════════════════════════════════
def generate_thread(topic: str, niche: str) -> str:
    prompt = f"""You are a viral X/Twitter thread writer specializing in {niche}.

Write a viral 8-tweet thread about: {topic}

Format each tweet with full content:

TWEET 1 (Hook — must make people click "Show more"):
[Complete tweet under 280 chars — use a bold claim or shocking statement]

TWEET 2-7:
[Complete tweets that deliver escalating value, each under 280 chars]
[Use line breaks for readability]
[Include numbers, specifics, and concrete examples]

TWEET 8 (CTA):
[Engagement-driving tweet that asks for replies, retweets, or follows]

Rules:
- Each tweet must standalone AND flow into the next
- Use white space strategically
- Tweet 1 must be a pattern interrupt
- Include 1-2 relevant emojis per tweet max"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# CONTENT REPURPOSER
# ══════════════════════════════════════════
def repurpose_content(original: str, target_platform: str) -> str:
    prompt = f"""You are a content repurposing expert.

Repurpose this content for {target_platform}:

ORIGINAL CONTENT:
{original}

Deeply adapt the tone, length, format, hooks, and style specifically for {target_platform}.
Preserve the core message but make it completely native to the platform.

Output:

REPURPOSED CAPTION:
[Fully written adapted caption with platform-native tone and format]

REPURPOSED HASHTAGS:
[Platform-specific hashtags that perform on {target_platform}]

REPURPOSED HOOK:
[Platform-optimized opening line]

REPURPOSED CTA:
[Platform-appropriate call to action]

ADAPTATION NOTES:
[2-3 sentences explaining what you changed and why for {target_platform}]"""
    return safe_generate(prompt)

# ══════════════════════════════════════════
# STORYFLOW AI — STORY GENERATION
# ══════════════════════════════════════════
def generate_story(
    story_type: str,
    character: str,
    duration: int,
    style: str,
    platform: str,
    ending_type: str,
    custom_character: str = "",
    custom_story_idea: str = ""
) -> str:
    char = custom_character if custom_character else character
    idea_context = f"\nAdditional story idea/context: {custom_story_idea}" if custom_story_idea else ""

    prompt = f"""You are a master viral AI animal story writer specializing in {style}-style animated videos for {platform}.

Create 3 complete story options for a {duration}-second {story_type} {style}-style animated video featuring: {char}
Ending type: {ending_type}{idea_context}

For EACH story option follow this EXACT structure:

═══════════════════════════════════
STORY OPTION [N]
═══════════════════════════════════

TITLE: [Catchy viral title]

VIRALITY SCORE: [X/100]
EMOTION SCORE: [X/100]
RETENTION SCORE: [X/100]
HOOK STRENGTH: [X/100]
ESTIMATED WATCH %: [X%]

LOGLINE: [One sentence that makes someone NEED to watch this]

FULL STORY BREAKDOWN:

HOOK (0-3 seconds):
[Describe exactly what happens visually in these 3 seconds — camera angle, character action, expression, environment detail. Make it grab attention instantly.]

GOAL/CURIOSITY (3-8 seconds):
[Describe exactly what the character wants and why viewers become invested. What visual makes them root for the character?]

FIRST CONFLICT (8-{duration//3} seconds):
[Describe the problem in detail — what goes wrong, character reaction, facial expression, body language, environment interaction]

ESCALATION ({duration//3}-{2*duration//3} seconds):
[Describe how the conflict gets worse — funny or emotional escalation, cause-and-effect chain, character's increasing desperation]

TWIST/HELP ({2*duration//3}-{duration-5} seconds):
[Describe the unexpected turn, helper character arrival, or clever solution — what surprises the viewer]

PAYOFF ({duration-5}-{duration} seconds):
[Describe the {ending_type} ending in detail — exact visuals, character expressions, emotional peak moment]

SCENE OBJECTS (MUST ALL APPEAR IN FRAME 1):
[List every prop, character, and environment element that appears in the story]

VIRALITY HOOK:
[Why will people share this? What emotion or reaction does it trigger?]

AI CONFIDENCE: [X%]

═══════════════════════════════════

Generate all 3 story options following this format exactly.
Make each story completely different in approach.
Option 1 = safe viral formula
Option 2 = unexpected twist approach  
Option 3 = maximum emotional impact"""

    return safe_generate(prompt)

# ══════════════════════════════════════════
# STORYFLOW AI — CHARACTER SHEET
# ══════════════════════════════════════════
def generate_character_sheet(character: str, style: str, story_context: str = "") -> str:
    prompt = f"""You are a professional character designer for {style}-style 3D animation.

Generate a complete character design sheet prompt for: {character}
Animation style: {style}
Story context: {story_context if story_context else "General animated short"}

Provide TWO things:

1. MASTER CHARACTER SHEET PROMPT:
[A complete, detailed image generation prompt (150-200 words) for creating a professional character model sheet.
Include: character description with specific physical details, fur/skin texture, eye color and size, clothing/accessories,
personality conveyed through design, expression range.
Format: "[Character description] character model sheet, animation turnaround, multiple angles.
Top Row: Full body neutral pose from front view, left side view, back view, right side view, and 3/4 view.
Bottom Row: Character details grid with close-up macro shots of key features, color palette swatches with hex codes,
and expressions reference grid showing Happy, Excited, Sad, Curious, Determined, and Surprised faces.
Style: Professional {style} 3D animation character sheet, clean white background, warm studio lighting, 4K quality."]

2. EXPRESSION PROMPTS (generate 6 individual expression prompts):

HAPPY EXPRESSION:
[Prompt for just the character's happy face — specific details about smile, eye shape, cheek position]

EXCITED EXPRESSION:
[Prompt for excited face]

SAD EXPRESSION:
[Prompt for sad face]

CURIOUS EXPRESSION:
[Prompt for curious face]

DETERMINED EXPRESSION:
[Prompt for determined face]

SURPRISED EXPRESSION:
[Prompt for surprised face]

3. CHARACTER BIBLE:
[200-word description of this character's personality, quirks, movement style, and what makes them visually memorable and loveable]"""

    return safe_generate(prompt)

# ══════════════════════════════════════════
# STORYFLOW AI — ENVIRONMENT & FRAME 1
# ══════════════════════════════════════════
def generate_frame1_prompt(
    story_summary: str,
    character: str,
    scene_objects: str,
    style: str,
    platform: str
) -> str:
    prompt = f"""You are a master cinematographer and prompt engineer for {style} 3D animated films.

Create the perfect Frame 1 (establishing shot) prompt for this story:

STORY: {story_summary}
MAIN CHARACTER: {character}
ALL OBJECTS THAT MUST APPEAR: {scene_objects}
ANIMATION STYLE: {style}
ASPECT RATIO: {"9:16 vertical" if platform in ["Instagram Reels","TikTok","YouTube Shorts"] else "16:9 horizontal"}

Generate:

FRAME 1 MASTER PROMPT:
[Write a complete 200-250 word image generation prompt that:
- Establishes the full environment beautifully
- Places the main character in the foreground with their establishing expression
- Plants ALL story objects visibly in the scene (even minor ones)
- Sets the camera angle that will work for the entire story
- Establishes the lighting and mood that matches the story tone
- Uses {style} quality language throughout
- Ends with: "{style}-style 3D animation, 4K cinematic quality, {"vertical 9:16" if platform in ["Instagram Reels","TikTok","YouTube Shorts"] else "horizontal 16:9"}, professional studio lighting, high detail, warm and inviting atmosphere"]

OBJECT PLACEMENT GUIDE:
[Explain exactly where each story object is placed and why it makes sense visually]

CAMERA NOTES:
[Camera height, angle, focal length suggestion, and why this angle works best for the full story]

CONTINUITY CHECKLIST:
[List every element that MUST remain consistent across all future prompts]

ENVIRONMENT CONSISTENCY RULES:
[5 specific rules about what must NEVER change between prompts to maintain visual continuity]"""

    return safe_generate(prompt)

# ══════════════════════════════════════════
# STORYFLOW AI — VIDEO PROMPT CHAIN
# ══════════════════════════════════════════
def generate_prompt_chain(
    story_breakdown: str,
    character: str,
    scene_objects: str,
    duration: int,
    style: str,
    platform: str
) -> str:
    segment_duration = 8
    num_prompts = max(2, duration // segment_duration)
    aspect = "vertical 9:16" if platform in ["Instagram Reels", "TikTok", "YouTube Shorts"] else "horizontal 16:9"

    prompt = f"""You are a master AI video prompt engineer specializing in {style} animated story continuity.

Create a complete {num_prompts}-prompt video chain for this story:

FULL STORY: {story_breakdown}
CHARACTER: {character}
ALL SCENE OBJECTS: {scene_objects}
TOTAL DURATION: {duration} seconds
SEGMENTS: {num_prompts} prompts × {segment_duration} seconds each
STYLE: {style}
ASPECT RATIO: {aspect}

Generate ALL {num_prompts} prompts following this EXACT format:

For PROMPT 1:
═══════════════════════════════════
PROMPT 1 — [SCENE NAME] ({segment_duration} SECONDS)
═══════════════════════════════════

SETUP LINE:
[One sentence describing the starting visual state]

CONTINUITY LOCK:
- Character appearance: [exact description]
- Environment: [exact description]  
- Camera: [exact angle and height]
- Lighting: [exact lighting description]
- All objects: [list with positions]

FULL PROMPT:
[Write the complete video generation prompt — 200-250 words.
Start with: "Ultra-cute {style}-quality 3D animated [character]. 4K cinematic quality. {aspect}. One continuous camera shot. No scene changes. No cuts."
Then describe second-by-second action:
0-2 sec: [exact action]
2-4 sec: [exact action]  
4-6 sec: [exact action]
6-8 sec: [exact action with end frame description]]

END FRAME REQUIREMENT:
[Describe exactly what the LAST FRAME looks like — character pose, expression, position, all objects visible, ready for next prompt]

MOTION PHYSICS:
[Describe the cause→effect chain in this segment]

═══════════════════════════════════

For PROMPTS 2 through {num_prompts}:
Follow the same format BUT add at the top:

CONTINUATION INSTRUCTION:
"IMPORTANT: Start from the EXACT frame shown in the attached screenshot. Match everything: character appearance, position, expression, camera angle, lighting, all object positions. Continue seamlessly. No cuts. No teleporting. No new objects. Same environment throughout."

Generate all {num_prompts} prompts now.
Each prompt must end on a STABLE FRAME (character not mid-air, expression clear, ready for screenshot).
The final prompt must deliver the complete story payoff."""

    return safe_generate(prompt)

# ══════════════════════════════════════════
# STORYFLOW AI — COMPLETE PACKAGE
# ══════════════════════════════════════════
def generate_complete_storyflow(
    story_type: str, character: str, duration: int,
    style: str, platform: str, ending_type: str,
    selected_story_index: int = 0,
    custom_character: str = "", custom_story_idea: str = ""
) -> dict:
    """Generate the complete StoryFlow package for a selected story"""
    char = custom_character if custom_character else character

    story_summary = f"{story_type} {char} story, {duration} seconds, {ending_type} ending"
    scene_objects_prompt = f"""Based on a {story_type} {duration}-second animated story featuring {char} with a {ending_type} ending,
list ALL objects, props, supporting characters, and environment elements needed.
Format as a simple comma-separated list."""

    scene_objects = safe_generate(scene_objects_prompt)

    frame1 = generate_frame1_prompt(story_summary, char, scene_objects, style, platform)
    char_sheet = generate_character_sheet(char, style, story_summary)
    prompt_chain = generate_prompt_chain(story_summary, char, scene_objects, duration, style, platform)

    return {
        "scene_objects": scene_objects,
        "frame1": frame1,
        "character_sheet": char_sheet,
        "prompt_chain": prompt_chain,
    }
