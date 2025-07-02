import streamlit as st
import datetime
import uuid
from chatbot import load_faq
from nlp_agent import get_best_match
from database import init_db, log_interaction, log_feedback, log_escalation

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Bitsy - BITS College AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR STYLE ---
st.markdown("""
<style>
/* Header with the logo's dark gray to green gradient */
.main-header {
    background: linear-gradient(90deg, #4a525b 0%, #7dc53f 100%);
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    text-align: center;
    color: white;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-weight: 700;
}
.main-header h1 {
    margin: 0;
    font-size: 2.4rem;
    letter-spacing: 0.05em;
}
.main-header p {
    margin: 0.2rem 0 0;
    font-size: 1.1rem;
    opacity: 0.85;
    font-weight: 400;
}

/* Chat container with subtle light gray background */
.chat-container {
    max-height: 600px;
    overflow-y: auto;
    padding: 1rem;
    border: 1px solid #d0d5db; /* soft gray */
    border-radius: 12px;
    background-color: #f9fafb; /* very light gray */
}

/* Feedback buttons style */
.feedback-buttons {
    margin-top: 0.5rem;
}

/* Sidebar background uses the light gray */
[data-testid="stSidebar"] {
    background-color: #f3f4f6; /* soft off-white */
    color: #4a525b; /* dark gray text */
}

/* Button styling to match green accent */
button, .stButton>button {
    background-color: #7dc53f;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 8px 14px;
    font-weight: 600;
    transition: background-color 0.3s ease;
}
button:hover, .stButton>button:hover {
    background-color: #6bb22d;
}

/* Chat messages with subtle shadow */
.stChatMessage {
    box-shadow: 0 2px 6px rgba(74, 82, 91, 0.1);
    border-radius: 8px;
    padding: 10px 14px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Input box styling */
[data-testid="stTextInput"] > div > input {
    height: 44px;
    border-radius: 8px;
    border: 1.5px solid #7dc53f;
    font-size: 1rem;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    padding-left: 10px;
}
</style>


""", unsafe_allow_html=True)

# --- SIDEBAR: Quick Help + Info ---
with st.sidebar:
    st.header("📚 Quick Help")

    # Quick action buttons to pre-fill common questions
  
    if st.button("📋 Course Registration"):
        st.session_state['chat_input'] = "How do I register for classes?"
    if st.button("📊  Attendance Policy"):
        st.session_state['chat_input'] = "What is the attendance requirement?"
    if st.button("💰 Payment Information"):
        st.session_state['chat_input'] = "Can I pay tuition in installments?"
    if st.button("📜 Get Transcript"):
        st.session_state['chat_input'] = "How do I get my transcript?"

    # Common FAQ topics listed as text
    st.subheader("📋 Common Topics")
    topics = [
        "Class Registration",
        "Attendance Policy",
        "Tuition Payment",
        "Academic Advising",
        "Course Exemptions",
        "Transcripts"
    ]
    for topic in topics:
        st.write(f"• {topic}")

    # Contact info for human help
    st.subheader("📞 Need Human Help?")
    st.info(
        "📧 Email: registrar@bits.edu.et\n"
        "📱 Phone: +251-11-000-0000\n"
        "🕒 Office Hours: 8AM-5PM"
    )

    # Chat statistics example (replace with dynamic value if available)
    if 'history' in st.session_state and st.session_state.history:
        st.subheader("📈 Chat Stats")
        st.metric("Messages", len(st.session_state.history))

# --- INITIALIZATION ---
init_db()
faq = load_faq()
all_patterns = [pattern for item in faq for pattern in item.get("patterns", [])]
pattern_to_response = {pattern: item.get("response", "") for item in faq for pattern in item.get("patterns", [])}

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'history' not in st.session_state:
    st.session_state.history = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🎓 Bitsy - BITS College AI Assistant</h1>
    <p>Your intelligent companion for college queries and support</p>
