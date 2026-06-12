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
    prompt = f"""You are a world-class viral content strategist and professional scriptwriter.

Generate complete social media content for:
TOPIC: {topic}
NICHE: {niche}
PLATFORM: {platform}
TONE: {tone}

Return EXACTLY in this format:

==CAPTIONS==

SHORT (under 50 words):
[Write a complete, punchy caption under 50 words. Must end with a hook question or CTA.]

MEDIUM (50-100 words):
[Write a full, engaging caption between 50-100 words. Include a story element, value proposition, and end with a CTA.]

LONG (100-150 words):
[Write a rich, detailed caption between 100-150 words. Include context, emotional connection, value, and a strong CTA.]

==HASHTAGS==

HIGH VOLUME (1M+ posts):
[10 hashtags on one line, space-separated]

MEDIUM VOLUME (100K-1M posts):
[10 hashtags on one line, space-separated]

NICHE COMMUNITY (under 100K posts):
[10 hashtags on one line, space-separated]

==SCRIPT==

HOOK (0-3 seconds):
[Write a single powerful, curiosity-driving opening line spoken directly to the viewer. This must create immediate pattern interruption or shock. Write it as actual spoken dialogue, not a keyword.]

BODY (3-25 seconds):
[Write 6-8 complete spoken sentences, each punchy and under 10 words. These should flow naturally as a spoken script — not bullet keywords. Each line should be a complete thought that builds tension, delivers value, or escalates the story. Write them numbered like:
1. [full spoken line]
2. [full spoken line]
...]

CTA (25-30 seconds):
[Write one specific, compelling call-to-action as a full spoken sentence. Tell the viewer exactly what to do and why right now.]

SUGGESTED AUDIO:
[Describe the music vibe, tempo, and specific mood for the background track. Be specific — e.g. "Dark trap beat, 140 BPM, building tension with bass drops at key emotional moments"]

==THUMBNAIL==

IMAGE PROMPT:
[Write a 60-90 word hyper-specific, cinematic image generation prompt. Include subject, action, lighting, camera angle, background, mood, and visual style.]

STYLE KEYWORDS:
[6-8 specific visual style descriptors separated by commas]

COLOR PALETTE:
[3-4 specific hex codes with color names, e.g. #FF4B2B Deep Crimson, #1A1A2E Midnight Navy]

Rules:
- Match {tone} tone throughout every section
- Optimize specifically for {platform} algorithm and audience behavior
- Every caption must feel natural and human — not AI-generated
- Script hook must create immediate curiosity, shock, or pattern interruption
- Script body lines must be actual spoken sentences — not fragment keywords
- Hashtag mix must be strategic: not all mega-popular, spread the range
- Thumbnail prompt must be hyper-specific enough to paste directly into Midjourney or Ideogram"""

    raw = safe_generate(prompt)
    return parse_sections(raw)


# ══════════════════════════════════════════
# HOOK IDEAS
# ══════════════════════════════════════════

def generate_hooks(topic: str, niche: str, count: int = 5) -> str:
    prompt = f"""You are a viral content hook specialist with deep expertise in psychology-driven content.

Generate {count} different powerful opening hooks for a {niche} reel about: {topic}

Each hook must be under 12 words, immediately compelling, and a distinctly different style.
Write each hook as a complete sentence of spoken dialogue — not a keyword or fragment.

Format exactly:
HOOK 1 (Question): [full hook sentence]
HOOK 2 (Shock): [full hook sentence]
HOOK 3 (Controversy): [full hook sentence]
HOOK 4 (Story): [full hook sentence]
HOOK 5 (Number): [full hook sentence]

After each hook, add one line explaining WHY it works psychologically.
WHY: [one sentence explanation]"""
    return safe_generate(prompt)


# ══════════════════════════════════════════
# CONTENT SERIES
# ══════════════════════════════════════════

def generate_series(topic: str, niche: str, platform: str, num_posts: int = 5) -> str:
    prompt = f"""You are a viral content strategist planning a high-retention series.

Create a {num_posts}-post content series for a {niche} account on {platform} about: {topic}

Each post must build curiosity for the next one — like a Netflix series.

For each post provide:
POST [N]:
ANGLE: [unique angle or sub-topic]
HOOK: [full opening line spoken to viewer — not a keyword]
CAPTION PREVIEW: [first 2-3 full sentences of the caption]
HASHTAG THEME: [4 core hashtags most relevant to this specific post]
BEST DAY: [day of week and why]
CLIFFHANGER: [one sentence that makes viewers want to see the next post]"""
    return safe_generate(prompt)


# ══════════════════════════════════════════
# CAROUSEL
# ══════════════════════════════════════════

