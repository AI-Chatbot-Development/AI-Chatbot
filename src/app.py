import streamlit as st
from chatbot import load_faq
from nlp_agent import get_best_match

st.title("Bitsy")

user_input = st.text_input("Ask a question:")
faq = load_faq()

all_patterns = []
pattern_to_response = {}
for item in faq:
    for pattern in item.get("patterns", []):
        all_patterns.append(pattern)
        pattern_to_response[pattern] = item.get("response", "")

if user_input:
    best_q, best_score = get_best_match(user_input, all_patterns)

    if best_q and best_score >= 0.8:
        st.markdown(f"**Matched Question:** {best_q}")
        st.success(pattern_to_response[best_q])
        st.caption(f"Confidence Score: {best_score:.2f}")
    else:
        st.warning("I couldn’t confidently match your question. Here are a few close ones:")
        scored = []
        for q in all_patterns:
            _, score = get_best_match(user_input, [q])
            scored.append((q, score))
        scored.sort(key=lambda x: x[1], reverse=True)

        for q, score in scored[:3]:
            st.markdown(f"**{q}**")
            st.info(pattern_to_response[q])
            st.caption(f"Score: {score:.2f}")
