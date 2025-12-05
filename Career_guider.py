import streamlit as st
import requests
import fitz  # PyMuPDF
import docx
import os
import random
import tempfile
import speech_recognition as sr
import sys

# --------------------------- CONFIG ---------------------------
API_KEY = "AIzaSyDg8MSjNfjJDfczC0nJjFZcEh3w9XiDH-8"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
st.set_page_config(page_title="CareerMate.AI", layout="wide", page_icon="🎯")
st.title("🎯 CareerMate.AI - Your AI Career Co-Pilot")

# --------------------------- Gemini API Call ---------------------------
def ask_gemini(query):  # renamed prompt -> query to avoid shadowing
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": query}]}]}
    api_response = requests.post(GEMINI_API_URL, headers=headers, params={"key": API_KEY}, json=data)  # renamed response -> api_response
    if api_response.status_code == 200:
        return api_response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"❌ Error: {api_response.text}"

# --------------------------- Resume Parsing ---------------------------
def extract_text_from_resume(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text("text")  # Explicit "text" param to avoid IDE warning
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text.strip()

# --------------------------- Session State Initialization ---------------------------
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "language" not in st.session_state:
    st.session_state.language = "English"
if "current_question" not in st.session_state:
    st.session_state.current_question = None

# --------------------------- Sidebar Menu ---------------------------
menu = st.sidebar.selectbox(
    "Menu",
    [
        "Home",
        "Career Guidance",
        "Resume Analyzer",
        "Mock Interviews",
        "Networking & Job Portals",
        "Skill Recommendations",
        "Job Insights",
        "Settings"
    ]
)

# --------------------------- Home Section ---------------------------
if menu == "Home":
    st.image("https://tse3.mm.bing.net/th/id/OIP.-JGZy3m0GMFVgNIyuEe04wHaDI?pid=Api&P=0&h=180", use_container_width=True)
    st.markdown("""
    Welcome to **CareerMate.AI** – your all-in-one AI-based career counselor. Explore the sidebar to:
    - Get personalized career guidance
    - Analyze and optimize your resume
    - Get AI-based skill, job, and mentor suggestions
    """)

# --------------------------- Career Guidance Section ---------------------------
elif menu == "Career Guidance":
    st.header("🎓 AI-Powered Career Guidance")
    if st.session_state.user_name:
        st.write(f"👤 Hello, {st.session_state.user_name}!")
    user_input = st.text_area("Describe your background, skills, and interests:")
    if st.button("Get Career Suggestions"):
        prompt_text = f"""You are an AI career advisor. Based on the following background, suggest 3-5 suitable career paths with descriptions, necessary skills, and estimated average salaries.\n\nBackground:\n{user_input}"""
        response_text = ask_gemini(prompt_text)
        st.markdown(response_text)

# --------------------------- Resume Analyzer Section ---------------------------
elif menu == "Resume Analyzer":
    st.header("📄 Resume Analyzer & Optimization")
    if st.session_state.user_name:
        st.write(f"👋 {st.session_state.user_name}, upload your resume below for analysis.")
    uploaded = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
    if uploaded:
        resume_text = extract_text_from_resume(uploaded)
        st.success("✅ Resume text extracted successfully.")
        st.subheader("📜 Resume Preview")
        st.text_area("Extracted Text:", resume_text, height=300)
        if st.button("Analyze Resume"):
            prompt_text = f"""You are an AI career assistant. Analyze this resume content:\n\n{resume_text}\n\nProvide a list of strengths, weaknesses, and suggestions for improvement."""
            result_text = ask_gemini(prompt_text)
            st.markdown(result_text)

# --------------------------- Mock Interviews Section ---------------------------
elif menu == "Mock Interviews":
    import tempfile
    import speech_recognition as sr
    import random

    # List of interview questions
    questions = [
        "Tell me about yourself.",
        "Why do you want to work in this industry?",
        "What are your strengths and weaknesses?",
        "Describe a challenging situation and how you handled it.",
        "Where do you see yourself in 5 years?",
        "Why should we hire you?",
        "Tell me about a time you worked in a team.",
        "What is your greatest professional achievement?",
        "How do you handle pressure or tight deadlines?",
        "What do you know about our company?"
    ]

    # Initialize current question if not in session state
    if "current_question" not in st.session_state or st.session_state.current_question is None:
        st.session_state.current_question = random.choice(questions)

    st.header("🎤 AI-Powered Mock Interview Simulator")
    st.markdown("Simulate a real interview: get random questions and respond by **voice** or **text**.")

    st.subheader(f"🗣️ Question: {st.session_state.current_question}")

    input_mode = st.radio("Choose response method:", ["Type Answer", "Upload Audio"], key="mock_input_mode")

    user_answer = ""
    transcribed_text = ""
    audio_file = None

    if input_mode == "Type Answer":
        user_answer = st.text_area("Your Response", key="text_answer")

        if st.button("Evaluate Text Answer", key="eval_text"):
            if not user_answer.strip():
                st.warning("⚠️ Please type your answer before evaluating.")
            else:
                prompt_text = f"""Evaluate the following mock interview response:\n\nQuestion: {st.session_state.current_question}\nAnswer: {user_answer}\n\nProvide strengths, improvements, tone, and clarity analysis."""
                feedback = ask_gemini(prompt_text)
                st.markdown(feedback)

    else:  # Upload Audio
        audio_file = st.file_uploader("Upload your answer (WAV/MP3/M4A)", type=["wav", "mp3", "m4a"], key="audio_upload")
        if audio_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_file.read())
                audio_path = tmp.name

            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
                try:
                    transcribed_text = recognizer.recognize_google(audio)
                    st.text_area("📝 Transcribed Text:", transcribed_text, key="transcribed_text")

                    if st.button("Evaluate Audio Response", key="eval_audio"):
                        if not transcribed_text.strip():
                            st.warning("⚠️ Transcribed text is empty. Please try again with clearer audio.")
                        else:
                            prompt_text = f"""Evaluate the following mock interview response:\n\nQuestion: {st.session_state.current_question}\nAnswer: {transcribed_text}\n\nProvide strengths, improvements, tone, and clarity analysis."""
                            feedback = ask_gemini(prompt_text)
                            st.markdown(feedback)

                except sr.UnknownValueError:
                    st.error("😕 Could not understand the audio. Please try again.")
                except sr.RequestError as e:
                    st.error(f"API error: {e}")

        else:
            st.info("ℹ️ Please upload an audio file to proceed.")

    # Next Question Button
    if st.button("Next Question"):
        if input_mode == "Type Answer" and not user_answer.strip():
            st.warning("⚠️ Please answer the question before proceeding.")
        elif input_mode == "Upload Audio" and not transcribed_text.strip():
            st.warning("⚠️ Please upload and transcribe your audio answer before proceeding.")
        else:
            available_questions = [q for q in questions if q != st.session_state.current_question]
            st.session_state.current_question = random.choice(available_questions)
            # No st.experimental_rerun() needed, session state change triggers rerun automatically

