# How I Built the Symphony Orchestrator
*How I planned, built, debugged, and shipped a working tool over one weekend — using Cursor as my IDE and Gemini as the brain.*

**Project:** [tiktok-aigc-pm-project](https://github.com/swa311096/tiktok-aigc-pm-project)
**Build time:** one weekend (Mar 20–21, 2026), plus a second weekend for the longer writeup
**Tools:** Cursor (agent mode) · Gemini Flash API · Streamlit · git/GitHub

---

## Phase 0 — Finding a problem (the week before)

I was doing a PM teardown of TikTok's Symphony Creative Studio for my portfolio. The model under the hood (ByteDance's Seedance 1.5) is really good — I tested it with a tricky prompt (an Indian teen at USC tilting his head, lowering his gaze, turning his body, and smiling, with a camera pan, all in 5 seconds) and it handled the sequence well.

But the product around the model felt rough. Three things kept tripping me up:

1. **Videos cap at 5 seconds.** A normal TikTok ad is 15–30s. To make one, you split your idea into 6 prompts.
2. **The prompt guide is good, but you have to read it.** Most SMB advertisers won't.
3. **The model has no memory between clips.** "Same character across 6 clips" turns into 6 different people.

The model is fine. The thing missing is a layer between the user and the model. That's a wrapper, not a research project — which felt like something I could actually build in a weekend.

