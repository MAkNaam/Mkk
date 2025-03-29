import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import seaborn as sns
import pydeck as pdk

st.header("แดชบอร์ดอุบัติเหตุทางถนน 🚗💥")
import streamlit as st

#------------------------------------------------------------------------------
st.markdown("""
 <br>
 <br>
""", unsafe_allow_html=True)
# กำหนด font ภาษาไทย
font_path = "THSarabunNew Bold.ttf"  # แก้ไขพาธ font ของคุณ
try:
    font_manager.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'TH Sarabun New'  # เปลี่ยนเป็นชื่อ font ของคุณ
except FileNotFoundError:
    st.warning("ไม่พบไฟล์ฟอนต์ THSarabunNew Bold.ttf โปรดตรวจสอบพาธของไฟล์")
    st.stop()
except OSError as e :
    st.warning(f"เกิดข้อผิดพลาดกับไฟล์ฟอนต์: {e}")
    st.stop()

# อ่านไฟล์ data2020_2022_fixed.csv
@st.cache_data
def load_data():
    return pd.read_csv("data2020_2022_fixed.csv") #แก้ไข path file

#------------------------------------------------------------------------------
data2020_2022 = load_data()
# กำหนดตัวกรองข้อมูลใน Sidebar
st.sidebar.header("ตัวกรองข้อมูล")
selected_year = st.sidebar.multiselect(
    "เลือกปีที่ต้องการดูข้อมูล",
    options=data2020_2022['ปีที่เกิดเหตุ'].dropna().unique(),
    default=data2020_2022['ปีที่เกิดเหตุ'].dropna().unique()
)

selected_province = st.sidebar.multiselect(
    "เลือกจังหวัดที่ต้องการดูข้อมูล",
    options=data2020_2022['จังหวัด'].dropna().unique(),
    default=data2020_2022['จังหวัด'].dropna().unique()
)

# กรองข้อมูลตามตัวเลือก
filtered_data = data2020_2022[
    (data2020_2022['ปีที่เกิดเหตุ'].isin(selected_year)) &
    (data2020_2022['จังหวัด'].isin(selected_province))
]
#------------------------------------------------------------------------------
# สร้างแผนที่
st.subheader("แผนที่แสดงตำแหน่งอุบัติเหตุ")
if 'LATITUDE' in filtered_data.columns and 'LONGITUDE' in filtered_data.columns:
    map_data = filtered_data[['LATITUDE', 'LONGITUDE']].dropna()
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=map_data['LATITUDE'].mean(),
            longitude=map_data['LONGITUDE'].mean(),
            zoom=6,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=map_data,
                get_position='[LONGITUDE, LATITUDE]',
                get_color='[200, 30, 0, 160]',
                get_radius=200,
            ),
        ],
    ))
else:
    st.warning("ไม่มีข้อมูลตำแหน่งสำหรับแสดงแผนที่")
#------------------------------------------------------------------------------
# แสดงข้อมูลดิบ
st.subheader("ข้อมูลดิบ")
st.dataframe(filtered_data)
#------------------------------------------------------------------------------
# ตัวอย่างการปรับแต่งสีในกราฟ
sns.set_palette("coolwarm")
#------------------------------------------------------------------------------
# แปลงคอลัมน์ "เวลา" เป็น datetime object
filtered_data['เวลา'] = pd.to_datetime(filtered_data['เวลา'], format='%H:%M', errors='coerce')
# คำนวณจำนวนอุบัติเหตุในแต่ละจังหวัด และเลือก 10 อันดับแรก
province_accidents = filtered_data.groupby('จังหวัด')['จังหวัด'].count().nlargest(10)
# ตรวจสอบว่าคอลัมน์ "เวลา" ไม่มีค่า NaT ก่อนการคำนวณ
if filtered_data['เวลา'].isna().all():
    st.warning("ไม่มีข้อมูลเวลาที่สามารถใช้งานได้")
else:
    # ดึงข้อมูลชั่วโมงจากคอลัมน์ "เวลา"
    hourly_accidents = filtered_data.groupby(filtered_data['เวลา'].dt.hour)['เวลา'].count()

    # ข้อความสรุป
    st.markdown(f"""
    ### สรุปข้อมูล
    - จังหวัดที่มีอุบัติเหตุสูงสุด: **{province_accidents.index[0]}**
    - ช่วงเวลาที่เกิดอุบัติเหตุบ่อยที่สุด: **{hourly_accidents.idxmax()} นาฬิกา**
    """)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

data2020_2022 = load_data()

# คำนวณจำนวนอุบัติเหตุทั้งหมดในไฟล์ data2020_2022.csv
total_accidents_all = len(data2020_2022)

