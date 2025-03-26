# -*- coding: utf-8 -*-
"""Volume_Trend_2022_2024_ver7.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1hsWQRzgNmJaEXKfHtKa_T7NF9xHRBHms
"""

## Quarterly data table
## Volume per Transaction accuracy

## Add MCC Contribution % next to description
## Revise with ACTUAL DATA (SUM)

## Ver.7

import streamlit as st
import pandas as pd
import plotly.graph_objs as go

file_path = '22_24_Jan_Dec_live_accts_Yearly_streamlit.xlsx'

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
    title = "Avg. MCC All"
else:
    df_filtered = df[df["MCC"] == selected_mcc][vol_cols + trans_cols]
    title = f"{selected_label} (MCC {selected_mcc})"

# 평균으로 월별 데이터 생성
vol_avg = df_filtered[vol_cols].mean()
trans_avg = df_filtered[trans_cols].mean()
month_labels = [col.split()[-1] for col in vol_cols]

# 📌 월별 평균 데이터프레임 생성
if vol_avg.empty or trans_avg.empty:
    st.error("선택한 MCC에 대한 데이터가 부족합니다.")
    st.stop()

data = pd.DataFrame({
    'Month': pd.to_datetime(month_labels, format='%Y%m'),
    'Volume': vol_avg.values,
    'Transaction': trans_avg.values
}).sort_values('Month').reset_index(drop=True)

# ✅ 분기 컬럼 추가
data['Quarter'] = data['Month'].dt.to_period('Q')

# 📈 분기별 합계 계산
quarterly = data.groupby('Quarter').agg({
    'Volume': 'sum',
    'Transaction': 'sum'
}).reset_index()

quarterly['Volume per Tx'] = quarterly['Volume'] / quarterly['Transaction']

# 📊 라인 차트 출력
st.subheader("📈 Quarterly Total Volume & Transaction")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=quarterly['Quarter'].astype(str),
    y=quarterly['Volume'],
    mode='lines+markers',
    name='Quarterly Volume',
    line=dict(color='green')
))
fig.add_trace(go.Scatter(
    x=quarterly['Quarter'].astype(str),
    y=quarterly['Transaction'],
    mode='lines+markers',
    name='Quarterly Transaction',
    line=dict(color='blue')
))
fig.update_layout(
    title=title + " - Quarterly Volume & Transaction (Sum)",
    xaxis_title='Quarter',
    yaxis_title='Total',
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# 📋 테이블 출력
st.subheader("📋 Quarterly Sum Table")

quarterly['Volume'] = quarterly['Volume'].apply(lambda x: f"${x:,.0f}")
quarterly['Transaction'] = quarterly['Transaction'].apply(lambda x: f"{x:,.0f}")
quarterly['Volume per Tx'] = quarterly['Volume per Tx'].apply(lambda x: f"{x:,.1f}")

st.table(quarterly.rename(columns={
    'Quarter': 'Period',
    'Volume': 'Total Volume',
    'Transaction': 'Total Transaction',
    'Volume per Tx': 'Volume / Tx'
}))