# backend/app.py
import os
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(title="Coinryze Backend")

MODEL_PATH = os.environ.get("MODEL_PATH", "models/rf_model.joblib")

# Pydantic request shape
class PredictRequest(BaseModel):
    last_numbers: List[int]

class PredictResponse(BaseModel):
    predicted_number: int
    predicted_color: str
    predicted_size: str
    odd_even: str
    confidence: float = 0.0

# load model once at startup
model = None
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    model = None
    print("Warning: Could not load model:", e)


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available on server.")
    # Basic feature creation: use last N numbers -> simple features: last number, mean, std
    arr = np.array(req.last_numbers[-10:]) if len(req.last_numbers) else np.array([0])
    feat = np.array([[arr[-1], arr.mean(), arr.std()]])
    pred = model.predict(feat)[0]
    # infer properties
    odd_even = "even" if pred % 2 == 0 else "odd"
    # example color rule: even -> green, odd -> red
    color = "Green" if pred % 2 == 0 else "Red"
    size = "Big" if pred >= 25 else "Small"  # adjust threshold to suit the game's range
    conf = 0.6
    return PredictResponse(
        predicted_number=int(pred),
        predicted_color=color,
        predicted_size=size,
        odd_even=odd_even,
        confidence=conf
    )