# นับจำนวนอุบัติเหตุในแต่ละจังหวัด และเลือก 10 อันดับแรก
province_accidents = data2020_2022.groupby('จังหวัด')['จังหวัด'].count().nlargest(10)

#------------------------------------------------------------------------------
data2020_2022 = load_data()

# แปลงคอลัมน์ "เวลา" เป็น datetime object
data2020_2022['เวลา'] = pd.to_datetime(data2020_2022['เวลา'], format='%H:%M', errors='coerce')

# ดึงข้อมูลชั่วโมงจากคอลัมน์ "เวลา"
hourly_accidents = data2020_2022.groupby(data2020_2022['เวลา'].dt.hour)['เวลา'].count()

#------------------------------------------------------------------------------
data2020_2022 = load_data()

# นับจำนวนอุบัติเหตุในแต่ละมูลเหตุสันนิษฐาน
cause_counts = data2020_2022['มูลเหตุสันนิษฐาน'].value_counts()

# เลือกเฉพาะ 10 มูลเหตุที่พบบ่อยที่สุด
top_10_causes = cause_counts.nlargest(10)

#------------------------------------------------------------------------------
data2020_2022 = load_data()

# สร้างคอลัมน์ "รวมจำนวนผู้บาดเจ็บ"
data2020_2022['รวมจำนวนผู้บาดเจ็บ'] = data2020_2022['ผู้บาดเจ็บสาหัส'] + data2020_2022['ผู้บาดเจ็บเล็กน้อย']

# กรองข้อมูลสำหรับปี 2021 และ 2022
data_2021 = data2020_2022[data2020_2022['ปีที่เกิดเหตุ'] == 2021]
data_2022 = data2020_2022[data2020_2022['ปีที่เกิดเหตุ'] == 2022]

# จัดกลุ่มข้อมูลตามเดือน และคำนวณผลรวมของผู้เสียชีวิตและบาดเจ็บสำหรับแต่ละปี
casualties_2021 = data_2021.groupby(data_2021['วันที่เกิดเหตุ'].str[:2].astype(int))[['ผู้เสียชีวิต', 'รวมจำนวนผู้บาดเจ็บ']].sum()
casualties_2022 = data_2022.groupby(data_2022['วันที่เกิดเหตุ'].str[:2].astype(int))[['ผู้เสียชีวิต', 'รวมจำนวนผู้บาดเจ็บ']].sum()

#------------------------------------------------------------------------------
data2020_2022 = load_data()

# นับจำนวนอุบัติเหตุในแต่ละประเภทรถ
vehicle_type_counts = data2020_2022['รถคันที่1'].value_counts()

# เลือกเฉพาะ 5 อันดับแรก (หรือปรับตามต้องการ)
top_5_vehicle_types = vehicle_type_counts.head(5)

# รวมประเภทรถอื่นๆ นอกเหนือจาก 5 อันดับแรก
other_vehicle_types = vehicle_type_counts[5:].sum()

#------------------------------------------------------------------------------
# สร้างแดชบอร์ดด้วยการแบ่งคอลัมน์
col1, col2 = st.columns(2)  # แบ่งพื้นที่เป็น 2 คอลัมน์

# กราฟ 10 จังหวัดที่มีอุบัติเหตุสูงสุด
with col1:
    st.subheader("10 จังหวัดที่มีอุบัติเหตุสูงสุด")
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(province_accidents.index, province_accidents.values)
    ax.set_title(f'10 จังหวัดที่มีอุบัติเหตุสูงสุด (รวม {total_accidents_all} ครั้ง)', fontsize=12)
    ax.set_xlabel('จังหวัด', fontsize=10)
    ax.set_ylabel('จำนวนอุบัติเหตุ', fontsize=10)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval + 5, int(yval), ha='center', va='bottom', fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)

# กราฟช่วงเวลาที่เกิดอุบัติเหตุบ่อยที่สุด
with col2:
    st.subheader("ช่วงเวลาที่เกิดอุบัติเหตุบ่อยที่สุด")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(hourly_accidents.index, hourly_accidents.values, marker='o')
    ax.set_title('ช่วงเวลาที่เกิดอุบัติเหตุบ่อยที่สุด', fontsize=12)
    ax.set_xlabel('ชั่วโมง', fontsize=10)
    ax.set_ylabel('จำนวนอุบัติเหตุ', fontsize=10)
    ax.set_xticks(range(24))
    ax.grid(True)
    for i, v in enumerate(hourly_accidents.values):
        ax.text(hourly_accidents.index[i], v + 5, str(v), ha='center', fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)

