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
        st.session_state.pending_suggestion = "How do I register for classes?"
    if st.button("📊 Check Attendance Policy"):
        st.session_state.pending_suggestion = "What is the attendance requirement?"
    if st.button("💰 Payment Information"):
        st.session_state.pending_suggestion = "Can I pay tuition in installments?"
    if st.button("📜 Get Transcript"):
        st.session_state.pending_suggestion = "How do I get my transcript?"

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
                st.session_state.pending_suggestion = suggestion

# --- CHAT HISTORY ---
for i, message in enumerate(st.session_state.history):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Handle feedback for answers
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

        # Handle multiple choice options
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

# --- HANDLE PENDING SUGGESTIONS ---
if st.session_state.pending_suggestion:
    prompt = st.session_state.pending_suggestion
    st.session_state.pending_suggestion = None
    
    # Add user message
    st.session_state.history.append({"role": "user", "content": prompt})
    
    with st.spinner("Thinking..."):
        best_q, best_score = get_best_match(prompt, all_patterns)

        if best_q and best_score >= 0.75:
            response = pattern_to_response[best_q]
            interaction_id = log_interaction(st.session_state.session_id, prompt, response, best_score)
            st.session_state.history.append({"role": "assistant", "content": response, "type": "answer", "interaction_id": interaction_id})
        else:
            # Generate options for unclear queries
            scored = []
            for p in all_patterns:
                _, score = get_best_match(prompt, [p])
                scored.append((p, score))
            
            scored.sort(key=lambda x: x[1], reverse=True)
            options = [q for q, s in scored[:3] if s > 0.5]

            if options:
                response = "I'm not sure I understood. Did you mean one of these?"
                st.session_state.history.append({"role": "assistant", "content": response, "type": "options", "options": options})
            else:
                response = "I'm not sure how to answer that. This query has been escalated to a human agent."
                st.session_state.history.append({"role": "assistant", "content": response, "type": "escalated"})
                log_escalation(prompt)
    
    st.rerun()

# --- CHAT INPUT ---
if prompt := st.chat_input("Ask me anything about BITS College..."):
    # Add user message
    st.session_state.history.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):
        best_q, best_score = get_best_match(prompt, all_patterns)

        if best_q and best_score >= 0.75:
            response = pattern_to_response[best_q]
            interaction_id = log_interaction(st.session_state.session_id, prompt, response, best_score)
            st.session_state.history.append({"role": "assistant", "content": response, "type": "answer", "interaction_id": interaction_id})
        else:
            # Generate options for unclear queries
            scored = []
            for p in all_patterns:
                _, score = get_best_match(prompt, [p])
                scored.append((p, score))
            
            scored.sort(key=lambda x: x[1], reverse=True)
            options = [q for q, s in scored[:3] if s > 0.5]

            if options:
                response = "I'm not sure I understood. Did you mean one of these?"
                st.session_state.history.append({"role": "assistant", "content": response, "type": "options", "options": options})
            else:
                response = "I'm not sure how to answer that. This query has been escalated to a human agent."
                st.session_state.history.append({"role": "assistant", "content": response, "type": "escalated"})
                log_escalation(prompt)
    
    st.rerun()
