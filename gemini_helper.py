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

This script will be read by a human creator who needs to know EXACTLY what to say and do.
Every section below must be written in plain, complete, natural English sentences —
NEVER write keywords, fragments, labels-only, or bullet-point notes.
Imagine you are handing this to someone who will read it out loud word-for-word on camera.

HOOK (0-3 seconds):
Write the exact sentence the creator should say out loud in the first 3 seconds.
It must be ONE complete, natural spoken sentence that creates curiosity, shock, or a pattern interruption.
Do not write a topic or keyword — write the literal words to speak.

VISUAL DIRECTION FOR HOOK:
In one full sentence, describe what should be shown on screen during the hook (camera angle, action, text overlay).

BODY (3-25 seconds):
Write 6 to 8 numbered lines. Each line must be a COMPLETE spoken sentence the creator says out loud,
written in plain conversational English — not a keyword, not a topic, not a fragment.
Each sentence should be short (under 12 words) but fully formed, and should build the story, deliver value,
or escalate tension. Format like:
1. [complete natural sentence the creator says]
2. [complete natural sentence the creator says]
...continue to 6-8 lines.

CTA (25-30 seconds):
Write ONE complete spoken sentence telling the viewer exactly what to do right now and why
(e.g. follow, comment, save, share) — written as natural dialogue, not an instruction label.

SUGGESTED AUDIO:
Describe in one or two full sentences the music vibe, tempo (BPM), and mood for the background track.

PRODUCTION NOTES:
In 2-3 full sentences, give the creator practical filming tips for this specific script
(pacing, energy, where to pause, what to emphasize).

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
- The SCRIPT section especially must read like real spoken sentences a person can perform immediately —
  absolutely no keyword lists, no single-word lines, no notes-style fragments
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
# VIDEO STORY GENERATOR
# ══════════════════════════════════════════

def generate_video_story(animal: str, story_type: str, duration: int, style: str,
                          platform: str, ending_type: str) -> dict:
    """Generate 3 viral story options for the requested duration."""

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

The story must have enough plot material to sustain a {duration}-second video
broken into multiple sequential clips — make sure GOAL, CONFLICT, ESCALATION, and PAYOFF
each have enough distinct beats to fill that runtime without feeling repetitive.

Make each story distinctly different in structure and emotional arc."""

    stories_raw = safe_generate(story_prompt)

    return {"stories": stories_raw, "raw": stories_raw}


def generate_video_full_package(animal: str, story_title: str, story_logline: str,
                                  story_details: str, style: str, duration: int,
                                  platform: str, clip_length: int = 8) -> dict:
    """Given a selected story, generate the complete production package.

    duration: total video length in seconds. Any positive integer.
    clip_length: length of each individual clip — 8 or 10 seconds.
    num_prompts = duration / clip_length, rounded to nearest whole clip
    (minimum 1). No artificial cap — a 160s video at 8s clips yields 20 prompts,
    at 10s clips yields 16 prompts.
    """

    if clip_length not in (8, 10):
        clip_length = 8

    num_prompts = max(1, round(duration / clip_length))

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
TOTAL VIDEO LENGTH: {duration} seconds across {num_prompts} clips of {clip_length} seconds each

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

    # Generate prompt chain — story beat plan first so long videos stay coherent
    beat_prompt = f"""You are a {style}-style 3D animation story editor.

STORY TITLE: {story_title}
CHARACTER: {animal}
FULL STORY: {story_details}
TOTAL CLIPS: {num_prompts} (each clip is {clip_length} seconds, total runtime {duration} seconds)

Break this story into exactly {num_prompts} sequential narrative beats — one beat per clip —
so the full {duration}-second video tells a complete, well-paced story with rising action,
escalation, and a satisfying ending on the final beat. Avoid repetitive or filler beats.

Format:
BEAT 1: [one sentence describing what happens in this clip]
BEAT 2: [one sentence]
...
BEAT {num_prompts}: [one sentence]"""

    beats_raw = safe_generate(beat_prompt)
    # Parse beats into a list (fallback to empty string per beat if parsing fails)
    beat_lines = []
    for line in beats_raw.splitlines():
        line = line.strip()
        if line.upper().startswith("BEAT"):
            colon_idx = line.find(":")
            if colon_idx != -1:
                beat_lines.append(line[colon_idx+1:].strip())
    while len(beat_lines) < num_prompts:
        beat_lines.append("")

    prompts_output = []
    for i in range(1, num_prompts + 1):
        is_first = (i == 1)
        is_last = (i == num_prompts)
        beat_text = beat_lines[i-1]

        prompt_gen = f"""You are a {style}-style 3D animated video director creating Prompt {i} of {num_prompts} for:

STORY TITLE: {story_title}
CHARACTER: {animal}
FULL STORY: {story_details}
STYLE: {style}
PLATFORM: {platform}
TOTAL PROMPTS: {num_prompts}
THIS PROMPT: {i} of {num_prompts}
CLIP DURATION: {clip_length} seconds
THIS CLIP'S STORY BEAT: {beat_text if beat_text else "Continue the story naturally from the previous clip."}

{"This is PROMPT 1 — Start from the First Frame established earlier." if is_first else f"This is PROMPT {i} — MUST start with: 'IMPORTANT: Start from the exact frame shown in the attached image. Match everything exactly: character appearance, position, expression, camera angle, lighting, environment, all object positions. Continue seamlessly. No cuts. No teleporting. No regeneration.'"}

{"This is the FINAL PROMPT — End with the complete emotional payoff and a perfect, stable, shareable final frame." if is_last else ""}

Write a complete, detailed video generation prompt for this {clip_length}-second clip that includes:

1. OPENING: Exact starting state (character position, expression, environment)
2. TIMELINE BREAKDOWN: Split the {clip_length} seconds into 4 roughly equal segments and describe
   the specific action with physical details happening in each segment.
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
            "beat": beat_text,
            "text": prompt_text
        })

    # Continuity checklist
    continuity_prompt = f"""Create a production continuity checklist for this {style} animated story:
TITLE: {story_title}
CHARACTER: {animal}
{num_prompts} prompts total, {clip_length} seconds each, {duration} seconds total runtime

List 10 specific things the creator must check between every prompt to maintain perfect visual continuity.
Format as a numbered checklist with specific, actionable items — not generic advice."""

    continuity_raw = safe_generate(continuity_prompt)

    return {
        "character_analysis": char_raw,
        "first_frame": frame_raw,
        "beats": beats_raw,
        "prompts": prompts_output,
        "continuity": continuity_raw,
        "num_prompts": num_prompts,
        "clip_length": clip_length,
        "duration": duration
    }