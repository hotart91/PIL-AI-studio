import streamlit as st
from PIL import Image, ImageOps
import replicate
import os
import requests
from io import BytesIO
import random
from rembg import remove # <--- Critical new import

# ==========================================
# 1. PAGE CONFIGURATION & SESSION MEMORY
# ==========================================
st.set_page_config(page_title="PIL | Digital Innovator", layout="wide", initial_sidebar_state="collapsed")

if 'final_image' not in st.session_state:
    st.session_state.final_image = None
if 'generation_successful' not in st.session_state:
    st.session_state.generation_successful = False

# ==========================================
# 2. STUDIO COMPOSITING LOGIC (LOGO MASK FIX)
# ==========================================
def apply_campaign_branding(final_composite_image):
    """Overlays transparent logos with proper masking logic to force transparency."""
    temp_composite = final_composite_image.convert("RGBA")
    
    # Capitalization matters on Linux (Streamlit Cloud)
    token_path, pil_path = "assets/AI token.png", "assets/pil-logo.png"
    
    for path, pos in [(token_path, "TL"), (pil_path, "BR")]:
        if os.path.exists(path):
            logo = Image.open(path).convert("RGBA")
            # We must isolate the alpha channel to use as a dynamic mask
            alpha_mask = logo.split()[3]
            
            # Sizing Logic
            scale = 0.12 if pos == "TL" else 0.18
            nw = int(temp_composite.width * scale)
            nh = int(logo.size[1] * (nw / logo.size[0]))
            
            # Resize the logo and the mask simultaneously
            logo_res = logo.resize((nw, nh), Image.Resampling.LANCZOS)
            alpha_res = alpha_mask.resize((nw, nh), Image.Resampling.LANCZOS)
            
            # Position Logic
            p_x = 30 if pos == "TL" else temp_composite.width - nw - 30
            p_y = 30 if pos == "TL" else temp_composite.width - nh - 30
            
            # THE FIX: Paste using the alpha mask
            temp_composite.paste(logo_res, (p_x, p_y), mask=alpha_res)
            
    return temp_composite.convert("RGB")

def composite_hero_onto_backdrop(transparent_hero_cutout, static_backdrop_path):
    """Logically composites a clean hero onto unmodified background asset."""
    
    # 1. Open the static, brand-accurate background asset
    if not os.path.exists(static_backdrop_path):
        st.warning(f"Backdrop asset not found. Skipping composite workflow.")
        return transparent_hero_cutout.convert("RGB")
        
    backdrop = Image.open(static_backdrop_path).convert("RGBA")
    
    # 2. Natural Positioning Logic
    # Resize hero to fit naturally in the frame (e.g., to ~85% background height)
    target_height = int(backdrop.height * 0.85)
    ratio = target_height / float(transparent_hero_cutout.size[1])
    target_width = int(float(transparent_hero_cutout.size[0]) * float(ratio))
    hero_res = transparent_hero_cutout.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Center hero horizontally, anchor to bottom
    p_x = (backdrop.width - target_width) // 2
    p_y = backdrop.height - target_height
    
    # 3. Paste the clean cutout
    backdrop.paste(hero_res, (p_x, p_y), hero_res)
    
    return backdrop.convert("RGB")

# ==========================================
# 3. INVENTORIES (BACKDROPS ARE NOW FILES)
# ==========================================
bg_inventory = {
    "Original Campaign Poster (Default)": "assets/background 1.png",
    "Cyber-City Environment": "assets/background 2.png",
    "Quantum Lab Environment": "assets/background 3.png",
    "Logistics Deck Environment": "assets/background 4.png",
    "Tactical Port Environment": "assets/background 5.png"
}

style_inventory = {
    "The Vanguard (Heavy Armor)": "wearing heavy, imposing cybernetic mecha armor with glowing blue power nodes and reinforced plating.",
    "The Speedster (Sleek Nano-suit)": "wearing a sleek, aerodynamic nano-tech suit with glowing energy lines and a streamlined silhouette.",
    "The Phantom (Stealth Gear)": "wearing matte black tactical stealth gear with subtle, transparent visors.",
    "The Commander (Regal Tactical)": "wearing an authoritative, high-tech command trench coat over reinforced tactical fiber armor."
}

# ==========================================
# 4. MAIN USER INTERFACE & CX (SIDE-BY-SIDE)
# ==========================================
st.title("⚡ DIGITAL INNOVATOR TRANSFORMATION")
st.toast("UI matrix loaded. Secure connection to AI Studio established.", icon="🌐")

left_col, right_col = st.columns([1, 1.2], gap="large")

