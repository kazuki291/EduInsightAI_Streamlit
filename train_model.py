import pandas as pd 
from sklearn.svm import SVC
from sklearn.tree import plot_tree
from sklearn.metrics import accuracy_score 
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import RandomForestClassifier
import seaborn as sns
import matplotlib.pyplot as plt

# ------------------------------------- 
# STEP 1: LOAD DATASET 
# ------------------------------------- 
dataset = pd.read_csv('student_performance_data.csv') 

# ------------------------------------- 
# STEP 2: FILTER RELEVANT FEATURES 
# ------------------------------------- 
dataset['Test'] = dataset['final_exam_score'] 
dataset['Homework'] = dataset['assignment_score'] 
dataset['Punctuality'] = dataset['attendance_percentage'] 

# ------------------------------------- 
# STEP 3: CREATING ACTUAL SCORE 
# ------------------------------------- 
dataset['Score'] = (
    dataset['Test'] * 0.4 + 
    dataset['Homework'] * 0.35 + 
    dataset['Punctuality'] * 0.25
)

# ------------------------------------- 
# STEP 3.5: BASIC DATA ANALYSIS (EDA)
# ------------------------------------- 

# Average values of main features
avg_values = dataset[['Test', 'Homework', 'Punctuality']].mean()

print("\nAverage Performance Metrics:\n", avg_values)

# Plot bar chart
avg_values.plot(kind='bar', figsize=(8,5))

plt.title('Average Student Performance Metrics')
plt.ylabel('Score / Percentage')
plt.xlabel('Metrics')

plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()

plt.savefig("average_metrics.png")
plt.close()

# ------------------------------------- 
# STEP 4: CREATE PERFORMANCE CATEGORIES
# ------------------------------------- 
def get_performance(score):
    if score >= 75:
        return "High Performance"
    elif score >= 50:
        return "Moderate Performance"
    else:
        return "Low Performance"
    
# ------------------------------------- 
# STEP 4.5: EXPLANATION FUNCTION
# ------------------------------------- 
def explain_prediction(exam, hw, att):
    explanation = []

    # Exam
    if exam >= 75:
        explanation.append("Exam score is high")
    elif exam >= 50:
        explanation.append("Exam score is moderate")
    else:
        explanation.append("Exam score is low")

    # Homework
    if hw >= 75:
        explanation.append("Assignment score is high")
    elif hw >= 50:
        explanation.append("Assignment score is average")
    else:
        explanation.append("Assignment score is low")

    # Attendance
    if att >= 75:
        explanation.append("Attendance is good")
    elif att >= 50:
        explanation.append("Attendance is moderate")
    else:
        explanation.append("Attendance is poor")

    return explanation

# ------------------------------------- 
# STEP 4.6: Input Validation (Edge Cases)
# ------------------------------------- 

def validate_input(exam, hw, att):
    if exam is None or hw is None or att is None:
        return "Missing input values"

    if not (0 <= exam <= 100):
        return "Exam score must be between 0 and 100"

    if not (0 <= hw <= 100):
        return "Assignment score must be between 0 and 100"

    if not (0 <= att <= 100):
        return "Attendance must be between 0 and 100"

    return "Valid"

# ------------------------------------- 
# STEP 5: PREPARE DATA FOR MODEL
# ------------------------------------- 
dataset['Result'] = dataset['Score'].apply(get_performance)
X = dataset[['Test', 'Homework', 'Punctuality']] 
y = dataset['Result'] 

# ------------------------------------- 
# STEP 6: SPLIT DATA
# ------------------------------------- 
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
# ------------------------------------- 
# STEP 7: TRAIN MODEL
# ------------------------------------- 

clf = DecisionTreeClassifier(max_depth=3, random_state=42)
clf.fit(X_train, y_train)
print("Model trained successfully ") 

# ------------------------------------- 
# STEP 8: EVALUATE MODEL 
# ------------------------------------- 
print("Evaluating model...")
print("Starting prediction...")
predictions = clf.predict(X_test) 
accuracy = accuracy_score(y_test, predictions) 

print(f"Decision Tree Accuracy: {accuracy:.2%}")

# ------------------------------------- 
# STEP 8.5: VISUALIZE DECISION TREE
# ------------------------------------- 

