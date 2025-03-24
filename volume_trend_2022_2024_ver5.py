# -*- coding: utf-8 -*-
"""Volume_Trend_2022_2024_ver5.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1HImWqIvwQ2afwQ9i3YId9b9YzGc-M9hB
"""

!pip install dask[complete] pandas plotly dash openpyxl

## Ver.5

## Monthly Volume tracking by MCC type
## Monthly Volume per transaction tracking by MCC type

## Data table below to show 6-month volume change

## Completed


from google.colab import drive
drive.mount('/content/drive')

# 2.
import pandas as pd
import dask.dataframe as dd
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output
from dash import dash_table
import threading
import time
from google.colab import output
import dash

# 3. MCC label
mcc_labels = {
    7230: "Beauty Services", 5812: "Restaurants", 7216: "Dry Cleaning", 5499: "Specialty Foods",
    5999: "Misc. Retail", 7297: "Massage", 5691: "Clothing Stores", 8021: "Dentists", 8099: "Medical Services",
    5621: "Women's Apparel", 5814: "Fast Food", 8299: "Educational Services", 7538: "Auto Repair",
    5921: "Alcohol Stores", 4812: "Telecom Services", 5944: "Jewelry Stores", 5462: "Bakeries",
    5137: "Men’s Clothing", 5310: "Discount Stores", 5631: "Women's Accessories"
}
mcc_list = list(mcc_labels.keys())

# 4.
file_path = '/content/drive/MyDrive/22-24 Jan-dec live accts exercise2.xlsx'
df_pd = pd.read_excel(file_path, engine='openpyxl')
df = dd.from_pandas(df_pd, npartitions=4)

# 5.
vol_cols = [f'vol {year}{month:02d}' for year in range(2022, 2025) for month in range(1, 13)][:36]
trans_cols = [f'trans {year}{month:02d}' for year in range(2022, 2025) for month in range(1, 13)][:36]