def generate_carousel(topic: str, niche: str, platform: str) -> str:
    prompt = f"""You are a carousel content specialist who creates high-save, high-share posts.

Create a 7-slide carousel post for {platform} about: {topic}
Niche: {niche}

For each slide:
SLIDE [N]:
HEADLINE: [bold headline under 6 words — punchy and direct]
BODY: [2-3 complete, value-packed sentences. No bullet fragments. Real sentences.]
VISUAL: [specific visual design suggestion with colors and layout]
MICRO-CTA: [one-line action or thought prompt for this slide]

Slide 1 must stop the scroll. Slide 7 must convert viewers to followers or saves.
After all slides, add:
COVER DESIGN: [detailed visual description of the cover slide]
CAPTION: [full 3-sentence caption for the carousel post]"""
    return safe_generate(prompt)


# ══════════════════════════════════════════
# TWITTER/X THREAD
# ══════════════════════════════════════════

def generate_thread(topic: str, niche: str) -> str:
    prompt = f"""You are a viral X/Twitter thread writer who consistently hits 1M+ impressions.

Write a viral 8-tweet thread about: {topic}
Niche: {niche}

Rules:
- Every tweet must be a complete, engaging thought under 280 characters
- Tweet 1 must make someone stop scrolling instantly
- Each tweet must naturally lead to the next
- Tweets 2-7 must deliver real, specific value
- Tweet 8 must drive follows, bookmarks, or replies

Format:
TWEET 1 (Hook): [tweet — under 280 chars]
TWEET 2: [tweet]
TWEET 3: [tweet]
TWEET 4: [tweet]
TWEET 5: [tweet]
TWEET 6: [tweet]
TWEET 7: [tweet]
TWEET 8 (CTA): [engagement CTA tweet]

After the thread, add:
THREAD TITLE: [what to call this thread for saving]
BEST TIME TO POST: [day and time with reason]"""
    return safe_generate(prompt)


# ══════════════════════════════════════════
# CONTENT REPURPOSER
# ══════════════════════════════════════════

def repurpose_content(original: str, target_platform: str) -> str:
    prompt = f"""You are a content repurposing expert who understands each platform's unique algorithm and culture.

Repurpose this content for {target_platform}:

ORIGINAL CONTENT:
{original}

Analyze the core message and value, then rewrite it natively for {target_platform}.

Output:
REPURPOSED CAPTION:
[Full caption rewritten specifically for {target_platform}'s culture, tone, and character limits. Not a simple edit — a complete native rewrite.]

REPURPOSED HASHTAGS:
[10 hashtags optimized specifically for {target_platform}'s tagging culture]

REPURPOSED HOOK:
[Opening line rewritten for {target_platform}'s specific viewer behavior and scroll patterns]

REPURPOSED CTA:
[Platform-appropriate call to action that fits {target_platform}'s engagement mechanics]

PLATFORM NOTES:
[3 specific observations about how this content was adapted and why those changes help performance on {target_platform}]"""
    return safe_generate(prompt)


# ══════════════════════════════════════════
# VIDEO STORY GENERATOR (NEW)
# ══════════════════════════════════════════

def generate_video_story(animal: str, story_type: str, duration: int, style: str,
                          platform: str, ending_type: str) -> dict:
    """Generate complete video story workflow including story options, character sheets,
    environment analysis, first frame prompt, and full prompt chain."""

    # Step 1: Generate 3 story options
    story_prompt = f"""You are a world-class viral AI animal video story creator specializing in {style}-style animated short films.

Generate 3 different viral story options for:
- Character: {animal}
- Story Type: {story_type}
- Duration: {duration} seconds
- Style: {style}
- Platform: {platform}
- Ending: {ending_type}

For EACH story option, provide:

STORY [N]:
TITLE: [catchy title]
LOGLINE: [one sentence summary]
HOOK (0-3 sec): [exactly what happens in first 3 seconds to stop scrolling]
GOAL: [what does the character want?]
CONFLICT: [what obstacle stands in the way?]
ESCALATION: [how does it get worse or more tense?]
PAYOFF: [the emotional or funny resolution]
ENDING: [the final {ending_type} moment — be specific]
VIRALITY SCORE: [1-100]
EMOTION SCORE: [1-100]
RETENTION SCORE: [1-100]
ESTIMATED WATCH %: [percentage]
WHY IT WORKS: [2 sentences on the psychological hooks that make this viral]

Make each story distinctly different in structure and emotional arc."""

    stories_raw = safe_generate(story_prompt)

    return {"stories": stories_raw, "raw": stories_raw}


