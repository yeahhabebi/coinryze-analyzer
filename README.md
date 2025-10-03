# 🎨 Coinryze Analyzer

Educational project to analyze **Coinryze colour trading game data**,  
automatically fetch new draws, run ML predictions, and visualize results with an interactive dashboard.  

---

## 🚀 Features
- ✅ Automated data collection (from [coinryze.org](https://coinryze.org))  
- ✅ Store history in CSV/Parquet  
- ✅ LSTM/ML backend predictions (number, color, size, odd/even)  
- ✅ FastAPI backend for serving predictions  
- ✅ APScheduler worker to run 24/7  
- ✅ Interactive dashboard with **Streamlit**  
- ✅ Toggle between *Sample Data* and *Live Data*  
- ✅ Colorful real-time charts & tables  

---

## 📂 Project Structure
coinryze-analyzer/
├── backend/ # FastAPI ML prediction API
│ └── app.py
├── fetcher/ # Worker service (scraper/scheduler)
│ └── fetch_coinryze.py
├── frontend/ # Streamlit dashboard
│ └── app.py
├── models/ # Saved ML models (e.g. LSTM / RF)
├── docker-compose.yml # Local multi-service runner
├── render.yaml # Render deploy configuration
├── requirements.txt # Python dependencies
├── README.md # Project docs
└── architecture.png # Architecture diagram

---

## 🖼️ Architecture
![CoinryzeAnalyzer Architecture](architecture.png)

---

## 📦 Setup (Local)

Clone repo and install:
```bash
git clone https://github.com/yourname/coinryze-analyzer.git
cd coinryze-analyzer
pip install -r requirements.txt

---
Run dashboard locally:
streamlit run frontend/app.py

Run backend API locally:
uvicorn backend.app:app --reload

Run worker locally:
python fetcher/fetch_coinryze.py

Run full stack with Docker:
docker-compose up --build


## 🌐 Deploy on Render
1. Push this repo to GitHub.
2. On [Render](https://dashboard.render.com):
   - Create **Web Service** for the streamlit frontend 
   - Build Command:
     ```bash
     pip install -r requirements.txt
     ```
   - Start Command:
     ```bash
     streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0
     ```
   - Create **Web Service** for the Backend (FastAPI)
   - Build Command:
     ```bash
     pip install -r requirements.txt
     ```
   - Start Command:
     ```bash
     uvicorn backend.app:app --host 0.0.0.0 --port $PORT

   - Create **Web Service** for the Fetcher
   - Build Command:
     ```bash
     pip install -r requirements.txt
     ```
   - Start Command:
     ```bash
     ./render-worker.sh

3. Open your live apps at:
   • Dashboard: https://your-frontend.onrender.com
   • API: https://your-backend.onrender.com

     ``
📌 Notes
  • This project is educational only (not financial advice).
  • Scraping must comply with coinryze.org  ~ ToS and rate limits.
  • Extendable: plug in new models, APIs, or databases.
---
👉 This `README.md` is **one-shot, copy-paste ready** for your repo root.  
It includes:
- All features  
- Local + Docker setup  
- Render deployment (Frontend + Backend + Worker)  
- Our architecture diagram  

---
