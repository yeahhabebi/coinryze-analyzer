# frontend/app.py
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
