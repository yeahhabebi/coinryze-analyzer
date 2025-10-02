import os, requests, pandas as pd
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq

S3_BUCKET = os.getenv("S3_BUCKET")
USE_S3 = bool(S3_BUCKET)
if USE_S3:
    import boto3
    s3_client = boto3.client("s3", region_name=os.getenv("AWS_REGION"))

URL = os.getenv("COINRYZE_URL","https://coinryze.org")
CSV_PATH = os.getenv("CSV_PATH","frontend/coinryze_history.csv")
PARQUET_PATH = os.getenv("PARQUET_PATH","frontend/coinryze_history.parquet")
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL_MIN","1"))
USER_AGENT = os.getenv("USER_AGENT","CoinryzeAnalyzerBot/1.0 (+contact@example.com)")
HEADERS = {"User-Agent": USER_AGENT}

def upload_file_to_s3(local_path, s3_key):
    try:
        s3_client.upload_file(local_path, S3_BUCKET, s3_key)
        print(f"Uploaded {local_path} to s3://{S3_BUCKET}/{s3_key}")
    except Exception as e:
        print("S3 upload error:", e)

def parse_latest_draws(soup):
    rows = []
    for item in soup.select(".draw-row"):  # <-- update selector
        try:
            issue = item.select_one(".issue").text.strip()
            number = int(item.select_one(".number").text.strip())
            timestamp = item.select_one(".time").text.strip()
            color = item.select_one(".color").text.strip() if item.select_one(".color") else ""
            size = item.select_one(".size").text.strip() if item.select_one(".size") else ""
            rows.append({
                "issue_id": issue,
                "timestamp": timestamp,
                "number": number,
                "color": color,
                "size": size,
                "odd_even": "Odd" if number % 2 else "Even"
            })
        except Exception:
            continue
    return rows

def fetch_and_save():
    try:
        resp = requests.get(f"{URL}/m/history", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text,"lxml")
        scraped = parse_latest_draws(soup)
        if not scraped:
            print("No draws parsed, update selectors.")
            return

        existing_df = pd.DataFrame()
        if os.path.exists(PARQUET_PATH):
            try:
                existing_df = pq.read_table(PARQUET_PATH).to_pandas()
            except:
                pass

        existing_issues = set(existing_df['issue_id'].astype(str).tolist()) if not existing_df.empty else set()
        new_rows = [r for r in scraped if str(r['issue_id']) not in existing_issues]

        if not new_rows:
            print("No new rows.")
            return

        df_new = pd.DataFrame(new_rows)
        df_new.to_csv(CSV_PATH, mode='a', header=not os.path.exists(CSV_PATH), index=False)

        df_total = pd.concat([existing_df, df_new], ignore_index=True) if not existing_df.empty else df_new
        df_total = df_total.astype({"issue_id":str,"timestamp":str,"number":int,"color":str,"size":str,"odd_even":str})
        pq.write_table(pa.Table.from_pandas(df_total, preserve_index=False), PARQUET_PATH)

        if USE_S3:
            upload_file_to_s3(CSV_PATH, os.path.basename(CSV_PATH))
            upload_file_to_s3(PARQUET_PATH, os.path.basename(PARQUET_PATH))

        print(f"Saved {len(new_rows)} new rows at {datetime.utcnow().isoformat()}")
    except Exception as e:
        print("Error fetch_and_save:", e)

if __name__=="__main__":
    fetch_and_save()
    scheduler = BlockingScheduler()
    scheduler.add_job(fetch_and_save, "interval", minutes=FETCH_INTERVAL)
    print(f"Worker started, fetching every {FETCH_INTERVAL} min")
    scheduler.start()