# 6. Dash
app = Dash(__name__)
app.layout = html.Div([
    html.H1("📊 MCC별 Volume & Transaction 변화 대시보드"),

    html.Div([
        html.Button("MCC All", id='mcc_all', n_clicks=0)
    ] + [
        html.Button(label, id=f'mcc_{mcc}', n_clicks=0) for mcc, label in mcc_labels.items()
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px', 'marginBottom': '20px'}),

    dcc.Graph(id='volume-trend'),

    html.H3("📋 6개월 단위 평균 Volume"),
    dash_table.DataTable(
        id='volume-table',
        columns=[
            {"name": "Month Range", "id": "Month"},
            {"name": "Average Volume", "id": "Average Volume"}
        ],
        data=[],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
        style_header={'fontWeight': 'bold'},
    )
])

# 7.
@app.callback(
    [Output('volume-trend', 'figure'),
     Output('volume-table', 'data')],
    [Input('mcc_all', 'n_clicks')] + [Input(f'mcc_{mcc}', 'n_clicks') for mcc in mcc_list]
)
def update_output(*args):
    ctx = dash.callback_context

    if not ctx.triggered:
        selected = 'all'
    else:
        btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if btn_id == 'mcc_all':
            selected = 'all'
        else:
            selected = int(btn_id.replace('mcc_', ''))

    # 데이터 필터링
    if selected == 'all':
        df_filtered = df[vol_cols + trans_cols].compute()
        title = "전체 MCC 평균"
    else:
        df_filtered = df[df['MCC'] == selected][vol_cols + trans_cols].compute()
        title = f"{mcc_labels[selected]} (MCC {selected})"

    vol_avg = df_filtered[vol_cols].mean()
    trans_avg = df_filtered[trans_cols].mean()

    month_labels = [col.split()[-1] for col in vol_cols]  # '202201' ~ '202412'
    data = pd.DataFrame({
        'month': pd.to_datetime(month_labels, format='%Y%m'),
        'volume': vol_avg.values,
        'transaction': trans_avg.values
    }).sort_values('month')

    data['period'] = (data.index // 6) + 1
    grouped = data.groupby('period').agg({
        'month': ['min', 'max'],
        'volume': 'mean'
    }).reset_index()
    grouped.columns = ['period', 'start_month', 'end_month', 'avg_volume']
    table_data = [{
        "Month": f"{row['start_month'].strftime('%Y-%m')} ~ {row['end_month'].strftime('%Y-%m')}",
        "Average Volume": f"{row['avg_volume']:,.0f}"
    } for _, row in grouped.iterrows()]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['month'],
        y=data['volume'],
        mode='lines+markers',
        name='Volume',
        line=dict(color='black')
    ))
    fig.add_trace(go.Scatter(
        x=data['month'],
        y=data['transaction'],
        mode='lines+markers',
        name='Transaction',
        line=dict(color='blue')
    ))
    fig.update_layout(
        title=title + " - 월별 평균 Volume & Transaction",
        xaxis_title='Month',
        yaxis_title='Average Value'
    )

    return fig, table_data

# 8. Dash
def run_dash():
    app.run(port=8050, debug=False)

thread = threading.Thread(target=run_dash)
thread.start()
time.sleep(2)
output.eval_js('window.open("http://127.0.0.1:8050", "_blank")')

!pip install streamlit

import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Volume Dashboard", layout="wide")

# --- TITLE ---
st.title("📊 MCC별 Volume & Transaction 변화 대시보드")

# --- MCC 라벨 정의 ---
mcc_labels = {
    7230: "Beauty Services", 5812: "Restaurants", 7216: "Dry Cleaning", 5499: "Specialty Foods",
    5999: "Misc. Retail", 7297: "Massage", 5691: "Clothing Stores", 8021: "Dentists", 8099: "Medical Services",
    5621: "Women's Apparel", 5814: "Fast Food", 8299: "Educational Services", 7538: "Auto Repair",
    5921: "Alcohol Stores", 4812: "Telecom Services", 5944: "Jewelry Stores", 5462: "Bakeries",
    5137: "Men’s Clothing", 5310: "Discount Stores", 5631: "Women's Accessories"
}
mcc_options = {"All MCCs": "all"} | {v: k for k, v in mcc_labels.items()}  # dropdown용

# --- 데이터 로딩 ---
@st.cache_data
def load_data():

    file_path = '/content/drive/MyDrive/22-24 Jan-dec live accts exercise2.xlsx'
    df = pd.read_excel(file_path, engine="openpyxl")
    return df

df = load_data()

# --- 컬럼 정의 ---
vol_cols = [f"vol {year}{month:02d}" for year in range(2022, 2025) for month in range(1, 13)][:36]
trans_cols = [f"trans {year}{month:02d}" for year in range(2022, 2025) for month in range(1, 13)][:36]

# --- MCC 선택 ---
selected_label = st.selectbox("MCC 선택", list(mcc_options.keys()))
selected_mcc = mcc_options[selected_label]

# --- 필터링 ---
if selected_mcc == "all":
    df_filtered = df[vol_cols + trans_cols]
    title = "전체 MCC 평균"
else:
    df_filtered = df[df["MCC"] == selected_mcc][vol_cols + trans_cols]
    title = f"{selected_label} (MCC {selected_mcc})"

# --- 평균 계산 ---
vol_avg = df_filtered[vol_cols].mean()
trans_avg = df_filtered[trans_cols].mean()
months = [col.split()[-1] for col in vol_cols]

data = pd.DataFrame({
    "Month": pd.to_datetime(months, format="%Y%m"),
    "Volume": vol_avg.values,
    "Transaction": trans_avg.values
}).sort_values("Month")

# --- 📈 라인 차트 ---
st.subheader("📈 월별 평균 추이")
st.line_chart(data.set_index("Month"))

# --- 📋 6개월 단위 평균 테이블 ---
st.subheader("📋 6개월 단위 평균 Volume")
data["Period"] = (data.index // 6) + 1
summary = data.groupby("Period").agg(
    Start=("Month", "min"),
    End=("Month", "max"),
    AvgVolume=("Volume", "mean")
).reset_index()

summary["Period"] = summary["Start"].dt.strftime("%Y-%m") + " ~ " + summary["End"].dt.strftime("%Y-%m")
summary["AvgVolume"] = summary["AvgVolume"].apply(lambda x: f"{x:,.0f}")
st.table(summary[["Period", "AvgVolume"]].rename(columns={
    "Period": "Month Range", "AvgVolume": "Average Volume"
}))