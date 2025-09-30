# fetcher/fetch_coinryze.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

BASE = "https://coinryze.org"
HEADERS = {"User-Agent": "CoinryzeAnalyzerBot/1.0 (+your-email@example.com)"}
OUT_CSV = os.environ.get("HISTORY_CSV", "data/coinryze_history.csv")

def fetch_recent():
    url = BASE + "/m/history"  # example path - update to the real one
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    rows = []
    # You must inspect the page and replace the selector below:
    for row in soup.select(".history-row"):  # <-- adapt!
        issue = row.select_one(".issue").get_text(strip=True)
        number = row.select_one(".number").get_text(strip=True)
        color = row.select_one(".color").get_text(strip=True) if row.select_one(".color") else ""
        timestamp = row.select_one(".time").get_text(strip=True) if row.select_one(".time") else ""
        rows.append({"issue": issue, "number": int(number), "color": color, "ts": timestamp})
    return pd.DataFrame(rows)

def main():
    os.makedirs("data", exist_ok=True)
    try:
        df = fetch_recent()
        if not df.empty:
            if os.path.exists(OUT_CSV):
                old = pd.read_csv(OUT_CSV)
                combined = pd.concat([old, df]).drop_duplicates(subset=["issue"]).sort_values("issue")
            else:
                combined = df
            combined.to_csv(OUT_CSV, index=False)
            print("Wrote", len(combined), "rows to", OUT_CSV)
        else:
            print("No rows fetched")
    except Exception as e:
        print("Fetch error:", e)

if __name__ == "__main__":
    main()
