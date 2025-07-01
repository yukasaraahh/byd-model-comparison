import streamlit as st
import pandas as pd
import requests
import re
from io import StringIO

# Page setup
st.set_page_config(page_title="BYD เปรียบเทียบรถ | BYD ชลบุรี", layout="wide")

# --- Hide Streamlit UI ---
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.block-container { padding-top: 1rem; padding-bottom: 1rem; }
.compare-container {
    display: flex; flex-direction: row; justify-content: space-around;
    gap: 20px; flex-wrap: wrap;
}
.compare-box {
    border: 1px solid #eee;
    border-radius: 16px;
    padding: 20px;
    flex: 1;
    min-width: 320px;
    max-width: 450px;
    background: #ffffff;
    box-shadow: 0 6px 12px rgba(0,0,0,0.05);
    transition: all 0.2s ease-in-out;
}
.compare-box:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.08);
}
.compare-box h3 {
    font-size: 20px;
    font-weight: 600;
    margin-top: 12px;
}
.spec-row {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
  padding-bottom: 6px;
  border-bottom: 1px dashed #e0e0e0;
}

.spec-label {
    font-size: 13px;
    color: #777;
    text-transform: none;
    letter-spacing: 0.3px;
}

.spec-value {
    font-size: 18px;
    font-weight: 500;
    color: #111;
}
.model-title {
    font-size: 24px;
    font-weight: 600;
    color: #111;
    margin-bottom: 4px;
    text-align: center;
}

.model-variant {
    font-size: 14px;
    color: #888;
    text-align: center;
    margin-bottom: 10px;
}

.model-price {
    font-size: 22px;
    font-weight: 600;
    color: #111;
    text-align: center;
    margin-bottom: 20px;
}
.spec-block {
    margin-bottom: 24px;
    text-align: center;
}

.spec-label-small {
    font-size: 13px;
    color: #777;
    letter-spacing: 0.3px;
    margin-bottom: 2px;
}

.spec-value-big {
    font-size: 22px;
    font-weight: 600;
    color: #111;
}
</style>
""", unsafe_allow_html=True)

# --- Google Sheet Functions ---
def convert_google_sheet_link_to_csv(shared_link: str) -> str:
    sheet_id_match = re.search(r"/d/([a-zA-Z0-9-_]+)", shared_link)
    gid_match = re.search(r"gid=([0-9]+)", shared_link)
    if sheet_id_match:
        sheet_id = sheet_id_match.group(1)
        gid = gid_match.group(1) if gid_match else "0"
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    return shared_link

def read_google_sheet_csv(csv_url):
    try:
        response = requests.get(csv_url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.content.decode('utf-8')))
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

def get_image_url(link):
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", link)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    return link

# --- Load your Google Sheet ---
sheet_link = "https://docs.google.com/spreadsheets/d/1haRAYhZrOXFX817BgJNwo2rcIUgy8K5ZNGUnT8juy1w/edit?usp=sharing"
csv_link = convert_google_sheet_link_to_csv(sheet_link)
df = read_google_sheet_csv(csv_link)

# --- Check and render UI ---
if df.empty or 'model' not in df.columns:
    st.error("❌ Unable to load comparison data from Google Sheet.")
    st.stop()

car_names = df['model'].unique().tolist()
col1, col2 = st.columns(2)

with col1:
    car_1 = st.selectbox("🚗 เลือกรถคันที่ 1", car_names, key="car1")
with col2:
    car_2 = st.selectbox("🚗 เลือกรถคันที่ 2", car_names, index=1 if len(car_names) > 1 else 0, key="car2")

car1_data = df[df['model'] == car_1].iloc[0]
car2_data = df[df['model'] == car_2].iloc[0]

st.markdown("### 🔍 เปรียบเทียบรุ่นรถ BYD")
st.markdown('<div class="compare-container">', unsafe_allow_html=True)

# --- Render Card Function ---
def render_compare_box(data):
    st.image(get_image_url(data["image_url"]), use_container_width=True)
    
    st.markdown(f"""
    <div class="model-title">{data['model']}</div>
    <div class="model-variant">{data['variant']}</div>
    <div class="model-price">฿{int(data['price']):,}</div>
""", unsafe_allow_html=True)

    specs = {
        "💰 ราคา": f"฿{int(data['price']):,}",
        "🔋 ระยะทาง": f"{data['range_km']} กม.",
        "🪑 ที่นั่ง": f"{int(data['seats'])} ที่นั่ง",
        "⚡ อัตราเร่ง": f"{data['acceleration_0_100']} วินาที (0–100)",
        "🚀 ความเร็วสูงสุด": f"{data['top_speed_kmph']} กม./ชม.",
        "📦 พื้นที่สัมภาระ": f"{data['cargo_liters']} ลิตร",
        "🔧 ระบบขับเคลื่อน": data['drivetrain'],
        "🔋 แบตเตอรี่": data['battery_kwh'],
    }

    for label, value in specs.items():
        st.markdown(f"""
            <div class="spec-block">
                <div class="spec-label-small">{label}</div>
                <div class="spec-value-big">{value}</div>
            </div>
        """, unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    render_compare_box(car1_data)
with col2:
    render_compare_box(car2_data)

