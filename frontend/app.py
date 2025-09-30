# frontend/app.py
import os
import json
import random
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import requests

st.set_page_config(page_title="Coinryze Analyzer", layout="wide")
st.title("📊 Coinryze Analyzer")

# Backend URL (optional) - set as environment variable on Render or leave blank to skip prediction requests
BACKEND_URL = os.environ.get("BACKEND_URL", "").rstrip("/")

# --- UI: data source toggle ---
st.sidebar.header("Data Source")
data_source = st.sidebar.radio("Choose data:", ["Sample Data (bundled)", "Upload CSV"])

uploaded_file = None
df = None

if data_source == "Upload CSV":
    uploaded_file = st.file_uploader("Upload your game history CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("✅ Uploaded CSV loaded")
        except Exception as e:
            st.error(f"Failed to read uploaded CSV: {e}")
            st.stop()
else:
    # Try load bundled sample
    sample_path = os.path.join(os.path.dirname(__file__), "sample_history.csv")
    if os.path.exists(sample_path):
        try:
            df = pd.read_csv(sample_path)
            st.info("📂 Loaded bundled sample_history.csv")
        except Exception as e:
            st.error(f"Failed to load bundled sample CSV: {e}")
            st.stop()
    else:
        st.warning("No bundled sample file found. Please upload a CSV.")
        st.stop()

# Normalize columns
df.columns = [c.strip() for c in df.columns]

# Basic preview
st.subheader("🔎 Data Preview")
st.dataframe(df.head(50))

# Guess useful columns (customize if your CSV uses other names)
possible_number_cols = [c for c in df.columns if "number" in c.lower() or "winning" in c.lower()]
possible_color_cols = [c for c in df.columns if "color" in c.lower()]
possible_size_cols = [c for c in df.columns if "big" in c.lower() or "small" in c.lower() or "size" in c.lower()]

num_col = possible_number_cols[0] if possible_number_cols else None
color_col = possible_color_cols[0] if possible_color_cols else None
size_col = possible_size_cols[0] if possible_size_cols else None

st.sidebar.write("Detected columns:")
st.sidebar.write(f"Number: {num_col}")
st.sidebar.write(f"Color: {color_col}")
st.sidebar.write(f"Size/Small-Big: {size_col}")

# Summary stats
st.subheader("📈 Summary Statistics")
st.write(f"Total draws: **{len(df)}**")

cols = st.columns(3)
with cols[0]:
    if num_col:
        st.metric("Latest number", df[num_col].iloc[-1])
    else:
        st.write("No number column detected.")

with cols[1]:
    if color_col:
        st.write(df[color_col].value_counts().to_frame("count"))
    else:
        st.write("No color column detected.")

with cols[2]:
    if size_col:
        st.write(df[size_col].value_counts().to_frame("count"))
    else:
        st.write("No size column detected.")

# Charts
st.subheader("📊 Charts")
if num_col:
    st.write("Recent number trend (last 50)")
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(df[num_col].tail(50).values, marker="o")
    ax.set_xlabel("Draw (most recent at right)")
    ax.set_ylabel("Number")
    st.pyplot(fig)

if color_col:
    st.write("Color distribution")
    st.bar_chart(df[color_col].value_counts())

# Prediction demo (client to backend)
st.subheader("🤖 Predictions")

# Build a small input payload: recent N numbers
N = st.slider("Use last N draws for prediction", min_value=5, max_value=200, value=20)

last_values = df[num_col].tail(N).tolist() if num_col else []
st.write("Input to model (last numbers):", last_values)

predict_button = st.button("Request prediction from backend (if configured)")

if predict_button:
    if not BACKEND_URL:
        st.error("No BACKEND_URL configured. Set environment variable BACKEND_URL to call an API.")
    else:
        payload = {"last_numbers": last_values}
        try:
            r = requests.post(f"{BACKEND_URL}/predict", json=payload, timeout=15)
            r.raise_for_status()
            out = r.json()
            st.success("Prediction received")
            st.json(out)
        except Exception as e:
            st.error(f"Prediction request failed: {e}")

# Small local demo prediction fallback
st.write("---")
st.write("If backend isn't available, use a small local demo prediction:")
if st.button("Local demo prediction"):
    if num_col:
        last = df[num_col].iloc[-1]
        demo_num = random.choice(sorted(df[num_col].unique()))
        demo_color = None
        if demo_num % 2 == 0:
            demo_color = "Green (even)" 
        else:
            demo_color = "Red (odd)"
        demo_size = "Big" if demo_num >= (df[num_col].max() / 2) else "Small"
        st.write(f"Demo predicted number: **{demo_num}**")
        st.write(f"Demo predicted color: **{demo_color}**")
        st.write(f"Demo predicted size: **{demo_size}**")
    else:
        st.write("No numeric column detected to demo prediction.")

st.caption("Tip: For live automation, deploy a backend and a scheduler fetcher. See README for full pipeline.")
