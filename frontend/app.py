import os
import random
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# -----------------------------
# Title
# -----------------------------
st.set_page_config(page_title="Coinryze Analyzer", layout="wide")
st.title("📊 Coinryze Analyzer")
st.write("Analyze historical game draws, visualize patterns, and test predictions.")

# -----------------------------
# Load CSV (Upload or Default)
# -----------------------------
uploaded = st.file_uploader("Upload your game history CSV", type="csv")

df = None
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        st.success("✅ Loaded uploaded CSV")
    except Exception as e:
        st.error(f"Could not read uploaded CSV: {e}")

# Fallback: bundled sample_history.csv
if df is None:
    here = os.path.dirname(os.path.abspath(__file__))
    sample_path = os.path.join(here, "sample_history.csv")

    if os.path.exists(sample_path):
        try:
            df = pd.read_csv(sample_path)
            st.info("📂 Loaded bundled sample dataset (sample_history.csv)")
        except Exception as e:
            st.error(f"Found sample CSV but failed to load: {e}")

# Final fallback
if df is None:
    st.warning("⚠️ No CSV loaded. Please upload a file to continue.")
    st.stop()

# -----------------------------
# Clean & Prepare Data
# -----------------------------
# Try to normalize column names
df.columns = [c.strip().lower() for c in df.columns]

# Guess expected columns
# Example assumption: ['issue no.', 'winning number', 'winning results', 'winning color']
num_col = None
color_col = None
size_col = None

for c in df.columns:
    if "number" in c:
        num_col = c
    if "color" in c:
        color_col = c
    if "big" in c or "small" in c or "result" in c:
        size_col = c

# -----------------------------
# Show Preview
# -----------------------------
st.subheader("🔎 Data Preview")
st.dataframe(df.head())

# -----------------------------
# Stats Section
# -----------------------------
st.subheader("📈 Summary Statistics")

total_draws = len(df)
st.metric("Total Draws", total_draws)

if size_col:
    size_counts = df[size_col].value_counts()
    st.write("Size Distribution:")
    st.bar_chart(size_counts)

if color_col:
    color_counts = df[color_col].value_counts()
    st.write("Color Distribution:")
    st.bar_chart(color_counts)

# -----------------------------
# Number Trend Visualization
# -----------------------------
if num_col:
    st.subheader("📊 Recent Number Trend")
    plt.figure(figsize=(10,4))
    plt.plot(df[num_col].tail(50).values, marker="o")
    plt.title("Last 50 Draws")
    plt.xlabel("Draw")
    plt.ylabel("Number")
    st.pyplot(plt)

# -----------------------------
# Simple Prediction (Demo)
# -----------------------------
st.subheader("🎯 Prediction Demo")

if num_col:
    last_number = df[num_col].iloc[-1]
    next_guess = random.choice(df[num_col].unique())
    st.write(f"Last number: **{last_number}**")
    st.success(f"Predicted next number (demo): **{next_guess}**")

    if size_col:
        st.write(f"Based on last result, trend suggests: **{df[size_col].iloc[-1]} → ?**")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("🚀 Coinryze Analyzer — powered by Streamlit & Render")
