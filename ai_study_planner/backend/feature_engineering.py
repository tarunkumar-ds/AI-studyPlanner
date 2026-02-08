import pandas as pd


df = pd.read_csv("D:/ai_study_planner/study_burnout_dataset.csv")


df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")



df["StudyLoad"] = df["StudyHours"] / (
    df["SleepHours"] + df["BreakHours"]
)


df["SleepDebt"] = (8 - df["SleepHours"]).clip(lower=0)


df["Study_7day_avg"] = df["StudyHours"].rolling(7).mean()
df["Sleep_7day_avg"] = df["SleepHours"].rolling(7).mean()
df["Stress_7day_avg"] = df["StressLevel"].rolling(7).mean()
df["Fatigue_7day_avg"] = df["FatigueScore"].rolling(7).mean()


df["StudyConsistency"] = df["StudyHours"].rolling(7).std()


df["FatigueTrend"] = (
    df["FatigueScore"] - df["Fatigue_7day_avg"]
)


df.fillna(method="bfill", inplace=True)


df.to_csv("burnout_features.csv", index=False)

print("Feature engineering completed.")
