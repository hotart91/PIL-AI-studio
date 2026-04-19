import streamlit as st
from PIL import Image, ImageOps
import replicate
import os
import requests
from io import BytesIO
import random

# ==========================================
# 1. PAGE CONFIGURATION & SESSION MEMORY
# ==========================================
st.set_page_config(page_title="PIL | Digital Innovator", layout="wide", initial_sidebar_state="collapsed")

if 'final_image' not in st.session_state:
    st.session_state.final_image = None
if 'generation_successful' not in st.session_state:
    st.session_state.generation_successful = False

# ==========================================
# 2. PREMIUM UX STYLING (CSS)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .block-container { padding-top: 3rem; padding-bottom: 2rem; max-width: 1200px; }
    h1, h2, h3, h4 { color: #ffffff !important; font-family: 'Helvetica Neue', sans-serif; letter-spacing: 0.5px; }
    h1 { border-bottom: 1px solid #30363d; padding-bottom: 15px; margin-bottom: 30px; }
    div.stButton > button:first-child {
        background-color: #005A9C; color: white; border-radius: 4px; font-weight: 600;
        border: none; padding: 12px 24px; transition: all 0.2s ease-in-out; width: 100%;
        text-transform: uppercase; letter-spacing: 1.5px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div.stButton > button:first-child:hover { background-color: #0073e6; transform: translateY(-1px); box-shadow: 0 6px 12px rgba(0,0,0,0.4); }
    div.stDownloadButton > button:first-child {
        background-color: #238636; color: white; border-radius: 4px; font-weight: 600; width: 100%; border: none;
    }
    div.stDownloadButton > button:first-child:hover { background-color: #2ea043; }
    img { border-radius: 6px; border: 1px solid #30363d; }
    .stAlert { border-radius: 4px; border: none; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. BRANDING LOGIC & INVENTORIES
# ==========================================
def apply_campaign_branding(generated_image):
    base_img = generated_image.convert("RGBA")
    token_path, pil_path = "assets/AI token.png", "assets/pil-logo.png"
    
    try:
        if os.path.exists(token_path):
            ai_token = Image.open(token_path).convert("RGBA")
            t_width = int(base_img.width * 0.12)
            t_ratio = t_width / float(ai_token.size[0])
            t_height = int(float(ai_token.size[1]) * float(t_ratio))
            token_resized = ai_token.resize((t_width, t_height), Image.Resampling.LANCZOS)
            base_img.paste(token_resized, (30, 30), token_resized) 

        if os.path.exists(pil_path):
            pil_logo = Image.open(pil_path).convert("RGBA")
            p_width = int(base_img.width * 0.18)
            p_ratio = p_width / float(pil_logo.size[0])
            p_height = int(float(pil_logo.size[1]) * float(p_ratio))
            pil_resized = pil_logo.resize((p_width, p_height), Image.Resampling.LANCZOS)
            p_x, p_y = base_img.width - p_width - 30, base_img.height - p_height - 30
            base_img.paste(pil_resized, (p_x, p_y), pil_resized)
    except Exception:
        pass
    return base_img.convert("RGB")

bg_inventory = {
    "Original Campaign Poster": {"file": "assets/background 1.png", "prompt": "Background is a vibrant sunset over a bustling industrial shipping port with massive cranes and cargo containers."},
    "Cyber-City Environment": {"file": "assets/background 2.png", "prompt": "Background is a futuristic cyberpunk city skyline with glowing neon lights and flying vehicles."},
    "Quantum Lab Environment": {"file": "assets/background 3.png", "prompt": "Background is a glowing blue quantum physics laboratory with floating holographic data."},
    "Logistics Deck Environment": {"file": "assets/background 4.png", "prompt": "Background is a high-tech logistics command deck with holographic global maps and sleek white interfaces."},
    "Tactical Port Environment": {"file": "assets/background 5.png", "prompt": "Background is a moody, rain-slicked tactical shipping port at night with dramatic spotlighting."}
}

style_inventory = {
    "Random Regional Archetype (Surprise Me)": "RANDOM",
    "The Commander (Regal Tactical)": "wearing an authoritative, high-tech command trench coat over reinforced tactical fiber armor.",
    "The Vanguard (Heavy Armor)": "wearing heavy, imposing cybernetic mecha armor with glowing blue power nodes and reinforced plating.",
    "The Speedster (Sleek Nano-suit)": "wearing a sleek, aerodynamic nano-tech suit with glowing energy lines and a streamlined silhouette.",
    "The Phantom (Stealth Gear)": "wearing matte black tactical stealth gear with dark visors and subtle low-light accents."
}

# ==========================================
# 4. MAIN USER INTERFACE
# ==========================================
st.title("⚡ DIGITAL INNOVATOR TRANSFORMATION")

left_col, right_col = st.columns([1, 1.2], gap="large")

with left_col:
    st.markdown("### 1. IDENTITY UPLOAD")
    st.caption("For optimal neural mapping, please provide a solo, front-facing portrait. Group photos may cause identity extraction failures.")
    
    uploaded_file = st.file_uploader("Provide a clear, front-facing portrait", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        raw_user_image = Image.open(uploaded_file)
        user_image = ImageOps.exif_transpose(raw_user_image)
        st.image(user_image, caption="Identity Registered", use_container_width=True)

with right_col:
    st.markdown("### 2. CAMPAIGN PARAMETERS")
    selected_style_name = st.selectbox("Hero Archetype:", list(style_inventory.keys()))
    
    selected_bg_name = st.selectbox("Environmental Reference:", list(bg_inventory.keys()))
    selected_data = bg_inventory[selected_bg_name]
    
    with st.expander("View Environment Reference", expanded=False):
        if os.path.exists(selected_data["file"]):
            st.image(selected_data["file"], use_container_width=True)
        else:
            st.caption(f"Reference image '{selected_data['file']}' not found in assets.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 5. EXECUTION & DYNAMIC STATUS
    # ==========================================
    if st.button("ASSEMBLE MY AI-VENGER", use_container_width=True):
        if uploaded_file is not None:
            os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
            
            with st.status("Initializing PIL AI Engine...", expanded=True) as status:
                try:
                    st.write("Optimizing image payload...")
                    max_size = 1024
                    if max(user_image.size) > max_size:
                        user_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                    
                    optimized_buffer = BytesIO()
                    user_image.convert("RGB").save(optimized_buffer, format="JPEG", quality=85)
                    optimized_buffer.seek(0)

                    st.write("Executing Identity-Preserving Neural Transfer...")
                    
                    # Logic to handle the Random Archetype
                    raw_style_prompt = style_inventory[selected_style_name]
                    if raw_style_prompt == "RANDOM":
                        # Pick a random style excluding the "RANDOM" key
                        actual_style_prompt = random.choice([v for k, v in style_inventory.items() if v != "RANDOM"])
                    else:
                        actual_style_prompt = raw_style_prompt

                    base_prompt = "A masterpiece, cinematic portrait of a solo person as a digital innovator superhero, "
                    full_prompt = f"{base_prompt} {actual_style_prompt} {selected_data['prompt']} Professional studio lighting, highly detailed, photorealistic."
                    negative_prompt = "ugly, deformed, mutated, noisy, blurry, poor quality, bad anatomy, bad background, messy, multiple people, everyday clothes"
                    
                    # API Call with Foolproof Parameters
                    output = replicate.run(
                        "zsxkib/instant-id:6af8583c541261472e92155d87bba80d5ad98461665802f2ba196ac099aaedc9",
                        input={
                            "image": optimized_buffer,
                            "prompt": full_prompt,
                            "negative_prompt": negative_prompt,
                            "ip_adapter_scale": 0.85, # High: keeps the face looking exactly like the user
                            "controlnet_conditioning_scale": 0.4 # Low: allows the AI to completely replace original clothes and background
                        }
                    )
                    
                    st.write("Applying corporate branding matrices...")
                    response = requests.get(output[0])
                    raw_ai_image = Image.open(BytesIO(response.content))
                    
                    st.session_state.final_image = apply_campaign_branding(raw_ai_image)
                    st.session_state.generation_successful = True
                    
                    status.update(label="Transformation Complete!", state="complete", expanded=False)
                    
                except Exception as e:
                    status.update(label="System Error", state="error", expanded=True)
                    st.error(f"Execution failed: {e}")
                    st.session_state.generation_successful = False
        else:
            st.warning("⚠️ Identity Upload required before assembly.")

    # ==========================================
    # 6. RESULT DISPLAY & DOWNLOAD
    # ==========================================
    if st.session_state.generation_successful and st.session_state.final_image is not None:
        st.image(st.session_state.final_image, caption=f"Final Asset: {selected_style_name}", use_container_width=True)
        
        buf = BytesIO()
        st.session_state.final_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="⬇️ DOWNLOAD CAMPAIGN ASSET",
            data=byte_im,
            file_name="PIL_Digital_Innovator.png",
            mime="image/png",
            use_container_width=True
        )

# ==========================================
# 7. PROFESSIONAL CORPORATE FOOTER
# ==========================================
st.markdown("<br><hr style='border-color: #30363d;'>", unsafe_allow_html=True)
st.markdown("#### DIGITAL INNOVATOR INITIATIVE")
st.caption("This module utilizes an advanced identity-preserving neural network designed for commercial operations and logistics professionals. By extracting high-level facial mapping and synthesizing it with custom maritime and cyber-infrastructure environments, the system generates high-fidelity, campaign-ready visual assets. This ensures brand consistency across digital transformation campaigns while maintaining strict architectural continuity within generated environments.")
