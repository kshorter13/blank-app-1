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
# Add a state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

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
    
    # Convert image to bytes
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

# --- Main Application ---
st.title("🙋 Student Help Desk & Q&A Board")
st.markdown("Scan the QR code to access this page. Join the queue for help or ask a question for your peers!")

# --- Sidebar for QR Code and Admin Login ---
st.sidebar.title("App Access & Admin")

# --- QR Code Display ---
# IMPORTANT: Change this URL after deploying!
APP_URL = "https://blank-app-jqryzdh49zi.streamlit.app/" 
try:
    qr_image_bytes = generate_qr_code(APP_URL)
    # **FIX APPLIED HERE:** Use st.image with the byte data directly.
    st.sidebar.image(qr_image_bytes, caption="Scan to open this app", use_container_width=True)
except Exception as e:
    st.sidebar.error(f"Error generating QR code: {e}")
    
st.sidebar.info(f"App URL: {APP_URL}")
st.sidebar.markdown("---")


# --- Password Protection ---
def check_password():
    """Returns `True` if the user had the correct password."""
    # Use st.form to prevent the page from rerunning on every key press
    with st.sidebar.form("password_form"):
        st.write("Helper Login")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        # **IMPORTANT:** For better security, use Streamlit Secrets Management.
        # This is just a simple example.
        if submitted:
            if password == "teacher123":
                st.session_state["authenticated"] = True
                st.rerun() # Rerun to hide the form and show controls
            else:
                st.sidebar.error("Incorrect password")

# If not authenticated, show the password form
if not st.session_state.get("authenticated", False):
    check_password()
else:
    st.sidebar.success("Logged in as Helper")
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

# --- Main Layout (Two Columns) ---
col1, col2 = st.columns([1, 1.5], gap="large")

# --- Column 1: Help Queue ---
with col1:
    st.header("🤝 Live Help Queue")

    with st.form("join_queue_form", clear_on_submit=True):
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

    # --- Helper/Teacher Controls (Now inside the password check) ---
    if st.session_state.authenticated:
        st.markdown("---")
        st.subheader("👨‍🏫 Helper Controls")
        if st.session_state.help_queue:
            if st.button("Help Next Student", use_container_width=True):
                st.session_state.help_queue.pop(0)
                st.toast("The queue has been updated.", icon="✅")
                st.rerun()

        if st.button("Clear Entire Queue", use_container_width=True):
            st.session_state.help_queue = []
            st.toast("The help queue has been cleared.", icon="🗑️")
            st.rerun()

