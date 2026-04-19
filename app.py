import streamlit as st
from PIL import Image
import replicate
import os

# 1. Page Configuration
st.set_page_config(page_title="PIL | Digital Innovator", layout="centered")

# 2. Header
st.title("AI-Vengers Assemble")
st.subheader("Transform into a PIL Digital Innovator")

# 3. Inputs
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Portrait", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Original Portrait", use_container_width=True)

with col2:
    bg_option = st.selectbox(
        "Select Campaign Backdrop",
        ("PIL Port Sunset", "Cyber-City Skyline", "Quantum Lab")
    )

st.markdown("---")

# 4. The Transformation Logic
if st.button("ASSEMBLE MY AI-VENGER", use_container_width=True):
    if uploaded_file is not None:
        
        # Grab the secure API key from Streamlit Cloud
        os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
        
        with st.spinner("Executing Neural Style Transfer..."):
            try:
                # The exact prompt instructing the AI
                ai_prompt = "A cinematic portrait of a person as a digital innovator superhero, wearing a high-tech futuristic tactical suit with subtle blue accents. Professional lighting, highly detailed, photorealistic."
                
                # Calling the Replicate API (Using an SDXL Image-to-Image model)
                output = replicate.run(
                    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                    input={
                        "prompt": ai_prompt,
                        "image": uploaded_file,
                        "prompt_strength": 0.65 # Keeps 35% of the original face, 65% AI style
                    }
                )
                
                st.success("Transformation Successful!")
                st.image(output[0], caption=f"Final Result: {bg_option}", use_container_width=True)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload a portrait first.")
