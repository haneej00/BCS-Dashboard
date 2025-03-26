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
month_range = pd.date_range(start="2022-01-01", periods=36, freq="MS")
quarter_labels = month_range.to_period("Q")

st.title("BCS Account Volume Trend")

selected_label = st.selectbox("Choose Business type", list(mcc_options.keys()))
selected_mcc = mcc_options[selected_label]

if selected_mcc == "all":
    df_filtered = df.copy()
    title = "Total MCC (All)"
else:
    df_filtered = df[df["MCC"] == selected_mcc]

    # ✅ 퍼센트 계산
    total_count = len(df)
    selected_count = len(df_filtered)
    percent = (selected_count / total_count) * 100

    title = f"{selected_label} (MCC {selected_mcc}) - {percent:.1f}% of total"
    st.subheader(title)

# 각 월별 데이터를 DataFrame으로 준비
vol_df = df_filtered[vol_cols].copy()
trans_df = df_filtered[trans_cols].copy()
vol_df.columns = month_range
trans_df.columns = month_range

# 월을 분기로 변경
vol_df.columns = vol_df.columns.to_period("Q")
trans_df.columns = trans_df.columns.to_period("Q")

# 분기별 SUM
vol_quarterly = vol_df.groupby(axis=1, level=0).sum().sum(axis=0)
trans_quarterly = trans_df.groupby(axis=1, level=0).sum().sum(axis=0)

# Plot 1: Volume
st.subheader("Quarterly Total Volume (SUM)")
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=vol_quarterly.index.astype(str),
    y=vol_quarterly.values,
    mode='lines+markers',
    name='Total Volume',
    line=dict(color='green')
))
fig1.update_layout(title=title + " - Quarterly Volume", xaxis_title="Quarter", yaxis_title="Total Volume")
st.plotly_chart(fig1, use_container_width=True)

# Plot 2: Transaction
st.subheader("Quarterly Total Volume per Transaction (SUM)")
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=trans_quarterly.index.astype(str),
    y=trans_quarterly.values,
    mode='lines+markers',
    name='Total Transactions',
    line=dict(color='red')
))
fig2.update_layout(title=title + " - Quarterly Volume per Transaction", xaxis_title="Quarter", yaxis_title="Total Transactions")
st.plotly_chart(fig2, use_container_width=True)

# 📋 Table
st.subheader("Quarterly Summary Data Table")

summary = pd.DataFrame({
    "Period": vol_quarterly.index.astype(str),
    "Total Volume": vol_quarterly.values,
    "Volume per Transaction": trans_quarterly.values
})

summary["Total # of Transaction"] = (summary["Total Volume"] / summary["Volume per Transaction"]).astype(int).astype(str)

summary["Total Volume"] = summary["Total Volume"].apply(lambda x: f"${x:,.0f}")
summary["Volume per Transaction"] = summary["Volume per Transaction"].apply(lambda x: f"${x:,.0f}")

# 컬럼 순서 조정
summary = summary[["Period", "Total Volume", "Total # of Transaction", "Volume per Transaction"]]
st.table(summary)



