import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib


df = pd.read_csv("burnout_features.csv")


features = [
    col for col in df.columns
    if col not in ["Date", "Subject", "BurnoutLevel"]
]

X = df[features]
y = df["BurnoutLevel"]


encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)


X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)


model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

model.fit(X_train, y_train)


pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, pred))
print(classification_report(y_test, pred))


joblib.dump(model, "burnout_model.pkl")
joblib.dump(encoder, "label_encoder.pkl")

print("Model trained and saved successfully.")