plt.figure(figsize=(12,8))
plot_tree(
    clf,
    feature_names=['Test', 'Homework', 'Punctuality'],
    class_names=clf.classes_,
    filled=True
)

plt.savefig("decision_tree.png")
plt.close()

# ------------------------------------- 
# STEP 8.6: CONFUSION MATRIX  
# ------------------------------------- 

cm = confusion_matrix(y_test, predictions)

plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=clf.classes_,
            yticklabels=clf.classes_)

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")

plt.xticks(rotation=30)
plt.yticks(rotation=0)
plt.tight_layout()

plt.savefig("confusion_matrix.png")
plt.close()

# ------------------------------------- 
# STEP 8.7: RANDOM FOREST MODEL
# ------------------------------------- 

# Create model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train
rf_model.fit(X_train, y_train)

# Predict
rf_predictions = rf_model.predict(X_test)

# Accuracy
rf_accuracy = accuracy_score(y_test, rf_predictions)

print(f"Random Forest Accuracy: {rf_accuracy:.2%}")

# -------------------------------------
# STEP 8.75: TRAIN SVM MODEL
# -------------------------------------

svm_model = SVC()

svm_model.fit(X_train, y_train)

svm_predictions = svm_model.predict(X_test)

svm_accuracy = accuracy_score(y_test, svm_predictions)

print(f"SVM Accuracy: {svm_accuracy:.2%}")

# ------------------------------------- 
# STEP 8.8: MODEL COMPARISON
# ------------------------------------- 

print("\nModel Comparison:")
print("Decision Tree Accuracy:", accuracy)
print("Random Forest Accuracy:", rf_accuracy)
print("SVM Accuracy:", svm_accuracy)

# ------------------------------------- 
# STEP 8.9: RANDOM FOREST FEATURE IMPORTANCE
# ------------------------------------- 

importances = rf_model.feature_importances_

feature_importance_df = pd.DataFrame({
    'Feature': X.columns,
    'Importance': importances
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

print("\nFeature Importance:\n", feature_importance_df)

# Plot
feature_importance_df.plot(kind='bar', x='Feature', y='Importance', legend=False, figsize=(6,4))

plt.title('Feature Importance (Random Forest)')
plt.ylabel('Importance Score')

plt.tight_layout()
plt.savefig("feature_importance.png")
plt.close()

# -------------------------------------
# STEP 8.91: MODEL ACCURACY CHART
# -------------------------------------

models = ['Decision Tree', 'Random Forest', 'SVM']
scores = [accuracy * 100, rf_accuracy * 100, svm_accuracy * 100]

plt.figure(figsize=(8,5))
plt.bar(models, scores)

plt.title("Model Accuracy Comparison")
plt.ylabel("Accuracy (%)")
plt.xlabel("Algorithms")
plt.ylim(0, 100)

for i, v in enumerate(scores):
    plt.text(i, v + 0.5, f"{v:.2f}%", ha='center')

plt.tight_layout()
plt.savefig("model_accuracy_comparison.png")
plt.close()

# -------------------------------------
# STEP 8.92: SVM CONFUSION MATRIX
# -------------------------------------

svm_cm = confusion_matrix(y_test, svm_predictions)

plt.figure(figsize=(6,5))
sns.heatmap(
    svm_cm,
    annot=True,
    fmt='d',
    cmap='Greens',
    xticklabels=svm_model.classes_,
    yticklabels=svm_model.classes_
)

plt.title("SVM Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")

plt.tight_layout()
plt.savefig("svm_confusion_matrix.png")
plt.close()

# ------------------------------------- 
# STEP 9: SIMPLE VERSION AND EXPLANATION
# ------------------------------------- 

student_id = 100012

# Get student directly
student_row = dataset[dataset['student_id'] == student_id]

if student_row.empty:
    print("Student not found")

else:
    # Convert safely to single row
    student = student_row.squeeze()

    exam = student['Test']
    hw = student['Homework']
    att = student['Punctuality']

    print("\nSelected Student Data:")
    print(student[['Test', 'Homework', 'Punctuality']])

    
    input_data = pd.DataFrame(
        [[exam, hw, att]],
        columns=['Test', 'Homework', 'Punctuality']
    )

    prediction = svm_model.predict(input_data)

    print("\nPrediction:", prediction[0])

print("\nReason:")

reasons = explain_prediction(exam, hw, att)

for r in reasons:
    print("-", r)

