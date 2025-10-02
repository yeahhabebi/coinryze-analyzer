import requests, os
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

CSV_PATH = "frontend/coinryze_history.csv"
PARQUET_PATH = "frontend/coinryze_history.parquet"

def fetch_and_save():
    try:
        url = "https://coinryze.org"  # TODO: replace with correct endpoint
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        # TODO: update selectors based on site’s HTML
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

        row = {
            "issue_id": issue_id,
            "timestamp": timestamp,
            "number": number,
            "color": color,
            "size": size,
            "odd_even": odd_even
        }

        # Append to CSV
        write_header = not os.path.exists(CSV_PATH)
        df_csv = pd.DataFrame([row])
        df_csv.to_csv(CSV_PATH, mode="a", header=write_header, index=False)

        # Append to Parquet safely
        df_parquet = pd.DataFrame([row])
        # Ensure types are consistent
        df_parquet = df_parquet.astype({
            "issue_id": str,
            "timestamp": str,
            "number": int,
            "color": str,
            "size": str,
            "odd_even": str
        })
        if os.path.exists(PARQUET_PATH):
            table_existing = pq.read_table(PARQUET_PATH)
            df_existing = table_existing.to_pandas()
            df_parquet = pd.concat([df_existing, df_parquet], ignore_index=True)
        table = pa.Table.from_pandas(df_parquet, preserve_index=False)
        pq.write_table(table, PARQUET_PATH)

        print("Saved row:", row)

    except Exception as e:
        print("Error fetching or saving:", e)

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(fetch_and_save, "interval", minutes=1)
    print("Fetcher started... writing to", CSV_PATH, "and", PARQUET_PATH)
    scheduler.start()
