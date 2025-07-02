import streamlit as st
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
<style>
.spec-table {
    width: 100%;
    table-layout: fixed;  /* ✅ บังคับให้แบ่ง column เท่ากัน */
    border-collapse: collapse;
    margin-top: 20px;
    font-family: 'Noto Sans Thai', sans-serif;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.spec-table th, .spec-table td {
    width: 50%;  /* ✅ ทำให้แต่ละช่องกว้างเท่ากัน */
    padding: 14px;
    font-size: 15px;
    text-align: center;
    background-color: #fff;
    border-bottom: 1px solid #eee;
    word-wrap: break-word;  /* ✅ ป้องกันข้อความล้น */
}

.spec-table tr th:first-child[colspan="2"] {
    width: 100%;  /* ✅ สำหรับแถวหัวข้อกลาง (เช่น ระยะทาง) */
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
</style>


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
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", link)
    if match:
        return f"https://drive.google.com/uc?export=view&id={match.group(1)}"
    return link

# ✅ วางตรงนี้!
def show_model_card(data):
    html = """
    <div class="compare-box">
        <img src="{img}" alt="{model}" style="width:100%; border-radius: 10px;">
        <div class="model-title">{model}</div>
        <div class="model-variant">{variant}</div>
        <div class="model-price">&#3647;{price:,}</div>
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
numeric_columns = ['price', 'range_km', 'seats', 'top_speed_kmph', 'acceleration_0_100', 'battery_kwh']
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

if df.empty or 'model' not in df.columns:
    st.error("❌ ไม่พบข้อมูลรถ กรุณาตรวจสอบ Google Sheet")
    st.stop()

# ---------------- User Inputs ----------------
car_names = df['model'].unique().tolist()
col1, col2 = st.columns(2)
with col1:
    car_1 = st.selectbox("🚗 เลือกรถคันที่ 1", car_names, key="car1")
with col2:
    car_2 = st.selectbox("🚗 เลือกรถคันที่ 2", car_names, index=1 if len(car_names) > 1 else 0, key="car2")

car1_data = df[df['model'] == car_1].iloc[0]
car2_data = df[df['model'] == car_2].iloc[0]

# ---------------- Render Car Boxes ----------------
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

# ---------------- Render Comparison Table ----------------
def render_comparison_table(data1, data2):
    specs = {
        "ระยะทาง": ("range_km", "กม."),
        "จำนวนที่นั่ง": ("seats", "ที่นั่ง"),
        "ความเร็วสูงสุด": ("top_speed_kmph", "กม./ชม."),
        "อัตราเร่ง 0–100": ("acceleration_0_100", "วิ"),
        "ระบบขับเคลื่อน": ("drivetrain", ""),
        "ความจุแบตเตอรี่": ("battery_kwh", "kWh"),
    }

    rows = ["<table class='spec-table'><tbody>"]

    # ✅ แถวชื่อรถ
    rows.append(f"""
    <tr>
      <th>{data1.get("model", "")}</th>
      <th>{data2.get("model", "")}</th>
    </tr>
    """)

    for label, (key, unit) in specs.items():
        val1 = data1.get(key, "–")
        val2 = data2.get(key, "–")

        val1 = f"{val1} {unit}" if pd.notnull(val1) else "–"
        val2 = f"{val2} {unit}" if pd.notnull(val2) else "–"

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
