# Improving TikTok Symphony with LLM Orchestrator


## TL;DR
**Symphony Creative Studio** is TikTok’s answer to leveraging AI to democratize the ad creation process, enabling users to easily build TikTok-native ads. However, the current user experience has friction points: 
1. Generation is limited to only 5-second output videos.
2. Users face a steep learning curve in understanding how to write the right, consistent prompts.
3. Stitching 5-second mini-clips together to form a coherent ad is difficult. 

To solve this, I built an LLM-powered orchestration wrapper (trained on the Bytedance prompt guide) that transforms raw user input into a sequence of actionable 5-second prompts. These prompts can be plugged directly into Symphony to generate a complete end-to-end video ad using text-to-video, remix, and dub solutions. By enforcing strict character and temporal consistency rules, this solution significantly reduces user friction and drives platform adoption, aligning with the long-term goal of inclusive AI-driven solutions.

![Final Output — TikTok Symphony Orchestrated Ad](../assets/final-output.mp4)
*The final end-to-end stitched TikTok ad, produced using the Symphony Orchestrator pipeline.*

---

## 1. Context & The Core Problem
The overarching goal of **Symphony Creative Studio** is to make TikTok ad creation universally accessible through AI. But the reality of the current user experience introduced several pain points:
1. **The 5-Second Limit:** Current models only output 5-second video chunks.
2. **The Prompting Education Gap:** Users don't natively know how to write the highly specific visual prompts required to get good results.
3. **The Cohesion Challenge:** Taking disjointed 5-second clips and forming a single coherent, logical advertisement is daunting.

Even with ByteDance's official prompt guides, there is an underlying expectation that users will invest time to learn prompt engineering, manually break down their complete ad into logical pieces, and painstakingly write prompts for each scene. 

**The Insight:** No matter how novel the technology is, a steep learning curve deters adoption. I experienced this firsthand during my summer internship at AWS, where startups would avoid AWS entirely because the initial learning curve was too steep. The Symphony UX felt like a very similar friction problem.

