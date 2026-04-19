import streamlit as st
from PIL import Image, ImageOps
import replicate
import os
import requests
from io import BytesIO
import random
from streamlit_lottie import st_lottie
from rembg import remove # Used for clean subject isolation

# ==========================================
# 1. PAGE CONFIGURATION & CACHING
# ==========================================
st.set_page_config(page_title="PIL | Digital Innovator", layout="wide", initial_sidebar_state="collapsed")

@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

if 'final_image' not in st.session_state:
    st.session_state.final_image = None
if 'generation_successful' not in st.session_state:
    st.session_state.generation_successful = False

# ==========================================
# 2. BRANDING LOGIC & INVENTORIES
# ==========================================
def apply_branding(base_img):
    """Safely apply logos only if files exist"""
    temp_img = base_img.convert("RGBA")
    
    # Capitalization matters on Linux (Streamlit Cloud)
    token_path, pil_path = "assets/AI token.png", "assets/pil-logo.png"
    
    for path, pos in [(token_path, "TL"), (pil_path, "BR")]:
        if os.path.exists(path):
            logo = Image.open(path).convert("RGBA")
            # We must isolate the alpha channel to use as a dynamic mask
            alpha_mask = logo.split()[3]
            scale = 0.12 if pos == "TL" else 0.18
            nw = int(temp_img.width * scale)
            nh = int(logo.size[1] * (nw / logo.size[0]))
            # Resize the logo AND the mask simultaneously
            logo_res = logo.resize((nw, nh), Image.Resampling.LANCZOS)
            alpha_res = alpha_mask.resize((nw, nh), Image.Resampling.LANCZOS)
            coords = (30, 30) if pos == "TL" else (temp_img.width - nw - 30, temp_img.height - nh - 30)
            # Use alpha_res as the logical 'mask' for perfect transparency
            temp_img.paste(logo_res, coords, mask=alpha_res)
    return temp_img.convert("RGB")

bg_inventory = {
    "Vessel Operations (Default)": {"file": "assets/background 1.png", "prompt": "Background is a vibrant sunset over a bustling industrial shipping port with massive cranes and cargo containers."},
    "Digital Logistics City": {"file": "assets/background 2.png", "prompt": "Background is a futuristic cyberpunk city skyline with glowing neon lights and flying vehicles."},
    "Quantum Tech Hub": {"file": "assets/background 3.png", "prompt": "Background is a glowing blue quantum physics laboratory with floating holographic data."},
    "Global Command Deck": {"file": "assets/background 4.png", "prompt": "Background is a high-tech logistics command deck with holographic global maps and sleek white interfaces."},
    "Strategic Port Night": {"file": "assets/background 5.png", "prompt": "Background is a moody, rain-slicked tactical shipping port at night with dramatic spotlighting."}
}

# Revised Prompts for accurate face preservation and grounded techwear aesthetics
style_inventory = {
    "Regional Randomizer": "RANDOM",
    "The Vanguard (Grounded Techwear)": "accurate photorealistic facial reconstruction, wearing a sleek modern tactical corporate jacket, subtle glowing blue data nodes, uncovered human head.",
    "The Strategist (Executive)": "accurate photorealistic facial reconstruction, wearing an authoritative minimalist techwear uniform, holographic logistics accents, sharp clean lines, uncovered human head.",
    "The Phantom (Stealth Gear)": "accurate photorealistic facial reconstruction, wearing matte black modern tactical gear, subtle low-light AI interface visors (transparent)."
}

