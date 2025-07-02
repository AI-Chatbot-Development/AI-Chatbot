import streamlit as st
from chatbot import get_answer, load_faq
import datetime
import os

LOG_PATH = os.path.join(os.path.dirname(__file__), '../data/log.txt')

def log_interaction(user_input, response, match_score=None, selected=None):
    print(f"[LOG] INPUT: {user_input} | SCORE: {match_score}")  # Log to terminal
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now().isoformat()} | INPUT: {user_input} | RESPONSE: {response} | SCORE: {match_score} | SELECTED: {selected}\n")

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
            st.success(pattern_to_response[best_q])
            log_interaction(user_input, pattern_to_response[best_q], best_score, best_q)
        else:
            scored = []
            for q in all_patterns:
                _, score = get_best_match(user_input, [q])
                scored.append((q, score))
            scored.sort(key=lambda x: x[1], reverse=True)
            options = [q for q, s in scored[:3]]
            if len(options) == 1:
                st.info(pattern_to_response[options[0]])
                log_interaction(user_input, pattern_to_response[options[0]], best_score, options[0])
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
                        st.info(pattern_to_response[selected])
                        log_interaction(user_input, pattern_to_response[selected], best_score, selected)
                    else:
                        st.warning("This question has been forwarded to support.")
                        log_interaction(user_input, "Forwarded to support", best_score, None)
