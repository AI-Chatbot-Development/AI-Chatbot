import streamlit as st
import datetime
import uuid
import time
from chatbot import load_faq
from nlp_agent import get_best_match
from database import init_db, log_interaction, log_feedback, log_escalation

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Bitsy - BITS College AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'history' not in st.session_state:
    st.session_state.history = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'chat_input' not in st.session_state:
    st.session_state.chat_input = ""
if 'pending_suggestion' not in st.session_state:
    st.session_state.pending_suggestion = None

# --- INIT DB & FAQ ---
init_db()
faq = load_faq()
all_patterns = [pattern for item in faq for pattern in item.get("patterns", [])]
pattern_to_response = {pattern: item.get("response", "") for item in faq for pattern in item.get("patterns", [])}

# --- SIDEBAR ---
with st.sidebar:
    st.header("📚 Quick Help")

    st.subheader("🚀 Quick Actions")
    if st.button("📋 Course Registration"):
        st.session_state.chat_input = "How do I register for classes?"
    if st.button("📊 Check Attendance Policy"):
        st.session_state.chat_input = "What is the attendance requirement?"
    if st.button("💰 Payment Information"):
        st.session_state.chat_input = "Can I pay tuition in installments?"
    if st.button("📜 Get Transcript"):
        st.session_state.chat_input = "How do I get my transcript?"

    st.subheader("📋 Common Topics")
    for topic in [
        "Class Registration", "Attendance Policy", "Tuition Payment",
        "Academic Advising", "Course Exemptions", "Transcripts"
    ]:
        st.write(f"• {topic}")

    st.subheader("📞 Need Human Help?")
    st.info(
        "📧 Email: registrar@bits.edu.et\n"
        "📱 Phone: +251-11-xxx-xxxx\n"
        "🕒 Office Hours: 8AM-5PM"
    )

    if st.session_state.history:
        st.subheader("📈 Chat Stats")
        st.metric("Messages", len(st.session_state.history))

# --- HEADER ---
st.markdown("""
<div style="background: linear-gradient(90deg, #4a525b 0%, #7dc53f 100%);
            padding: 1rem; border-radius: 10px; margin-bottom: 2rem; text-align:center; color:white;">
    <h1 style="margin:0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">🎓 Bitsy - BITS College AI Assistant</h1>
    <p style="margin:0.2rem 0 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        Your intelligent companion for college queries and support
    </p>
</div>
""", unsafe_allow_html=True)

# --- CENTER GREETING UI ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if not st.session_state.user_name:
        st.markdown("### 👋 Let's get started!")
        name_input = st.text_input("What should I call you?", placeholder="Enter your name here...")
        if name_input:
            st.session_state.user_name = name_input
            st.balloons()
            st.success(f"Nice to meet you, {name_input}! 🎉")

# --- CHAT GREETING ---
if st.session_state.user_name:
    hour = datetime.datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"

    with st.chat_message("assistant", avatar="🎓"):
        st.write(f"{greeting}, {st.session_state.user_name}! I'm here to help with BITS College questions.")

    if not st.session_state.history:
        st.write("Here are some things you can ask me:")
        for i, suggestion in enumerate([
            "How do I register for classes?",
            "What's the attendance policy?",
            "Can I pay tuition in installments?"
        ]):
            if st.button(suggestion, key=f"suggestion_{i}"):
                st.session_state.chat_input = suggestion

# --- CHAT HISTORY ---
st.markdown('<div style="max-height: 600px; overflow-y:auto; border:1px solid #d0d5db; border-radius:12px; padding:1rem; background-color:#f9fafb;">', unsafe_allow_html=True)
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT INPUT + RESPONSE HANDLER ---
if st.session_state.chat_input:
    user_input = st.session_state.chat_input
    st.session_state.chat_input = ""  # Clear it after use

    st.session_state.history.append({"role": "user", "content": user_input})

    # Typing animation
    placeholder = st.empty()
    placeholder.markdown("**Bot:** _Typing..._")
    time.sleep(1.5)

    best_q, best_score = get_best_match(user_input, all_patterns)

    if best_q and best_score >= 0.75:
        response = pattern_to_response[best_q]
        interaction_id = log_interaction(st.session_state.session_id, user_input, response, best_score)
        st.session_state.history.append({
            "role": "assistant",
            "content": response,
            "type": "answer",
            "interaction_id": interaction_id
        })
    else:
        response = "Sorry, I don't have an answer for that. I've escalated your question to a human staff member."
        log_escalation(user_input)
        st.session_state.history.append({"role": "assistant", "content": response, "type": "escalated"})

    placeholder.empty()

# Live input box
chat_typed = st.chat_input("Ask me anything about BITS College...")
if chat_typed:
    st.session_state.chat_input = chat_typed
