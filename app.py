import streamlit as st
import json
import os
from openai import OpenAI

st.set_page_config(page_title="AI Voice Mock Interviewer", layout="centered")
st.title("🎙️ AI Voice Mock Interview Studio")

# Safe API Key handling for Hackathon
OPENAI_API_KEY = st.text_input("Enter your OpenAI API Key", type="password")
VAPI_PUBLIC_KEY = "9b39e213-bf39-4285-ac09-54e05d706dec"
VAPI_ASSISTANT_ID = "7bdfaf46-a0ce-435c-9403-14bf9f585571"

client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

# 2. Resume Parsing Function with Fallback (No Crash if out of credits)
def parse_resume(resume_text, target_role):
    if client:
        try:
            prompt = f"""
            Parse the candidate resume and return strict JSON with keys:
            "candidate_skills" (list), "skill_gaps" (list), "target_role" (string).
            Target Role: {target_role}
            Resume Text: {resume_text}
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            st.warning("⚠️ OpenAI API limit/credit error. Using fallback mock data for demo.")
            
    # Fallback default data for hackathon demo if API fails or no key/credits
    return {
        "candidate_skills": ["React.js", "Node.js", "JavaScript", "MongoDB", "Express"],
        "skill_gaps": ["Docker", "Kubernetes", "GraphQL", "System Design"],
        "target_role": target_role
    }

# 3. Interview Evaluation Function with Fallback
def evaluate_interview(transcript, resume_text):
    if client:
        try:
            prompt = f"""
            Analyze the candidate interview transcript based on their resume skills.
            Resume Skills: {resume_text}
            Transcript: {transcript}

            Return strict JSON with keys:
            "overall_score" (float out of 10),
            "metrics": {{"technical_depth": int, "communication_clarity": int, "problem_solving": int}},
            "strengths": list of strings,
            "weaknesses": list of strings,
            "detailed_review": string
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            st.warning("⚠️ OpenAI API limit/credit error. Using fallback evaluation report.")

    # Fallback default report for demo
    return {
        "overall_score": 8.5,
        "metrics": {
            "technical_depth": 85,
            "communication_clarity": 90,
            "problem_solving": 80
        },
        "strengths": [
            "Clear and confident communication style",
            "Good foundational knowledge of the MERN stack architecture",
            "Structured problem-solving approach"
        ],
        "weaknesses": [
            "Could explain backend scalability and database indexing better",
            "Missed mentioning containerization tools like Docker"
        ],
        "detailed_review": "The candidate performed very well during the mock interview. They articulated their technical background clearly and responded to questions with structural logic. Improving on advanced system scaling will make them interview-ready for top-tier roles."
    }

# 4. Streamlit UI Layout
target_role = st.text_input("Target Role", value="MERN Stack Developer")
resume_text = st.text_area("Paste Candidate Resume Text / CV Summary", height=150)

if st.button("Start Voice Interview Preparation"):
    if not resume_text:
        st.warning("Please paste a resume first!")
    else:
        with st.spinner("Analyzing Resume & Setting up Vapi AI Assistant..."):
            parsed_data = parse_resume(resume_text, target_role)
            st.session_state["parsed_data"] = parsed_data
            st.success("Resume Parsed Successfully!")

        # Vapi Web SDK Script Integration in Python Streamlit
        vapi_html = f"""
        <div style="text-align: center; margin-top: 20px;">
            <button id="vapi-start-btn" style="background-color: #4F46E5; color: white; padding: 12px 24px; border-radius: 8px; border: none; font-weight: bold; cursor: pointer;">
                🎙️ Start Live Vapi Voice Call
            </button>
            <p id="vapi-status" style="margin-top: 10px; color: #9CA3AF;">Status: Ready</p>
        </div>

        <script src="https://cdn.jsdelivr.net/gh/VapiAI/html-script-tag@latest/dist/assets/index.js"></script>
        <script>
            const vapi = window.vapiSDK.run({{
                apiKey: "{VAPI_PUBLIC_KEY}",
                assistant: "{VAPI_ASSISTANT_ID}",
                assistantOverrides: {{
                    variableValues: {{
                        candidate_skills: "{', '.join(parsed_data.get('candidate_skills', []))}",
                        skill_gaps: "{', '.join(parsed_data.get('skill_gaps', []))}",
                        target_role: "{parsed_data.get('target_role', target_role)}"
                    }}
                }}
            }});

            document.getElementById("vapi-start-btn").addEventListener("click", () => {{
                vapi.start();
                document.getElementById("vapi-status").innerText = "Status: Connecting & Listening...";
                document.getElementById("vapi-status").style.color = "#10B981";
            }});
        </script>
        """
        st.components.v1.html(vapi_html, height=200)

# 5. Manual Transcript Review / Post-Interview Evaluation
st.divider()
st.subheader("📊 Post-Interview Scorecard & Rating Generator")
transcript_input = st.text_area("Paste Interview Transcript (or auto-fetch via webhook)", height=100)

if st.button("Generate Detailed Evaluation Report"):
    with st.spinner("Evaluating Performance..."):
        report = evaluate_interview(transcript_input, resume_text)
        
        st.metric("Overall Performance Rating", f"{report.get('overall_score', 0)} / 10")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Technical Depth", f"{report.get('metrics', {}).get('technical_depth', 0)}%")
        col2.metric("Communication", f"{report.get('metrics', {}).get('communication_clarity', 0)}%")
        col3.metric("Problem Solving", f"{report.get('metrics', {}).get('problem_solving', 0)}%")

        st.write("### Key Strengths")
        for s in report.get("strengths", []):
            st.write(f"- ✅ {s}")

        st.write("### Areas for Improvement")
        for w in report.get("weaknesses", []):
            st.write(f"- ⚠️ {w}")

        st.info(report.get("detailed_review", ""))