# ==========================================
# 3. UI STYLING (Premium Corporate Theme)
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
# 4. MAIN USER INTERFACE
# ==========================================
st.title("⚡ DIGITAL INNOVATOR TRANSFORMATION")
st.toast("System Initialized. UI matrix ready.", icon="🌐")

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown("### 1. IDENTITY UPLOAD")
    # Added crucial instruction for exact face accuracy
    st.caption("For precise facial reconstruction and architectural consistency, please provide a solo, front-facing portrait. Group photos may cause identity distortion.")
    uploaded_file = st.file_uploader("Upload Identity", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        raw_user_image = Image.open(uploaded_file)
        # Apply standard EXIF correction automatically
        user_image = ImageOps.exif_transpose(raw_user_image)
        st.image(user_image, caption="Subject Registered", use_container_width=True)

with col2:
    st.markdown("### 2. CAMPAIGN PARAMETERS")
    selected_style_name = st.selectbox("Hero Aesthetic Archetype:", list(style_inventory.keys()))
    
    selected_bg_name = st.selectbox("Environmental Backdrop:", list(bg_inventory.keys()))
    selected_data = bg_inventory[selected_bg_name]
    
    # 3. Backdrop Preview (UX Fix)
    with st.expander("View Environment Reference", expanded=False):
        if os.path.exists(selected_data["file"]):
            st.image(selected_data["file"], use_container_width=True)
        else:
            st.caption(f"Asset '{selected_data['file']}' not found in 'assets/' folder.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 5. EXECUTION ENGINE (Dynamic Console)
    # ==========================================
    if st.button("ASSEMBLE MY AI-VENGER", use_container_width=True):
        if uploaded_file is not None:
            if "REPLICATE_API_TOKEN" not in st.secrets:
                st.error("Authentication Error: Replicate API Token missing from secrets.")
            else:
                os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
                
                # Dynamic Lottie Loader (replaces clunky static text)
                lottie_placeholder = st.empty()
                with lottie_placeholder.container():
                    lottie_anim = load_lottieurl("https://lottie.host/80a0b986-9dc4-4d16-9ea0-422201977759/hC33x5D0Yj.json")
                    if lottie_anim: st_lottie(lottie_anim, height=200, key="loading_radar")

                # Dynamic Status Console (detailed steps as requested)
                with st.status("Initializing PIL AI Studio Pipeline...", expanded=True) as status:
                    try:
                        st.write("1. Subject isolation: neutralizing original environment...")
                        # 1. Subject Isolation (Using rembg)
                        # Ensure image isn't too huge for the cloud memory
                        max_sz = 1024
                        if max(user_image.size) > max_sz:
                            user_image.thumbnail((max_sz, max_sz), Image.Resampling.LANCZOS)
                            
                        # rembg automatically removes the garden/room background
                        isolated_subject = remove(user_image.convert("RGBA"))
                        
                        # Composite onto a clean white background for the AI to read clearly
                        canvas_img = Image.new("RGB", isolated_subject.size, (255, 255, 255))
                        canvas_img.paste(isolated_subject, mask=isolated_subject.split()[3])
                        
                        optimized_buf = BytesIO()
                        canvas_img.convert("RGB").save(optimized_buf, format="JPEG", quality=85)
                        optimized_buf.seek(0)

                        st.write("2. Neural Identity Mapping: synthesizing techwear aesthetic...")
                        # 2. Neural Transfer
                        # Logic to handle Randomizer choice
                        raw_style_prompt = style_inventory[selected_style_name]
                        if raw_style_prompt == "RANDOM":
                            # We pick a random prompt excluding the "RANDOM" key itself
                            actual_style_prompt = random.choice([v for k, v in style_inventory.items() if v != "RANDOM"])
                        else:
                            actual_style_prompt = raw_style_prompt

                        base_prompt = "A cinematic masterpiece portrait of a solo person as a digital innovator superhero, uncovered human head, "
                        full_prompt = f"{base_prompt} {actual_style_prompt} {selected_data['prompt']} Professional lighting, highly detailed, 8k resolution, photorealistic."
                        
                        # Robust negative prompt to forbid masks and covered faces
                        negative_prompt = "ugly, deformed, mutated, noisy, blurry, poor quality, bad anatomy, helmet, mask, covered face, obscured face, full armor, multiple people, group shot, messy background people"
                        
                        output = replicate.run(
                            "zsxkib/instant-id:6af8583c541261472e92155d87bba80d5ad98461665802f2ba196ac099aaedc9",
                            input={
                                "image": optimized_buf,
                                "prompt": full_prompt,
                                "negative_prompt": negative_prompt,
                                "ip_adapter_scale": 0.8, # Keeps face very accurate to input
                                "controlnet_conditioning_scale": 0.65 # Keeps some pose consistency
                            }
                        )
                        
                        st.write("3. Finalizing Marketing Composite: applying corporate branding...")
                        # 3. Branding
                        response = requests.get(output[0])
                        raw_ai_image = Image.open(BytesIO(response.content))
                        
                        # Apply logic to enforce transparency
                        st.session_state.final_image = apply_branding(raw_ai_image)
                        st.session_state.generation_successful = True
                        
                        status.update(label="Campaign Transformation Complete!", state="complete", expanded=False)
                        
                    except Exception as e:
                        status.update(label="Critical System Error", state="error", expanded=True)
                        st.error(f"Execution failed: {e}")
                        st.session_state.generation_successful = False
                
                # Erase the dynamic loader once complete
                lottie_placeholder.empty()
                
        else:
            st.warning("⚠️ Identity Upload required before assembly.")

    # ==========================================
    # 6. RESULT DISPLAY (UX Polish)
    # ==========================================
    if st.session_state.generation_successful and st.session_state.final_image is not None:
        st.image(st.session_state.final_image, caption=f"Final Asset: {selected_style_name} | {selected_bg_name}", use_container_width=True)
        
        # Prepare PNG download for strict asset control
        out_buf = BytesIO()
        st.session_state.final_image.save(out_buf, format="PNG")
        byte_im = out_buf.getvalue()
        
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
st.caption("This module utilizes advanced identity-preserving neural transfer, neutralizing input environmental noise before synthesizing accurate facial mapping with grounded corporate techwear aesthetics. This ensures brand fidelity by maintaining uncompromised subject identity across validated maritime and digital campaign environments.")
