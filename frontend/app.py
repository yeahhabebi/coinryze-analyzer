# CoinryzeAnalyzer — copy-paste files + step-by-step deploy & fetcher guide

This document contains everything you asked for:

* **Full `frontend/app.py`** (copy-paste ready)
* **Fetcher** template `fetcher/fetch_coinryze.py` with APScheduler (polite scraping template)
* `requirements.txt` and short `Procfile` / Render instructions
* How to adapt CSS selectors for coinryze.org (quick guide)
* Termux / Android (Samsung tablet) install notes + fixes for pandas
* Step-by-step Render deployment notes and troubleshooting

> **Important:** always check coinryze.org Terms of Service and `robots.txt` before scraping. If they provide an API: use the API instead of scraping.

---

## 1) `frontend/app.py` (copy-paste ready)

Create folder `frontend/` (if it does not exist) and create `frontend/app.py` with exactly the contents below.

```python
# frontend/app.py
# Streamlit frontend for CoinryzeAnalyzer
# Paste this file into frontend/app.py

import os
import io
import json
import requests
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime

# --- Configuration ---
BACKEND_URL = os.environ.get("BACKEND_URL", "")  # optional backend predictions endpoint
SAMPLE_PATH = os.path.join("frontend", "sample_history.csv")
AUTOLOAD_PATH = os.path.join("frontend", "coinryze_history.csv")  # autoload if present
COLOR_MAP = {
    'Red': '#e63946',
    'Blue': '#1d4ed8',
    'Green': '#2a9d8f',
    'Yellow': '#ffd166',
    # add more if you use different names
}

st.set_page_config(page_title="Coinryze Analyzer", layout="wide")
st.title("🎯 Coinryze Analyzer")

# --- Helpers ---
@st.cache_data
def load_csv_from_path(path_or_buffer):
    try:
        if hasattr(path_or_buffer, 'read'):
            return pd.read_csv(path_or_buffer)
        if not os.path.exists(path_or_buffer):
            return None
        return pd.read_csv(path_or_buffer)
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None


def compute_derived(df):
    # normalize column names
    df = df.copy()
    # common column name guesses
    possible_num_cols = [c for c in df.columns if "number" in c.lower() or "winning" in c.lower()]
    if not possible_num_cols:
        # try first numeric column
        for c in df.columns:
            if pd.api.types.is_integer_dtype(df[c]) or pd.api.types.is_float_dtype(df[c]):
                possible_num_cols = [c]
                break
    if possible_num_cols:
        num_col = possible_num_cols[0]
        df['number'] = pd.to_numeric(df[num_col], errors='coerce')
    else:
        df['number'] = pd.NA

    # color column
    color_cols = [c for c in df.columns if 'color' in c.lower()]
    df['color'] = df[color_cols[0]] if color_cols else pd.NA

    # size: example threshold approach (you can change). If numbers 1-9, treat >4 as Big.
    df['size'] = pd.NA
    if df['number'].notna().any():
        df['size'] = df['number'].apply(lambda v: 'Big' if v >= 5 else 'Small' if pd.notna(v) else pd.NA)
    df['odd_even'] = df['number'].apply(lambda v: 'Odd' if pd.notna(v) and int(v) % 2 == 1 else ('Even' if pd.notna(v) else pd.NA))
    return df


def style_df(df):
    # style sample for color column
    def color_bg(val):
        cmap = COLOR_MAP
        if pd.isna(val):
            return ''
        return f'background-color: {cmap.get(str(val), "transparent")}; color: white;'
    try:
        return df.style.applymap(lambda v: color_bg(v) if isinstance(v, str) else '', subset=['color'])
    except Exception:
        return df


# --- UI: Data selection ---
col1, col2 = st.columns([1, 3])
with col1:
    st.header("Data source")
    mode = st.radio("Pick data", ['Sample data (auto load)', 'Upload CSV', 'Autoload saved CSV (coinryze_history.csv)'])
    use_backend = st.checkbox("Enable backend predictions (use BACKEND_URL)", value=bool(BACKEND_URL))
    if use_backend and not BACKEND_URL:
        st.info("Set BACKEND_URL environment variable in your deployment to enable backend requests.")

with col2:
    # show preview markdown
    st.write("Use the controls on the left to pick a data source. You can also upload a CSV.\nColumns commonly used: issue_id / timestamp / Winning Number / Winning Color")

# load dataset
df = None
uploaded = None
if mode == 'Sample data (auto load)':
    df = load_csv_from_path(SAMPLE_PATH)
    if df is None:
        st.warning(f"Sample file not found at {SAMPLE_PATH}. You can upload a CSV instead or create {SAMPLE_PATH}.")
elif mode == 'Autoload saved CSV (coinryze_history.csv)':
    df = load_csv_from_path(AUTOLOAD_PATH)
    if df is None:
        st.warning(f"Autoload file {AUTOLOAD_PATH} not found.")
elif mode == 'Upload CSV':
    uploaded = st.file_uploader("Upload your coinryze CSV", type=['csv'], accept_multiple_files=False)
    if uploaded is not None:
        df = load_csv_from_path(uploaded)

if df is None:
    st.stop()

# --- Data processing and UI ---
st.subheader("Preview & summary")
df = compute_derived(df)

left, right = st.columns([1, 2])
with left:
    st.write("Rows:", len(df))
    if 'timestamp' in df.columns:
        try:
            tmin = pd.to_datetime(df['timestamp']).min()
            tmax = pd.to_datetime(df['timestamp']).max()
            st.write(f"Range: {tmin} — {tmax}")
        except Exception:
            pass
    if 'issue_id' in df.columns:
        st.write("Last issue:", df['issue_id'].astype(str).iat[-1])

with right:
    st.write("Frequency of numbers (top 10)")
    if 'number' in df.columns:
        freq = df['number'].value_counts().rename_axis('number').reset_index(name='count')
        chart = alt.Chart(freq.head(20)).mark_bar().encode(x='number:O', y='count:Q')
        st.altair_chart(chart, use_container_width=True)

st.subheader("Data table")
st.dataframe(df.head(200))

# styled view (color column highlighted)
try:
    st.write(style_df(df.head(200)).to_html(), unsafe_allow_html=True)
except Exception:
    pass

# Edit last record form
st.subheader("Edit / Add last result (manual)")
with st.form("edit_last"):
    issue = st.text_input("Issue id", value=str(df.get('issue_id', pd.Series([None])).iat[-1] if 'issue_id' in df else ''))
    ts = st.text_input("Timestamp (ISO)", value=str(df.get('timestamp', pd.Series([None])).iat[-1] if 'timestamp' in df else datetime.utcnow().isoformat()))
    num = st.number_input("Number", value=int(df['number'].dropna().iat[-1]) if df['number'].notna().any() else 0, step=1)
    color = st.selectbox("Color", options=list(COLOR_MAP.keys()), index=0)
    submitted = st.form_submit_button("Save to local coinryze_history.csv")
    if submitted:
        new = {'issue_id': issue, 'timestamp': ts, 'Winning Number': num, 'Winning Color': color}
        row = pd.DataFrame([new])
        outpath = AUTOLOAD_PATH
        if os.path.exists(outpath):
            try:
                old = pd.read_csv(outpath)
                combined = pd.concat([old, row], ignore_index=True)
            except Exception:
                combined = row
        else:
            combined = row
        combined.to_csv(outpath, index=False)
        st.success(f"Saved. Local file updated: {outpath}")

# Prediction call (local simulation or backend)
st.subheader("Prediction")
if st.button("Request prediction (backend)"):
    payload = {"recent": df[['number', 'color']].tail(50).to_dict(orient='records')}
    if BACKEND_URL:
        try:
            r = requests.post(BACKEND_URL.rstrip('/') + '/predict', json=payload, timeout=10)
            r.raise_for_status()
            st.write("Backend response:")
            st.json(r.json())
        except Exception as e:
            st.error(f"Backend request failed: {e}")
    else:
        # simple placeholder: most common color + next number by mode
        mode_num = int(df['number'].mode().iat[0]) if df['number'].notna().any() else 0
        mode_col = df['color'].mode().iat[0] if 'color' in df.columns and df['color'].notna().any() else 'Unknown'
        st.info("No BACKEND_URL — showing simple heuristic prediction")
        st.markdown(f"**Predicted next number:** {mode_num}\n\n**Predicted color:** {mode_col}")

st.markdown("---")
st.caption("Tip: set BACKEND_URL env var and run a backend `/predict` endpoint for proper ML predictions.")
```