</div>
""", unsafe_allow_html=True)

# --- GREETING LOGIC ---
hour = datetime.datetime.now().hour
greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"

if not st.session_state.user_name:
    st.session_state.user_name = st.text_input("What's your name?")
    if st.session_state.user_name:
        st.balloons()
        st.success(f"Welcome, {st.session_state.user_name}!")

if st.session_state.user_name:
    with st.chat_message("assistant"):
        st.write(f"{greeting}, {st.session_state.user_name}! How can I help you today?")

# --- CHAT HISTORY ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for i, message in enumerate(st.session_state.history):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("type") == "answer" and "interaction_id" in message:
            interaction_id = message['interaction_id']
            feedback_state_key = f"feedback_given_{interaction_id}"
            feedback_type_key = f"feedback_type_{interaction_id}"

            if not st.session_state.get(feedback_state_key, False):
                col1, col2, _ = st.columns([1, 1, 8])
                if col1.button("👍", key=f"up_{interaction_id}", help="This answer was helpful"):
                    log_feedback(interaction_id, 1)
                    st.session_state[feedback_state_key] = True
                    st.session_state[feedback_type_key] = "positive"
                    st.rerun()
                if col2.button("👎", key=f"down_{interaction_id}", help="This answer was not helpful"):
                    log_feedback(interaction_id, -1)
                    st.session_state[feedback_state_key] = True
                    st.session_state[feedback_type_key] = "negative"
                    st.rerun()
            else:
                feedback_type = st.session_state.get(feedback_type_key, "unknown")
                if feedback_type == "positive":
                    st.success("🎉 Thank you for your feedback! We're glad this was helpful.")
                elif feedback_type == "negative":
                    st.info("💡 Thank you for your feedback! We'll use it to improve our responses.")
                else:
                    st.success("✅ Thank you for your feedback!")

        if message.get("type") == "options" and message.get("options") and not message.get("selection_made"):
            options = message["options"]
            original_prompt = st.session_state.history[i-1]['content']
            for option in options:
                if st.button(option, key=f"option_{i}_{option}"):
                    response = pattern_to_response[option]
                    st.session_state.history.append({"role": "user", "content": option})
                    interaction_id = log_interaction(st.session_state.session_id, original_prompt, response, 0.85)
                    st.session_state.history.append({"role": "assistant", "content": response, "type": "answer", "interaction_id": interaction_id})
                    st.session_state.history[i]["selection_made"] = True
                    st.rerun()
            if st.button("None of these", key=f"escalate_{i}"):
                response = "I'm sorry I couldn't help. Your query has been escalated to a human agent."
                st.session_state.history.append({"role": "user", "content": "None of these"})
                st.session_state.history.append({"role": "assistant", "content": response, "type": "escalated"})
                log_escalation(original_prompt)
                st.session_state.history[i]["selection_made"] = True
                st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT INPUT ---
if prompt := st.chat_input("Ask me anything about BITS College..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):
        best_q, best_score = get_best_match(prompt, all_patterns)

        if best_q and best_score >= 0.75:
            response = pattern_to_response[best_q]
            interaction_id = log_interaction(st.session_state.session_id, prompt, response, best_score)
            st.session_state.history.append({"role": "assistant", "content": response, "type": "answer", "interaction_id": interaction_id})
            st.rerun()
        else:
            scored = []
            for p in all_patterns:
                _, score = get_best_match(prompt, [p])
                scored.append((p, score))
            scored.sort(key=lambda x: x[1], reverse=True)
            options = [q for q, s in scored[:3] if s > 0.5]
            if options:
                response = "I'm not sure I understood. Did you mean one of these?"
                st.session_state.history.append({"role": "assistant", "content": response, "type": "options", "options": options})
                st.rerun()
            else:
                response = "I'm not sure how to answer that. This query has been escalated to a human agent."
                st.session_state.history.append({"role": "assistant", "content": response, "type": "escalated"})
                log_escalation(prompt)
                st.rerun()
