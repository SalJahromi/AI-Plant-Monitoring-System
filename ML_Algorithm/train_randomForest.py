import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, confusion_matrix

# -----------------------------
# Load dataset
# -----------------------------
df = pd.read_csv("plant_health_data.csv")


# -----------------------------
# Encode target labels
# -----------------------------
custom_mapping = {
    "Healthy": 0,
    "Moderate Stress": 1,
    "High Stress": 2
}

df["Plant_Health_Status_Encoded"] = df["Plant_Health_Status"].map(custom_mapping)


# -----------------------------
# Reduced feature set
# -----------------------------
features = [
    "Ambient_Temperature",
    "Soil_Moisture",
    "Light_Intensity",
    "Humidity"
]

X = df[features]
y = df["Plant_Health_Status_Encoded"]


# -----------------------------
# Train/test split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# -----------------------------
# Scale features
# -----------------------------
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


# -----------------------------
# Train final model
# -----------------------------
model = RandomForestClassifier(random_state=42)

model.fit(X_train_scaled, y_train)


# -----------------------------
# Evaluate model
# -----------------------------
y_train_pred = model.predict(X_train_scaled)
y_test_pred = model.predict(X_test_scaled)
y_test_prob = model.predict_proba(X_test_scaled)

train_accuracy = accuracy_score(y_train, y_train_pred)
test_accuracy = accuracy_score(y_test, y_test_pred)
auc = roc_auc_score(y_test, y_test_prob, multi_class="ovr")

print("\n==============================")
print("Random Forest Training Results")
print("==============================")

print(f"Training Accuracy: {train_accuracy:.3f}")
print(f"Testing Accuracy:  {test_accuracy:.3f}")
print(f"AUC Score:         {auc:.3f}")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_test_pred,
        target_names=["Healthy", "Moderate Stress", "High Stress"]
    )
)

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_test_pred)
print(cm)

print("\nFeature Importance:")
for feature, importance in zip(features, model.feature_importances_):
    print(f"{feature}: {importance:.3f}")


# -----------------------------
# Save model, scaler, and labels
# -----------------------------
model_package = {
    "model": model,
    "scaler": scaler,
    "features": features,
    "label_mapping": {
        0: "Healthy",
        1: "Moderate Stress",
        2: "High Stress"
    }
}

joblib.dump(model_package, "plant_health_model.pkl")

print("\nModel saved as plant_health_model.pkl")