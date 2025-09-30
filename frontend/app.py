import os
import pandas as pd
import streamlit as st

st.title("Coinryze Analyzer")

# --- Automatic file loader ---
uploaded = st.file_uploader("Upload your game history CSV", type="csv")

df = None
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        st.success("Loaded uploaded CSV ✅")
    except Exception as e:
        st.error(f"Could not read uploaded CSV: {e}")

# If no file uploaded, try sample_history.csv from frontend/
if df is None:
    here = os.path.dirname(os.path.abspath(__file__))
    sample_path = os.path.join(here, "sample_history.csv")

    if os.path.exists(sample_path):
        try:
            df = pd.read_csv(sample_path)
            st.info("Loaded bundled sample dataset 📂 (sample_history.csv)")
        except Exception as e:
            st.error(f"Found sample CSV but failed to load: {e}")

# Final fallback
if df is None:
    st.warning("⚠️ No CSV loaded. Please upload a file to continue.")
else:
    st.write("Preview of dataset:")
    st.dataframe(df.head())

    # 🔽 put your existing charts/logic here, e.g.:
    # draw trends, run predictions, etc.