---

## 2) `fetcher/fetch_coinryze.py` (polite scraping template + APScheduler)

Create folder `fetcher/` and drop this file as `fetcher/fetch_coinryze.py`.

```python
# fetcher/fetch_coinryze.py
# polite scraper template — adjust selectors to the actual coinryze page

import os
import time
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('fetcher')

BASE = os.environ.get('COINRYZE_BASE', 'https://coinryze.org')
HISTORY_CSV = os.environ.get('HISTORY_CSV', 'frontend/coinryze_history.csv')
HEADERS = {'User-Agent': 'CoinryzeAnalyzerBot/1.0 (+your-email@example.com)'}

# --- Adjust this function to match site structure ---

def fetch_recent():
    """
    Fetch recent draws from coinryze. Edit the CSS selectors below after inspecting the site.
    Return a pandas.DataFrame with columns: issue_id, timestamp, number, color
    """
    url = urljoin(BASE, '/')  # change to exact page like '/m/history' if needed
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')

    rows = []
    # Example: find table rows — change selector to match site
    # 1) Inspect coinryze HTML with your browser and update the selector below.
    for tr in soup.select('table tr'):
        cols = [td.get_text(strip=True) for td in tr.find_all('td')]
        if not cols:
            continue
        # heuristic: look for a row that has an issue id and a number
        # You must adapt the parsing logic to the real page.
        try:
            issue = cols[0]
            number = int(cols[1])
            timestamp = cols[2] if len(cols) > 2 else ''
            color = cols[3] if len(cols) > 3 else ''
            rows.append({'issue_id': issue, 'timestamp': timestamp, 'number': number, 'color': color})
        except Exception:
            continue

    df = pd.DataFrame(rows)
    logger.info(f'Fetched {len(df)} rows')
    return df


def append_new(df_new, out_path=HISTORY_CSV):
    if df_new.empty:
        logger.info('No new rows')
        return
    if os.path.exists(out_path):
        try:
            df_old = pd.read_csv(out_path)
        except Exception:
            df_old = pd.DataFrame()
        if not df_old.empty and 'issue_id' in df_old.columns:
            new = df_new[~df_new['issue_id'].isin(df_old['issue_id'])]
            combined = pd.concat([df_old, new], ignore_index=True)
        else:
            combined = pd.concat([df_old, df_new], ignore_index=True)
    else:
        combined = df_new

    combined.to_csv(out_path, index=False)
    logger.info(f'Appended data to {out_path} (total {len(combined)} rows)')


def job():
    try:
        df = fetch_recent()
        if not df.empty:
            append_new(df)
    except Exception as e:
        logger.exception('Error in fetch job: %s', e)


if __name__ == '__main__':
    logger.info('Starting fetcher scheduler (runs every minute)')
    sched = BlockingScheduler()
    sched.add_job(job, 'interval', minutes=1)
    try:
        job()  # run once at start
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()
```

