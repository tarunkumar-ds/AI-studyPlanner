from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

model = joblib.load(BASE_DIR / "burnout_model.pkl")
encoder = joblib.load(BASE_DIR / "label_encoder.pkl")
history = pd.read_csv(BASE_DIR / "burnout_features.csv")


OPTIMAL_SLEEP = 7.5

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout="wide"
)

# ================= PURE BLACK & WHITE THEME =================
st.markdown("""
<style>

html, body, [class*="css"] {
    background: white !important;
    color: black !important;
}

section[data-testid="stSidebar"] {
    background: black !important;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}

div[data-testid="metric-container"] {
    background: white !important;
    border: 1px solid black !important;
    padding: 12px !important;
}

button {
    background: black !important;
    color: white !important;
}

input, textarea, select {
    border: 1px solid black !important;
}

div[data-baseweb="slider"] > div,
div[data-baseweb="slider"] span {
    background: black !important;
}

div[data-baseweb="slider"] div[role="slider"] {
    background: black !important;
    border: 2px solid white !important;
}

canvas {
    filter: grayscale(100%) !important;
}

</style>
""", unsafe_allow_html=True)
# ===========================================================

st.title(APP_TITLE)
st.caption("Behavioral ML • Productivity Intelligence • Adaptive Planning")


def load_artifacts():
    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)
    return model, encoder


def calculate_fatigue(study_hours, sleep_hours, stress_level):
    return (stress_level * study_hours) / max(sleep_hours, 1)


def compute_productivity(study_hours, sleep_hours, stress, focus, consistency):

    if 5 <= study_hours <= 7:
        study_score = 100
    elif study_hours < 5:
        study_score = (study_hours / 5) * 100
    else:
        study_score = max(0, 100 - (study_hours - 7) * 15)

    focus_score = (focus / 5) * 100

    sleep_score = 100 if 7 <= sleep_hours <= 8 else max(
        0, 100 - abs(OPTIMAL_SLEEP - sleep_hours) * 20
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


# ================= LOAD =================

model, encoder = load_artifacts()
history = pd.read_csv(HISTORY_PATH)

# ================= SIDEBAR =================

st.sidebar.header("Today's Study Data")

study_hours = st.sidebar.slider("Study Hours", 0.0, 12.0, 5.0)
break_hours = st.sidebar.slider("Break Hours", 0.0, 4.0, 1.0)
sleep_hours = st.sidebar.slider("Sleep Hours", 0.0, 10.0, 7.0)
stress_level = st.sidebar.slider("Stress Level (1–5)", 1, 5, 3)
focus_level = st.sidebar.slider("Focus Level (1–5)", 1, 5, 3)

# ================= FEATURES =================

fatigue_score = calculate_fatigue(study_hours, sleep_hours, stress_level)
study_load = study_hours / (sleep_hours + break_hours + 0.1)
sleep_debt = max(0, 8 - sleep_hours)

recent = history.tail(7)

study_avg = recent["StudyHours"].mean()
sleep_avg = recent["SleepHours"].mean()
stress_avg = recent["StressLevel"].mean()
fatigue_avg = recent["FatigueScore"].mean()
consistency = recent["StudyHours"].std()

fatigue_trend = fatigue_score - fatigue_avg

productivity_score = compute_productivity(
    study_hours,
    sleep_hours,
    stress_level,
    focus_level,
    consistency
)

X = np.array([[study_hours, break_hours, sleep_hours, stress_level,
               focus_level, fatigue_score, study_load, sleep_debt,
               study_avg, sleep_avg, stress_avg, fatigue_avg,
               consistency, fatigue_trend]])

prediction = model.predict(X)[0]
confidence = model.predict_proba(X).max()
burnout_level = encoder.inverse_transform([prediction])[0]

# ================= DASHBOARD =================

st.subheader("Daily Performance Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Burnout Level", burnout_level)
c2.metric("Confidence", f"{confidence*100:.1f}%")
c3.metric("Fatigue Score", round(fatigue_score, 2))
c4.metric("Productivity", f"{productivity_score}/100")

st.divider()

# ================= BURNOUT DISPLAY =================

st.markdown(f"## Current Burnout Level: **{burnout_level}**")

# ================= STUDY PLAN =================

st.subheader("Adaptive Study Plan")

if burnout_level == "High":
    st.markdown("""
### High Burnout Plan
- Study: **2–3 hours**
- Break every **30 minutes**
- Sleep **8–9 hours**
- Light revision only
- Take rest tomorrow
""")

elif burnout_level == "Medium":
    st.markdown("""
### Balanced Plan
- Study: **4–5 hours**
- Break: 10 min every 45 min
- Sleep: **7–8 hours**
- Mix easy + medium topics
""")

else:
    st.markdown("""
### Productive Plan
- Study: **6–8 hours**
- Break every hour
- Minimum **7 hours sleep**
- Focus on difficult topics
""")

# ================= PRODUCTIVITY =================

st.subheader("Productivity Interpretation")

if productivity_score >= 85:
    st.markdown("Excellent productivity — keep going!")
elif productivity_score >= 70:
    st.markdown("Very good productivity — minor improvements possible.")
elif productivity_score >= 50:
    st.markdown("Moderate productivity — improve sleep and focus.")
else:
    st.markdown("Low productivity — burnout prevention recommended.")

# ================= TRENDS =================

st.subheader("Weekly Behavior Trends")

trend = history.tail(14)[
    ["StudyHours", "SleepHours", "StressLevel", "FatigueScore"]
]

st.line_chart(trend)

st.caption("AI Study Planner | Monochrome Edition")




