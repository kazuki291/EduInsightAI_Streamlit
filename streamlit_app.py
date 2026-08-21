import streamlit as st
import pandas as pd
from database import get_connection
from utils.svm_predict import predict_student
from utils.groq_ai import generate_recommendation
from utils.pdf_generator import generate_student_pdf

st.set_page_config(
    page_title="EduInsight AI",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
<style>
.stButton>button{
    width:100%;
    height:50px;
    border-radius:10px;
    font-size:18px;
}
div[data-testid="metric-container"]{
    background:#f8f9fa;
    border-radius:10px;
    padding:15px;
}
</style>
""", unsafe_allow_html=True)

st.title("🎓 EduInsight AI")
st.subheader("AI-Based Student Academic Performance Prediction System")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Menu",
    [
        "🏠 Dashboard",
        "➕ Add Student",
        "🤖 Predict Student",
        "📊 Prediction History"
    ]
)

if page == "🏠 Dashboard":
    st.header("📊 Dashboard")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM teacher_students")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM teacher_students WHERE prediction='High Performance'")
    high = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM teacher_students WHERE prediction='Moderate Performance'")
    moderate = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM teacher_students WHERE prediction='Low Performance'")
    low = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT ROUND(AVG(attendance_percentage),2) AS avg_attendance
        FROM teacher_students
    """)
    avg = cursor.fetchone()["avg_attendance"] or 0

    cursor.execute("""
        SELECT
            student_name,
            prediction,
            confidence_score,
            prediction_date
        FROM teacher_students
        ORDER BY prediction_date DESC
        LIMIT 5
    """)
    history = cursor.fetchall()
    conn.close()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("👨‍🎓 Students", total)
    col2.metric("🟢 High", high)
    col3.metric("🟡 Moderate", moderate)
    col4.metric("🔴 Low", low)
    col5.metric("📈 Avg Attendance", f"{avg}%")

    st.markdown("---")
    
    col_chart, col_table = st.columns([1, 1])
    
    with col_chart:
        st.subheader("Prediction Distribution")
        prediction_counts = pd.DataFrame({
            "Category": ["High", "Moderate", "Low"],
            "Students": [high, moderate, low]
        })
        st.bar_chart(prediction_counts.set_index("Category"))

    with col_table:
        st.subheader("🕒 Recent Predictions")
        if history:
            st.dataframe(pd.DataFrame(history), use_container_width=True)
        else:
            st.info("No predictions available.")

elif page == "➕ Add Student":
    st.header("➕ Add Student")

    with st.form("student_form"):
        col1, col2 = st.columns(2)

        with col1:
            student_id = st.text_input("Student ID")
            student_name = st.text_input("Student Name")
            gender = st.selectbox("Gender", ["Male", "Female"])
            study_hours = st.number_input("Study Hours Per Day", 0.0, 24.0, 2.0)
            attendance = st.number_input("Attendance Percentage", 0.0, 100.0, 80.0)
            assignment = st.number_input("Assignment Score", 0.0, 100.0, 70.0)

        with col2:
            midterm = st.number_input("Midterm Score", 0.0, 100.0, 70.0)
            final_exam = st.number_input("Final Exam Score", 0.0, 100.0, 70.0)
            participation = st.number_input("Participation Score", 0.0, 100.0, 70.0)
            sleep = st.number_input("Sleep Hours", 0.0, 24.0, 7.0)
            internet = st.selectbox("Internet Access", ["Yes", "No"])
            extra = st.selectbox("Extra Classes", ["Yes", "No"])
            education = st.selectbox("Parent Education", ["High School", "Bachelor", "Master", "PhD"])

        submitted = st.form_submit_button("💾 Save Student")

    if submitted:
        if not student_id or not student_name:
            st.error("Please enter both Student ID and Student Name.")
        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO teacher_students(
                student_id, student_name, gender, study_hours_per_day,
                attendance_percentage, assignment_score, midterm_score,
                final_exam_score, participation_score, internet_access,
                extra_classes, parent_education, sleep_hours
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                student_id, student_name, gender, study_hours,
                attendance, assignment, midterm, final_exam,
                participation, internet, extra, education, sleep
            ))

            conn.commit()
            conn.close()
            st.success("✅ Student added successfully!")

elif page == "🤖 Predict Student":
    st.header("🤖 Student Performance Prediction")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, student_name FROM teacher_students ORDER BY student_name")
    students = cursor.fetchall()
    conn.close()

    if not students:
        st.warning("No students found. Please add a student first.")
        st.stop()

    student_names = {f"{s['student_name']} (ID: {s['id']})": s["id"] for s in students}
    selected = st.selectbox("Select Student", list(student_names.keys()))
    selected_db_id = student_names[selected]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teacher_students WHERE id=%s", (selected_db_id,))
    student = cursor.fetchone()
    conn.close()

    st.subheader("Student Academic Profile")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Student Name:**", student["student_name"])
        st.write("**Attendance:**", f"{student['attendance_percentage']}%")
        st.write("**Study Hours:**", f"{student['study_hours_per_day']} hrs/day")
        st.write("**Assignment Score:**", student["assignment_score"])

    with col2:
        st.write("**Midterm Score:**", student["midterm_score"])
        st.write("**Final Exam Score:**", student["final_exam_score"])
        st.write("**Participation Score:**", student["participation_score"])
        st.write("**Sleep Hours:**", f"{student['sleep_hours']} hrs/night")

    predict_btn = st.button("🚀 Run AI Prediction & Recommendation")

    if predict_btn:
        with st.spinner("Analyzing student metrics with SVM and generating recommendation..."):
            prediction, confidence = predict_student(student)
            recommendation = generate_recommendation(student, prediction)

            # Persist to database
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE teacher_students
                SET prediction=%s, confidence_score=%s, recommendation=%s, prediction_date=NOW()
                WHERE id=%s
            """, (prediction, confidence, recommendation, selected_db_id))
            conn.commit()
            conn.close()

        st.success(f"**Prediction:** {prediction}")
        st.progress(min(max(float(confidence) / 100.0, 0.0), 1.0))
        st.metric("Model Confidence Score", f"{confidence:.2f}%")

        st.subheader("🧠 Personalized Learning Recommendation")
        st.write(recommendation)

        # PDF Download Button
        pdf_data = generate_student_pdf(student, prediction, confidence, recommendation)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_data,
            file_name=f"{student['student_name']}_Report.pdf",
            mime="application/pdf"
        )

elif page == "📊 Prediction History":
    st.header("📊 Prediction History")

    conn = get_connection()
    query = """
        SELECT
            id,
            student_id,
            student_name,
            prediction,
            confidence_score,
            prediction_date
        FROM teacher_students
        ORDER BY prediction_date DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        st.info("No prediction records found.")
    else:
        search = st.text_input("🔍 Search Student Name or ID")
        if search:
            df = df[
                df["student_name"].str.contains(search, case=False, na=False) |
                df["student_id"].astype(str).str.contains(search, case=False, na=False)
            ]

        st.dataframe(df, use_container_width=True) 