
import pandas as pd
import joblib


model_package = joblib.load("ML_Algorithm/plant_health_model.pkl")

model = model_package["model"]
scaler = model_package["scaler"]
features = model_package["features"]
label_mapping = model_package["label_mapping"]


def predict_plant_health(ambient_temperature, soil_moisture, light_intensity, humidity):
    input_data = pd.DataFrame([{
        "Ambient_Temperature": ambient_temperature,
        "Soil_Moisture": soil_moisture,
        "Light_Intensity": light_intensity,
        "Humidity": humidity
    }])

    input_scaled = scaler.transform(input_data)

    prediction = model.predict(input_scaled)[0]
    probabilities = model.predict_proba(input_scaled)[0]

    print(probabilities)

    return {
        "prediction": label_mapping[prediction],
        "healthy_probability": round(float(probabilities[0]), 3),
        "moderate_stress_probability": round(float(probabilities[1]), 3),
        "high_stress_probability": round(float(probabilities[2]), 3),
        "confidence": round(float(max(probabilities)), 3)
    }

def diagnose_with_sensors(sensor_data):

    readings = {}

    try:
        parts = sensor_data.split(",")

        for part in parts:
            key, value = part.split(":")
            readings[key.strip()] = float(value.strip())

    except Exception:
        return None
    

    if readings is None:
          return {
              "success": False,
              "message": "I could not read my sensor data clearly enough to diagnose myself."
          }

    required_keys = ["TEMP", "SOIL", "LUM", "HUM"]


    for key in required_keys:
        if key not in readings:
            return {
                "success": False,
                "message": f"I am missing the {key} sensor reading, so I cannot diagnose myself."
            }

    result = predict_plant_health(
        ambient_temperature=readings["TEMP"],
        soil_moisture=readings["SOIL"],
        light_intensity=readings["LUM"],
        humidity=readings["HUM"]
    )

    return {
        "success": True,
        "sensor_readings": readings,
        "prediction": result
    }


