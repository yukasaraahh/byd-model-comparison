import streamlit as st
st.set_page_config(page_title="เปรียบเทียบสเปครถ BYD ทุกรุ่น | BYD ชลบุรี ออโตโมทีฟ", page_icon="🚗", layout="wide")

# ---------------- Font ----------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;700&display=swap');

    * {
        font-family: 'Noto Sans Thai', sans-serif !important;
    }

    html, body, div, span, input, select, button, label, textarea,
    .css-1d391kg, .css-ffhzg2, .css-1cpxqw2, .css-1offfwp, .stButton button {
        font-family: 'Noto Sans Thai', sans-serif !important;
    }
x

    </style>
""", unsafe_allow_html=True)

import pandas as pd
import requests
import re
from io import StringIO

# ---------------- Page Setup ----------------
st.set_page_config(page_title="BYD เปรียบเทียบรถ | BYD ชลบุรี", layout="wide")

# ---------------- CSS Styling ----------------
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 1rem;}

.compare-container {
  display: flex;
  flex-direction: row;
  justify-content: center;
  gap: 12px;
  padding: 0px;
  flex-wrap: nowrap;
  overflow-x: hidden;
  box-sizing: border-box;
}

.compare-box {
  flex: 1 1 0;
  max-width: 50%;
  box-sizing: border-box;
  background: #fff;
  border-radius: 16px;
  padding: 0px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  text-align: center;
}

.compare-box img {
  width: 100%;
  aspect-ratio: 1/1;
  object-fit: contain;
  border-radius: 10px;
}

@media screen and (max-width: 768px) {
  .compare-container {
    padding: 0 4px;
    gap: 8px;
  }

  .compare-box {
    flex: 1 1 50%;
    max-width: 50%;
  }
}

.model-title {
    font-size: 22px; font-weight: bold; text-align: center; margin-top: 10px;
}
.model-variant {
    font-size: 14px; text-align: center; color: #888; margin-bottom: 4px;
}
.model-price {
    font-size: 20px; font-weight: 600; text-align: center; margin-bottom: 16px; color: #111;
}

@media screen and (max-width: 768px) {
  .compare-container {
    gap: 12px;
    padding: 0 8px 16px;
  }
  .model-title {
    font-size: 16px;
  }
  .model-price {
    font-size: 18px;
  }
}

.spec-table {
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    margin-top: 20px;
    font-family: 'Noto Sans Thai', sans-serif;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.spec-table th, .spec-table td {
    width: 50%;
    padding: 14px;
    font-size: 15px;
    text-align: center;
    background-color: #fff;
    border-bottom: 1px solid #eee;
    word-wrap: break-word;
}

.spec-table tr:first-child th {
    background-color: #cc0000 !important;
    color: #fff !important;
}

.spec-table tr:first-child th:first-child {
    border-top-left-radius: 12px;
}
.spec-table tr:first-child th:last-child {
    border-top-right-radius: 12px;
}

.spec-table tr th:first-child[colspan="2"] {
    width: 100%;
}

.spec-table th {
    background-color: #f4f4f4;
    font-size: 16px;
    font-weight: bold;
    color: #222;
}

.spec-table tr:nth-child(even) td {
    background-color: #fafafa;
}
.spec-table td:hover {
    background-color: #f0f0f0;
    transition: background-color 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Utility Functions ----------------
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
        st.error(f"❌ โหลดข้อมูลไม่สำเร็จ: {e}")
        return pd.DataFrame()

def get_image_url(link):
    if pd.isna(link) or not isinstance(link, str):
        return ""
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", link)
    if match:
        return f"https://drive.google.com/uc?export=view&id={match.group(1)}"
    return link

def format_value(val, unit):
    if pd.isnull(val):
        return "–"
    if isinstance(val, (int, float)) and float(val).is_integer():
        return f"{int(val)} {unit}"
    return f"{val} {unit}"

# ✅ วางตรงนี้!
def show_model_card(data):
    html = """
    <div class="compare-box">
        <img src="{img}" alt="{model}" style="width:100%; border-radius: 10px;">
        <div class="model-title">{model}</div>
        <div class="model-variant">{variant}</div>
        <div class="model-price">บาท{price:,}</div>
    </div>
    """.format(
        img=get_image_url(data['image']),
        model=data['model'],
        variant=data['variant'],
        price=int(data['price'])
    )
    st.markdown(html, unsafe_allow_html=True)


# ---------------- Load Sheet ----------------
sheet_link = "https://docs.google.com/spreadsheets/d/1haRAYhZrOXFX817BgJNwo2rcIUgy8K5ZNGUnT8juy1w/edit?usp=sharing"
csv_link = convert_google_sheet_link_to_csv(sheet_link)
df = read_google_sheet_csv(csv_link)

# ---------------- Data Clean ----------------
numeric_columns = ['price', 'range_km', 'top_speed_kmph', 'acceleration_0_100', 'battery_kwh']
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

if df.empty or 'model' not in df.columns:
    st.error("❌ ไม่พบข้อมูลรถ กรุณาตรวจสอบ Google Sheet")
    st.stop()

# ---------------- User Inputs ----------------
# ✅ เพิ่มคอลัมน์ใหม่สำหรับการแสดงชื่อรถ + รุ่นย่อย
df["label"] = df["model"] + " - " + df["variant"]

# ✅ ใช้ label แสดงใน dropdown
car_names = df["label"].tolist()
col1, col2 = st.columns(2)

with col1:
    car_1_label = st.selectbox("🚗 เลือกรถคันที่ 1", car_names, key="car1")
with col2:
    car_2_label = st.selectbox("🚗 เลือกรถคันที่ 2", car_names, index=1 if len(car_names) > 1 else 0, key="car2")

# ✅ ดึงข้อมูลแถวของรถแต่ละคัน
car1_data = df[df["label"] == car_1_label].iloc[0]
car2_data = df[df["label"] == car_2_label].iloc[0]

# ---------------- Render Car Boxes ----------------
def render_model_boxes(data1, data2):
    html = f"""
    <div class="compare-container">
        <div class="compare-box">
            <img src="{get_image_url(data1['image'])}" alt="{data1['model']}" style="width:100%; border-radius: 10px;">
            <div class="model-title">{data1['model']}</div>
            <div class="model-variant">{data1['variant']}</div>
            <div class="model-price">&#3647;{int(data1['price']):,}</div>
        </div>
        <div class="compare-box">
            <img src="{get_image_url(data2['image'])}" alt="{data2['model']}" style="width:100%; border-radius: 10px;">
            <div class="model-title">{data2['model']}</div>
            <div class="model-variant">{data2['variant']}</div>
            <div class="model-price">&#3647;{int(data2['price']):,}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ---------------- Render Comparison Table ----------------
