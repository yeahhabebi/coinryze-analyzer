# Coinryze Analyzer

Educational project to analyze **Coinryze colour trading game data**, 
run predictions, and visualize results.

## 🚀 Features
- Load CSV game history
- Frequency & Chi-square analysis
- Markov chain predictor
- Monte Carlo simulator for strategies
- Interactive dashboard with Streamlit

---

## 📦 Setup (Local)
```bash
pip install -r requirements.txt
streamlit run frontend/app.py
```

---

## 🌐 Deploy on Render
1. Push this repo to GitHub.
2. On [Render](https://dashboard.render.com):
   - Create **Web Service**
   - Build Command:
     ```bash
     pip install -r requirements.txt
     ```
   - Start Command:
     ```bash
     streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0
     ```

3. Open your live app at:
```
https://your-app-name.onrender.com
```

---
