import streamlit as st
import fitz  # PyMuPDF for PDF
import docx
import spacy
import re
import pandas as pd

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# ---------- FUNCTIONS ----------

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# Extract text from DOCX
def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    return "\n".join([p.text for p in doc.paragraphs])

# Extract Skills
def extract_skills(text):
    skill_keywords = [
        "python","java","c++","sql","excel","machine learning","deep learning",
        "html","css","javascript","react","node","data analysis","ai","communication",
        "leadership","project management"
    ]
    text_lower = text.lower()
    found = [skill.capitalize() for skill in skill_keywords if skill in text_lower]
    return list(set(found))

# Extract Education
def extract_education(text):
    education_patterns = [
        "b\.?tech", "bachelor", "b\.?e", "m\.?tech", "master", "m\.?s", "ph\.?d", "12th", "10th"
    ]
    matches = []
    for pattern in education_patterns:
        found = re.findall(pattern, text.lower())
        if found:
            matches.extend(found)
    return list(set(matches))

# Extract Experience (Years)
def extract_experience(text):
    exp_pattern = r"(\d+)\s+(?:years|year|yrs|yr)\s+of\s+experience"
    matches = re.findall(exp_pattern, text.lower())
    if matches:
        return f"{max(map(int, matches))} years"
    else:
        # Try general mention like "experience in"
        if "experience" in text.lower():
            return "Mentioned but not specific"
        else:
            return "Not mentioned"

# ---------- STREAMLIT UI ----------

st.set_page_config(page_title="Smart Resume Parser", layout="centered")
st.title("🧠 Smart Resume Parser")
st.write("Upload your resume (PDF or DOCX) to extract key information.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = extract_text_from_docx(uploaded_file)
    
    # Process text with spaCy
    doc = nlp(resume_text)
    
    # Extract info
    skills = extract_skills(resume_text)
    education = extract_education(resume_text)
    experience = extract_experience(resume_text)
    
    st.subheader("📄 Extracted Information")
    st.write("**Skills:**", ", ".join(skills) if skills else "Not found")
    st.write("**Education:**", ", ".join(education) if education else "Not found")
    st.write("**Experience:**", experience)
    
    # Optional: Show extracted text
    with st.expander("Show Full Extracted Text"):
        st.text(resume_text)

    # Save extracted info to CSV
    data = {"Skills": [", ".join(skills)], "Education": [", ".join(education)], "Experience": [experience]}
    df = pd.DataFrame(data)
    df.to_csv("parsed_resume_data.csv", index=False)
    st.success("✅ Extracted info saved to parsed_resume_data.csv")
