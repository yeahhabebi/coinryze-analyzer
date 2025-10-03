# models/train_lstm.py
import os
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.optimizers import Adam

CSV = os.getenv("TRAIN_CSV", "frontend/coinryze_history.csv")
OUT = os.getenv("LSTM_OUT", "models/lstm_model.h5")
TIMESTEPS = int(os.getenv("LSTM_TIMESTEPS", "30"))

df = pd.read_csv(CSV)
nums = df['number'].astype(float).tolist()

# Build sequences
X, y = [], []
for i in range(TIMESTEPS, len(nums)):
    seq = nums[i-TIMESTEPS:i]
    X.append(seq)
    y.append(nums[i])
X = np.array(X).reshape(-1, TIMESTEPS, 1)
y = np.array(y)

if len(X) == 0:
    raise SystemExit("Not enough data to train LSTM. Need at least TIMESTEPS+1 rows.")

model = Sequential([
    LSTM(64, input_shape=(TIMESTEPS,1)),
    Dense(32, activation='relu'),
    Dense(1, activation='linear')
])
model.compile(optimizer=Adam(0.001), loss='mse')
mc = ModelCheckpoint(OUT, save_best_only=True, monitor='loss')
model.fit(X, y, epochs=50, batch_size=32, callbacks=[mc])
print("Saved LSTM to", OUT)