# --------------------------- Networking & Job Portals ---------------------------
elif menu == "Networking & Job Portals":
    st.header("🔗 Professional Networking & Job Portals")

    role = st.text_input(
        "Enter your target role (e.g. Data Scientist, Software Engineer, Marketing Manager)",
        key="networking_role"
    )
    interests = st.text_input(
        "Enter your interests/skills (comma separated, e.g. Python, Machine Learning)",
        key="networking_interests"
    )

    if st.button("Find Networking & Job Platforms", key="networking_button"):
        if not role.strip():
            st.warning("⚠️ Please enter your target role to proceed.")
        else:
            # Create URL query strings
            role_query = role.replace(" ", "+")
            interests_query = "+".join(skill.strip().replace(" ", "+")
                                      for skill in interests.split(",")) if interests else ""

            st.subheader("Recommended Platforms for Networking & Job Search:")

            linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={role_query}+{interests_query}"
            st.markdown(f"[🔗 LinkedIn Jobs for '{role}']({linkedin_url})")

            naukri_url = f"https://www.naukri.com/{role_query}-jobs"
            st.markdown(f"[🔗 Naukri Jobs for '{role}']({naukri_url})")

            glassdoor_url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={role_query}+{interests_query}"
            st.markdown(f"[🔗 Glassdoor Jobs for '{role}']({glassdoor_url})")

            meetup_query = role.replace(" ", "-")
            meetup_url = f"https://www.meetup.com/find/?keywords={meetup_query}"
            st.markdown(f"[🔗 Meetup Events for '{role}']({meetup_url})")

            st.info(
                """
                💡 Tips to enhance networking:
                • Complete and optimize your LinkedIn profile  
                • Join relevant LinkedIn or Meetup groups  
                • Use Glassdoor to research companies  
                • Keep your Naukri resume updated  
                • Attend local networking and tech events  
                """
            )




# --------------------------- Skill Recommendations Section ---------------------------
elif menu == "Skill Recommendations":
    st.header("💡 Skill Gap Analysis & Course Suggestions")
    job_title = st.text_input("Enter your target job role:")
    resume_text = st.text_area("Paste your current resume or skillset:")
    if st.button("Suggest Skills & Courses"):
        prompt_text = f"""The user wants to become a {job_title}. Based on this resume:\n{resume_text}\n\nWhat skills are missing? Suggest learning paths or online courses to fill the gap."""
        result_text = ask_gemini(prompt_text)
        st.markdown(result_text)

# --------------------------- Job Insights Section ---------------------------
elif menu == "Job Insights":
    st.header("📈 Real-Time Job Market Insights")
    keyword = st.text_input("Enter a job role or skill:")
    if st.button("Get Insights"):
        prompt_text = f"""What are the current job market trends for '{keyword}' in 2025? Include demand level, average salary (worldwide or India), and popular industries hiring for this role."""
        result_text = ask_gemini(prompt_text)
        st.markdown(result_text)

# --------------------------- Settings Section ---------------------------
elif menu == "Settings":
    st.header("⚙️ Settings")
    st.session_state.user_name = st.text_input("Enter your name:", st.session_state.user_name)
    st.session_state.language = st.selectbox("Select your preferred language:", ["English", "Hindi"], index=0 if st.session_state.language == "English" else 1)
    st.markdown("Settings saved automatically.")

# --------------------------- Footer ---------------------------
st.markdown("---")
st.markdown("© 2025 CareerMate.AI — Made with ❤️ by Rahul Kumar")
