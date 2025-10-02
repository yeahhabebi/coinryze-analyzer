import os
import requests, pandas as pd
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq

# Environment variables
URL = os.getenv("COINRYZE_URL", "https://coinryze.org")
CSV_PATH = os.getenv("CSV_PATH", "frontend/coinryze_history.csv")
PARQUET_PATH = os.getenv("PARQUET_PATH", "frontend/coinryze_history.parquet")
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL_MIN", "1"))

def fetch_and_save():
    try:
        r = requests.get(URL, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        issue_id = soup.select_one(".issue-class").text.strip()
        number_text = soup.select_one(".number-class").text.strip()
        color = soup.select_one(".color-class").text.strip()
        size = soup.select_one(".size-class").text.strip()

        try:
            number = int(number_text)
        except ValueError:
            print("Invalid number:", number_text)
            return

        odd_even = "Odd" if number % 2 else "Even"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = {"issue_id": issue_id, "timestamp": timestamp, "number": number,
               "color": color, "size": size, "odd_even": odd_even}

        # CSV
        write_header = not os.path.exists(CSV_PATH)
        pd.DataFrame([row]).to_csv(CSV_PATH, mode="a", header=write_header, index=False)

        # Parquet
        df_parquet = pd.DataFrame([row])
        df_parquet = df_parquet.astype({
            "issue_id": str, "timestamp": str, "number": int,
            "color": str, "size": str, "odd_even": str
        })
        if os.path.exists(PARQUET_PATH):
            df_existing = pq.read_table(PARQUET_PATH).to_pandas()
            df_parquet = pd.concat([df_existing, df_parquet], ignore_index=True)
        pq.write_table(pa.Table.from_pandas(df_parquet, preserve_index=False), PARQUET_PATH)

        print("Saved row:", row)

    except Exception as e:
        print("Error fetching or saving:", e)

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(fetch_and_save, "interval", minutes=FETCH_INTERVAL)
    print(f"Fetcher started... writing to {CSV_PATH} and {PARQUET_PATH} every {FETCH_INTERVAL} min")
    scheduler.start()
