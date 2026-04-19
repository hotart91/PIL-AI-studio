import streamlit as st
import os

# 1. Page config MUST be the very first Streamlit command
st.set_page_config(page_title="PIL | Digital Innovator", layout="wide", initial_sidebar_state="collapsed")

# 2. Wrapped Imports to prevent initialization crashes
try:
    from PIL import Image, ImageOps
    import replicate
    import requests
    from io import BytesIO
    import random
    from rembg import remove
    from streamlit_lottie import st_lottie
except ImportError as e:
    st.error(f"Initialization Error: Missing library {e}. Please check requirements.txt")

# ==========================================
# CORE FUNCTIONS & CACHING
# ==========================================

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

def apply_branding(base_img):
    """Overlays the AI Token and PIL Logo onto the final composite."""
    temp_img = base_img.convert("RGBA")
    tk_p, pl_p = "assets/AI token.png", "assets/pil-logo.png"
    
    for path, pos in [(tk_p, "TL"), (pl_p, "BR")]:
        if os.path.exists(path):
            logo = Image.open(path).convert("RGBA")
            scale = 0.12 if pos == "TL" else 0.18
            nw = int(temp_img.width * scale)
            nh = int(logo.size[1] * (nw / logo.size[0]))
            logo_res = logo.resize((nw, nh), Image.Resampling.LANCZOS)
            coords = (30, 30) if pos == "TL" else (temp_img.width - nw - 30, temp_img.height - nh - 30)
            temp_img.paste(logo_res, coords, logo_res)
    return temp_img.convert("RGB")

# ==========================================
# PREMIUM UX STYLING
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .block-container { padding-top: 2rem; animation: fadeUp 1.2s ease; }
    @keyframes fadeUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    
    h1, h2, h3 { color: #ffffff !important; font-family: 'Helvetica Neue', sans-serif; }
    div.stButton > button:first-child {
        background-color: #005A9C; color: white; border-radius: 4px; font-weight: 600;
        border: none; padding: 12px 24px; width: 100%; text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(0, 90, 156, 0.4);
    }
    div.stButton > button:first-child:hover { background-color: #0073e6; transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# MAIN INTERFACE
# ==========================================
st.title("⚡ DIGITAL INNOVATOR TRANSFORMATION")
st.toast("System Online. Identity Mapping Active.", icon="🌐")

bg_inv = {
    "Vessel Operations (Primary)": "assets/background 1.png",
    "Digital Logistics City": "assets/background 2.png",
    "Quantum Tech Hub": "assets/background 3.png",
    "Global Command Deck": "assets/background 4.png",
    "Strategic Port Night": "assets/background 5.png"
}
styles = {
    "Regional Randomizer": "RANDOM",
    "The Vanguard (Techwear)": "wearing sleek modern tactical corporate jacket, subtle blue tech nodes.",
    "The Strategist (Executive)": "wearing authoritative minimalist techwear uniform, sharp clean lines.",
    "The Phantom (Stealth)": "wearing matte black modern tactical gear, subtle AI visors."
}

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown("### 1. IDENTITY UPLOAD")
    st.caption("Solo portraits are recommended for precise architectural alignment.")
    up_file = st.file_uploader("Upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if up_file:
        input_img = ImageOps.exif_transpose(Image.open(up_file))
        st.image(input_img, caption="Subject Registered", use_container_width=True)

with col2:
    st.markdown("### 2. CAMPAIGN PARAMETERS")
    s_choice = st.selectbox("Archetype:", list(styles.keys()))
    b_choice = st.selectbox("Backdrop:", list(bg_inv.keys()))
    
    if st.button("ASSEMBLE MY AI-VENGER"):
        if up_file:
            if "REPLICATE_API_TOKEN" not in st.secrets:
                st.error("Missing API Token in Secrets.")
            else:
                os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
                
                anim_box = st.empty()
                with anim_box.container():
                    l_data = load_lottieurl("https://lottie.host/80a0b986-9dc4-4d16-9ea0-422201977759/hC33x5D0Yj.json")
                    if l_data: st_lottie(l_data, height=200)

                with st.status("Generating Campaign Asset...") as status:
                    try:
                        st.write("Neutralizing environment...")
                        max_sz = 1024
                        if max(input_img.size) > max_sz: input_img.thumbnail((max_sz, max_sz), Image.Resampling.LANCZOS)
                        iso = remove(input_img.convert("RGBA"))
                        canvas = Image.new("RGB", iso.size, (255, 255, 255))
                        canvas.paste(iso, mask=iso.split()[3])
                        
                        buf = BytesIO()
                        canvas.save(buf, format="JPEG")
                        buf.seek(0)

                        st.write("Mapping identity...")
                        p_style = styles[s_choice]
                        if p_style == "RANDOM":
                            p_style = random.choice([v for k,v in styles.items() if v != "RANDOM"])
                        
                        prompt = f"Full-body portrait, {p_style} Isolated on white background. Photorealistic, 8k."
                        
                        output = replicate.run(
                            "zsxkib/instant-id:6af8583c541261472e92155d87bba80d5ad98461665802f2ba196ac099aaedc9",
                            input={
                                "image": buf, "prompt": prompt, 
                                "negative_prompt": "messy background, room, casual clothes",
                                "ip_adapter_scale": 0.85, "controlnet_conditioning_scale": 0.4
                            }
                        )

                        st.write("Compositing marketing asset...")
                        ai_img = Image.open(BytesIO(requests.get(output[0]).content)).convert("RGBA")
                        hero_no_bg = remove(ai_img)
                        
                        bg_path = bg_inv[b_choice]
                        if os.path.exists(bg_path):
                            final_bg = Image.open(bg_path).convert("RGBA")
                            h_target = int(final_bg.height * 0.85)
                            w_target = int(hero_no_bg.width * (h_target / hero_no_bg.height))
                            hero_final = hero_no_bg.resize((w_target, h_target), Image.Resampling.LANCZOS)
                            final_bg.paste(hero_final, ((final_bg.width - w_target) // 2, final_bg.height - h_target), hero_final)
                            st.session_state.final_image = apply_branding(final_bg)
                        else:
                            st.session_state.final_image = apply_branding(hero_no_bg)

                        st.session_state.generation_successful = True
                        status.update(label="Asset Ready!", state="complete", expanded=False)
                    except Exception as e:
                        st.error(f"Error: {e}")
                anim_box.empty()
        else:
            st.warning("Upload portrait first.")

    if st.session_state.generation_successful and st.session_state.final_image:
        st.image(st.session_state.final_image, use_container_width=True)
        out_buf = BytesIO()
        st.session_state.final_image.save(out_buf, format="PNG")
        st.download_button("⬇️ DOWNLOAD CAMPAIGN ASSET", out_buf.getvalue(), "PIL_Asset.png", "image/png", use_container_width=True)

# ==========================================
# CORPORATE FOOTER
# ==========================================
st.markdown("<br><hr style='border-color: #30363d;'>", unsafe_allow_html=True)
st.markdown("#### DIGITAL INNOVATOR INITIATIVE")
st.caption("Leveraging advanced identity-preserving neural transfer to synthesize high-fidelity visual assets. This system ensures strict brand fidelity by compositing identity-mapped subjects directly onto validated corporate marketing environments.")