## 2. The Solution: An LLM-Powered Orchestrator
To solve this, I decided to build an **LLM-powered orchestrated wrapper**. [The open-source code is available on my GitHub repository](#), where the core logic is driven by a rule-based python script (`scripts/symphony_orchestrator.py`). The workflow is simple: users choose their preferred LLM platform (in my case, I chose Gemini), enter their API key directly into the UI along with their raw ad idea, and instantly receive a perfectly structured list of 5-second generative prompts.

![Symphony Orchestrator Prompt Generator Demo](../assets/symphony_orchestrator_demo.webp)
*Demo of the Orchestrator turning a raw idea into sequential Symphony-optimized prompts.* 

The underlying logic was built by extracting best practices from the official ByteDance prompt guidelines, and iteratively enforcing new rules to handle prominent edge cases (like character morphing and clothing inconsistency).

### End-to-End User Flow
1. **Input:** The orchestrator takes the user’s raw, messy ad content draft and their desired total ad duration (e.g., 30 seconds).
2. **Transformation:** The LLM breaks the raw idea down logically into $n$ number of highly-optimized 5-second prompt blocks.
3. **Execution:** These $n$ prompts are fed into TikTok Symphony (Text-to-Video) to generate $n$ separate 5-second video clips.
4. **Finalization:** Using TikTok Symphony Studio’s native **Remix** tool, the generated clips are uploaded together and mixed into a polished, end-to-end TikTok-ready ad output.

![Remix Finalization Step — Combining Clips into End-to-End Ad](../assets/remix_finalization_step.png)
*Using TikTok Symphony’s Remix feature to stitch the individual 5-second clips into a complete, coherent ad.*

---

## 3. Iterative Development & Engineering the Rules

### The Initial Rule Set
To transform a raw prompt into Symphony-ready lines, I established these base constraints:
1. **AVOID CONVERSATIONAL PROMPTS:** Directly state what happens. (No "Please create...").
2. **NO GENERATIVE TEXT, LOGOS, OR BRAND NAMES:** AIGC models struggle with spelling. Instead of writing "FitPro," say "a colorful fitness app icon." 
3. **VISUALS ONLY (NO AUDIO):** Describe visuals only. No voiceovers or music in the prompt.
4. **DESCRIBE SCENE, NOT SCRIPT:** Focus purely on visual action.
5. **SINGLE SCENE PER PROMPT:** No multiple transitions within one 5-second block.

### Iteration 1: The Raw Test
**Input:** *I need a 30-second ad for a new food delivery app called 'QuickBite'. The ad starts with a tired woman in her late 20s wearing a blue fluffy sweater, sitting on her living room floor surrounded by cardboard moving boxes. She looks super exhausted and hungry. Then she picks up her phone and opens the app... The doorbell rings and she opens the door to hold a huge hot pizza box. End the video with her sitting on the couch happily eating a slice of pizza.*

**The Resulting Output Prompts:**
1. *A low-angle, wide shot of a young woman in her late twenties, wearing a blue fluffy sweater, sitting defeatedly on the floor of an empty room surrounded by stacked, messy cardboard moving boxes. Warm, dim lighting suggests evening. Camera slowly zooms in on her exhausted facial expression.*
2. *A tight close-up shot focusing only on the hands of the young woman in the blue sweater. Her fingers slowly reach for a glowing smartphone lying near a crumpled piece of packing paper. The background is blurred.*
3. *An extreme close-up on the smartphone screen, showing a bright, modern delivery app interface displaying various food icons. The woman's thumb decisively taps a large confirmation button near the bottom of the screen. The screen glows brightly.*
4. *A static frontal shot capturing the young woman in the blue sweater standing up near her apartment door. Her eyes widen slightly in anticipation as she hears a sharp sound from off-camera.*
5. *A medium shot from inside the apartment. The young woman enthusiastically opens the door to reveal a delivery person (only hands visible) handing her a large, steaming, cardboard pizza box. Steam visibly rises from the box.*
6. *A cozy medium shot of the young woman now comfortably seated on a sofa, wearing the blue sweater. She holds an open book in one hand and takes a large, satisfied bite of a pizza slice with the other. Soft ambient lighting illuminates the scene.*

**The Issue:** Symphony Text-to-Video does not retain generated elements across separate prompts. The "young woman in her late twenties" was rendered as a completely different person in every 5-second clip, leading to massive inconsistency.

---

### Iteration 2: Fixing Character Awareness
**Opportunity:** Retain the character's facial elements across the sequential prompts. 
**Fix:** To prevent the AI from generating random faces, I added a rule to lock a reference name. I injected `"a young woman who looks exactly like Emma Watson"` into every prompt.

**The Resulting Output Prompts:**
1. *A medium low-angle shot of a young woman who looks exactly like Emma Watson, wearing a bright blue fluffy sweater, sitting defeatedly on a hardwood floor surrounded by stacked, open cardboard moving boxes. Warm afternoon light streams from a window behind her. The camera slowly zooms in on her tired face.*
2. *An extreme close-up, high-angle shot looking directly down onto the hands of the young woman who looks exactly like Emma Watson. Her fingers hesitantly swipe across a smartphone screen displaying a vibrant, clean interface for a food delivery application.*
3. *A tight close-up shot focusing only on the smartphone screen held by the young woman who looks exactly like Emma Watson. Her thumb taps a large, glowing button on the screen. A subtle, brief animation of food items quickly spinning appears on the screen before the shot cuts.*
4. *A static, wide shot showing the front door of a dimly lit apartment hallway. The young woman who looks exactly like Emma Watson, now looking hopeful, quickly walks from the background into the foreground and pulls the door open.*
5. *An over-the-shoulder shot from behind the young woman who looks exactly like Emma Watson, as she reaches out with both hands to accept a very large, steaming pizza box from an unseen delivery person just outside the frame. Focus is sharp on the embossed texture of the cardboard box.*
6. *A comfortable wide shot of a modern living room with unpacked boxes in the corner. The young woman who looks exactly like Emma Watson is now relaxed on a plush couch, holding a thick hardcover book in one hand and biting joyfully into a large slice of pizza held in the other. Soft interior lighting highlights her contented expression.*

**The Issue:** The physical face became consistent, but because I didn't heavily enforce the clothing alongside the locked face, the AI lost temporal awareness. The clothing changed randomly, and pushing similar camera angles caused the AI to morph the backgrounds poorly.

![Iteration 1 & 2 Output — Inconsistent Character Across Clips](../assets/iteration1_inconsistent_faces.png)
*Even with face-locking attempts, the same character prompt rendered as completely different people across each 5-second clip in TikTok Symphony.*

---

### Iteration 3: The Final Polish (Clothing Lock & Anti-Morphing)
To achieve true temporal consistency, I explicitly isolated character clothing and MECE (Mutually Exclusive, Collectively Exhaustive) scene elements to strictly prevent hallucinations.

**New Enforced Rules:**
> **6. CELEBRITY AND CLOTHING LOCK:** Generative video AI has zero memory between clips. To force perfect facial and outfit consistency, pick a celebrity lookalike AND a specific outfit. You MUST paste this exact combined description into EVERY single prompt.
> 
> **7. SHOT VARIETY (ANTI-MORPHING):** Reusing the exact same camera angle across scenes causes noticeable AI morphing of props. To hide this without breaking the story's location, drastically change the CAMERA ANGLE or SHOT TYPE per clip (Wide Shot -> Extreme Close-Up -> Over-the-shoulder).

**The Winning Output Sequence:**
1. *An extreme wide shot of a young woman who looks exactly like Emma Stone wearing a blue fluffy sweater, sitting on the dusty wooden floor surrounded by stacks of brown cardboard moving boxes in a dimly lit apartment. Camera slowly zooms in on her face showing exhaustion.*
2. *An over-the-shoulder shot behind the young woman who looks exactly like Emma Stone wearing a blue fluffy sweater, as she lifts a smartphone from the floor. The screen displays a colorful food ordering interface icon, not text.*
3. *An extreme close-up shot focusing only on the young woman's fingers who looks exactly like Emma Stone wearing a blue fluffy sweater, tapping a single large button on the phone screen interface. Her eyes widen slightly in anticipation.*
4. *A low-angle shot looking up at a modern wooden front door. A hand wearing a black delivery uniform sleeve briefly knocks, then a doorbell rings. The door handle begins to turn from the outside.*
5. *A medium shot capturing the young woman who looks exactly like Emma Stone wearing a blue fluffy sweater, accepting a very large, steaming cardboard pizza box from an unseen delivery person. Her face shows relief and a slight smile.*
6. *A shallow depth of field close-up shot of the young woman who looks exactly like Emma Stone wearing a blue fluffy sweater, sitting comfortably on a modern couch. She takes a large, satisfying bite of a cheese pizza slice while holding an open paperback book in the other hand. The lighting is warm and cozy.*

![Iteration 3 Final Output — Consistent Character & Clothing Across Clips](../assets/iteration3_consistent_output.png)
*With Celebrity + Clothing Lock and Shot Variety enforced, the same character appears coherently across all 5-second clips.*

---

## 4. Product Trade-offs
To build an effective product workflow, I had to balance technological constraints with a seamless user experience. This required accepting the following trade-offs:

1. **Automation vs. Hyper-Specific Creative Control:** By automatically locking characters and changing shot types to avoid morphing, the Orchestrator dictates some creative decisions (like camera angles) on behalf of the user. **Why it's acceptable:** For SMBs lacking creative resources, generating a cohesive video quickly provides significantly more value than total creative control resulting in a jarring, inconsistent video.
2. **Excluding Text Generation:** AIGC struggles with spelling and graphic overlays. I intentionally blocked the LLM from generating text prompts (e.g., stopping it from rendering a "50% Off" sign in the video). **Why it's acceptable:** Text can (and should) be natively overlaid using the TikTok video editor UI in post-production. The focus of the Orchestrator strictly remains on visual continuity.

---

## 5. Success Metrics (KPIs)
If this Orchestrator were integrated directly into the Symphony Creative Studio, I would track its success and business impact through the following metrics:

1. **Adoption Rate (Core Metric):** The percentage of advertisers who initiate the workflow and publish a final stitched ad vs. abandonment rate, indicating the Orchestrator effectively reduced friction.
2. **Time-to-Publish (Efficiency):** Decrease in the average time taken from entering a raw prompt to generating a ready-to-publish campaign compared to manual scene-by-scene ad creation.
3. **Retention Rate:** Percentage of users who return to specifically use the Orchestrated text-to-video workflow for their next campaign within 30 days.

---

## 6. Results & Future Vision
![Final Output Video](../assets/final-output.mp4)
*The complete end-to-end stitched TikTok ad — generated using the Symphony Orchestrator pipeline.*

The final orchestrated output is remarkably consistent. While the face rendering varies slightly under close scrutiny, the strictly unified clothing and shot variety make differences unnoticeable to the average viewer. Pushing these outputs through Remix, Dub, and the Video Editor results in a highly cohesive ad. 

**The Future Integration:**
Currently, this is a stitched middleware workflow. However, integrating this directly into the platform (where Text-to-Video and Image-to-Video live) would be transformative. A user provides a raw input, the system automatically breaks it down into $n$ micro-prompts behind the scenes, generates the creative videos, and adds them to a timeline one-by-one. 

This creates a seamless user experience with a significantly reduced learning curve. With further iteration, we can bring more improvements to make this truly democratized for users—but this orchestration pipeline is a powerful start!
