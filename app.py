# app.py
import streamlit as st
import pandas as pd

# Flexible imports: either backend package or modules at root
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
st.markdown("Upload a Coinryze CSV history file (or use sample_history.csv).")

uploaded = st.file_uploader("Upload CSV", type=["csv"])

def read_csv_file(u):
    try:
        u.seek(0)
    except Exception:
        pass
    return pd.read_csv(u)

if uploaded:
    try:
        if data_loader and hasattr(data_loader, "load_history"):
            df = data_loader.load_history(uploaded)
        else:
            df = read_csv_file(uploaded)
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        raise

    st.subheader("Preview data")
    st.dataframe(df.head(20))

    if "Winning Number" in df.columns:
        st.subheader("Winning Number frequency")
        freq = df["Winning Number"].value_counts().sort_index()
        st.bar_chart(freq)

    if "Winning Color" in df.columns:
        st.subheader("Winning Color frequency")
        freqc = df["Winning Color"].value_counts()
        st.bar_chart(freqc)

    if predictor and hasattr(predictor, "MarkovPredictor") and "Winning Color" in df.columns:
        try:
            model = predictor.MarkovPredictor()
            model.fit(df["Winning Color"].tolist())
            last = df["Winning Color"].iloc[-1]
            pred = model.predict_next(last)
            st.info(f"Last Color: {last} — Predicted next: {pred}")
        except Exception as e:
            st.write("Prediction failed:", e)
else:
    st.info("Please upload a CSV file. (Try sample_history.csv in the repo.)")
