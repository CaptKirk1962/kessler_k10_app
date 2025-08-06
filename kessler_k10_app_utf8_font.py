import streamlit as st
from fpdf import FPDF  # fpdf2
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import io
import os

# -------------------------
# Kessler K10 Questions
# -------------------------
questions = [
    "In the past 4 weeks, about how often did you feel tired out for no good reason?",
    "In the past 4 weeks, about how often did you feel nervous?",
    "In the past 4 weeks, about how often did you feel so nervous that nothing could calm you down?",
    "In the past 4 weeks, about how often did you feel hopeless?",
    "In the past 4 weeks, about how often did you feel restless or fidgety?",
    "In the past 4 weeks, about how often did you feel so restless you could not sit still?",
    "In the past 4 weeks, about how often did you feel depressed?",
    "In the past 4 weeks, about how often did you feel that everything was an effort?",
    "In the past 4 weeks, about how often did you feel so sad that nothing could cheer you up?",
    "In the past 4 weeks, about how often did you feel worthless?"
]

options = {
    "None of the time": 1,
    "A little of the time": 2,
    "Some of the time": 3,
    "Most of the time": 4,
    "All of the time": 5
}

# Interpretation bands
bands = [
    (10, 15, "Low Distress", "Your score indicates a low level of psychological distress."),
    (16, 21, "Moderate Distress", "Your score indicates a moderate level of distress. This may be a good time to check in on your mental well-being."),
    (22, 29, "High Distress", "Your score suggests a high level of distress. It may help to speak with a healthcare professional."),
    (30, 50, "Very High Distress", "Your score indicates a very high level of psychological distress. We strongly recommend seeking professional help.")
]

# -------------------------
# PDF Generation with Unicode font preloaded
# -------------------------
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
        self.add_font("DejaVu", "", font_path, uni=True)

    def header(self):
        self.set_font("DejaVu", "", 16)
        self.cell(0, 10, "Life Minus Work - Kessler K10 Results", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 10, "Life Minus Work | Page " + str(self.page_no()), 0, 0, "C")

def generate_pdf(name, score, category, guidance):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("DejaVu", "", 12)
    if name:
        pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Kessler K10 Score: {score}", ln=True)
    pdf.cell(0, 10, f"Distress Category: {category}", ln=True)
    pdf.multi_cell(0, 10, f"Guidance: {guidance}")
    pdf_output = io.BytesIO()
    pdf_bytes = pdf.output(dest="S")  # no encode()
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output

# -------------------------
# Email Sending
# -------------------------
def send_email(recipient_email, pdf_buffer, filename):
    sender_email = "your_email@example.com"
    sender_password = "your_password"
    subject = "Your Kessler K10 Results"
    body = "Attached is your Kessler K10 Psychological Distress Test result from Life Minus Work."

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    part = MIMEBase("application", "octet-stream")
    part.set_payload(pdf_buffer.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={filename}")
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Kessler K10 Test", layout="centered")
st.title("🧠 Kessler K10 Psychological Distress Test")
st.write("This test measures your level of psychological distress over the past 4 weeks.")

if "responses" not in st.session_state:
    st.session_state.responses = []
if "page" not in st.session_state:
    st.session_state.page = 0
if "name" not in st.session_state:
    st.session_state.name = ""
if "email" not in st.session_state:
    st.session_state.email = ""

def reset_test():
    st.session_state.responses = []
    st.session_state.page = 0
    st.session_state.name = ""
    st.session_state.email = ""

if st.session_state.page < len(questions):
    q = questions[st.session_state.page]
    st.markdown(f"**Q{st.session_state.page + 1}: {q}**")
    for opt_text, opt_value in options.items():
        if st.button(opt_text, key=f"{st.session_state.page}-{opt_text}"):
            st.session_state.responses.append(opt_value)
            st.session_state.page += 1
else:
    st.session_state.name = st.text_input("Your Name (optional)", st.session_state.name)
    st.session_state.email = st.text_input("Your Email (optional, to receive results)")

    if st.button("Get Results"):
        score = sum(st.session_state.responses)
        category, guidance = None, None
        for low, high, cat, msg in bands:
            if low <= score <= high:
                category, guidance = cat, msg
                break

        st.success(f"Your Kessler K10 Score: {score} — {category}")
        st.write(guidance)

        pdf_buffer = generate_pdf(st.session_state.name, score, category, guidance)

        st.download_button(
            label="📥 Download Your Results (PDF)",
            data=pdf_buffer,
            file_name="Kessler_K10_Results.pdf",
            mime="application/pdf"
        )

        if st.session_state.email:
            try:
                pdf_buffer.seek(0)
                send_email(st.session_state.email, pdf_buffer, "Kessler_K10_Results.pdf")
                st.info("📧 Results sent to your email!")
            except Exception as e:
                st.error(f"Email sending failed: {e}")

    st.button("🔄 Restart Test", on_click=reset_test)