def generate_video_full_package(animal: str, story_title: str, story_logline: str,
                                  story_details: str, style: str, duration: int,
                                  platform: str) -> dict:
    """Given a selected story, generate the complete production package."""

    # Calculate number of prompts
    clip_duration = 8
    num_prompts = max(1, round(duration / clip_duration))

    # Character analysis
    char_prompt = f"""You are a {style}-style 3D animation character designer.

For this story:
TITLE: {story_title}
STORY: {story_details}
MAIN CHARACTER: {animal}

Extract ALL characters and objects needed for the complete story.

OUTPUT FORMAT:
CHARACTERS:
[list every character that appears, one per line]

STORY OBJECTS (props):
[list every important prop/object, one per line]

ENVIRONMENT ELEMENTS:
[list every environment component, one per line]

CHARACTER SHEET PROMPT for {animal}:
[Write a complete, detailed character design prompt for {animal} in {style} style.
Include: fur/skin color, eye shape/color, distinguishing features, accessories, personality conveyed through design.
Format as: "{animal} character model sheet, animation turnaround, multiple angles.
Top Row (Turnaround Views): Full body, neutral standing pose, repeating from different angles including front view, side view (left), back view, side view (right), and a top-down view.
Bottom Row (Character Details & Expressions): A Character Details grid showcasing close-up macro shots of specific features. A Color Palette & Texture box with clean color swatches. An Expressions Reference grid showing 6 expressions: Happy, Excited, Sad, Curious, Determined, Surprised.
Style: Professional 3D animation character sheet, smooth {style}-style 3D render, high detail, 4K quality, warm studio lighting, clean neutral background. [specific character description here]"]"""

    char_raw = safe_generate(char_prompt)

    # First frame
    frame_prompt = f"""You are a {style}-style cinematic 3D animation director of photography.

Create the MASTER FIRST FRAME prompt for this story:
TITLE: {story_title}
CHARACTER: {animal}
STORY: {story_details}
STYLE: {style}
PLATFORM: {platform} (vertical 9:16)

The first frame must:
1. Establish the entire environment
2. Show ALL story-important objects visually pre-planted (balloon stuck in tree, box nearby, mud puddle, bird on branch — adapt to this story)
3. Set the camera angle that will be maintained throughout
4. Introduce the character with their emotional starting state
5. Create immediate visual storytelling

Write a complete, detailed image generation prompt (150-200 words) that covers:
- Character position, expression, and body language
- Complete environment with ALL future props already visible
- Lighting and time of day
- Camera position and angle (this MUST be maintained in all future prompts)
- Mood and atmosphere
- Technical specs: {style}-quality 3D animation, 4K, vertical 9:16, cinematic

FIRST FRAME PROMPT:
[full detailed prompt here]

CONTINUITY NOTES:
[List 5-8 specific visual anchors that MUST remain consistent in every prompt: object positions, camera angle, lighting, etc.]"""

    frame_raw = safe_generate(frame_prompt)

    # Generate prompt chain
    prompts_output = []
    for i in range(1, num_prompts + 1):
        is_first = (i == 1)
        is_last = (i == num_prompts)

        prompt_gen = f"""You are a {style}-style 3D animated video director creating Prompt {i} of {num_prompts} for:

STORY TITLE: {story_title}
CHARACTER: {animal}
FULL STORY: {story_details}
STYLE: {style}
PLATFORM: {platform}
TOTAL PROMPTS: {num_prompts}
THIS PROMPT: {i} of {num_prompts}
CLIP DURATION: 8 seconds

{"This is PROMPT 1 — Start from the First Frame established earlier." if is_first else f"This is PROMPT {i} — MUST start with: 'IMPORTANT: Start from the exact frame shown in the attached image. Match everything exactly: character appearance, position, expression, camera angle, lighting, environment, all object positions. Continue seamlessly. No cuts. No teleporting. No regeneration.'"}

{"This is the FINAL PROMPT — End with the complete emotional payoff and a perfect, stable, shareable final frame." if is_last else ""}

Write a complete, detailed video generation prompt for this 8-second clip that includes:

1. OPENING: Exact starting state (character position, expression, environment)
2. TIMELINE BREAKDOWN:
   0-2 sec: [specific action with physical details]
   2-4 sec: [specific action with physical details]  
   4-6 sec: [specific action with physical details]
   6-8 sec: [specific action leading to end frame]
3. MOTION PHYSICS: Describe how movements feel (weight, speed, bounce, reaction)
4. FACIAL EXPRESSIONS: Specific emotions at each moment
5. END FRAME REQUIREMENT: Exact final state — stable pose, clear face, ready for next prompt (or final emotional image if last)
6. TECHNICAL: {style}-quality 3D animation, 4K cinematic, vertical 9:16, one continuous shot, no camera cuts

Be extremely specific about physical actions — not "puppy jumps" but "puppy crouches low, pushes off with both hind legs, ears flying up, mouth open in excitement, reaches 60% of the balloon height before gravity pulls it back down."

PROMPT {i}:
[full detailed prompt here]"""

        prompt_text = safe_generate(prompt_gen)
        prompts_output.append({
            "number": i,
            "text": prompt_text
        })

    # Continuity checklist
    continuity_prompt = f"""Create a production continuity checklist for this {style} animated story:
TITLE: {story_title}
CHARACTER: {animal}
{num_prompts} prompts total

List 10 specific things the creator must check between every prompt to maintain perfect visual continuity.
Format as a numbered checklist with specific, actionable items — not generic advice."""

    continuity_raw = safe_generate(continuity_prompt)

    return {
        "character_analysis": char_raw,
        "first_frame": frame_raw,
        "prompts": prompts_output,
        "continuity": continuity_raw,
        "num_prompts": num_prompts
    }