> **Important:** The CSS selector `'table tr'` above is just a placeholder — use the quick guide below to find the correct selectors.

---

## 3) `requirements.txt`

```
streamlit
pandas
altair
requests
beautifulsoup4
lxml
apscheduler
```

(You can pin versions if desired; keep `streamlit` and `pandas` versions compatible with your environment.)

---

## 4) Render deployment: recommended settings (step-by-step)

1. Push your updated repo to GitHub (make sure you have `frontend/app.py` and `requirements.txt` at repo root). Your repo tree should look like:

```
coinryze-analyzer/
  frontend/
    app.py
    sample_history.csv   (optional)
    coinryze_history.csv (created by app or fetcher)
  fetcher/
    fetch_coinryze.py
  requirements.txt
  README.md
```

2. On Render **Create → Web Service** and connect your GitHub repo.

3. Fill these fields on the New Web Service page:

* **Name:** CoinryzeAnalyzer (or whatever)
* **Branch:** main
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0`

4. Environment variables (optional):

* `BACKEND_URL` — set your backend's URL (if you create one)
* `COINRYZE_BASE` — base coinryze URL for fetcher (if you run fetcher service)
* `HISTORY_CSV` — path where fetcher writes csv (default `frontend/coinryze_history.csv`)

5. If you want the fetcher to run 24/7 on Render, create a **separate Render Service** (type: Background Worker) or another Web Service with `Start Command` like `python fetcher/fetch_coinryze.py`.

6. Deploy. Watch **Events → Logs**. Common errors and fixes:

* `Error: File does not exist: frontend/app.py` — ensure file exists and path in Start Command is exact.
* `streamlit: command not found` — ensure `streamlit` listed in `requirements.txt` and build succeeded.
* `Exited with status 1 while building` — check build logs; often caused by missing files or wrong root directory.

---

## 5) Quick guide: adapt / discover CSS selectors for coinryze.org (step-by-step)

1. **Open coinryze page in desktop browser (Chrome recommended)**
2. Right-click the entry that contains one draw (a row showing draw number/color/time) and choose **Inspect**.
3. In DevTools, the DOM node for that draw will be highlighted. Look at the tag and its classes. Example: `<tr class="result-row">` or `<div class="draw-item">`.
4. Note the smallest selector that matches *each draw row*. Good selectors:

   * `table.history > tbody > tr` (if the page uses a table)
   * `.draw-item` or `.result-row`
5. Inside each row look for child elements that hold: issue id, number, timestamp, color. Note their selectors (e.g. `.issue`, `.num`, `.time`, `.color`).
6. Update `fetcher/fetch_coinryze.py` selectors accordingly:

   * replace `for tr in soup.select('table tr'):` with `for tr in soup.select('.draw-item'):` (example)
   * for each `tr`, find its children:

     ```py
     issue = tr.select_one('.issue').get_text(strip=True)
     number = int(tr.select_one('.num').get_text(strip=True))
     timestamp = tr.select_one('.time').get_text(strip=True)
     color = tr.select_one('.color').get_text(strip=True)
     ```
7. **Test locally**: run `python fetcher/fetch_coinryze.py` (it will run once then start scheduler). See console logs for the HTML you retrieved. If nothing found, print `soup.prettify()` and inspect output — sometimes the page uses JS and content is rendered dynamically (then you need Selenium).

**If page is JS-heavy**: coinryze may render history table client-side. In that case you have two options:

* Look for a network API used by the page. In DevTools → Network tab, reload and inspect XHR / fetch calls. If there is an API endpoint (JSON), call that directly from `requests`.
* If there is no API, use Selenium / Playwright to run the page headlessly (more complex on Termux / Render) — use only if allowed by ToS.

---

## 6) How to run fetcher 24/7 on Render (short)

* Option A (recommended): Create a new Render **Background Worker** or Web Service running `python fetcher/fetch_coinryze.py`. It will run the scheduler and fetch every minute.
* Option B: Use a VPS (DigitalOcean, Linode) or a small VM and run the script under `systemd` or `screen`.

---

## 7) Termux on Android (Samsung tablet) — install & fix notes

You already used Termux. A common problem is `pandas` requiring compilation. Here is a reliable sequence to install the packages used by the fetcher and run it locally in Termux.

1. Update termux packages

```bash
pkg update && pkg upgrade -y
pkg install -y python git clang make pkg-config libxml2 libxslt libffi openssl
termux-setup-storage   # allow access to storage if you need files in shared storage
```

2. Upgrade pip & install binaries (prefer-binary)

```bash
python -m pip install --upgrade pip setuptools wheel
pip install --prefer-binary requests beautifulsoup4 pandas lxml apscheduler
```

3. If pandas still tries building and fails, preinstall numpy and try again:

```bash
pip install --prefer-binary numpy
pip install --prefer-binary pandas
```

4. If you still get build errors, an alternative is to write a *fetcher* that doesn’t use pandas: use the Python `csv` module to append rows. That avoids heavy builds on Android.

---

### Lightweight CSV-only fetcher (no pandas)

If you cannot install `pandas` on Termux, use this tiny script instead of the previous fetcher — it writes CSV using the `csv` stdlib.

```python
# fetcher/fetch_coinryze_light.py
import os, requests, csv
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
BASE='https://coinryze.org'
OUT='frontend/coinryze_history.csv'
HEADERS={'User-Agent':'CoinryzeAnalyzerBot/1.0 (+you@example.com)'}