(I'd seen this exact shape at AWS during my internship. Startups bounced off the platform not because AWS was bad but because the on-ramp was steep. Same problem here.)

So my plan: **build a thin layer that takes one messy ad brief and turns it into 6 clean, model-ready 5-second prompts.**

---

## Phase 1 — Setting up the weekend

I gave myself two days. Rules I set up front:

- **No training, no RAG, no infra.** If a system prompt couldn't do it, my plan was wrong.
- **Demo-able by Sunday.** A Streamlit app a non-technical friend could click through, with mock output so I didn't have to hand out my API key.
- **Public repo by Sunday night.** Code + writeup + screenshots, or it doesn't count as shipped.

Choices I made in ~10 minutes and didn't revisit:

| Choice | Pick | Why |
|---|---|---|
| Model | Gemini Flash | Free tier, JSON mode built in, fast. |
| UI | Streamlit | Shortest path from Python to "click here." |
| Output | Strict JSON | If it ever returns prose, the pipeline breaks. |
| Storage | None | Stateless function. No DB needed for an MVP. |

If Gemini's JSON mode hadn't worked I'd have switched to OpenAI. It worked.

---

## Phase 2 — Turning the prompt guide into rules

This was the most useful hour of the weekend, and it wasn't really coding.

I sat with ByteDance's prompt guide and a notebook and pulled out every "the model fails when…" line. Then I turned them into 5 rules I could enforce in a system prompt:

1. **No conversational language** ("Please create…" → just describe the scene)
2. **No text inside the video** (the model can't spell — write "a colorful app icon," not "an app saying GlowUp")
3. **Visuals only** (no audio or voiceover — that's a different tool)
4. **One scene per prompt** (no transitions inside 5 seconds)
5. **One shot per prompt** (the model breaks if asked to do two things)

These five became the spine of the system prompt. I wrote it as a single Python string with `{ad_length}` and `{num_segments}` as the only placeholders. Started at maybe 400 words. By Sunday it was 1,200.

The output schema:

```json
{
  "ad_summary": "A 1-sentence overview.",
  "segments": [
    {
      "segment_number": 1,
      "estimated_time": "0s - 5s",
      "symphony_optimized_prompt": "..."
    }
  ]
}
```

That's the shape Symphony's text-to-video tool needs. If the LLM honors it, the rest is plumbing.

---

## Phase 3 — First build, with Cursor

I opened Cursor in agent mode and asked something like:

> *"Write a single-file Python script that takes a raw ad brief and an `ad_length`, calls Gemini with a system prompt I'll provide, and returns parsed JSON matching this schema. Use `google-generativeai`. Read the API key from `GEMINI_API_KEY`."*

It wrote the file in one shot. I had to push back on two things:

1. **It hardcoded the model name** (`gemini-1.5-flash`). I'd been burned by this before — Google deprecates these. I asked it to call `genai.list_models()`, filter for ones that support `generateContent`, prefer Flash, and fall back to whatever's there. That's lines 71–87 in `scripts/symphony_orchestrator.py`. 15 extra lines, but the script keeps working when 1.5 is gone.
2. **It wrapped the API call in too many try/excepts.** I asked it to let exceptions bubble up so the Streamlit layer could show real error messages.

First run: I fed it the QuickBite food-delivery brief. Got back valid JSON with 6 segments, each ~50 words, each following my 5 rules. Took about an hour to get from blank file to first working output.

Then the harder part started.

---

## Phase 4 — Three rounds of debugging

The orchestrator was producing prompts. The prompts ran fine in Symphony. But when I watched the actual videos, I'd only solved the easy part.

### Round 1 — "Why is the woman a different person in every clip?"

I generated all 6 clips for QuickBite. Stitched them in Symphony's Remix tool. Watched it.

Six different women. Same description in every prompt ("young woman, late 20s, blue sweater, exhausted"), six different faces.

| | |
|---|---|
| **What I saw** | No character continuity across clips |
| **Guess** | "Young woman in blue sweater" matches millions of faces. The model has no reason to pick the same one twice. |
| **Fix** | Lock the face to a celebrity. Added a 6th rule: every prompt must say *"a young woman who looks exactly like Emma Watson…"* |
| **Result** | Faces stayed the same. Felt like I was done. |

(See `assets/iteration1_inconsistent_faces.png` — six clearly different faces.)

### Round 2 — "Faces are locked. Why does her sweater change every clip?"

Re-ran. Watched playback. Faces: locked, same Emma Watson. But:

- Clip 1 — blue fluffy sweater
- Clip 2 — light blue knit
- Clip 3 — navy turtleneck
- Clip 4 — different navy
- Clip 5 — back to fluffy
- Clip 6 — gray cardigan

Also the cardboard moving boxes in the background changed shape and color between clips.

| | |
|---|---|
| **What I saw** | Clothes drifting, props morphing, even with faces locked |
| **Guess** | The celebrity lock pinned the face. Nothing pinned the rest. |
| **Fix** | Two changes. (1) Force the exact same clothing description string into every prompt. (2) Use a different camera angle in each clip. Hunch: prop morphing is most visible when angles match, so changing angles would hide it. |
| **Result** | Clothes held. Backgrounds still drifted a little, but the changing camera angles made it harder to notice. |

The thing I didn't expect: locking the character isn't enough. You have to lock the clothing too, *and* change the camera angle each clip so the model's prop drift gets hidden by intentional shot variety. I wouldn't have guessed that combo without watching the failures.

### Round 3 — Final pass

By round 3 the system prompt had 7 rules (the original 5 plus celebrity-lock and shot-variety). I ran it end-to-end. Output is in `assets/final-output.mp4` — same character, same outfit, different shots, coherent story. Not perfect up close, but good enough for an SMB ad. (See `assets/iteration3_consistent_output.png` for the final grid.)

The pattern I kept hitting: **I couldn't predict either failure from theory.** Both came from generate → watch → notice → patch → re-run. That loop was most of the weekend.

---

## Phase 5 — Shipping (Saturday night → Sunday)

The orchestrator worked. Now I had to make it usable.

- **Streamlit app (`app.py`).** Two inputs (brief + duration), one button, output as code blocks ready to copy-paste. Cursor wrote the layout; I rewrote about half of it because the agent kept reaching for `st.dataframe` when I wanted `st.code`.
- **Demo mode.** I didn't want anyone clicking the link to need a Gemini API key. Added a sidebar toggle that returns fake but realistic output. ~30 lines of code. The app runs end-to-end with zero setup.
- **GitHub push, README, screenshots.** Looking at my commits that night (`d33a329` → `eb721c0`), most of them are me fighting with markdown image paths between `assets/` and `portfolio_articles/assets/`. About 90 minutes of "why isn't this image rendering on GitHub" that had nothing to do with the actual product. Fix: GitHub renders relative paths from the file's location, so I duplicated assets into both folders.

By Sunday night the repo was public, the writeup was up, the demo video was embedded, and the Streamlit app worked from a fresh clone.

---

## What AI tools actually did

**Where Cursor helped:**
- Writing the boring code (Streamlit layout, argparse, the test `__main__` block)
- Writing the model-fallback logic when I described what I wanted
- Catching off-by-one errors in segment counting that I'd have missed
- Drafting README sections quickly

**Where Gemini was the product:**
- Every round of rule-tuning was just editing the system prompt and watching what changed. The model itself does the work.
- I never trained anything. The "intelligence" is the system prompt + JSON schema.

**Where AI tools didn't help:**
- Cursor was useless for the prompt-debugging loop because the only feedback was visual (watching clips). Can't lint a video.
- The agent kept adding defensive try/excepts that would've hidden real errors. I had to keep pushing back.
- Figuring out *which* failure mode was happening each round was 100% me. The agent can't watch a video and notice "her sweater is different in clip 3."

**What I'd do differently:**
- Build the Streamlit app first with mocked output. I built the orchestrator first and integration was a pain at the end.
- Save the system prompt as versioned text files, not a Python string. By round 3 I'd lost track of which version made which screenshot.

---

## What's next

Build this into Symphony itself. User types one brief, the platform breaks it into 6 prompts behind the scenes, generates 6 clips in parallel, drops them on a timeline, runs Remix automatically. End state: brief → 30-second ad in one click, no prompt engineering visible to the user.

The orchestrator I built this weekend is the proof that the wrapper is the missing piece — and that you can prove it without touching the model.
