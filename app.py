import streamlit as st
from PIL import Image, ImageOps
import replicate
import os
import requests
from io import BytesIO
import random
from rembg import remove
from streamlit_lottie import st_lottie

# ==========================================
# 1. PAGE CONFIGURATION & SESSION MEMORY
# ==========================================
st.set_page_config(page_title="PIL | Digital Innovator", layout="wide", initial_sidebar_state="collapsed")

# Cache the Lottie animation for performance
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

if 'final_image' not in st.session_state:
    st.session_state.final_image = None
if 'generation_successful' not in st.session_state:
    st.session_state.generation_successful = False

# ==========================================
# 2. PREMIUM UX STYLING & DYNAMIC ANIMATIONS
# ==========================================
st.markdown("""
<style>
    /* Base Theme & Entry Animation */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .block-container { 
        padding-top: 3rem; padding-bottom: 2rem; max-width: 1200px; 
        animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; 
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulseGlow {
        0% { box-shadow: 0 4px 15px rgba(0, 90, 156, 0.4); }
        50% { box-shadow: 0 4px 25px rgba(0, 115, 230, 0.7); }
        100% { box-shadow: 0 4px 15px rgba(0, 90, 156, 0.4); }
    }

    h1, h2, h3, h4 { color: #ffffff !important; font-family: 'Helvetica Neue', sans-serif; letter-spacing: 0.5px; }
    h1 { border-bottom: 1px solid #30363d; padding-bottom: 15px; margin-bottom: 30px; }

    /* Animated Primary Button */
    div.stButton > button:first-child {
        background-color: #005A9C; color: white; border-radius: 4px; font-weight: 600;
        border: none; padding: 12px 24px; transition: all 0.3s ease-in-out; width: 100%;
        text-transform: uppercase; letter-spacing: 1.5px;
        animation: pulseGlow 3s infinite;
    }
    div.stButton > button:first-child:hover { 
        background-color: #0073e6; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 115, 230, 0.9); 
    }

    /* Download Button */
    div.stDownloadButton > button:first-child {
        background-color: #238636; color: white; border-radius: 4px; font-weight: 600; width: 100%; border: none;
        transition: all 0.2s ease-in-out;
    }
    div.stDownloadButton > button:first-child:hover { background-color: #2ea043; transform: scale(1.02); }

    /* Interactive Images */
    img { border-radius: 6px; border: 1px solid #30363d; transition: all 0.3s ease; }
    img:hover { border-color: #005A9C; box-shadow: 0 0 15px rgba(0, 90, 156, 0.3); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. COMPOSITOR & BRANDING LOGIC
# ==========================================
def execute_studio_compositing(ai_hero_image, background_path):
    """Composites the AI Hero onto static marketing background with logos."""
    transparent_hero = remove(ai_hero_image.convert("RGBA"))
    
    if not os.path.exists(background_path):
        return transparent_hero.convert("RGB")
        
    backdrop = Image.open(background_path).convert("RGBA")
    
    # Scale hero to 85% of background height
    target_height = int(backdrop.height * 0.85)
    ratio = target_height / float(transparent_hero.size[1])
    target_width = int(float(transparent_hero.size[0]) * float(ratio))
    transparent_hero = transparent_hero.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Position hero center-bottom
    x_pos = (backdrop.width - target_width) // 2
    y_pos = backdrop.height - target_height
    backdrop.paste(transparent_hero, (x_pos, y_pos), transparent_hero)
    
    # Stamp Logos (Handles .png requirements)
    token_path, pil_path = "assets/AI token.png", "assets/pil-logo.png"
    try:
        if os.path.exists(token_path):
            tk = Image.open(token_path).convert("RGBA")
            tk_w = int(backdrop.width * 0.12)
            tk_h = int(tk.size[1] * (tk_w / tk.size[0]))
            backdrop.paste(tk.resize((tk_w, tk_h)), (30, 30), tk.resize((tk_w, tk_h)))
        if os.path.exists(pil_path):
            pl = Image.open(pil_path).convert("RGBA")
            pl_w = int(backdrop.width * 0.18)
            pl_h = int(pl.size[1] * (pl_w / pl.size[0]))
            backdrop.paste(pl.resize((pl_w, pl_h)), (backdrop.width - pl_w - 30, backdrop.height - pl_h - 30), pl.resize((pl_w, pl_h)))
    except: pass
    return backdrop.convert("RGB")

bg_inventory = {
    "Vessel Operations (Default)": "assets/background 1.png",
    "Digital Logistics City": "assets/background 2.png",
    "Quantum Tech Hub": "assets/background 3.png",
    "Global Command Deck": "assets/background 4.png",
    "Strategic Port Night": "assets/background 5.png"
}

style_inventory = {
    "Random Regional Aesthetic": "RANDOM",
    "The Vanguard (Techwear)": "wearing sleek modern tactical corporate jacket, glowing blue data nodes, smart-fabric.",
    "The Strategist (Executive Tech)": "wearing authoritative minimalist techwear uniform, holographic logistics accents.",
    "The Phantom (Stealth Innovator)": "wearing matte black modern tactical gear, subtle AI interface visors."
}

# ==========================================
# 4. MAIN USER INTERFACE
# ==========================================
st.title("⚡ DIGITAL INNOVATOR TRANSFORMATION")
st.toast("System Initialized. Identity Mapping Active.", icon="🌐")

l_col, r_col = st.columns([1, 1.2], gap="large")

with l_col:
    st.markdown("### 1. IDENTITY UPLOAD")
    st.caption("Upload a solo portrait. Backgrounds will be neutralized for campaign continuity.")
    uploaded_file = st.file_uploader("Upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        user_image = ImageOps.exif_transpose(Image.open(uploaded_file))
        st.image(user_image, caption="Identity Locked", use_container_width=True)

with r_col:
    st.markdown("### 2. CAMPAIGN PARAMETERS")
    style_name = st.selectbox("Hero Aesthetic:", list(style_inventory.keys()))
    bg_name = st.selectbox("Marketing Backdrop:", list(bg_inventory.keys()))
    
    with st.expander("View Environment Reference"):
        if os.path.exists(bg_inventory[bg_name]):
            st.image(bg_inventory[bg_name], use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 5. EXECUTION ENGINE
    # ==========================================
    if st.button("ASSEMBLE MY AI-VENGER", use_container_width=True):
        if uploaded_file is not None:
            os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
            
            anim_placeholder = st.empty()
            with anim_placeholder.container():
                lottie_url = "https://lottie.host/80a0b986-9dc4-4d16-9ea0-422201977759/hC33x5D0Yj.json"
                st_lottie(load_lottieurl(lottie_url), height=250, key="loader")
            
            with st.status("Executing Studio Compositing...", expanded=True) as status:
                try:
                    # Clean input
                    max_size = 1024
                    if max(user_image.size) > max_size: user_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                    isolated = remove(user_image.convert("RGBA"))
                    white_canvas = Image.new("RGB", isolated.size, (255, 255, 255))
                    white_canvas.paste(isolated, mask=isolated.split()[3])
                    
                    buf = BytesIO()
                    white_canvas.save(buf, format="JPEG", quality=85)
                    buf.seek(0)

                    # AI Generation
                    style_p = style_inventory[style_name]
                    if style_p == "RANDOM": style_p = random.choice([v for k,v in style_inventory.items() if v != "RANDOM"])
                    
                    prompt = f"Cinematic full-body portrait of a person, {style_p} Isolated on a pure solid white background. Photorealistic, corporate photography."
                    output = replicate.run(
                        "zsxkib/instant-id:6af8583c541261472e92155d87bba80d5ad98461665802f2ba196ac099aaedc9",
                        input={"image": buf, "prompt": prompt, "negative_prompt": "messy, room, cyborg, armor", "ip_adapter_scale": 0.85, "controlnet_conditioning_scale": 0.4}
                    )
                    
                    # Composite
                    ai_raw = Image.open(BytesIO(requests.get(output[0]).content))
                    st.session_state.final_image = execute_studio_compositing(ai_raw, bg_inventory[bg_name])
                    st.session_state.generation_successful = True
                    status.update(label="Campaign Asset Created!", state="complete", expanded=False)
                except Exception as e:
                    st.error(f"Error: {e}")
            anim_placeholder.empty()

    if st.session_state.generation_successful and st.session_state.final_image:
        st.image(st.session_state.final_image, use_container_width=True)
        img_buf = BytesIO()
        st.session_state.final_image.save(img_buf, format="PNG")
        st.download_button("⬇️ DOWNLOAD CAMPAIGN ASSET", img_buf.getvalue(), "PIL_Asset.png", "image/png", use_container_width=True)

# ==========================================
# 7. CORPORATE FOOTER
# ==========================================
st.markdown("<br><hr style='border-color: #30363d;'>", unsafe_allow_html=True)
st.caption("DIGITAL INNOVATOR INITIATIVE: Advanced identity-preserving neural transfer with automated brand-fidelity compositing.")