def fetch_once():
    r=requests.get(BASE, headers=HEADERS, timeout=15)
    soup=BeautifulSoup(r.text,'lxml')
    rows=[]
    for tr in soup.select('table tr'):
        cols=[td.get_text(strip=True) for td in tr.find_all('td')]
        if len(cols)>=2:
            rows.append((cols[0], cols[2] if len(cols)>2 else '', cols[1], cols[3] if len(cols)>3 else ''))
    if not rows:
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # append new rows only by issue_id check
    existing=set()
    if os.path.exists(OUT):
        with open(OUT,'r',newline='',encoding='utf8') as f:
            reader=csv.reader(f)
            for r in reader:
                if r: existing.add(r[0])
    with open(OUT,'a',newline='',encoding='utf8') as f:
        writer=csv.writer(f)
        for r in rows:
            if r[0] not in existing:
                writer.writerow(r)

if __name__=='__main__':
    sched=BlockingScheduler()
    sched.add_job(fetch_once,'interval',minutes=1)
    fetch_once()
    sched.start()
```

---

## 8) Colorful UI & toggles (how it’s implemented)

* The Streamlit app uses a `COLOR_MAP` dict: change the hex codes to match the colours used on coinryze.
* The UI shows color-coded table cells and charts built with Altair, which respects your color palette.

---

## 9) Final checklist & next steps

1. Create `frontend/` and paste `app.py`.
2. Add `fetcher/fetch_coinryze.py` (or `fetch_coinryze_light.py` for Termux without pandas).
3. Add `requirements.txt` and push to GitHub.
4. Deploy app on Render using the Start Command shown earlier.
5. (Optional) Create second Render service for `fetcher/` to run continuously.
6. Edit fetcher selectors after inspecting coinryze HTML.

---

If you want I can now:

* produce a **lighter CSV-only Streamlit `app.py`** that avoids pandas entirely (so Termux-friendly), OR
* produce the *exact* `frontend/sample_history.csv` example file (3–10 rows) so you can test the app right away.

Tell me which one I should generate next (I will paste it immediately).
