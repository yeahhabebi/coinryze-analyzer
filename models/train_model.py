# models/train_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

os.makedirs("models", exist_ok=True)
data_path = os.environ.get("HISTORY_CSV", "data/coinryze_history.csv")
df = pd.read_csv(data_path)

# Build simple features: for each row predict next number
# Create shifted target
df = df.reset_index(drop=True)
df['target'] = df['number'].shift(-1)
df = df.dropna()
# features: last, mean of last 5
X = []
y = []
for i in range(5, len(df)):
    last5 = df['number'].iloc[i-5:i].values
    X.append([last5[-1], last5.mean(), last5.std()])
    y.append(df['target'].iloc[i-1])
X = np.array(X)
y = np.array(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
print("Train score:", model.score(X_train, y_train), "Test score:", model.score(X_test, y_test))
joblib.dump(model, "models/rf_model.joblib")
print("Saved models/rf_model.joblib")
