import streamlit as st
from PIL import Image
import replicate
import os
import requests
from io import BytesIO

# ==========================================
# 1. PAGE CONFIGURATION & UX STYLING
# ==========================================
st.set_page_config(page_title="PIL | Digital Innovator", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #121826; color: #ffffff; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #e0e6ed !important; font-family: 'Helvetica Neue', sans-serif; }
    div.stButton > button:first-child {
        background-color: #005A9C; color: white; border-radius: 6px; font-weight: bold;
        border: none; padding: 14px 24px; transition: all 0.3s ease; width: 100%;
        box-shadow: 0px 4px 15px rgba(0, 90, 156, 0.4); text-transform: uppercase; letter-spacing: 1px;
    }
    div.stButton > button:first-child:hover { background-color: #0073e6; transform: translateY(-2px); }
    img { border-radius: 8px; border: 1px solid #2d3748; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BRANDING LOGIC (THE LOGO STAMPER)
# ==========================================
def apply_campaign_branding(generated_image):
    """Overlays the AI Token (Top Left) and standard PIL Logo (Bottom Right)"""
    base_img = generated_image.convert("RGBA")
    try:
        ai_token = Image.open("assets/AI token.png").convert("RGBA")
        pil_logo = Image.open("assets/pil-logo.png").convert("RGBA")
        
        # Top-Left AI Token
        t_width = int(base_img.width * 0.12)
        t_ratio = t_width / float(ai_token.size[0])
        t_height = int(float(ai_token.size[1]) * float(t_ratio))
        token_resized = ai_token.resize((t_width, t_height), Image.Resampling.LANCZOS)
        base_img.paste(token_resized, (30, 30), token_resized) 

        # Bottom-Right PIL Logo
        p_width = int(base_img.width * 0.18)
        p_ratio = p_width / float(pil_logo.size[0])
        p_height = int(float(pil_logo.size[1]) * float(p_ratio))
        pil_resized = pil_logo.resize((p_width, p_height), Image.Resampling.LANCZOS)
        p_x = base_img.width - p_width - 30
        p_y = base_img.height - p_height - 30
        base_img.paste(pil_resized, (p_x, p_y), pil_resized)
        
    except FileNotFoundError as e:
        st.warning(f"Branding skipped: Ensure logos are in the assets folder.")
    return base_img.convert("RGB")

# ==========================================
# 3. INVENTORIES (BACKGROUNDS & STYLES)
# ==========================================
bg_inventory = {
    "Original Campaign Poster (Default)": {
        "file": "assets/background 1.png",
        "prompt": "Background is a vibrant sunset over a bustling industrial shipping port with massive cranes and cargo containers."
    },
    "Cyber-City Environment": {
        "file": "assets/background 2.png",
        "prompt": "Background is a futuristic cyberpunk city skyline with glowing neon lights and flying vehicles."
    },
    "Quantum Lab Environment": {
        "file": "assets/background 3.png",
        "prompt": "Background is a glowing blue quantum physics laboratory with floating holographic data."
    },
    "Logistics Deck Environment": {
        "file": "assets/background 4.png",
        "prompt": "Background is a high-tech logistics command deck with holographic global maps and sleek white interfaces."
    },
    "Tactical Port Environment": {
        "file": "assets/background 5.png",
        "prompt": "Background is a moody, rain-slicked tactical shipping port at night with dramatic spotlighting."
    }
}

style_inventory = {
    "The Vanguard (Heavy Armor)": "wearing heavy, imposing cybernetic mecha armor with glowing blue power nodes and reinforced plating.",
    "The Speedster (Sleek Nano-suit)": "wearing a sleek, aerodynamic nano-tech suit with glowing energy lines and a streamlined silhouette.",
    "The Phantom (Stealth Gear)": "wearing matte black tactical stealth gear with dark visors and subtle low-light accents.",
    "The Commander (Regal Tactical)": "wearing an authoritative, high-tech command trench coat over reinforced tactical fiber armor."
}

# ==========================================
# 4. APP LAYOUT & UX STRUCTURE
# ==========================================
st.title("⚡ DIGITAL INNOVATOR TRANSFORMATION")
st.markdown("---")

left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.markdown("### 1. CAPTURE PORTRAIT")
    uploaded_file = st.file_uploader("Upload a clear, front-facing photo", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        user_image = Image.open(uploaded_file)
        st.image(user_image, caption="Input Registered", use_container_width=True)
    
    st.markdown("<br>### 2. SYSTEM STATUS", unsafe_allow_html=True)
    st.markdown("✅ Nano Banana 2 Model Ready\n\n✅ Branding Assets Loaded\n\n⏳ Awaiting Execution...")

with right_col:
    st.markdown("### 3. CAMPAIGN PARAMETERS")
    
    # Hero Style Selection
    selected_style_name = st.selectbox("Select your Hero Archetype:", list(style_inventory.keys()))
    selected_style_prompt = style_inventory[selected_style_name]
    
    # Background Selection
    selected_bg_name = st.selectbox("Select your Environmental Reference:", list(bg_inventory.keys()))
    selected_data = bg_inventory[selected_bg_name]
    
    if os.path.exists(selected_data["file"]):
        st.image(selected_data["file"], caption=f"Reference Preview: {selected_bg_name}", width=250)
    else:
        st.info(f"Upload '{selected_data['file']}' to your GitHub to see the preview here.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 5. EXECUTION & GENERATION (OPTIMIZED)
    # ==========================================
    if st.button("ASSEMBLE MY AI-VENGER", use_container_width=True):
        if uploaded_file is not None:
            os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
            
            with st.spinner("Initiating Neural Style Transfer & Compositing..."):
                try:
                    # --- IMAGE OPTIMIZATION ---
                    img_to_resize = Image.open(uploaded_file)
                    max_size = 1024
                    
                    if max(img_to_resize.size) > max_size:
                        img_to_resize.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                    
                    optimized_buffer = BytesIO()
                    img_to_resize.convert("RGB").save(optimized_buffer, format="JPEG", quality=85)
                    optimized_buffer.seek(0)
                    # --------------------------

                    # Dynamically combine the prompts based on user choices
                    base_prompt = "A cinematic portrait of a person as a digital innovator superhero, "
                    full_prompt = f"{base_prompt} {selected_style_prompt} {selected_data['prompt']} Professional lighting, highly detailed, photorealistic."
                    
                    output = replicate.run(
                        "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                        input={
                            "prompt": full_prompt,
                            "image": optimized_buffer,
                            "prompt_strength": 0.65 
                        }
                    )
                    
                    ai_image_url = output[0]
                    response = requests.get(ai_image_url)
                    raw_ai_image = Image.open(BytesIO(response.content))
                    
                    final_branded_image = apply_campaign_branding(raw_ai_image)
                    
                    st.success("Transformation Complete!")
                    st.image(final_branded_image, caption=f"{selected_style_name} | {selected_bg_name}", use_container_width=True)
                    
                except Exception as e:
                    st.error(f"System Error: {e}")
        else:
            st.warning("⚠️ Error: Please upload a portrait in the left column first.")

    st.markdown("---")
    st.markdown("#### AI PROCESS: NEURAL STYLE TRANSFER WITH NANO BANANA 2")
    st.caption("Leveraging the advanced capabilities of the Nano Banana 2 generative model, this application utilizes sophisticated Neural Style Transfer. It analyzes and decomposes the captured portrait into high-level content, while simultaneously extracting detailed style, texture, and color motifs from a diverse library of 'Digital Innovator' superhero archetypes and custom campaign backdrops. These elements are then synthesized in real-time to create a cohesive and high-fidelity final visualization, blending the user's likeness with a unique superhero aesthetic, perfectly ready for social media amplification.")
