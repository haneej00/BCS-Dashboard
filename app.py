import streamlit as st
import pandas as pd
import plotly.graph_objs as go

file_path = '22_24_streamlit.xlsx'

# MCC 라벨
mcc_labels = {
    7230: "Beauty Services", 5812: "Restaurants", 7216: "Dry Cleaning", 5499: "Specialty Foods",
    5999: "Misc. Retail", 7297: "Massage", 5691: "Clothing Stores", 8021: "Dentists", 8099: "Medical Services",
    5621: "Women's Apparel", 5814: "Fast Food", 8299: "Educational Services", 7538: "Auto Repair",
    5921: "Alcohol Stores", 4812: "Telecom Services", 5944: "Jewelry Stores", 5462: "Bakeries",
    5137: "Men’s Clothing", 5310: "Discount Stores", 5631: "Women's Accessories"
}

mcc_options = {"All MCCs": "all"}
mcc_options.update({v: k for k, v in mcc_labels.items()})

@st.cache_data
def load_data():
    df = pd.read_excel(file_path, engine='openpyxl')
    return df

df = load_data()

vol_cols = [f'vol {year}{month:02d}' for year in range(2022, 2025) for month in range(1, 13)][:36]
trans_cols = [f'trans {year}{month:02d}' for year in range(2022, 2025) for month in range(1, 13)][:36]

st.title("📊 BCS Account Volume by MCC Type")
selected_label = st.selectbox("Choose Business type", list(mcc_options.keys()))
selected_mcc = mcc_options[selected_label]

if selected_mcc == "all":
    df_filtered = df[vol_cols + trans_cols]
    title = "Total MCC (All)"
else:
    df_filtered = df[df["MCC"] == selected_mcc][vol_cols + trans_cols]
    title = f"{selected_label} (MCC {selected_mcc})"

# 월별 SUM
vol_sum = df_filtered[vol_cols].sum()
trans_sum = df_filtered[trans_cols].sum()
month_labels = [col.split()[-1] for col in vol_cols]

# 데이터프레임 구성
if vol_sum.empty or trans_sum.empty:
    st.error("선택한 MCC에 대한 데이터가 부족합니다.")
    st.stop()

data = pd.DataFrame({
    'Month': pd.to_datetime(month_labels, format='%Y%m'),
    'Volume': vol_sum.values,
    'Transaction': trans_sum.values  # 이미 Volume per Transaction 값
}).sort_values('Month').reset_index(drop=True)

# 분기 컬럼 생성
data['Quarter'] = data['Month'].dt.to_period('Q')

# 분기별 합계
quarterly = data.groupby('Quarter').agg({
    'Volume': 'sum',
    'Transaction': 'sum'
}).reset_index()

# 시각화
st.subheader("📈 Quarterly Total Volume & Volume/Transaction")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=quarterly['Quarter'].astype(str),
    y=quarterly['Volume'],
    mode='lines+markers',
    name='Total Volume',
    line=dict(color='green')
))
fig.add_trace(go.Scatter(
    x=quarterly['Quarter'].astype(str),
    y=quarterly['Transaction'],
    mode='lines+markers',
    name='Sum of Volume/Transaction',
    line=dict(color='orange')
))
fig.update_layout(
    title=title + " - Quarterly Volume & Volume/Transaction",
    xaxis_title='Quarter',
    yaxis_title='Sum',
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# 테이블 출력
st.subheader("📋 Quarterly Sum Table")

quarterly['Volume'] = quarterly['Volume'].apply(lambda x: f"${x:,.0f}")
quarterly['Transaction'] = quarterly['Transaction'].apply(lambda x: f"{x:,.0f}")

st.table(quarterly.rename(columns={
    'Quarter': 'Period',
    'Volume': 'Total Volume',
    'Transaction': 'Sum of Volume/Tx'
}))
