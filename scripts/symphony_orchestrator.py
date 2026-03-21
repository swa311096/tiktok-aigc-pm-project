import os
import json
from enum import Enum
try:
    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Please install the required libraries: pip install openai python-dotenv")
    exit(1)

# =====================================================================
# TikTok Symphony Ads Creative Studio - LLM Workflow Orchestrator
# =====================================================================
# This tool bypasses the 5-second / single-scene limitation of Symphony's 
# generative model by parsing a messy, overarching 30-40s ad vision and 
# orchestrating it into highly optimized, sequential 5-second modules 
# based strictly on Bytedance's official Prompt Guidelines.
# =====================================================================

SYSTEM_PROMPT = """
You are an expert AIGC Prompter explicitly trained on the "TikTok Symphony Image to Video & Text to Video Guide".
Your job is to take a messy, conversational, or lengthy (30-40 second) Ad idea from an advertiser and break it down into a sequence of highly-optimized 5-second generative scene prompts.

CRITICAL TIKTOK SYMPHONY CONSTRAINTS (YOU MUST OBEY THESE):
1. AVOID CONVERSATIONAL PROMPTS: Do not output "Please create..." or "Make it bigger". Directly state what happens.
2. NO GENERATIVE TEXT: Never ask the model to generate text overlays or captions inside the video.
3. VISUALS ONLY (NO AUDIO): Never ask for voiceovers, lipsyncs, or music in the prompt. Describe visuals only.
4. DESCRIBE SCENE, NOT SCRIPT: Focus on visual content, not the dialogue or ad copy (e.g. DO NOT say "A man looking for loans").
5. SINGLE SCENE PER PROMPT: Never use multiple scene transitions within one prompt. Each prompt must output exactly one natural 5-second continuous scene.

ENHANCERS TO INJECT INTO YOUR OUTPUT:
- Character Details: Always describe age, clothing, and facial expressions (e.g., "A young woman wearing a yellow jacket... smiling").
- Setting Details: Always establish lighting, colors, and atmosphere (e.g., "A cozy cafe lit by warm sunlight...").
- Mechanical Action: Break down complex actions into small physical steps (e.g., instead of "open a carton", write "twists open a cardboard milk carton and pours it").
- Camera & Motion: Use precise angles ("frontal shot", "overhead") and movement ("Camera pans right", "camera remains static").
- Cause and Effect: Detail natural reactions (e.g., "The spray covers the dirt and continues to spread").

IMAGE-TO-VIDEO EXCEPTION:
If a segment specifically mentions starting from an uploaded image, DO NOT describe the visual details of the subject again. Only describe the MOTION and CAMERA operation.

OUTPUT FORMAT:
You must return your output strictly in the following JSON format. Break the user's idea into 4 to 8 logical 5-second sequential segments.
{
  "ad_summary": "A 1 sentence overview of the 30-second ad.",
  "segments": [
    {
      "segment_number": 1,
      "estimated_time": "0s - 5s",
      "symphony_optimized_prompt": "A close-up frontal shot of a young woman in a red jacket running on a treadmill in a sunlit gym. The camera remains static as she breathes heavily."
    },
    ...
  ]
}
"""

def generate_symphony_workflow(user_raw_dump: str) -> dict:
    """Takes a messy user idea and orchestrates it into a 5-sec segmented JSON workflow."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable.")

    client = OpenAI(api_key=api_key)
    print(f"Orchestrating raw dump into Symphony prompts... (this takes a few seconds)")

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": f"Here is my raw ad idea. Please orchestrate it:\n{user_raw_dump}"}
        ],
        temperature=0.7
    )
    
    return json.loads(response.choices[0].message.content)

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
        workflow = generate_symphony_workflow(sample_advertiser_dump)
        
        print(f"\n✅ {workflow['ad_summary']}\n")
        print("🚀 SYMPHONY ORCHESTRATED PROMPT SEQUENCE:")
        for seg in workflow["segments"]:
            print(f"\n[Clip {seg['segment_number']} | {seg['estimated_time']}]")
            print(f"Copy/Paste to Symphony: \"{seg['symphony_optimized_prompt']}\"")
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("To test this locally: export OPENAI_API_KEY='your-key' && python symphony_orchestrator.py")
