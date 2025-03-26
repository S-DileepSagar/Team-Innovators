import streamlit as st
import pandas as pd
import google.generativeai as genai

# Set page configuration
st.set_page_config(page_title="LearnVeda AI", page_icon="📚", layout="wide")

# Custom CSS for UI
st.markdown(
    """
    <style>
    .main-content {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 10px;
        margin: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Page Header
st.markdown("""
    <h1 style='text-align: center; color: white;'>📚 LearnVeda AI - Your Personalized Study Planner</h1>
    <div class="main-content">
        <p style="color: black; font-size: 18px;">
            🎯 Welcome to LearnVeda AI! Get a customized study plan tailored to your strengths, weaknesses, and available time.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Configure Gemini API
API_KEY = "AIzaSyDurxLEf4EVkmlHbWrcFOFzkmpKij5RtwM"  # Replace with your actual Gemini API key
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")
    st.stop()

# AI-based Analysis Function
def analyze_strengths_weaknesses(subjects, strengths, weaknesses):
    prompt = f"""
    Given the following subjects, strengths, and weaknesses:
    Subjects: {subjects}
    Strengths: {strengths}
    Weaknesses: {weaknesses}
    Generate a study strategy prioritizing weak areas while maintaining strengths.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating analysis: {e}")
        return "Unable to generate analysis. Please check your API key."

# Study Timetable Generator
def generate_timetable(subjects, chapters, days, daily_hours, strengths, weaknesses):
    total_hours = days * daily_hours
    total_chapters = sum(chapters)
    analysis = analyze_strengths_weaknesses(subjects, strengths, weaknesses)
    
    time_allocation = [(chapters[i] / total_chapters) * total_hours for i in range(len(subjects))]
    for i in range(len(subjects)):
        if "struggle" in weaknesses[i].lower():
            time_allocation[i] *= 1.2
        if "good" in strengths[i].lower():
            time_allocation[i] *= 0.8
    
    chapters_per_day = [chapters[i] / days for i in range(len(subjects))]
    timetable = {}
    for day in range(1, days + 1):
        daily_schedule = {}
        for i, subject in enumerate(subjects):
            daily_schedule[subject] = {
                "Chapters": f"{int((day - 1) * chapters_per_day[i]) + 1} - {int(day * chapters_per_day[i])}",
                "Hours": round(time_allocation[i] / days, 2),
                "Focus": "Weak Areas" if "struggle" in weaknesses[i].lower() else "Strong Areas"
            }
        timetable[f"Day {day}"] = daily_schedule
    
    return timetable, analysis

# Streamlit App Logic
def main():
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    num_subjects = st.number_input("Number of Subjects", min_value=1, value=3)
    subjects, chapters, strengths, weaknesses = [], [], [], []
    
    for i in range(num_subjects):
        st.subheader(f"📘 Subject {i+1}")
        subject = st.text_input(f"Name of Subject {i+1}", value=f"Subject {i+1}")
        chapter = st.number_input(f"Number of Chapters for {subject}", min_value=1, value=10)
        strength = st.text_area(f"Your Strengths in {subject}")
        weakness = st.text_area(f"Your Weaknesses in {subject}")
        
        subjects.append(subject)
        chapters.append(chapter)
        strengths.append(strength)
        weaknesses.append(weakness)
    
    days = st.number_input("Total Days Available", min_value=1, value=4)
    daily_hours = st.number_input("Daily Study Hours", min_value=1, value=4)
    
    if st.button("🚀 Generate Timetable"):
        timetable, analysis = generate_timetable(subjects, chapters, days, daily_hours, strengths, weaknesses)
        
        st.subheader("🎯 Personalized Study Recommendations")
        st.write(analysis)
        
        st.subheader("📅 Your Study Timetable")
        for day, schedule in timetable.items():
            st.write(f"**{day}**")
            df = pd.DataFrame(schedule).T
            st.table(df)
    
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
