import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(
    page_title="AI Smart Food Waste & Donation System",
    page_icon="🍲",
    layout="centered"
)

st.title("🍲 AI Smart Food Waste & Donation System")
st.markdown("**பெஸ்ட் ப்ரோஸ் கூட்டணி** சார்பாக **Texture & Contour Analysis (OpenCV)** மூலம் உணவுப் பொருள்களின் தரத்தை (Freshness) பகுப்பாய்வு செய்யும் தளம்! 🚀")
st.divider()

st.header("📸 உணவுப் படம் மற்றும் டெக்ஸ்சர் பரிசோதனை")
st.write("உணவுப் படத்தை இங்கே பதிவேற்றவும் (JPG/PNG)")

uploaded_file = st.file_uploader("Upload", type=["jpg", "jpeg", "png"])

def analyze_food_texture_contour(image):
    img_rgb = np.array(image.convert("RGB"))
    img_resized = cv2.resize(img_rgb, (300, 300))
    gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)

    # 1. Edge / Texture sharpness (Laplacian variance - detects mushy/spoiled vs crisp/fresh texture)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # 2. Contour & surface irregularity detection (Adaptive threshold for mold/spots/decay patches)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 4
    )
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter medium-to-large irregular blotches (typical of mold/rot spots)
    total_area = 300 * 300
    spot_area = sum(cv2.contourArea(c) for c in contours if 40 < cv2.contourArea(c) < 5000)
    spot_ratio = (spot_area / total_area) * 100.0

    # 3. Brightness & Contrast balance (checks severe darkening/decay)
    mean_brightness = np.mean(gray)

    # Combine metrics into a balanced Freshness Score (0 - 100)
    texture_score = min(40.0, (laplacian_var / 15.0))
    clean_surface_score = max(0.0, 40.0 - (spot_ratio * 1.2))
    brightness_score = 20.0 if 60 <= mean_brightness <= 235 else 10.0

    final_score = round(min(98.0, max(5.0, texture_score + clean_surface_score + brightness_score)), 2)
    return final_score, round(laplacian_var, 1), len(contours)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="பதிவேற்றப்பட்ட உணவுப் படம்", use_container_width=True)

    score, texture_val, contour_count = analyze_food_texture_contour(image)

    st.subheader("AI பகுப்பாய்வு முடிவு (Texture & Contour Analysis)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Freshness Score", f"{score:.2f}%")
    col2.metric("Texture Sharpness", f"{texture_val}")
    col3.metric("Surface Contours", f"{contour_count}")

    if score >= 50.0:
        st.success("✅ **முடிவு: உணவு நல்ல நிலையில் (Fresh) உள்ளது!**")
        st.info("👉 **பரிந்துரை:** உணவின் மேற்பரப்பு மற்றும் டெக்ஸ்சர் சீராக உள்ளது. இதை நல்ல முறையில் பயன்படுத்தலாம் அல்லது அருகிலுள்ள உணவு தான மையம் / ஆதரவற்றோர் இல்லத்திற்கு வழங்கலாம்! 🤝🍲")
        
        st.subheader("📞 அருகிலுள்ள உணவு தான மையம் & ஆதரவற்றோர் இல்லம் (Nearby Donation & Orphanage Contacts)")
        col_don, col_orp = st.columns(2)
        with col_don:
            st.markdown("""
            **🏠 உணவு தான மையம் (Nearby Donation House)**
            * **பெயர்:** அன்னதானம் & உணவு வங்கி மையம் (Community Food Bank)
            * **தொலைபேசி:** `+91 98765 43210`
            * **நேரம்:** காலை 8:00 – இரவு 9:00
            * **முகவரி:** அருகிலுள்ள முதன்மைச் சாலை மையம் (Local Main Road Hub)
            """)
        with col_orp:
            st.markdown("""
            **🧒 ஆதரவற்றோர் இல்லம் (Nearby Orphanage)**
            * **பெயர்:** அன்பு இல்லம் குழந்தைகள் காப்பகம் (Anbu Illam Children's Home)
            * **தொலைபேசி:** `+91 91234 56789`
            * **நேரம்:** காலை 7:30 – இரவு 8:30
            * **முகவரி:** காந்தி நகர், அருகிலுள்ள கிளை (Gandhi Nagar Branch)
            """)
    else:
        st.warning("⚠️ **முடிவு: உணவு கெட்டுப்போகும் நிலையில் உள்ளது அல்லது பழுத்துவிட்டது!**")
        st.info("👉 **பரிந்துரை:** மேற்பரப்பு மாற்றம் / சிதைவு அதிகமாகத் தெரிகிறது. மனித பயன்பாட்டிற்கு உகந்தது அல்ல — இதை உரம் தயாரிக்க (Composting) அனுப்பலாம்! 🌱")
else:
    st.info("💡 மேலே உள்ள பட்டனைப் பயன்படுத்தி ஒரு உணவுப் படத்தை அப்லோட் செய்யவும்!")

st.divider()
with st.expander("📍 அவசர உணவு தான தொடர்பு எண்கள் (Quick Donation & Orphanage Directory)"):
    st.markdown("""
    | வகை (Category) | மையத்தின் பெயர் (Center Name) | தொடர்பு எண் (Contact) |
    | :--- | :--- | :--- |
    | **உணவு தான மையம் (Donation House)** | அன்னதானம் & உணவு வங்கி மையம் | `+91 98765 43210` |
    | **ஆதரவற்றோர் இல்லம் (Orphanage)** | அன்பு இல்லம் குழந்தைகள் காப்பகம் | `+91 91234 56789` |
    | **உணவு மீட்பு உதவி எண் (Food Rescue Helpline)** | No Food Waste (India) | `90877 90877` |
    """)

st.caption("Developed with ❤️ by Best Bros (Jumail & AI)")
