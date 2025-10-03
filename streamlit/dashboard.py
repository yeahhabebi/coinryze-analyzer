# streamlit/dashboard.py
import os, time, io
import pandas as pd
import requests
import streamlit as st
import plotly.express as px
from datetime import datetime
from urllib.parse import urljoin

# Config
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
CSV_LOCAL = os.getenv("CSV_PATH", "/app/frontend/coinryze_history.csv")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_BASE_URL = os.getenv("S3_BASE_URL")  # optionally served via CDN/object URL
AUTO_REFRESH_SEC = int(os.getenv("DASH_REFRESH_SEC", "10"))

st.set_page_config(page_title="CoinryzeAnalyzer Dashboard", layout="wide")

st.title("🎯 CoinryzeAnalyzer — Live Dashboard")

# Sidebar toggles
st.sidebar.header("Data Source")
data_mode = st.sidebar.radio("Choose data source", ("Sample Data", "Uploaded CSV", "Live CSV"))

auto_refresh = st.sidebar.checkbox("Auto refresh", True)
refresh_interval = st.sidebar.slider("Refresh interval (sec)", min_value=5, max_value=120, value=AUTO_REFRESH_SEC)

# Upload widget
uploaded_file = st.sidebar.file_uploader("Upload CSV (issue_id,timestamp,number,color,size,odd_even)", type=["csv"])

# Sample data generation
def sample_df(n=120):
    import random
    rows = []
    now = datetime.utcnow()
    for i in range(n):
        num = random.randint(0, 49)
        rows.append({
            "issue_id": f"S{i+1}",
            "timestamp": (now - pd.Timedelta(minutes=(n-i))).strftime("%Y-%m-%d %H:%M:%S"),
            "number": num,
            "color": "Green" if num%2==0 else ("Purple" if num%5==0 else "Red"),
            "size": "Big" if num>=25 else "Small",
            "odd_even": "Even" if num%2==0 else "Odd"
        })
    return pd.DataFrame(rows)

@st.cache_data(ttl=30)
def load_df():
    if data_mode == "Sample Data":
        return sample_df()
    if data_mode == "Uploaded CSV":
        if uploaded_file is not None:
            return pd.read_csv(uploaded_file)
        st.warning("Upload a CSV file to use Uploaded CSV mode.")
        return pd.DataFrame()
    # Live CSV: try S3 URL first, then local path
    df = pd.DataFrame()
    if S3_BASE_URL:
        try:
            url = urljoin(S3_BASE_URL, os.path.basename(CSV_LOCAL))
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            df = pd.read_csv(io.StringIO(resp.text))
            return df
        except Exception:
            pass
    if os.path.exists(CSV_LOCAL):
        try:
            df = pd.read_csv(CSV_LOCAL)
            return df
        except Exception as e:
            st.error("Error reading local CSV: " + str(e))
    st.warning("Live CSV not found. Consider running the worker or upload a CSV.")
    return pd.DataFrame()

# Auto refresh control
if auto_refresh:
    st.experimental_rerun()

# Main layout: charts + table + prediction panel
df = load_df()

col1, col2 = st.columns([2,1])

with col1:
    st.subheader("Recent Draws")
    if df.empty:
        st.info("No data to display")
    else:
        # Make a plotly line for numbers over time
        df_plot = df.copy()
        df_plot['ts'] = pd.to_datetime(df_plot['timestamp'])
        df_plot = df_plot.sort_values('ts')
        fig = px.line(df_plot, x='ts', y='number', title='Number over time')
        fig.update_traces(mode="lines+markers")
        st.plotly_chart(fig, use_container_width=True)

        # Color distribution pie
        fig2 = px.pie(df_plot, names='color', title='Color Distribution')
        st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Prediction")
    last_n = st.number_input("Use last N numbers for prediction", min_value=3, max_value=100, value=30)
    if st.button("Predict Next"):
        if df.empty:
            st.warning("No data available to predict.")
        else:
            seq = df['number'].astype(int).tolist()[-last_n:]
            try:
                resp = requests.post(urljoin(BACKEND_URL, "/predict"), json={"last_numbers": seq}, timeout=10)
                resp.raise_for_status()
                pred = resp.json()
                st.metric("Predicted Number", pred['predicted_number'])
                st.write("Color:", pred['predicted_color'])
                st.write("Size:", pred['predicted_size'])
                st.write("Odd/Even:", pred['odd_even'])
                st.write("Confidence (est):", pred.get('confidence', 0.0))
            except Exception as e:
                st.error("Prediction call failed: " + str(e))

st.markdown("----")
st.subheader("Live results table")
if not df.empty:
    # Build color mapping
    def color_map(val):
        val = str(val).lower()
        if "red" in val: return 'background-color: #ffcccc'
        if "green" in val: return 'background-color: #ccffcc'
        if "purple" in val: return 'background-color: #e6ccff'
        return ''

    st.write("Toggle columns, sort, or upload a CSV to update.")
    # Use plotly table for colored cells
    import plotly.graph_objects as go
    header_color = ['#4b0082']*len(df.columns)
    cell_colors = []
    # apply colors per row by 'color' column
    for _, r in df.iterrows():
        c = []
        color_val = str(r.get('color','')).lower()
        for col in df.columns:
            if col == 'color':
                if 'red' in color_val:
                    c.append('#ffcccc')
                elif 'green' in color_val:
                    c.append('#ccffcc')
                elif 'purple' in color_val:
                    c.append('#e6ccff')
                else:
                    c.append('white')
            else:
                c.append('white')
        cell_colors.append(c)
    table = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns), fill_color='#4b0082', font=dict(color='white', size=12)),
        cells=dict(values=[df[c].astype(str).tolist() for c in df.columns],
                   fill_color=list(map(list, zip(*cell_colors))) if cell_colors else 'white',
                   align='left'))
    ])
    st.plotly_chart(table, use_container_width=True)
else:
    st.info("No table data")

# Footer with auto refresh
st.sidebar.markdown("### Controls")
st.sidebar.write(f"Data mode: **{data_mode}**")
st.sidebar.write("If you plan to deploy to Render, configure S3 and set S3_BASE_URL to your bucket public URL for the dashboard to load CSVs.")

