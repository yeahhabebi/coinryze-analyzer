# fetcher/fetch_coinryze.py
import os, sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq

# Optional S3 upload
S3_BUCKET = os.getenv("S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION")
USE_S3 = bool(S3_BUCKET)

if USE_S3:
    import boto3
    s3_client = boto3.client(
        "s3",
        region_name=AWS_REGION or None
    )

URL = os.getenv("COINRYZE_URL", "https://coinryze.org")
CSV_PATH = os.getenv("CSV_PATH", "frontend/coinryze_history.csv")
PARQUET_PATH = os.getenv("PARQUET_PATH", "frontend/coinryze_history.parquet")
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL_MIN", "1"))

def upload_file_to_s3(local_path, s3_key):
    try:
        s3_client.upload_file(local_path, S3_BUCKET, s3_key)
        print(f"Uploaded {local_path} to s3://{S3_BUCKET}/{s3_key}")
    except Exception as e:
        print("S3 upload error:", e)

def fetch_and_save():
    try:
        r = requests.get(URL, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        # TODO: update selectors to match coinryze site
        issue_elem = soup.select_one(".issue-class")
        number_elem = soup.select_one(".number-class")
        color_elem = soup.select_one(".color-class")
        size_elem = soup.select_one(".size-class")

        if not (issue_elem and number_elem):
            print("Warning: required selectors not found on page.")
            return

        issue_id = issue_elem.text.strip()
        number_text = number_elem.text.strip()
        color = color_elem.text.strip() if color_elem else ""
        size = size_elem.text.strip() if size_elem else ""

        try:
            number = int(number_text)
        except ValueError:
            print("Invalid number:", number_text)
            return

        odd_even = "Odd" if number % 2 else "Even"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        row = {
            "issue_id": str(issue_id),
            "timestamp": timestamp,
            "number": int(number),
            "color": str(color),
            "size": str(size),
            "odd_even": str(odd_even)
        }

        # ---------- CSV ----------
        write_header = not os.path.exists(CSV_PATH)
        df_csv = pd.DataFrame([row])
        df_csv.to_csv(CSV_PATH, mode="a", header=write_header, index=False)

        # ---------- Parquet ----------
        df_parquet = pd.DataFrame([row])
        df_parquet = df_parquet.astype({
            "issue_id": str, "timestamp": str, "number": int,
            "color": str, "size": str, "odd_even": str
        })
        if os.path.exists(PARQUET_PATH):
            try:
                existing = pq.read_table(PARQUET_PATH).to_pandas()
                df_parquet = pd.concat([existing, df_parquet], ignore_index=True)
            except Exception as e:
                print("Warning reading existing parquet:", e)
        pq.write_table(pa.Table.from_pandas(df_parquet, preserve_index=False), PARQUET_PATH)

        print("Saved row:", row)

        # ---------- optional S3 upload ----------
        if USE_S3:
            try:
                upload_file_to_s3(CSV_PATH, os.path.basename(CSV_PATH))
                upload_file_to_s3(PARQUET_PATH, os.path.basename(PARQUET_PATH))
            except Exception as e:
                print("Error uploading to S3:", e)

    except Exception as e:
        print("Error fetching or saving:", e)

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(fetch_and_save, "interval", minutes=FETCH_INTERVAL)
    print(f"Fetcher started... writing to {CSV_PATH} and {PARQUET_PATH} every {FETCH_INTERVAL} min")
    # run one fetch immediately for quick sanity check
    fetch_and_save()
    scheduler.start()
