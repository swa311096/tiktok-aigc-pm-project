import os
import json
from enum import Enum
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()
except ImportError as e:
    print(f"ImportError: {e}")
    print("Please install the required libraries: pip install google-generativeai python-dotenv")
    exit(1)

# =====================================================================
# TikTok Symphony Ads Creative Studio - LLM Workflow Orchestrator
# =====================================================================
# This tool bypasses the 5-second / single-scene limitation of Symphony's 
# generative model by parsing a messy, overarching 30-40s ad vision and 
# orchestrating it into highly optimized, sequential 5-second modules 
# based strictly on Bytedance's official Prompt Guidelines.
# =====================================================================

SYSTEM_PROMPT_TEMPLATE = """
You are an expert AIGC Prompter explicitly trained on the "TikTok Symphony Image to Video & Text to Video Guide".
Your job is to take a messy, conversational, or lengthy ({ad_length} second) Ad idea from an advertiser and break it down into a sequence of highly-optimized 5-second generative scene prompts.

CRITICAL TIKTOK SYMPHONY CONSTRAINTS (YOU MUST OBEY THESE):
1. AVOID CONVERSATIONAL PROMPTS: Do not output "Please create..." or "Make it bigger". Directly state what happens.
2. NO GENERATIVE TEXT, LOGOS, OR BRAND NAMES: Never ask the model to generate text overlays, captions, specific brand names, or logos inside the video. AIGC models struggle with spelling. Instead of "a screen saying 'FitPro'", explicitly write "a screen displaying a colorful fitness app icon." DO NOT include any exact words or letters for the visuals.
3. VISUALS ONLY (NO AUDIO): Never ask for voiceovers, lipsyncs, or music in the prompt. Describe visuals only.
4. DESCRIBE SCENE, NOT SCRIPT: Focus on visual content, not the dialogue or ad copy (e.g. DO NOT say "A man looking for loans").
5. SINGLE SCENE PER PROMPT: Never use multiple scene transitions within one prompt. Each prompt must output exactly one natural 5-second continuous scene.
6. CELEBRITY AND CLOTHING LOCK (FOR CONSISTENCY): Generative video AI has zero memory between clips. To force perfect facial and outfit consistency, pick a famous celebrity lookalike and a specific outfit (e.g., "A young woman who looks exactly like Zendaya wearing a bright red sweater"). You MUST paste this exact same combined face+clothing description into EVERY single prompt. Do not drop the clothing description in later clips.
7. SHOT VARIETY (ANTI-MORPHING): Reusing the exact same camera angle across scenes causes noticeable AI morphing of props. To hide this without breaking the story's location, drastically change the CAMERA ANGLE or SHOT TYPE per clip (e.g., Scene 1: Wide Shot, Scene 2: Extreme Close-Up of the face, Scene 3: Over-the-shoulder). This masks generative inconsistencies.

ENHANCERS TO INJECT INTO YOUR OUTPUT:
- Character Details: Always describe age, clothing, and facial expressions (e.g., "A young woman wearing a yellow jacket... smiling").
- Setting Details: Always establish lighting, colors, and atmosphere (e.g., "A cozy cafe lit by warm sunlight...").
- Mechanical Action: Break down complex actions into small physical steps (e.g., instead of "open a carton", write "twists open a cardboard milk carton and pours it").
- Camera & Motion: Use precise angles ("frontal shot", "overhead") and movement ("Camera pans right", "camera remains static").
- Cause and Effect: Detail natural reactions (e.g., "The spray covers the dirt and continues to spread").

IMAGE-TO-VIDEO EXCEPTION:
If a segment specifically mentions starting from an uploaded image, DO NOT describe the visual details of the subject again. Only describe the MOTION and CAMERA operation.

OUTPUT FORMAT:
You must return your output strictly in the following JSON format. Break the user's idea into exactly {num_segments} logical 5-second sequential segments.
{
  "ad_summary": "A 1 sentence overview of the {ad_length}-second ad.",
  "segments": [
    {
      "segment_number": 1,
      "estimated_time": "0s - 5s",
      "symphony_optimized_prompt": "A close-up frontal shot of a young woman in a red jacket running on a treadmill in a sunlit gym. The camera remains static as she breathes heavily."
    }
  ]
}
"""

def generate_symphony_workflow(user_raw_dump: str, ad_length: int = 30) -> dict:
    """Takes a messy user idea and orchestrates it into a 5-sec segmented JSON workflow."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Please set the GEMINI_API_KEY environment variable.")

    genai.configure(api_key=api_key)
    print(f"Orchestrating raw dump into Symphony prompts... (this takes a few seconds)")

    num_segments = max(1, ad_length // 5)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.replace("{ad_length}", str(ad_length)).replace("{num_segments}", str(num_segments))

    # Dynamically find an available model since older models may be deprecated
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    if not available_models:
        raise ValueError("No generative models found for this API key.")
        
    # Prefer newer versions of flash
    flash_models = [m for m in available_models if 'flash' in m.lower()]
    
    if flash_models:
        # Sort to try and get the latest version (e.g. 2.5, 2.0, 1.5)
        flash_models.sort(reverse=True)
        chosen_model_name = flash_models[0]
    else:
        chosen_model_name = available_models[-1]
        
    print(f"Using model: {chosen_model_name}")

    model = genai.GenerativeModel(
        model_name=chosen_model_name,
        system_instruction=system_prompt.strip(),
        generation_config={"response_mime_type": "application/json"}
    )
    
    response = model.generate_content(f"Here is my raw ad idea. Please orchestrate it:\n{user_raw_dump}")
    
    return json.loads(response.text)

if __name__ == "__main__":
    # Example messy brain dump from an advertiser
    sample_advertiser_dump = """
    "I need a 30 second ad for a new skincare app. It should start with a girl looking at herself in the bathroom mirror looking super stressed because of acne. She sighs. Then she pulls out her phone and opens the 'GlowUp' app. She smiles as she taps on the screen. The screen should say 'AI Dermatologist'. Then I want a cool transition where it shows her face healing like magic. Next scene she is outside walking her dog and radiating confidence in the sun. Put a cool upbeat song in the background and end with the text 'Download GlowUp today'."
    """
    
    print("-" * 60)
    print("USER RAW DUMP:")
    print(sample_advertiser_dump.strip())
    print("-" * 60)
    
    try:
        workflow = generate_symphony_workflow(sample_advertiser_dump, ad_length=30)
        
        print(f"\n✅ {workflow['ad_summary']}\n")
        print("🚀 SYMPHONY ORCHESTRATED PROMPT SEQUENCE:")
        for seg in workflow["segments"]:
            print(f"\n[Clip {seg['segment_number']} | {seg['estimated_time']}]")
            print(f"Copy/Paste to Symphony: \"{seg['symphony_optimized_prompt']}\"")
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("To test this locally: export GEMINI_API_KEY='your-key' && python symphony_orchestrator.py")
