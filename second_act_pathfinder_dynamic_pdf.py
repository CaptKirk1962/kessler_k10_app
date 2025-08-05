import streamlit as st
import json
from collections import Counter

from fpdf import FPDF
import io

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Life Minus Work – Second Act Pathfinder", ln=True, align="C")
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, "Life Minus Work | Page " + str(self.page_no()), 0, 0, "C")

def generate_pdf(name, archetype, description):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    if name:
        pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Your Archetype: {archetype}", ln=True)
    pdf.multi_cell(0, 10, f"Description: {description}")
    pdf_output = io.BytesIO()
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output


# Load quiz questions
with open("archetype_quiz_questions.json", "r") as f:
    questions = json.load(f)

st.set_page_config(page_title="Second Act Pathfinder", layout="centered")
st.title("🧭 Second Act Pathfinder")
st.subheader("Discover your Life Minus Work Archetype")

# Archetype descriptions
archetype_descriptions = {
    "Explorer": "You thrive on adventure, discovery, and the thrill of new horizons. Your second act is all about embracing curiosity and seeking out experiences that excite you.",
    "Nurturer": "Your gift is caring for and connecting with others. In your second act, you'll find joy in building supportive relationships and creating safe spaces for people to grow.",
    "Creator": "You are fuelled by imagination and expression. This chapter is your chance to bring your ideas to life and share your creativity with the world.",
    "Seeker": "You are drawn to wisdom, insight, and meaning. Your second act is about exploring life’s deeper questions and finding purpose in the answers.",
    "Builder": "You create stability, systems, and legacies. This is your time to construct projects and initiatives that will have a lasting impact.",
    "Connector": "You are the glue that brings people together. Your second act is about fostering community, sparking conversations, and building meaningful networks."
}

# Initialize session state
if "responses" not in st.session_state:
    st.session_state.responses = []
if "page" not in st.session_state:
    st.session_state.page = 0

def reset_quiz():
    '''Reset the quiz to start over.'''
    st.session_state.responses = []
    st.session_state.page = 0

# Quiz logic
if st.session_state.page < len(questions):
    q = questions[st.session_state.page]
    st.markdown(f"**Q{st.session_state.page + 1}: {q['question']}**")
    for archetype, answer in q["options"].items():
        if st.button(answer, key=f"{st.session_state.page}-{archetype}"):
            st.session_state.responses.append(archetype)
            st.session_state.page += 1
else:
    # Determine archetype result
    result = Counter(st.session_state.responses).most_common(1)[0][0]
    st.success(f"🎉 You're a **{result}**!")

    # Show personalised description
    st.write(archetype_descriptions.get(result, ""))

    st.markdown("## 📥 Your Lifestyle Plan is ready!")

    
# Optional name input
name_input = st.text_input("Your Name (optional)")

# Generate dynamic PDF
pdf_buffer = generate_pdf(name_input, result, archetype_descriptions.get(result, ""))

# Download button
st.download_button(
    label=f"📥 Download Your {result} Lifestyle Plan (PDF)",
    data=pdf_buffer,
    file_name=f"{result}_Lifestyle_Plan.pdf",
    mime="application/pdf"
)

# Restart quiz button
st.button("🔄 Restart Quiz", on_click=reset_quiz)

