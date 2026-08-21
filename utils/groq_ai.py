import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found.")

client = Groq(api_key=api_key)

def generate_recommendation(student, prediction):

    prompt = f"""
You are EduInsight AI, an expert educational advisor.

Generate a personalized academic recommendation.

Output EXACTLY in this format.

🧠 Personalized Learning Recommendation

📊 Performance Analysis
Write 2-3 sentences analysing the student's academic performance.

✅ Strengths
• Point 1
• Point 2
• Point 3

⚠ Areas for Improvement
• Point 1
• Point 2
• Point 3

📚 Recommended Actions
1. Action 1
2. Action 2
3. Action 3
4. Action 4

🎯 Expected Outcome
Write 1-2 encouraging sentences.

Student Profile

Student Name: {student.get("student_name","Student")}
Prediction: {prediction}
Attendance: {student.get("attendance_percentage",0)}%
Study Hours: {student.get("study_hours_per_day",0)}
Assignment: {student.get("assignment_score",0)}
Midterm: {student.get("midterm_score",0)}
Final Exam: {student.get("final_exam_score",0)}
Participation: {student.get("participation_score",0)}
Sleep Hours: {student.get("sleep_hours",0)}

Do not mention Machine Learning, AI model or SVM.
Keep the response under 250 words.
"""

    try:

        response = client.chat.completions.create(
            model="gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=500
        )

        recommendation = response.choices[0].message.content.strip()
        recommendation = recommendation.replace("```", "")
        recommendation = recommendation.replace("#", "")

        return recommendation

    except Exception as e:

        print("Groq Error:", e)

        if prediction == "High Performance":

            return """🧠 Personalized Learning Recommendation

📊 Performance Analysis
The student demonstrates consistently strong academic performance with excellent learning discipline and assessment achievement. Current study habits indicate a high probability of maintaining excellent academic outcomes.

✅ Strengths
• Excellent attendance and learning commitment.
• Strong assessment and examination performance.
• Consistent daily study routine.

⚠ Areas for Improvement
• Continue challenging yourself with advanced topics.
• Increase participation in discussions.
• Maintain work-life balance to avoid burnout.

📚 Recommended Actions
1. Maintain your weekly study schedule.
2. Practise higher-order thinking questions.
3. Continue revising after every lecture.
4. Maintain attendance above 90%.

🎯 Expected Outcome
Maintaining these habits will help sustain high academic performance and continuous personal growth."""

        elif prediction == "Moderate Performance":

            return """🧠 Personalized Learning Recommendation

📊 Performance Analysis
The student demonstrates satisfactory academic performance with clear potential for improvement. More consistent revision and preparation will strengthen overall achievement.

✅ Strengths
• Good classroom attendance.
• Positive learning attitude.
• Basic understanding of course concepts.

⚠ Areas for Improvement
• Improve revision consistency.
• Increase independent study.
• Strengthen examination preparation.

📚 Recommended Actions
1. Follow a structured study timetable.
2. Revise at least 2 hours daily.
3. Complete additional practice exercises.
4. Seek clarification whenever needed.

🎯 Expected Outcome
With continuous effort and structured learning, the student has strong potential to achieve High Performance."""

        else:

            return """🧠 Personalized Learning Recommendation

📊 Performance Analysis
The student's current academic indicators suggest additional academic support is required. Improving study consistency and attendance will significantly enhance future performance.

✅ Strengths
• Demonstrates willingness to learn.
• Has potential for improvement with guidance.

⚠ Areas for Improvement
• Increase daily study hours.
• Improve attendance.
• Submit assignments on time.

📚 Recommended Actions
1. Create a daily revision schedule.
2. Attend all classes.
3. Meet lecturers regularly.
4. Complete weekly practice exercises.

🎯 Expected Outcome
With consistent effort and proper academic support, the student is expected to improve towards Moderate Performance."""