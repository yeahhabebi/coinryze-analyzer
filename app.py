import streamlit as st
import pandas as pd
import data_loader, predictor, simulator, utils

st.title("🎲 Coinryze Analyzer")

# Upload CSV
uploaded = st.file_uploader("Upload game history CSV", type="csv")

if uploaded:
    df = data_loader.load_history(uploaded)
    st.dataframe(df.head())

    # Frequency Analysis
    st.subheader("Frequency Analysis")
    freq = df['Winning Number'].value_counts()
    st.bar_chart(freq)

    # Markov Prediction
    st.subheader("Markov Chain Predictor")
    if 'Winning Color' in df.columns:
        markov = predictor.MarkovPredictor()
        markov.fit(df['Winning Color'].tolist())
        last = df['Winning Color'].iloc[-1]
        pred = markov.predict_next(last)
        st.write(f"Last Color: {last}, Predicted Next: {pred}")

    # Monte Carlo Simulation
    st.subheader("Monte Carlo Simulation")
    win_rate = simulator.monte_carlo_strategy(500)
    st.metric("Estimated Win Rate", f"{win_rate*100:.2f}%")

    # Chi-square placeholder
    st.subheader("Chi-square Test")
    st.write(utils.chi_square_test())