# --- Column 2: Q&A Board ---
with col2:
    st.header("❓ Peer Q&A Board")
    # ... (The rest of the Q&A code is unchanged) ...
    with st.expander("Ask a new question...", expanded=False):
        with st.form("new_question_form", clear_on_submit=True):
            question_author = st.text_input("Your Name:")
            question_text = st.text_area("Your Question:")
            submit_question = st.form_submit_button("Post Question", type="primary")

            if submit_question and question_text and question_author:
                st.session_state.questions.append({
                    "author": question_author,
                    "question": question_text,
                    "answers": []
                })
                st.success("Your question has been posted!")
            elif submit_question:
                st.error("Please fill in both your name and question.")

    st.markdown("---")

    if not st.session_state.questions:
        st.info("No questions have been asked yet. Be the first!")
    else:
        for idx, q in enumerate(reversed(st.session_state.questions)):
            st.markdown(f"**Q: {q['question']}** - *Asked by {q['author']}*")
            
            for ans in q['answers']:
                st.info(f"**A:** {ans['answer']} - *Answered by {ans['author']}*")
            
            with st.form(key=f"answer_form_{idx}", clear_on_submit=True):
                answer_author = st.text_input("Your Name:", key=f"ans_author_{idx}")
                answer_text = st.text_area("Your Answer:", key=f"ans_text_{idx}", height=100)
                submit_answer = st.form_submit_button("Submit Answer")

                if submit_answer and answer_text and answer_author:
                    original_idx = len(st.session_state.questions) - 1 - idx
                    st.session_state.questions[original_idx]['answers'].append({
                        "author": answer_author,
                        "answer": answer_text
                    })
                    st.rerun()
                elif submit_answer:
                    st.warning("Please provide your name and an answer.")
            st.markdown("---")    # --- Form to Join Queue ---
    with st.form("join_queue_form", clear_on_submit=True):
        student_name = st.text_input("Enter your name to join the queue:", key="student_name_input")
        submitted = st.form_submit_button("I Need Help!", type="primary")

        if submitted and student_name:
            # Check if name is already in the queue
            if any(student['name'] == student_name for student in st.session_state.help_queue):
                st.warning(f"{student_name}, you are already in the queue!")
            else:
                # Add student to the queue
                st.session_state.help_queue.append({
                    "name": student_name,
                    "time": datetime.now().strftime("%I:%M %p")
                })
                st.session_state.current_user_name = student_name
                st.success(f"You've been added to the queue, {student_name}!")
        elif submitted and not student_name:
            st.error("Please enter your name.")

    st.markdown("---")

    # --- Display The Queue ---
    st.subheader("Current Queue")
    if not st.session_state.help_queue:
        st.info("The queue is currently empty. 🎉")
    else:
        for i, student in enumerate(st.session_state.help_queue, 1):
            name = student['name']
            # Highlight the current user's position
            if name == st.session_state.current_user_name:
                st.markdown(f"### **{i}. {name} (You are here!)**")
            else:
                st.markdown(f"#### {i}. {name}")

    # --- Helper/Teacher Controls ---
    st.markdown("---")
    st.subheader("👨‍🏫 Helper Controls")
    if st.session_state.help_queue:
        if st.button("Help Next Student", use_container_width=True):
            helped_student = st.session_state.help_queue.pop(0)
            st.toast(f"Helping {helped_student['name']} now. The queue has been updated.", icon="✅")
            # Rerun to update the display immediately
            st.rerun()

    if st.button("Clear Entire Queue", use_container_width=True):
        st.session_state.help_queue = []
        st.toast("The help queue has been cleared.", icon="🗑️")
        st.rerun()

# --- Column 2: Q&A Board ---
with col2:
    st.header("❓ Q&A Board")

    # --- Form to Ask a Question ---
    with st.expander("Ask a new question...", expanded=False):
        with st.form("new_question_form", clear_on_submit=True):
            question_author = st.text_input("Your Name:")
            question_text = st.text_area("Your Question:")
            submit_question = st.form_submit_button("Post Question", type="primary")

            if submit_question and question_text and question_author:
                st.session_state.questions.append({
                    "author": question_author,
                    "question": question_text,
                    "answers": []
                })
                st.success("Your question has been posted!")
            elif submit_question:
                st.error("Please fill in both your name and question.")

    st.markdown("---")

    # --- Display Questions and Answers ---
    if not st.session_state.questions:
        st.info("No questions have been asked yet. Be the first!")
    else:
        # Display questions in reverse chronological order (newest first)
        for idx, q in enumerate(reversed(st.session_state.questions)):
            st.markdown(f"**Q: {q['question']}** - *Asked by {q['author']}*")
            
            # Display existing answers
            for ans in q['answers']:
                st.info(f"**A:** {ans['answer']} - *Answered by {ans['author']}*")
            
            # Form to submit an answer
            with st.form(key=f"answer_form_{idx}", clear_on_submit=True):
                answer_author = st.text_input("Your Name:", key=f"ans_author_{idx}")
                answer_text = st.text_area("Your Answer:", key=f"ans_text_{idx}", height=100)
                submit_answer = st.form_submit_button("Submit Answer")

                if submit_answer and answer_text and answer_author:
                    # Find the original question index to append the answer
                    original_idx = len(st.session_state.questions) - 1 - idx
                    st.session_state.questions[original_idx]['answers'].append({
                        "author": answer_author,
                        "answer": answer_text
                    })
                    st.rerun()
                elif submit_answer:
                    st.warning("Please provide your name and an answer.")
            st.markdown("---")