# กราฟจำนวนผู้เสียชีวิตและบาดเจ็บในแต่ละเดือน
with col1:
    st.subheader("จำนวนผู้เสียชีวิตและบาดเจ็บในแต่ละเดือน")
    fig, ax1 = plt.subplots(figsize=(6, 4))
    ax1.plot(casualties_2021.index, casualties_2021['ผู้เสียชีวิต'], label='ผู้เสียชีวิต 2021', marker='o', color='blue')
    ax1.plot(casualties_2022.index, casualties_2022['ผู้เสียชีวิต'], label='ผู้เสียชีวิต 2022', marker='o', color='green')
    ax1.set_xlabel('เดือน', fontsize=10)
    ax1.set_ylabel('จำนวนผู้เสียชีวิต (คน)', fontsize=10, color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax2 = ax1.twinx()
    ax2.plot(casualties_2021.index, casualties_2021['รวมจำนวนผู้บาดเจ็บ'], label='ผู้บาดเจ็บ 2021', marker='o', color='red')
    ax2.plot(casualties_2022.index, casualties_2022['รวมจำนวนผู้บาดเจ็บ'], label='ผู้บาดเจ็บ 2022', marker='o', color='orange')
    ax2.set_ylabel('จำนวนผู้บาดเจ็บ (คน)', fontsize=10, color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    plt.title('จำนวนผู้เสียชีวิตและบาดเจ็บในแต่ละเดือน', fontsize=12)
    plt.grid(True)
    fig.legend(loc='upper left', bbox_to_anchor=(1.1, 1))
    plt.tight_layout()
    st.pyplot(fig)

# กราฟสัดส่วนประเภทรถที่เกี่ยวข้องกับอุบัติเหตุ
with col2:
    st.subheader("สัดส่วนประเภทรถที่เกี่ยวข้องกับอุบัติเหตุ")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(
        [top_5_vehicle_types[vehicle_type] for vehicle_type in top_5_vehicle_types.index] + [other_vehicle_types],
        labels=top_5_vehicle_types.index.tolist() + ['อื่นๆ'],
        autopct='%1.1f%%',
        startangle=90,
    )
    ax.set_title('สัดส่วนประเภทรถที่เกี่ยวข้องกับอุบัติเหตุ', fontsize=12)
    plt.tight_layout()
    st.pyplot(fig)

#------------------------------------------------------------------------------

data2020_2022 = load_data()

# นับจำนวนอุบัติเหตุในแต่ละมูลเหตุสันนิษฐาน
cause_counts = data2020_2022['มูลเหตุสันนิษฐาน'].value_counts()

# เลือกเฉพาะ 10 มูลเหตุที่พบบ่อยที่สุด
top_10_causes = cause_counts.nlargest(10)

# สร้าง Bar Chart
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(top_10_causes.index, top_10_causes.values)
ax.set_title('10 มูลเหตุของอุบัติเหตุที่พบบ่อยที่สุด ในปี 2021-2022', fontsize=16)
ax.set_xlabel('มูลเหตุสันนิษฐาน', fontsize=14)
ax.set_ylabel('จำนวนอุบัติเหตุ', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)

# เพิ่มตัวเลขบนกราฟ
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, yval + 5, int(yval), ha='center', va='bottom', fontsize=10)

plt.tight_layout()
st.pyplot(fig)  # แสดงกราฟใน Streamlit


#------------------------------------------------------------------------------
data2020_2022 = load_data()

# เลือกเฉพาะคอลัมน์ที่ต้องการ
selected_data = data2020_2022[['จังหวัด', 'รถคันที่1', 'ผู้เสียชีวิต', 'ผู้บาดเจ็บสาหัส', 'ผู้บาดเจ็บเล็กน้อย']]

# คำนวณจำนวนผู้เสียชีวิต/บาดเจ็บทั้งหมด
selected_data['รวมผู้บาดเจ็บ'] = selected_data[['ผู้เสียชีวิต', 'ผู้บาดเจ็บสาหัส', 'ผู้บาดเจ็บเล็กน้อย']].sum(axis=1)

# เลือกเฉพาะอุบัติเหตุที่มีผู้เสียชีวิตหรือบาดเจ็บสาหัส
severe_accidents = selected_data[selected_data['รวมผู้บาดเจ็บ'] > 0]

# จัดกลุ่มข้อมูลตามจังหวัดและประเภทรถ
grouped_data = severe_accidents.groupby(['จังหวัด', 'รถคันที่1'])['รวมผู้บาดเจ็บ'].sum().reset_index()

# เลือกเฉพาะ 10 จังหวัดที่มีผู้เสียชีวิต/บาดเจ็บสูงสุด
top_10_provinces = grouped_data.groupby('จังหวัด')['รวมผู้บาดเจ็บ'].sum().nlargest(10).index
filtered_data = grouped_data[grouped_data['จังหวัด'].isin(top_10_provinces)]

# สร้าง Bar Chart แสดงจำนวนผู้เสียชีวิต/บาดเจ็บตามจังหวัดและประเภทรถ (10 อันดับแรก)
fig, ax = plt.subplots(figsize=(12, 6))
for vehicle_type in filtered_data['รถคันที่1'].unique():
    data_subset = filtered_data[filtered_data['รถคันที่1'] == vehicle_type]
    ax.bar(data_subset['จังหวัด'], data_subset['รวมผู้บาดเจ็บ'], label=vehicle_type)

# ปรับแต่งกราฟ
ax.set_xlabel('จังหวัด', fontsize=14)
ax.set_ylabel('จำนวนผู้เสียชีวิต/บาดเจ็บ', fontsize=14)
ax.set_title('การกระจายตัวของอุบัติเหตุรุนแรงตามจังหวัดและประเภทของยานพาหนะ (10 อันดับแรก)', fontsize=16)
ax.legend(title='ประเภทรถ', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.tight_layout()

# แสดงผลกราฟใน Streamlit
st.pyplot(fig)

#------------------------------------------------------------------------------
data2020_2022 = load_data()

# เลือกเฉพาะคอลัมน์ที่ต้องการ
selected_data = data2020_2022[['รถคันที่1', 'สภาพอากาศ', 'ผู้เสียชีวิต', 'ผู้บาดเจ็บสาหัส', 'ผู้บาดเจ็บเล็กน้อย']]

# จัดกลุ่มข้อมูลและคำนวณผลรวมผู้เสียชีวิต/บาดเจ็บ
bubble_data = selected_data.groupby(['รถคันที่1', 'สภาพอากาศ'])[['ผู้เสียชีวิต', 'ผู้บาดเจ็บสาหัส', 'ผู้บาดเจ็บเล็กน้อย']].sum().reset_index()
bubble_data['รวมผู้บาดเจ็บ'] = bubble_data[['ผู้เสียชีวิต', 'ผู้บาดเจ็บสาหัส', 'ผู้บาดเจ็บเล็กน้อย']].sum(axis=1)

# เลือกเฉพาะ 5 ประเภทรถและ 5 สภาพอากาศที่มีผู้เสียชีวิต/บาดเจ็บสูงสุด
top_5_vehicle_types = bubble_data.groupby('รถคันที่1')['รวมผู้บาดเจ็บ'].sum().nlargest(5).index
top_5_weather_conditions = bubble_data.groupby('สภาพอากาศ')['รวมผู้บาดเจ็บ'].sum().nlargest(5).index
filtered_data = bubble_data[bubble_data['รถคันที่1'].isin(top_5_vehicle_types) & bubble_data['สภาพอากาศ'].isin(top_5_weather_conditions)]

for vehicle_type in top_5_vehicle_types:
    filtered_data.loc[filtered_data['รถคันที่1'] == vehicle_type, 'รวมผู้บาดเจ็บ_normalized'] = \
        (filtered_data.loc[filtered_data['รถคันที่1'] == vehicle_type, 'รวมผู้บาดเจ็บ'] - \
         filtered_data.loc[filtered_data['รถคันที่1'] == vehicle_type, 'รวมผู้บาดเจ็บ'].min()) / \
        (filtered_data.loc[filtered_data['รถคันที่1'] == vehicle_type, 'รวมผู้บาดเจ็บ'].max() - \
         filtered_data.loc[filtered_data['รถคันที่1'] == vehicle_type, 'รวมผู้บาดเจ็บ'].min())

# สร้าง Bubble Chart
fig, ax = plt.subplots(figsize=(20, 8))

for vehicle_type in top_5_vehicle_types:
    for weather_condition in top_5_weather_conditions:
        data_subset = filtered_data[(filtered_data['รถคันที่1'] == vehicle_type) & (filtered_data['สภาพอากาศ'] == weather_condition)]
        if len(data_subset) > 0:  # ตรวจสอบว่ามีข้อมูลสำหรับประเภทรถและสภาพอากาศนี้หรือไม่
            # ใช้ 'รวมผู้บาดเจ็บ_normalized' สำหรับขนาด bubble
            ax.scatter(vehicle_type, weather_condition, s=data_subset['รวมผู้บาดเจ็บ_normalized'].values[0] * 200,  # ปรับ scaling factor ตามต้องการ
                       alpha=1, label=f'{vehicle_type} - {weather_condition}')

# ปรับแต่งกราฟ
ax.set_xlabel('ประเภทรถ', fontsize=14)
ax.set_ylabel('สภาพอากาศ', fontsize=14)
ax.set_title('ผลกระทบของอุบัติเหตุแยกตามประเภทของยานพาหนะ และสภาพอากาศ (5 อันดับแรก)', fontsize=16)
ax.legend(title='ประเภทรถ - สภาพอากาศ', bbox_to_anchor=(1.05, 1), loc='upper left')  # วาง legend ด้านนอก
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()

st.pyplot(fig)  # แสดงกราฟใน Streamlit
#------------------------------------------------------------------------------
data2020_2022 = load_data()

# สร้างคอลัมน์ "รวมจำนวนผู้บาดเจ็บ"
data2020_2022['รวมจำนวนผู้บาดเจ็บ'] = data2020_2022['ผู้บาดเจ็บสาหัส'] + data2020_2022['ผู้บาดเจ็บเล็กน้อย']

# แปลงคอลัมน์ "เวลา" เป็น datetime object
data2020_2022['เวลา'] = pd.to_datetime(data2020_2022['เวลา'], format='%H:%M', errors='coerce')

# จัดกลุ่มข้อมูลตามชั่วโมง และคำนวณผลรวมของผู้เสียชีวิตและบาดเจ็บ
hourly_casualties = data2020_2022.groupby(data2020_2022['เวลา'].dt.hour)[['ผู้เสียชีวิต', 'รวมจำนวนผู้บาดเจ็บ']].sum()

# สร้าง Line Chart
fig, ax1 = plt.subplots(figsize=(10, 6))

# เส้นสำหรับผู้เสียชีวิต (แกน y ด้านซ้าย)
ax1.plot(hourly_casualties.index, hourly_casualties['ผู้เสียชีวิต'], label='ผู้เสียชีวิต', marker='o', color='blue')
ax1.set_xlabel('ชั่วโมง', fontsize=14)
ax1.set_ylabel('จำนวนผู้เสียชีวิต (คน)', fontsize=14, color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# เส้นสำหรับผู้บาดเจ็บ (แกน y ด้านขวา)
ax2 = ax1.twinx()  # สร้างแกน y ด้านขวา
ax2.plot(hourly_casualties.index, hourly_casualties['รวมจำนวนผู้บาดเจ็บ'], label='ผู้บาดเจ็บ', marker='o', color='red')
ax2.set_ylabel('จำนวนผู้บาดเจ็บ (คน)', fontsize=14, color='red')
ax2.tick_params(axis='y', labelcolor='red')

plt.title('จำนวนผู้เสียชีวิตและบาดเจ็บในแต่ละชั่วโมง', fontsize=16)
plt.grid(True)
fig.legend(loc='upper left', bbox_to_anchor=(1.1, 1))  # แสดง legend นอกกราฟ
plt.tight_layout()
st.pyplot(fig)  # แสดงกราฟใน Streamlit
#------------------------------------------------------------------------------
data2020_2022 = load_data()

# แปลงคอลัมน์ "เวลา" เป็น datetime object
data2020_2022['เวลา'] = pd.to_datetime(data2020_2022['เวลา'], format='%H:%M', errors='coerce')

# เลือกเฉพาะข้อมูลที่ต้องการ
selected_data = data2020_2022[['รถคันที่1', 'เวลา']]

# จัดกลุ่มข้อมูลและนับจำนวนอุบัติเหตุ
hourly_accidents = selected_data.groupby([selected_data['เวลา'].dt.hour, 'รถคันที่1'])['รถคันที่1'].count().reset_index(name='จำนวนอุบัติเหตุ')

# เลือกเฉพาะ 5 ประเภทรถที่มีอุบัติเหตุสูงสุด
top_5_vehicle_types = hourly_accidents.groupby('รถคันที่1')['จำนวนอุบัติเหตุ'].sum().nlargest(5).index
filtered_data = hourly_accidents[hourly_accidents['รถคันที่1'].isin(top_5_vehicle_types)]

# สร้าง Line Chart - Multiple Lines
fig, ax = plt.subplots(figsize=(10, 6))

# สร้าง line chart สำหรับแต่ละประเภทรถ
for vehicle_type in top_5_vehicle_types:
    data_subset = filtered_data[filtered_data['รถคันที่1'] == vehicle_type]
    ax.plot(data_subset['เวลา'], data_subset['จำนวนอุบัติเหตุ'], label=vehicle_type, marker='o')

# ปรับแต่งกราฟ
ax.set_xlabel('ช่วงเวลา (ชั่วโมง)', fontsize=14)
ax.set_ylabel('จำนวนอุบัติเหตุ', fontsize=14)
ax.set_title('ช่วงเวลาที่เกิดอุบัติเหตุสูงสุด แยกตามประเภทของยานพาหนะ (5 อันดับแรก)', fontsize=16)
ax.set_xticks(range(24))  # กำหนดแกน x ให้แสดงชั่วโมง 0-23
ax.legend(title='ประเภทรถ')
ax.grid(True)
plt.tight_layout()

st.pyplot(fig)  # แสดงกราฟใน Streamlit
#------------------------------------------------------------------------------
data2020_2022 = load_data()

# เลือกเฉพาะข้อมูลที่ต้องการ
selected_data = data2020_2022[['จังหวัด', 'ปีที่เกิดเหตุ', 'รถคันที่1']]

# จัดกลุ่มข้อมูลและนับจำนวนอุบัติเหตุ
grouped_data = selected_data.groupby(['จังหวัด', 'ปีที่เกิดเหตุ', 'รถคันที่1'])['รถคันที่1'].count().reset_index(name='จำนวนอุบัติเหตุ')

# เลือกเฉพาะ 10 จังหวัดที่มีอุบัติเหตุสูงสุด
top_10_provinces = grouped_data.groupby('จังหวัด')['จำนวนอุบัติเหตุ'].sum().nlargest(10).index
filtered_data = grouped_data[grouped_data['จังหวัด'].isin(top_10_provinces)]

# เลือกเฉพาะ 5 ประเภทรถที่มีอุบัติเหตุสูงสุด
top_5_vehicle_types = filtered_data.groupby('รถคันที่1')['จำนวนอุบัติเหตุ'].sum().nlargest(5).index
filtered_data = filtered_data[filtered_data['รถคันที่1'].isin(top_5_vehicle_types)]

# สร้าง Stacked Bar Chart
fig, ax = plt.subplots(figsize=(12, 6))

# สร้าง Stacked Bar Chart
width = 0.35  # ความกว้างของแท่ง
provinces = filtered_data['จังหวัด'].unique()
vehicle_types = filtered_data['รถคันที่1'].unique()
years = filtered_data['ปีที่เกิดเหตุ'].unique()

bottom = [0] * len(provinces)

for year in years:
    for vehicle_type in vehicle_types:
        data_subset = filtered_data[(filtered_data['ปีที่เกิดเหตุ'] == year) & (filtered_data['รถคันที่1'] == vehicle_type)]

        # Get values for all provinces, filling with 0 if not present
        values = data_subset.set_index('จังหวัด')['จำนวนอุบัติเหตุ'].reindex(provinces, fill_value=0).values

        ax.bar(provinces, values, width, label=f'{vehicle_type} ({year})', bottom=bottom)
        bottom = [b + v for b, v in zip(bottom, values)]

# ปรับแต่งกราฟ
ax.set_xlabel('จังหวัด', fontsize=14)
ax.set_ylabel('จำนวนอุบัติเหตุ', fontsize=14)
ax.set_title('ผลกระทบของอุบัติเหตุแยกตามประเภทของยานพาหนะ, จังหวัด, และปีที่เกิดเหตุ (10 จังหวัด, 5 ประเภทรถ)', fontsize=16)
ax.legend(title='ประเภทรถ (ปี)', bbox_to_anchor=(1.05, 1), loc='upper left')  # แสดง legend นอกกราฟ
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.tight_layout()

st.pyplot(fig)  # แสดงกราฟใน Streamlit
#------------------------------------------------------------------------------
data2020_2022 = load_data()

casualties_by_province = data2020_2022.groupby('จังหวัด')[['ผู้เสียชีวิต', 'ผู้บาดเจ็บสาหัส', 'ผู้บาดเจ็บเล็กน้อย']].sum().reset_index()

# เลือกเฉพาะ 10 จังหวัดที่มีผู้เสียชีวิต/บาดเจ็บสูงสุด
casualties_by_province['รวมผู้บาดเจ็บ'] = casualties_by_province[['ผู้เสียชีวิต', 'ผู้บาดเจ็บสาหัส', 'ผู้บาดเจ็บเล็กน้อย']].sum(axis=1)
top_10_provinces = casualties_by_province.nlargest(10, 'รวมผู้บาดเจ็บ')['จังหวัด']
casualties_by_province = casualties_by_province[casualties_by_province['จังหวัด'].isin(top_10_provinces)]

# สร้าง Stacked Bar Chart
fig, ax = plt.subplots(figsize=(12, 6))

# สร้าง stacked bar chart
provinces = casualties_by_province['จังหวัด']
deaths = casualties_by_province['ผู้เสียชีวิต']
severe_injuries = casualties_by_province['ผู้บาดเจ็บสาหัส']
minor_injuries = casualties_by_province['ผู้บาดเจ็บเล็กน้อย']

ax.bar(provinces, deaths, label='ผู้เสียชีวิต')
ax.bar(provinces, severe_injuries, bottom=deaths, label='ผู้บาดเจ็บสาหัส')
ax.bar(provinces, minor_injuries, bottom=deaths + severe_injuries, label='ผู้บาดเจ็บเล็กน้อย')

# ปรับแต่งกราฟ
ax.set_xlabel('จังหวัด', fontsize=14)
ax.set_ylabel('จำนวนคน', fontsize=14)
ax.set_title('จำนวนผู้เสียชีวิตและบาดเจ็บจากอุบัติเหตุแยกตามจังหวัด (10 อันดับแรก)', fontsize=16)
ax.legend(loc='upper right')
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.tight_layout()

st.pyplot(fig)  # แสดงกราฟใน Streamlit
#------------------------------------------------------------------------------
data2020_2022 = load_data()

# แปลงคอลัมน์ "วันที่เกิดเหตุ" เป็น datetime object
data2020_2022['วันที่เกิดเหตุ'] = pd.to_datetime(data2020_2022['วันที่เกิดเหตุ'], format='%d/%m/%Y', errors='coerce')

# เลือกเฉพาะคอลัมน์ที่ต้องการ
selected_data = data2020_2022[['ปีที่เกิดเหตุ', 'วันที่เกิดเหตุ', 'รถคันที่1']]

# จัดกลุ่มข้อมูลและนับจำนวนอุบัติเหตุ
monthly_accidents = selected_data.groupby([selected_data['วันที่เกิดเหตุ'].dt.month, 'ปีที่เกิดเหตุ', 'รถคันที่1'])['รถคันที่1'].count().reset_index(name='จำนวนอุบัติเหตุ')

# เลือกเฉพาะ 5 ประเภทรถที่มีอุบัติเหตุสูงสุด
top_5_vehicle_types = monthly_accidents.groupby('รถคันที่1')['จำนวนอุบัติเหตุ'].sum().nlargest(5).index
filtered_data = monthly_accidents[monthly_accidents['รถคันที่1'].isin(top_5_vehicle_types)]

fig, ax = plt.subplots(figsize=(12, 6))

# สร้าง line chart สำหรับแต่ละประเภทรถและปี
for vehicle_type in top_5_vehicle_types:
    for year in filtered_data['ปีที่เกิดเหตุ'].unique():
        data_subset = filtered_data[(filtered_data['รถคันที่1'] == vehicle_type) & (filtered_data['ปีที่เกิดเหตุ'] == year)]

        # แก้ไข: ใช้ data_subset['วันที่เกิดเหตุ'] โดยตรง
        ax.plot(data_subset['วันที่เกิดเหตุ'], data_subset['จำนวนอุบัติเหตุ'], label=f'{vehicle_type} ({year})', marker='o')

# ปรับแต่งกราฟ
ax.set_xlabel('เดือนที่เกิดเหตุ', fontsize=14)
ax.set_ylabel('จำนวนอุบัติเหตุ', fontsize=14)
ax.set_title('จำนวนอุบัติเหตุในแต่ละเดือน แยกตามปีและประเภทของยานพาหนะ (5 อันดับแรก)', fontsize=16)
ax.set_xticks(range(1, 13))  # กำหนดแกน x ให้แสดงเดือน 1-12
ax.legend(title='ประเภทรถ (ปี)', bbox_to_anchor=(1.05, 1), loc='upper left')  # วาง legend ด้านนอก
ax.grid(True)
plt.tight_layout()

st.pyplot(fig)  # แสดงกราฟใน Streamlit
#------------------------------------------------------------------------------
data2020_2022 = load_data()

# เลือกเฉพาะคอลัมน์ที่ต้องการ
data = data2020_2022[['จังหวัด', 'รถคันที่1']]

# นับจำนวนอุบัติเหตุในแต่ละจังหวัดและประเภทรถ
province_vehicle_accidents = data.groupby(['จังหวัด', 'รถคันที่1'])['รถคันที่1'].count().unstack().fillna(0)

# เลือกเฉพาะ 10 จังหวัดที่มีอุบัติเหตุสูงสุด
top_10_provinces = province_vehicle_accidents.sum(axis=1).nlargest(10).index
province_vehicle_accidents = province_vehicle_accidents.loc[top_10_provinces]

# เลือกเฉพาะ 5 ประเภทรถที่เกิดอุบัติเหตุสูงสุด
top_5_vehicles = province_vehicle_accidents.sum().nlargest(5).index
province_vehicle_accidents = province_vehicle_accidents[top_5_vehicles]

# สร้าง Stacked Bar Chart
fig, ax = plt.subplots(figsize=(12, 6))
province_vehicle_accidents.plot(kind='bar', stacked=True, ax=ax)
ax.set_title('จำนวนอุบัติเหตุแยกตามประเภทของยานพาหนะและจังหวัด (10 อันดับแรก)', fontsize=16)
ax.set_xlabel('จังหวัด', fontsize=14)
ax.set_ylabel('จำนวนอุบัติเหตุ', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
ax.legend(title='ประเภทรถที่เกี่ยวข้อง')
plt.tight_layout()
st.pyplot(fig)  # แสดงกราฟใน Streamlit
#------------------------------------------------------------------------------
data2020_2022 = load_data()

# แปลงคอลัมน์ "เวลา" เป็น datetime object
data2020_2022['เวลา'] = pd.to_datetime(data2020_2022['เวลา'], format='%H:%M', errors='coerce')

# สร้างคอลัมน์ "ช่วงเวลา" (แบ่งเป็นช่วง ๆ)
data2020_2022['ช่วงเวลา'] = pd.cut(data2020_2022['เวลา'].dt.hour,
                                    bins=[0, 6, 12, 18, 24],
                                    labels=['กลางคืน', 'เช้า', 'บ่าย', 'เย็น'],
                                    include_lowest=True)

# คำนวณจำนวนผู้เสียชีวิต/บาดเจ็บในแต่ละช่วงเวลาและจังหวัด
heatmap_data = data2020_2022.groupby(['จังหวัด', 'ช่วงเวลา'])[['ผู้เสียชีวิต', 'ผู้บาดเจ็บสาหัส', 'ผู้บาดเจ็บเล็กน้อย']].sum().reset_index()
heatmap_data['รวมผู้บาดเจ็บ'] = heatmap_data[['ผู้เสียชีวิต', 'ผู้บาดเจ็บสาหัส', 'ผู้บาดเจ็บเล็กน้อย']].sum(axis=1)

# เลือกเฉพาะ 10 จังหวัดที่มีผู้เสียชีวิต/บาดเจ็บสูงสุด
top_10_provinces = heatmap_data.groupby('จังหวัด')['รวมผู้บาดเจ็บ'].sum().nlargest(10).index
filtered_data = heatmap_data[heatmap_data['จังหวัด'].isin(top_10_provinces)]

# Pivot the data for heatmap
heatmap_data_pivot = filtered_data.pivot(index='จังหวัด', columns='ช่วงเวลา', values='รวมผู้บาดเจ็บ')

# สร้าง Heatmap
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(heatmap_data_pivot, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax)  # annot=True เพื่อแสดงตัวเลข, fmt=".0f" เพื่อแสดงเป็นจำนวนเต็ม
ax.set_title('ความสัมพันธ์ระหว่างช่วงเวลา, จังหวัด และผลกระทบของอุบัติเหตุ (10 อันดับแรก)', fontsize=16)
ax.set_xlabel('ช่วงเวลา', fontsize=14)
ax.set_ylabel('จังหวัด', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()

st.pyplot(fig)  # แสดงกราฟใน Streamlit
#------------------------------------------------------------------------------
data2020_2022 = load_data()

# แปลงคอลัมน์ "เวลา" เป็น datetime object
data2020_2022['เวลา'] = pd.to_datetime(data2020_2022['เวลา'], format='%H:%M', errors='coerce')

# แปลงคอลัมน์ "วันที่เกิดเหตุ" เป็น datetime object
data2020_2022['วันที่เกิดเหตุ'] = pd.to_datetime(data2020_2022['วันที่เกิดเหตุ'], format='%d/%m/%Y', errors='coerce')

# สร้างคอลัมน์ "วันในสัปดาห์"
data2020_2022['วันในสัปดาห์'] = data2020_2022['วันที่เกิดเหตุ'].dt.day_name()

# สร้างคอลัมน์ "ช่วงเวลา" (แบ่งเป็นช่วง ๆ)
data2020_2022['ช่วงเวลา'] = pd.cut(data2020_2022['เวลา'].dt.hour,
                                    bins=[0, 6, 12, 18, 24],
                                    labels=['กลางคืน', 'เช้า', 'บ่าย', 'เย็น'],
                                    include_lowest=True)

# จัดกลุ่มข้อมูลและนับจำนวนอุบัติเหตุ
heatmap_data = data2020_2022.groupby(['วันในสัปดาห์', 'ช่วงเวลา'])['ช่วงเวลา'].count().reset_index(name='จำนวนอุบัติเหตุ')

# Pivot the data for heatmap
heatmap_data_pivot = heatmap_data.pivot(index='วันในสัปดาห์', columns='ช่วงเวลา', values='จำนวนอุบัติเหตุ')

# กำหนดลำดับของวันในสัปดาห์
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
heatmap_data_pivot = heatmap_data_pivot.reindex(day_order)

# สร้าง Heatmap
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(heatmap_data_pivot, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax)
ax.set_title('จำนวนอุบัติเหตุแยกตามวันของสัปดาห์และช่วงเวลา', fontsize=16)
ax.set_xlabel('ช่วงเวลา', fontsize=14)
ax.set_ylabel('วันในสัปดาห์', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()

st.pyplot(fig)  # แสดงกราฟใน Streamlit
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
