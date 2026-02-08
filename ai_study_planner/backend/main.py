from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np

app = FastAPI(title="AI Study Planner API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model + encoder + history
model = joblib.load("burnout_model.pkl")
encoder = joblib.load("label_encoder.pkl")
history = pd.read_csv("burnout_features.csv")

OPTIMAL_SLEEP = 7.5


# -------- Request Schema --------
class StudyInput(BaseModel):
    study_hours: float
    break_hours: float
    sleep_hours: float
    stress: int
    focus: int


# -------- Helpers --------
def calculate_fatigue(study, sleep, stress):
    return (stress * study) / max(sleep, 1)


def compute_productivity(study, sleep, stress, focus, consistency):

    if 5 <= study <= 7:
        study_score = 100
    elif study < 5:
        study_score = (study / 5) * 100
    else:
        study_score = max(0, 100 - (study - 7) * 15)

    focus_score = (focus / 5) * 100

    sleep_score = 100 if 7 <= sleep <= 8 else max(
        0, 100 - abs(OPTIMAL_SLEEP - sleep) * 20
    )

    stress_score = (1 - (stress - 1) / 4) * 100

    if consistency < 1:
        consistency_score = 100
    elif consistency < 2:
        consistency_score = 70
    else:
        consistency_score = 40

    return round(
        0.30 * study_score +
        0.20 * focus_score +
        0.20 * sleep_score +
        0.15 * stress_score +
        0.15 * consistency_score,
        1
    )


# -------- API --------
@app.post("/predict")
def predict(data: StudyInput):

    fatigue = calculate_fatigue(data.study_hours, data.sleep_hours, data.stress)
    study_load = data.study_hours / (data.sleep_hours + data.break_hours + 0.1)
    sleep_debt = max(0, 8 - data.sleep_hours)

    recent = history.tail(7)

    study_avg = recent["StudyHours"].mean()
    sleep_avg = recent["SleepHours"].mean()
    stress_avg = recent["StressLevel"].mean()
    fatigue_avg = recent["FatigueScore"].mean()
    consistency = recent["StudyHours"].std()

    fatigue_trend = fatigue - fatigue_avg

    productivity = compute_productivity(
        data.study_hours,
        data.sleep_hours,
        data.stress,
        data.focus,
        consistency
    )

    X = np.array([[data.study_hours, data.break_hours, data.sleep_hours,
                   data.stress, data.focus, fatigue, study_load,
                   sleep_debt, study_avg, sleep_avg, stress_avg,
                   fatigue_avg, consistency, fatigue_trend]])

    pred = model.predict(X)[0]
    burnout = encoder.inverse_transform([pred])[0]

    return {
        "burnout": burnout,
        "fatigue": round(fatigue, 2),
        "productivity": productivity
    }
