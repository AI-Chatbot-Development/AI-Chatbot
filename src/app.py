import streamlit as st
from chatbot import load_faq
from nlp_agent import get_best_match
from database import init_db, log_interaction, log_feedback, log_escalation
import datetime
import uuid

# --- INITIALIZATION ---
# Initialize database
init_db()

# Load FAQ data
faq = load_faq()
all_patterns = [pattern for item in faq for pattern in item.get("patterns", [])]
pattern_to_response = {pattern: item.get("response", "") for item in faq for pattern in item.get("patterns", [])}

# --- SESSION STATE ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'history' not in st.session_state:
    st.session_state.history = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- UI SETUP ---
st.title("Bitsy - The BITS College AI Assistant")

# --- PERSONALIZED GREETING ---
hour = datetime.datetime.now().hour
greeting = "Good morning"
if 12 <= hour < 18:
    greeting = "Good afternoon"
elif hour >= 18:
    greeting = "Good evening"

if not st.session_state.user_name:
    st.session_state.user_name = st.text_input("What's your name?")
    if st.session_state.user_name:
        st.balloons()
        st.success(f"Welcome, {st.session_state.user_name}!")

with st.chat_message("assistant"):
    st.write(f"{greeting}, {st.session_state.user_name}! How can I help you today?")

# --- CHAT HISTORY ---
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
