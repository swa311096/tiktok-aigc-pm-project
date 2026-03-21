# AIGC for TikTok Ads: Model Evaluation & Capabilities 📱

**Goal:** Evaluate the capabilities of the top 3 AI Generation Models (Google, OpenAI, ByteDance) specifically through the lens of a **Product Manager for the TikTok Ads Innovation Team**.

This project aims to programmatically and practically test these models to understand how easily they can be integrated into advertiser workflows to generate high-performing TikTok ad creatives (UGC style, dynamic product placements, and trend-focused video).

## 🎯 Approach & Methodology

Instead of general aesthetic tests, this evaluation is strictly focused on **Advertiser Utility**. If a brand wants to use AIGC to build a TikTok campaign, which model serves them best?

### 1. The Models
*   **Google:** Gemini 3 Pro / Imagen 3 / Veo 3.1
*   **OpenAI:** GPT-4o (DALL-E 3) / Sora
*   **ByteDance:** Seedream (Image) / Seedance 2.0 (Video)

### 2. Evaluation Parameters (PM Perspective)

We evaluate generated assets across the following 5 dimensions critical to TikTok Ads:

1.  **Platform Authenticity (UGC Feel):** Does the content look natively shot for TikTok on a smartphone? Or does it look like a highly-polished, sterile stock photo/video?
2.  **Product & Text Adherence:** Can the model accurately render a specific product, maintain brand colors, and flawlessly overlay campaign text (e.g., "50% OFF TODAY") without garbled spelling?
3.  **Temporal Consistency & Motion (Video):** Can it handle fast-paced transitions, trending dance movements, or dynamic product reveals without morphing characters?
4.  **Generation Speed & Cost:** For a high-volume ad ecosystem, how fast is the API response, and what is the cost per generation?
5.  **Safety & Brand Risk:** Does the model adhere to brand safety guidelines? Does it hallucinate inappropriate content or violate IP rules during edge-case prompts?

### 3. Automation Pipeline

To ensure standardized testing, we use a programmatic approach:
1.  Define standardized strict JSON prompts targeting TikTok ad archetypes.
2.  Use a robust Python automation script (`scripts/generate_assets.py`) to call the APIs for Google, OpenAI, and ByteDance simultaneously.
3.  Save the outputs directly to the `outputs/` folder.
4.  Perform automated (via Vision models) and manual qualitative evaluation logged in `evaluations/`.

## 📂 Project Structure

*   `prompts.json`: The core standardized prompts representing TikTok Ad archetypes.
*   `scripts/`: Python scripts for API automation.
*   `outputs/`: Raw AI-generated images and videos from the models.
*   `evaluations/`: The final comparison reports and scoring matrices.
