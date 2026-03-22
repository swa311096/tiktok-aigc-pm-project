import streamlit as st
import os
import sys

# Add the current directory to path to ensure we can import scripts
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.symphony_orchestrator import generate_symphony_workflow

st.set_page_config(page_title="TikTok Symphony Prompt Generator", page_icon="🎬", layout="centered")

st.title("TikTok Symphony Prompt Generator")
st.markdown("Break down your ad idea into a sequence of highly-optimized 5-second generative scene prompts for TikTok Symphony.")

# Ensure API key is set
api_key = os.environ.get("GEMINI_API_KEY")

with st.sidebar:
    st.header("Settings")
    demo_mode = st.toggle("Enable Demo Mode", value=True, help="Bypass the Gemini API and return mock results. Perfect for presenting the UI without needing API credits!")
    
    user_api_key = st.text_input("Gemini API Key (Optional if set in .env)", value=api_key if api_key else "", type="password", disabled=demo_mode)
    if user_api_key and not demo_mode:
        os.environ["GEMINI_API_KEY"] = user_api_key

if not demo_mode and not os.environ.get("GEMINI_API_KEY"):
    st.warning("⚠️ GEMINI_API_KEY is not set. Please provide it in the sidebar or enable Demo Mode to generate prompts.")

st.markdown("---")

# Input for ad length (min 5s, max 60s, default 30s)
ad_length = st.number_input(
    "1. Target Ad Length (in seconds)", 
    min_value=5, 
    max_value=60, 
    value=30, 
    step=5,
    help="How long should the final ad be? We'll break it down into 5-second segments."
)

# Input for ad description
ad_description = st.text_area(
    "2. Describe your ad idea", 
    placeholder="e.g. I need an ad for a new skincare app. It should start with a girl looking at herself in the bathroom mirror looking super stressed because of acne. She sighs. Then she pulls out her phone and opens the 'GlowUp' app...",
    height=150
)

# Generate Button
if st.button("Generate Prompts", type="primary"):
    if not demo_mode and not os.environ.get("GEMINI_API_KEY"):
        st.error("Please provide your Gemini API key in the sidebar.")
    elif not ad_description.strip():
        st.error("Please provide an ad description.")
    else:
        with st.spinner("Orchestrating raw idea into Symphony prompts..."):
            try:
                if demo_mode:
                    import time
                    time.sleep(1.5) # Simulate processing time
                    num_segments = int(ad_length) // 5
                    workflow = {
                        "ad_summary": f"A {ad_length}-second mock ad demonstrating highly optimized Symphony segments.",
                        "segments": [
                            {
                                "segment_number": i + 1,
                                "estimated_time": f"{i*5}s - {(i+1)*5}s",
                                "symphony_optimized_prompt": f"[DEMO] Scene {i+1}: A well-lit, frontal shot describing action {i+1} for: '{ad_description[:30]}...'. The camera pans smoothly."
                            } for i in range(num_segments)
                        ]
                    }
                else:
                    workflow = generate_symphony_workflow(ad_description, ad_length=int(ad_length))
                
                if demo_mode:
                    st.success("✅ Prompts Generated Successfully! (DEMO MODE)")
                else:
                    st.success("✅ Prompts Generated Successfully!")
                    
                st.subheader(f"Ad Summary: {workflow.get('ad_summary', 'N/A')}")
                
                st.markdown("### 🚀 Symphony Orchestrated Prompt Sequence")
                st.markdown("Copy and paste these directly into TikTok Symphony.")
                
                for seg in workflow.get("segments", []):
                    with st.container():
                        st.markdown(f"**Clip {seg.get('segment_number', '?')} | {seg.get('estimated_time', '?')}**")
                        st.code(seg.get('symphony_optimized_prompt', ''), language="text")
                        
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
