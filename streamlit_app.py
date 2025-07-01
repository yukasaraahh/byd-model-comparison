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
    border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px;
    flex: 1; min-width: 300px; max-width: 450px; background-color: #fff;
}
.compare-box h3 { margin-bottom: 10px; }
.spec-row {
    display: flex; justify-content: space-between; margin: 6px 0;
    font-size: 15px; border-bottom: 1px dashed #ddd; padding-bottom: 4px;
}
.spec-label { font-weight: 500; color: #555; }
.spec-value { font-weight: bold; color: #111; }
.car-image {
    width: 100%; border-radius: 8px; margin-bottom: 10px;
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
