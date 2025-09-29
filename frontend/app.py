# frontend/app.py
import os
import streamlit as st
import pandas as pd

# Try to import helper modules (either inside a backend package or at repo root)
try:
    from backend import data_loader, predictor, simulator, utils
except Exception:
    try:
        import data_loader, predictor, simulator, utils
    except Exception:
        data_loader = None
        predictor = None
        simulator = None
        utils = None

st.set_page_config(page_title="Coinryze Analyzer", layout="wide")
st.title("🎲 Coinryze Analyzer")

uploaded = st.file_uploader("Upload CSV (Coinryze history)", type=["csv"])

def read_uploaded(u):
    try:
        u.seek(0)
    except Exception:
        pass
    return pd.read_csv(u)

def load_sample_csv():
    # try repo root sample_history.csv
    p = os.path.join(os.getcwd(), "sample_history.csv")
    if os.path.exists(p):
        return pd.read_csv(p)
    return None

df = None
if uploaded:
    try:
        if data_loader and hasattr(data_loader, "load_history"):
            df = data_loader.load_history(uploaded)
        else:
            df = read_uploaded(uploaded)
    except Exception as e:
        st.error(f"Failed reading uploaded CSV: {e}")
        df = None

# If no upload, try using sample_history.csv at repo root (optional)
if df is None:
    sample = load_sample_csv()
    if sample is not None:
        st.info("Using sample_history.csv from repo root.")
        df = sample
    else:
        st.info("Upload a CSV file or add sample_history.csv to the repo (optional).")

if df is not None:
    st.subheader("Preview (top rows)")
    st.dataframe(df.head(20))

    # Frequency of winning number
    if "Winning Number" in df.columns:
        st.subheader("Winning Number frequency")
        freq = df["Winning Number"].value_counts().sort_index()
        st.bar_chart(freq)

    # Frequency of winning color
    if "Winning Color" in df.columns:
        st.subheader("Winning Color frequency")
        freqc = df["Winning Color"].value_counts()
        st.bar_chart(freqc)

    # Example Markov predictor if present
    if predictor and hasattr(predictor, "MarkovPredictor") and "Winning Color" in df.columns:
        try:
            model = predictor.MarkovPredictor()
            model.fit(df["Winning Color"].tolist())
            last = df["Winning Color"].iloc[-1]
            pred = model.predict_next(last)
            st.success(f"Last Color: {last} — Predicted next: {pred}")
        except Exception as e:
            st.warning(f"Prediction failed: {e}")
else:
    st.stop()
