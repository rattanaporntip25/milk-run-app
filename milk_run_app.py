import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

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
# -----------------------
# 🌍 แผนที่เส้นทาง (Milk Run)
# -----------------------

st.subheader("🗺️ แผนที่เส้นทาง Milk Run")

# สร้าง dict พิกัดเวนเดอร์ จาก Abbreviation
# เพิ่ม Daikin เข้าไปใน vendor_coords โดยตรง
vendor_coords = {
    row["Ab."]: (row["lat"], row["lng"])
    for _, row in vendors.iterrows()
}

# ✅ เพิ่มพิกัด Daikin (ตัวย่อ DIT)
vendor_coords["DIT"] = (13.4214134, 101.0101508)

# ให้ผู้ใช้เลือกวันที่และรถ
routes["date"] = pd.to_datetime(routes["date"])
selected_date = st.date_input("เลือกวันที่", value=routes["date"].min())
selected_vehicle = st.selectbox("เลือกรถ", sorted(routes["vehicle_id"].unique()))

# กรองข้อมูลตามวันและรถ
filtered = routes[
    (routes["date"] == pd.to_datetime(selected_date)) &
    (routes["vehicle_id"] == selected_vehicle)
].sort_values(["trip_no", "arrival_time"])

if filtered.empty:
    st.warning("ไม่มีข้อมูลรอบรถในวันนี้")
else:
    # สร้างแผนที่เริ่มต้น
    map_center = vendor_coords.get("DIT", (13.7, 100.5))
    route_map = folium.Map(location=map_center, zoom_start=9)

    colors = ["red", "blue", "green", "orange", "purple", "darkred"]

    for trip_no, group in filtered.groupby("trip_no"):
        coords = []

        # รายละเอียด trip สำหรับ popup
        trip_date = selected_date.strftime("%Y-%m-%d")
        trip_vehicle = selected_vehicle
        trip_info = f"Trip {trip_no}<br>วันที่: {trip_date}<br>รถ: {trip_vehicle}"

        # ✅ จุดเริ่มต้น: DIT (โรงงาน)
        dit_lat, dit_lng = vendor_coords["DIT"]
        coords.append((dit_lat, dit_lng))
        folium.Marker(
            location=(dit_lat, dit_lng),
            popup=f"🏭 DIT (เริ่มต้น)<br>{trip_info}",
            icon=folium.Icon(color="black", icon="industry", prefix="fa")
        ).add_to(route_map)

        # ✅ เวนเดอร์ใน trip
        for _, row in group.iterrows():
            abbr = row["Ab."]
            lat, lng = vendor_coords.get(abbr, (None, None))
            if lat and lng:
                coords.append((lat, lng))
                popup = f"📍 {abbr}<br>{row['arrival_time']} - {row['departure_time']}"
                folium.Marker(
                    location=(lat, lng),
                    popup=popup,
                    icon=folium.Icon(color=colors[trip_no % len(colors)])
                ).add_to(route_map)

        # ✅ จุดสิ้นสุด: DIT
        coords.append((dit_lat, dit_lng))
        folium.Marker(
            location=(dit_lat, dit_lng),
            popup=f"🏭 DIT (สิ้นสุด)<br>{trip_info}",
            icon=folium.Icon(color="black", icon="industry", prefix="fa")
        ).add_to(route_map)

        # ✅ วาดเส้นทาง
        if len(coords) >= 2:
            folium.PolyLine(
                coords,
                color=colors[trip_no % len(colors)],
                weight=3,
                opacity=0.8,
                tooltip=f"เส้นทาง Trip {trip_no}"
            ).add_to(route_map)

    # ✅ แสดงบน Streamlit
    st_data = st_folium(route_map, width=800, height=500)

