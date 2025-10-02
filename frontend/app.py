import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Coinryze Analyzer", layout="wide")

COLOR_MAP = {"Red": "#FF4B4B", "Green": "#28A745", "Blue": "#007BFF"}

def load_data(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=["issue_id","timestamp","number","color","size","odd_even"])

st.title("🎲 Coinryze Analyzer")

option = st.radio("📊 Select Data Source:", ["Sample Data", "Upload CSV", "Auto-load coinryze_history.csv"])

if option == "Sample Data":
    df = pd.DataFrame({
        "issue_id": ["#202509300001", "#202509300002", "#202509300003"],
        "timestamp": ["2025-09-30 12:00", "2025-09-30 12:01", "2025-09-30 12:02"],
        "number": [5, 8, 2],
        "color": ["Red", "Green", "Blue"],
        "size": ["Small", "Big", "Small"],
        "odd_even": ["Odd", "Even", "Even"]
    })
elif option == "Upload CSV":
    uploaded = st.file_uploader("Upload your coinryze_history.csv", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
    else:
        df = pd.DataFrame()
else:
    df = load_data("frontend/coinryze_history.csv")

if df.empty:
    st.warning("No data available. Please upload or wait for fetcher.")
else:
    st.dataframe(df, use_container_width=True)

    st.subheader("Summary")
    st.write(df.describe(include="all"))

    st.subheader("📈 Color Counts")
    st.bar_chart(df["color"].value_counts())

    st.subheader("🟢 Last Result")
    last = df.iloc[-1]
    st.markdown(f"**Issue:** {last['issue_id']} | **Number:** {last['number']} | "
                f"**Color:** <span style='color:{COLOR_MAP.get(last['color'],'black')}'>{last['color']}</span> | "
                f"**Size:** {last['size']} | **Odd/Even:** {last['odd_even']}",
                unsafe_allow_html=True)
