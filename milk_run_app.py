import streamlit as st
import pandas as pd

st.set_page_config(page_title="Milk Run Viewer", layout="wide")
st.title("Milk Run Viewer")
st.markdown("ระบบจัดการเส้นทาง Milk Run - Daikin (เชื่อม Google Sheets)")

# ฟังก์ชันโหลด Google Sheet
@st.cache_data
def load_sheet(sheet_gid, name):
    url = f"https://docs.google.com/spreadsheets/d/1IQ2T_v2y9z3KCsZ6ul3qQtGBKgnx3s0OtwRaDIuuUSc/export?format=csv&gid={sheet_gid}"
    try:
        df = pd.read_csv(url)
        st.success(f"✅ โหลดข้อมูล {name} สำเร็จ")
        return df
    except Exception as e:
        st.error(f"❌ โหลดข้อมูล {name} ล้มเหลว: {e}")
        return pd.DataFrame()

# โหลดทุกชีท
vendors = load_sheet(0, "Vendors")
vehicles = load_sheet(1327265658, "Vehicles")
routes = load_sheet(498856514, "Routes")
pallet_by_day = load_sheet(593344550, "Vendor Pallet By Day")
frequency = load_sheet(1620015243, "Frequency")

# แสดงข้อมูล
st.header("Vendors")
st.dataframe(vendors)

st.header("Vehicles")
st.dataframe(vehicles)

st.header("Routes")
st.dataframe(routes)

st.header("Pallets by Day")
st.dataframe(pallet_by_day)

st.header("Frequency")
st.dataframe(frequency)