def render_comparison_table(data1, data2):
    specs = {
        "ชนิดรถยนต์": ("car_type", ""),
        "ประเภทรถยนต์": ("powertrain_type", ""),
        "ขนาด (ยาว x กว้าง x สูง)": ("dimension", "มม."),
        "จำนวนที่นั่ง": ("seats", "ที่นั่ง"),
        "ระบบขับเคลื่อน": ("drivetrain", ""),
        "ระยะทางวิ่งไฟฟ้าสูงสุด (มาตรฐาน NEDC)": ("ev_range", "กม."),
        "ความจุแบตเตอรี่": ("battery_kwh", "kWh"),
        "ความจุถังน้ำมัน (ลิตร)": ("fuel_tank", "ลิตร"),
        "ระยะทางวิ่งไฟฟ้า+น้ำมันสูงสุด": ("total_range", "กม."),
        "กำลังรวมสูงสุด (แรงม้า)": ("max_power", "แรงม้า"),
        "แรงบิดรวมสูงสุด (Nm)": ("max_torque", "Nm"),
        "อัตราเร่ง 0-100 กม./ชม. (วินาที)": ("acceleration_0_100", "วินาที"),
        "รองรับหัวชาร์จ AC Type 2 - กำลังสูงสุด": ("ac_charging_power", "kW"),
        "รองรับหัวชาร์จ DC CCS2 - กำลังสูงสุด": ("dc_charging_power", "kW"),
        "ความจุพื้นที่เก็บสัมภาระท้ายรถ": ("cargo_capacity", "ลิตร"),
        "ความสูงใต้ท้องรถ": ("ground_clearance", "มม."),
    }

    rows = ["<table class='spec-table'><tbody>"]

    # ✅ แถวชื่อรถ
    rows.append(f"""
    <tr>
      <th>{data1.get("model", "")} - {data1.get("variant", "")}</th>
      <th>{data2.get("model", "")} - {data2.get("variant", "")}</th>
    </tr>
    """)

    for label, (key, unit) in specs.items():
        val1 = data1.get(key, "–")
        val2 = data2.get(key, "–")

        val1 = format_value(data1.get(key, None), unit)
        val2 = format_value(data2.get(key, None), unit)

        # ✅ หัวข้อสเปคกลางแถว
        rows.append(f"<tr><th colspan='2'>{label}</th></tr>")
        rows.append(f"<tr><td>{val1}</td><td>{val2}</td></tr>")

    rows.append("</tbody></table>")
    st.markdown("".join(rows), unsafe_allow_html=True)

# ---------------- Render Output ----------------
st.markdown("### 🔍 เปรียบเทียบรุ่นรถ BYD")
render_model_boxes(car1_data, car2_data)

st.markdown("### 📋 ตารางเปรียบเทียบสเปกรถ")
render_comparison_table(car1_data, car2_data)

# ---------------- Footer ----------------

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none !important;}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .custom-footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: #f8f8f8;
        text-align: center;
        padding: 10px;
        font-size: 13px;
        color: #666;
        border-top: 1px solid #eaeaea;
        font-family: 'Noto Sans Thai', sans-serif;
    }
    </style>

    <div class="custom-footer">
        © 2025 <strong>BYD ชลบุรี ออโตโมทีฟ</strong> | <a href="https://www.bydchonburi.com" target="_blank" style="color:#666;text-decoration:none;">bydchonburi.com</a>
    </div>
""", unsafe_allow_html=True)
