import joblib
import numpy as np
import os


# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load trained model
svm_model = joblib.load(
    os.path.join(BASE_DIR, "models", "svm_model.pkl")
)

# Load scaler
scaler = joblib.load(
    os.path.join(BASE_DIR, "models", "scaler.pkl")
)

def predict_student(student):

    # Convert categorical values
    internet = 1 if student["internet_access"] == "Yes" else 0

    extra = 1 if student["extra_classes"] == "Yes" else 0

    education = {
        "High School": 1,
        "Bachelor": 2,
        "Master": 3,
        "PhD": 4
    }.get(student["parent_education"], 1)

    features = [[
        student["study_hours_per_day"],
        student["attendance_percentage"],
        student["assignment_score"],
        student["midterm_score"],
        student["final_exam_score"],
        student["participation_score"],
        student["sleep_hours"],
        internet,
        extra,
        education
    ]]

    features = scaler.transform(features)

    prediction = svm_model.predict(features)[0]

    probabilities = svm_model.predict_proba(features)[0]

    print("\n========== AI Prediction ==========")
    print("Prediction:", prediction)
    print("Probability Array:", probabilities)
    print("Highest Probability:", max(probabilities))
    print("Confidence:", round(max(probabilities) * 100, 2), "%")
    print("===================================\n")

    confidence = round(max(probabilities) * 100, 2)

    return prediction, confidence

