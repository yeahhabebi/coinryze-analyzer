# fetcher/fetch_coinryze.py


BASE = os.environ.get('COINRYZE_BASE', 'https://coinryze.org')
HISTORY_CSV = os.environ.get('HISTORY_CSV', 'frontend/coinryze_history.csv')
HEADERS = {'User-Agent': 'CoinryzeAnalyzerBot/1.0 (+your-email@example.com)'}


# --- Adjust this function to match site structure ---


def fetch_recent():
"""
Fetch recent draws from coinryze. Edit the CSS selectors below after inspecting the site.
Return a pandas.DataFrame with columns: issue_id, timestamp, number, color
"""
url = urljoin(BASE, '/') # change to exact page like '/m/history' if needed
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
if not df_old.empty and 'issue_id
