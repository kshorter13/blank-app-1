import streamlit as st
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(
    page_title="Student Help Desk",
    page_icon="🙋",
    layout="wide"
)

# --- Session State Initialization ---
if 'help_queue' not in st.session_state:
    st.session_state.help_queue = []
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_user_name' not in st.session_state:
    st.session_state.current_user_name = None

# --- Helper Functions ---
def generate_qr_code(url):
    """Generates a QR code image from a given URL."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

# --- Main Application ---
st.title("🙋 Student Help Desk & Q&A Board")
st.markdown("Scan the QR code to access this page. Join the queue for help or ask a question for your peers!")

# --- Sidebar for QR Code ---
st.sidebar.title("App Access")
APP_URL = "https://blank-app-jqryzdh49zi.streamlit.app/" # IMPORTANT: Change this URL after deploying!
try:
    qr_image_bytes = generate_qr_code(APP_URL)
    st.sidebar.image(qr_image_bytes, caption="Scan to open this app", use_container_width=True)
except Exception as e:
    st.sidebar.error(f"Error generating QR code: {e}")
st.sidebar.info(f"App URL: {APP_URL}")

# --- Main Layout (Two Columns) ---
col1, col2 = st.columns([1, 1.5], gap="large")

# --- Column 1: Help Queue ---
with col1:
    st.header("🤝 Live Help Queue")

    with st.form("student_join_form", clear_on_submit=True):
        student_name = st.text_input("Enter your name to join the queue:", key="student_name_input")
        submitted = st.form_submit_button("I Need Help!", type="primary")

        if submitted and student_name:
            if any(student['name'] == student_name for student in st.session_state.help_queue):
                st.warning(f"{student_name}, you are already in the queue!")
            else:
                st.session_state.help_queue.append({
                    "name": student_name,
                    "time": datetime.now().strftime("%I:%M %p")
                })
                st.session_state.current_user_name = student_name
                st.success(f"You've been added to the queue, {student_name}!")
        elif submitted and not student_name:
            st.error("Please enter your name.")

    st.markdown("---")

    st.subheader("Current Queue")
    if not st.session_state.help_queue:
        st.info("The queue is currently empty. 🎉")
    else:
        for i, student in enumerate(st.session_state.help_queue, 1):
            name = student['name']
            if name == st.session_state.current_user_name:
                st.markdown(f"### **{i}. {name} (You are here!)**")
            else:
                st.markdown(f"#### {i}. {name}")

    st.markdown("---")

    # --- NEW HELPER CONTROLS SECTION ---
    with st.expander("👨‍🏫 Helper Controls (Password Required)"):
        password = st.text_input("Enter password to manage queue", type="password", key="password_input")

        # Check if
