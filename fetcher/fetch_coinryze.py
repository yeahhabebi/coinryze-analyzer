import requests, csv, os
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

CSV_PATH = "frontend/coinryze_history.csv"

def fetch_and_save():
    url = "https://coinryze.org"  # TODO: replace with correct endpoint
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "lxml")

    # TODO: update selectors based on site’s HTML
    issue_id = soup.select_one(".issue-class").text.strip()
    number = soup.select_one(".number-class").text.strip()
    color = soup.select_one(".color-class").text.strip()
    size = soup.select_one(".size-class").text.strip()
    odd_even = "Odd" if int(number) % 2 else "Even"

    row = [issue_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), number, color, size, odd_even]
    write_header = not os.path.exists(CSV_PATH)

    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["issue_id","timestamp","number","color","size","odd_even"])
        writer.writerow(row)

    print("Saved row:", row)

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(fetch_and_save, "interval", minutes=1)
    print("Fetcher started... writing to", CSV_PATH)
    scheduler.start()
