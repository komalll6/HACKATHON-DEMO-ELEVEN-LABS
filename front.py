import streamlit as st
import io

def generate_professional_resume_html(name, email, phone, linkedin, github, summary, skills, education, experience, projects, certs):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Times New Roman', Times, serif; margin: 30px; color: #000; line-height: 1.4; }}
            .header {{ text-align: left; border-bottom: 2px solid #1E3A8A; padding-bottom: 10px; margin-bottom: 15px; }}
            h1 {{ margin: 0; font-size: 24px; color: #1E3A8A; }}
            .contact-info {{ font-size: 12px; color: #333; margin-top: 5px; }}
            h2 {{ font-size: 14px; color: #1E3A8A; border-bottom: 1px solid #ccc; padding-bottom: 2px; margin-top: 15px; text-transform: uppercase; }}
            p, li {{ font-size: 12px; }}
            ul {{ margin: 5px 0; padding-left: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{name}</h1>
            <div class="contact-info">
                Email: {email} | Mobile: {phone} | LinkedIn: {linkedin} | GitHub: {github}
            </div>
        </div>

        <h2>Professional Summary</h2>
        <p>{summary}</p>

        <h2>Skills & Impact Proof</h2>
        <p>{skills}</p>

        <h2>Education</h2>
        <p>{education.replace('\\n', '<br>')}</p>

        <h2>Experience</h2>
        <p>{experience.replace('\\n', '<br>')}</p>

        <h2>Projects</h2>
        <p>{projects.replace('\\n', '<br>')}</p>

        <h2>Certifications</h2>
        <p>{certs.replace('\\n', '<br>')}</p>
    </body>
    </html>
    """
    return html_content

# Streamlit UI - Blank Fields for Custom Input
st.subheader("📄 Professional Resume Generator (ATS-Ready)")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Full Name", value="")
    email = st.text_input("Email", value="")
    phone = st.text_input("Mobile", value="")
    linkedin = st.text_input("LinkedIn URL", value="")
    github = st.text_input("GitHub URL", value="")

with col2:
    summary = st.text_area("Professional Summary", value="")
    skills = st.text_area("Skills & Tech Stack", value="")

education = st.text_area("Education", value="")
experience = st.text_area("Experience", value="")
projects = st.text_area("Projects", value="")
certs = st.text_area("Certifications", value="")

if st.button("Generate Professional Resume"):
    if name and email:
        resume_html = generate_professional_resume_html(name, email, phone, linkedin, github, summary, skills, education, experience, projects, certs)
        st.download_button(
            label="📥 Download Resume (.doc)",
            data=resume_html,
            file_name=f"{name.replace(' ', '_')}_Resume.doc",
            mime="application/msword"
        )
    else:
        st.warning("Please fill in at least Full Name and Email!")