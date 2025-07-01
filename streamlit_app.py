
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
.model-title {
    font-size: 24px;
    font-weight: 600;
    color: #111;
    margin-top: 12px;
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
</style>
""", unsafe_allow_html=True)

# --- Utility functions ---
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
        st.error(f"โหลดข้อมูลไม่สำเร็จ: {e}")
        return pd.DataFrame()

def get_image_url(link):
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", link)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    return link

# --- Load Google Sheet ---
sheet_link = "https://docs.google.com/spreadsheets/d/1haRAYhZrOXFX817BgJNwo2rcIUgy8K5ZNGUnT8juy1w/edit?usp=sharing"
csv_link = convert_google_sheet_link_to_csv(sheet_link)
df = read_google_sheet_csv(csv_link)

# ✅ แปลง column ที่ควรเป็นตัวเลข
numeric_columns = ['price', 'range_km', 'seats', 'top_speed_kmph', 'acceleration_0_100', 'battery_kwh']
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# ✅ เช็กว่าโหลดได้จริง
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

# --- Render Top Section ---
def render_model_boxes(data1, data2):
    html = f"""
    <div class="compare-container">
        <div class="compare-box">
            <img src="{get_image_url(data1['image'])}" alt="{data1['model']}" style="width:100%; border-radius: 10px;">
            <div class="model-title">{data1['model']}</div>
            <div class="model-variant">{data1['variant']}</div>
            <div class="model-price">฿{int(data1['price']):,}</div>
        </div>
        <div class="compare-box">
            <img src="{get_image_url(data2['image'])}" alt="{data2['model']}" style="width:100%; border-radius: 10px;">
            <div class="model-title">{data2['model']}</div>
            <div class="model-variant">{data2['variant']}</div>
            <div class="model-price">฿{int(data2['price']):,}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
def render_comparison_table(data1, data2):
    specs = {
        "ระยะทาง": (f"{data1['range_km']} กม.", f"{data2['range_km']} กม."),
        "ที่นั่ง": (f"{int(data1['seats'])} ที่นั่ง", f"{int(data2['seats'])} ที่นั่ง"),
        "อัตราเร่ง 0–100": (f"{data1['acceleration_0_100']} วิ", f"{data2['acceleration_0_100']} วิ"),
        "ความเร็วสูงสุด": (f"{data1['top_speed_kmph']} กม./ชม.", f"{data2['top_speed_kmph']} กม./ชม."),
        "ระบบขับเคลื่อน": (data1['drivetrain'], data2['drivetrain']),
        "ความจุแบตเตอรี่": (f"{data1['battery_kwh']} kWh", f"{data2['battery_kwh']} kWh"), # Added kWh for clarity
    }

    html = f"""
    <style>
    .spec-table {{
        width: 100%;
        border-collapse: collapse;
        font-family: 'Sarabun', sans-serif;
        margin-top: 20px;
    }}
    .spec-table th, .spec-table td {{
        border: 1px solid #ddd;
        padding: 12px;
        text-align: center;
    }}
    .spec-table th {{
        background-color: #f4f4f4;
        font-weight: bold;
    }}
    </style>
    <table class="spec-table">
        <thead>
            <tr>
                <th>สเปค</th>
                <th>{data1['model']}</th>
                <th>{data2['model']}</th>
            </tr>
        </thead>
        <tbody>
    """

    for label, (val1, val2) in specs.items():
        html += f"""
        <tr>
            <td>{label}</td>
            <td>{val1}</td>
            <td>{val2}</td>
        </tr>
        """

    html += "</tbody></table>"

    st.markdown(html, unsafe_allow_html=True)


# --- Render Output ---
st.markdown("### 🔍 เปรียบเทียบรุ่นรถ BYD")
render_model_boxes(car1_data, car2_data)
st.markdown("### 📋 ตารางเปรียบเทียบสเปกรถ")
render_comparison_table(car1_data, car2_data)