with left_col:
    st.markdown("### 1. IDENTITY UPLOAD")
    # Clarified instruction to manage expectations on group shots
    st.caption("For accurate facial mapping and architectural consistency, please provide a tight, solo portrait.")
    uploaded_file = st.file_uploader("Upload Identity", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        raw_user_image = Image.open(uploaded_file)
        # Apply standard EXIF correction automatically
        user_image = ImageOps.exif_transpose(raw_user_image)
        st.image(user_image, caption="Identity Locked", use_container_width=True)

with right_col:
    st.markdown("### 2. CAMPAIGN PARAMETERS")
    selected_style_name = st.selectbox("Hero Archetype Aesthetic:", list(style_inventory.keys()))
    
    selected_bg_name = st.selectbox("Static Marketing Backdrop (Exact Reference):", list(bg_inventory.keys()))
    selected_bg_path = bg_inventory[selected_bg_name]
    
    # Re-integrated the Expandable Element for CX professionalism
    with st.expander("View Exact Backdrop asset", expanded=False):
        if os.path.exists(selected_bg_path):
            st.image(selected_bg_path, use_container_width=True)
        else:
            st.caption(f"Asset file '{selected_bg_path}' not found in 'assets/' folder.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 5. STUDIO COMPOSITING ENGINE
    # ==========================================
    if st.button("ASSEMBLE MY AI-VENGER", use_container_width=True):
        if uploaded_file is not None:
            if "REPLICATE_API_TOKEN" not in st.secrets:
                st.error("Authentication Error: Replicate API Token missing from Streamlit secrets.")
            else:
                os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
                
                lottie_placeholder = st.empty()
                # (You can re-add the Lottie radar here if you still have that logic)

                # Definitive Corporate status console (Rewritten as requested)
                with st.status("Initializing PIL Studio Compositing Pipeline...", expanded=True) as status:
                    try:
                        st.write("1. Subject isolation: neutralizing original environmental noise...")
                        
                        # A. Ensure image isn't too huge for the cloud memory
                        max_sz = 1024
                        if max(user_image.size) > max_sz:
                            user_image.thumbnail((max_sz, max_sz), Image.Resampling.LANCZOS)
                            
                        # B. Use rembg to isolate user from the background/room
                        isolated_subject = remove(user_image.convert("RGBA"))
                        
                        # C. Composite onto a clean white background for the AI to read clearly
                        canvas_img = Image.new("RGB", isolated_subject.size, (255, 255, 255))
                        canvas_img.paste(isolated_subject, mask=isolated_subject.split()[3])
                        
                        optimized_buf = BytesIO()
                        canvas_img.convert("RGB").save(optimized_buf, format="JPEG", quality=85)
                        optimized_buf.seek(0)

                        st.write("2. Neural Identity Mapping: synthesizing techwear aesthetic (solo mode)...")
                        
                        # D. Neural Transfer: Generating clean hero cutouts
                        base_prompt = "A cinematic masterpiece portrait of a solo person as a digital innovator superhero, clear face, "
                        full_prompt = f"{base_prompt} {style_inventory[selected_style_name]} photorealistic, 8k resolution. Solid pure white background."
                        # Strict negative prompt for accuracy
                        negative_prompt = "ugly, deformed, mutated, noisy, blurry, poor quality, bad background, scenic background, multiple people, casual clothes"
                        
                        output = replicate.run(
                            "zsxkib/instant-id:6af8583c541261472e92155d87bba80d5ad98461665802f2ba196ac099aaedc9",
                            input={
                                "image": optimized_buf,
                                "prompt": full_prompt,
                                "negative_prompt": negative_prompt,
                                "ip_adapter_scale": 0.8, # Keeps the face looking EXACTLY like the user
                                "controlnet_conditioning_scale": 0.4 # Allows the AI to replace the original messy clothes with clean armor
                            }
                        )
                        
                        st.write("3. Studio Compositing: mapping hero to static marketing backdrop...")
                        
                        # E. Get the generated AI raw result
                        response = requests.get(output[0])
                        raw_ai_hero = Image.open(BytesIO(response.content))
                        
                        # F. STUDIO MAGIC: Remove background from the AI raw result
                        clean_hero_cutout = remove(raw_ai_hero.convert("RGBA"))
                        
                        # G. STUDIO MAGIC: Composite clean cutout directly onto static background asset
                        final_composite_img = composite_hero_onto_backdrop(clean_hero_cutout, selected_bg_path)
                        
                        st.write("4. Finalizing Assets: applying corporate branding matrices...")
                        # H. Final logic: Apply the now-transparent logos
                        st.session_state.final_image = apply_campaign_branding(final_composite_img)
                        st.session_state.generation_successful = True
                        
                        # Polish complete as requested
                        status.update(label="Campaign Transformation Definitive.", state="complete", expanded=False)
                        
                    except Exception as e:
                        status.update(label="Critical System Error", state="error", expanded=True)
                        st.error(f"Execution failed: {e}")
                        st.session_state.generation_successful = False
                
                lottie_placeholder.empty()
                
        else:
            st.warning("⚠️ Identity Upload required before assembly.")

    # ==========================================
    # 6. RESULT DISPLAY (PNG Focus for asset control)
    # ==========================================
    if st.session_state.generation_successful and st.session_state.final_image is not None:
        st.image(st.session_state.final_image, caption=f"Campaign Asset | Archetype: {selected_style_name} | Environment: {selected_bg_name}", use_container_width=True)
        
        # Prepare strictly as PNG for transparency control on re-use
        out_buf = BytesIO()
        st.session_state.final_image.save(out_buf, format="PNG")
        byte_im = out_buf.getvalue()
        
        st.download_button(
            label="⬇️ DOWNLOAD FINAL CAMPAIGN ASSET",
            data=byte_im,
            file_name="PIL_Digital_Innovator.png",
            mime="image/png",
            use_container_width=True
        )

# ==========================================
# 7. CX Polish: Professional Footer copy rewritten
# ==========================================
st.markdown("<br><hr style='border-color: #30363d;'>", unsafe_allow_html=True)
st.markdown("#### DIGITAL INNOVATOR INITIATIVE")
st.caption("This module utilizing an advanced multi-stage studio compositing pipeline. Subjects are neutralized from environmental noise before undergoing identity-preserving neural transfer. The resulting assets are then digitally composited directly onto official marketing environments to guarantee 100% brand and architectural fidelity, ready for immediate social media amplification.")
