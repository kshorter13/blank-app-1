import streamlit as st
from datetime import datetime
import qrcode
from io import BytesIO
import firebase_admin
from firebase_admin import credentials, db
import json

# --- Page Configuration ---
st.set_page_config(page_title="Student Help Desk", page_icon="🙋", layout="wide")

# --- Firebase Initialization ---
@st.cache_resource
def init_firebase():
    """Initializes the Firebase connection."""
    try:
        # Get credentials from Streamlit secrets
        firebase_creds_dict = dict(st.secrets["firebase_credentials"])
        
        # The private_key in secrets is often read with escape characters.
        # This line ensures it's parsed correctly.
        firebase_creds_dict["private_key"] = firebase_creds_dict["private_key"].replace('\\n', '\n')

        cred = credentials.Certificate(firebase_creds_dict)
        
        # Check if the app is already initialized
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_config"]["databaseURL"]
            })
        return True
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}. Please check your Streamlit secrets.")
        return False

# Initialize Firebase and proceed only if successful
if init_firebase():
    # --- Firebase Data Functions ---
    def get_data(path):
        """Fetches data from a specified path in Firebase."""
        ref = db.reference(path)
        return ref.get()

    def set_data(path, data):
        """Writes or overwrites data at a specified path."""
        ref = db.reference(path)
        ref.set(data)

    # --- Main Application ---
    st.title("🙋 Central Help Desk & Q&A Board")
    st.markdown("This is a live, shared help desk. All students see the same queue and questions.")

    # --- Sidebar for QR Code ---
    # (The QR code and sidebar logic remains the same)
    st.sidebar.title("App Access")
    APP_URL = "https://blank-app-jqryzdh49zi.streamlit.app/" # IMPORTANT: Change your URL
    # ... (QR code generation code as before) ...
    
    col1, col2 = st.columns([1, 1.5], gap="large")

    # --- Column 1: Help Queue ---
    with col1:
        st.header("🤝 Live Help Queue")
        
        # Fetch current queue from Firebase
        help_queue = get_data("/help_queue") or []

        with st.form("student_join_form", clear_on_submit=True):
            student_name = st.text_input("Enter your name to join the queue:")
            submitted = st.form_submit_button("I Need Help!", type="primary")

            if submitted and student_name:
                # Append new student and update Firebase
                new_entry = {"name": student_name, "time": datetime.now().strftime("%I:%M %p")}
                help_queue.append(new_entry)
                set_data("/help_queue", help_queue)
                st.success(f"You've been added to the queue, {student_name}!")
                st.rerun() # Rerun to show the updated queue immediately

        st.markdown("---")
        st.subheader("Current Queue")

        if not help_queue:
            st.info("The queue is currently empty. 🎉")
        else:
            for i, student in enumerate(help_queue, 1):
                st.markdown(f"#### {i}. {student['name']}")

        st.markdown("---")

        with st.expander("👨‍🏫 Helper Controls (Password Required)"):
            password = st.text_input("Enter password", type="password")
            if password == "teacher123":
                st.success("Correct Password. Controls are active.", icon="✅")
                
                if help_queue:
                    student_options = [f"{i+1}. {s['name']}" for i, s in enumerate(help_queue)]
                    student_to_remove = st.selectbox("Select student to remove:", options=student_options)
                    
                    if st.button("Remove Selected Student"):
                        selected_index = student_options.index(student_to_remove)
                        help_queue.pop(selected_index)
                        set_data("/help_queue", help_queue)
                        st.toast("Student removed.", icon="🗑️")
                        st.rerun()

                if st.button("Clear Entire Queue", type="primary"):
                    set_data("/help_queue", [])
                    st.toast("Queue cleared!", icon="💥")
                    st.rerun()
    
    # --- Column 2: Q&A Board ---
    with col2:
        st.header("❓ Peer Q&A Board")
        
        # Fetch questions from Firebase
        questions = get_data("/questions") or []

        with st.expander("Ask a new question..."):
            with st.form("new_question_form", clear_on_submit=True):
                author = st.text_input("Your Name:")
                text = st.text_area("Your Question:")
                if st.form_submit_button("Post Question", type="primary"):
                    new_question = {"author": author, "question": text, "answers": []}
                    questions.append(new_question)
                    set_data("/questions", questions)
                    st.success("Question posted!")
                    st.rerun()

        st.markdown("---")

        if not questions:
            st.info("No questions yet. Be the first!")
        else:
            # Iterate through questions in reverse for newest first
            for idx, q in enumerate(reversed(questions)):
                st.markdown(f"**Q: {q['question']}** - *Asked by {q['author']}*")
                
                # Display answers if they exist
                if 'answers' in q and q['answers']:
                    for ans in q['answers']:
                        st.info(f"**A:** {ans['answer']} - *Answered by {ans['author']}*")

                with st.form(key=f"answer_form_{idx}", clear_on_submit=True):
                    ans_author = st.text_input("Your Name:", key=f"ans_auth_{idx}")
                    ans_text = st.text_area("Your Answer:", key=f"ans_text_{idx}")
                    if st.form_submit_button("Submit Answer"):
                        new_answer = {"author": ans_author, "answer": ans_text}
                        
                        # Find the original question index
                        original_idx = len(questions) - 1 - idx
                        
                        # Initialize 'answers' list if it doesn't exist
                        if 'answers' not in questions[original_idx]:
                            questions[original_idx]['answers'] = []
                            
                        questions[original_idx]['answers'].append(new_answer)
                        set_data("/questions", questions)
                        st.rerun()
                st.markdown("---")
