import streamlit as st
from chatbot import get_answer, load_faq
import uuid
from database import init_db, log_interaction as db_log_interaction, log_escalation

init_db()

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("Bitsy")

col1, col2 = st.columns([0.85, 0.15])
user_input = col1.text_input("Ask a question:", label_visibility="collapsed", placeholder="Ask a question...")
send_button = col2.button("➤")


faq = load_faq()
all_patterns = []
pattern_to_response = {}
for item in faq:
    patterns = item.get("patterns", [])
    response = item.get("response", "")
    for pattern in patterns:
        all_patterns.append(pattern)
        pattern_to_response[pattern] = response

if user_input or send_button:
    from nlp_agent import get_best_match

    with st.spinner("Searching for the best answer..."):
        best_q, best_score = get_best_match(user_input, all_patterns)
        if best_q and best_score >= 0.8:
            response = pattern_to_response[best_q]
            st.success(response)
            db_log_interaction(st.session_state.session_id, user_input, response, best_score)
        else:
            scored = []
            for q in all_patterns:
                _, score = get_best_match(user_input, [q])
                scored.append((q, score))
            scored.sort(key=lambda x: x[1], reverse=True)
            options = [q for q, s in scored[:3]]
            if len(options) == 1:
                response = pattern_to_response[options[0]]
                st.info(response)
                db_log_interaction(st.session_state.session_id, user_input, response, best_score)
            else:
                st.warning("Did you mean one of these?")
                selected = None
                for i, q in enumerate(options):
                    col = st.columns(1)[0]
                    if col.button(q, key=f"btn_{i}"):
                        selected = q
                col = st.columns(1)[0]
                if col.button("Forward to support", key="btn_support"):
                    selected = "Forward to support"
                if selected:
                    if selected != "Forward to support":
                        response = pattern_to_response[selected]
                        st.info(response)
                        db_log_interaction(st.session_state.session_id, user_input, response, best_score)
                    else:
                        st.warning("This question has been forwarded to support.")
                        log_escalation(user_input)
