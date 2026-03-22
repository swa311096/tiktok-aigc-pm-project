# TikTok Symphony AIGC — PM Deep Dive & Orchestrator Solution

A product management portfolio project exploring TikTok's **Symphony Creative Studio** — its AIGC capabilities, UX friction points, and a working LLM-powered orchestration solution to solve its core limitations.

---

## Overview

TikTok's Symphony Creative Studio is a powerful suite of AIGC tools for ad creation, but it comes with significant UX friction. This project documents a hands-on PM deep dive into Symphony, identifies its core pain points, and ships a working solution: an **LLM-powered prompt orchestrator** that removes the learning curve and unlocks longer-form ad creation.

---

## Portfolio Articles

### Article 1 — [Deep Dive into Symphony Creative Studio](portfolio_articles/article_02_symphony_creative_studio_generation.md)
A full teardown of Symphony's UX, video generation, and image generation features — covering what works, what breaks, and why. Key topics include:
- UX hierarchy and landing page analysis
- Video generation (Text-to-Video) wins and friction points
- Image generation model selection (Nano Banana vs. Flux Kontext Max)
- Root-cause analysis of platform performance issues (DOM bloat, rendering latency)

### Article 2 — [The Symphony Orchestrator Solution](portfolio_articles/article_5_symphony_orchestrator_solution.md)
Documents the full iterative development of the LLM orchestrator — from problem framing through three prompt engineering iterations to the final working output. Covers:
- The core problem: 5-second limit, prompting education gap, cohesion challenge
- Rule engineering (7 constraints derived from ByteDance's official prompt guide)
- Three iterations of testing: character inconsistency → clothing drift → final consistent output
- Product trade-offs, KPIs, and future integration vision

---

## The Orchestrator — How It Works

The orchestrator (`scripts/symphony_orchestrator.py`) takes a raw, messy ad idea and transforms it into a sequence of perfectly structured 5-second Symphony-ready prompts using Gemini.

**Core rules enforced:**
1. No conversational prompts — describe what happens, not instructions
2. No generative text, logos, or brand names
3. Visuals only — no audio descriptions
4. Single scene per prompt — no multi-step transitions
5. Celebrity + clothing lock — forces character consistency across clips
6. Shot variety (anti-morphing) — alternates camera angles to hide generative drift

### Streamlit App

A web UI (`app.py`) wraps the orchestrator with a clean interface. Supports a **Demo Mode** (no API key needed) and live mode with a Gemini API key.

**Run locally:**

```bash
pip install streamlit google-generativeai python-dotenv

# Option 1: Demo Mode (no API key needed)
streamlit run app.py

# Option 2: Live Mode
export GEMINI_API_KEY="your-key-here"
streamlit run app.py
```

### Run as a Script

```bash
export GEMINI_API_KEY="your-key-here"
python scripts/symphony_orchestrator.py
```

---

## Project Structure

```
tiktok-aigc-pm-project/
├── app.py                          # Streamlit UI for the orchestrator
├── prompts.json                    # Standardized Symphony prompt templates
├── scripts/
│   └── symphony_orchestrator.py   # Core LLM orchestration logic (Gemini)
├── assets/                         # Root-level media assets
│   ├── final-output.mp4
│   ├── iteration1_inconsistent_faces.png
│   ├── iteration2.png
│   ├── iteration3_consistent_output.png
│   ├── remix_finalization_step.png
│   └── symphony_orchestrator_demo.webp
└── portfolio_articles/
    ├── article_02_symphony_creative_studio_generation.md
    ├── article_5_symphony_orchestrator_solution.md
    └── assets/                     # Images and video embedded in articles
```

---

## Key Takeaways (PM Perspective)

- Symphony's underlying ByteDance models (Seedance 1.5) are **world-class** — the friction is entirely UX/workflow, not model capability.
- The 5-second generation limit is a solvable orchestration problem, not a fundamental blocker.
- An LLM middleware layer (like this orchestrator) can bridge the gap between raw advertiser intent and model-ready structured prompts — dramatically reducing time-to-publish and eliminating the prompt engineering learning curve for SMBs.
