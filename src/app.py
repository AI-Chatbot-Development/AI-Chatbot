import streamlit as st
from chatbot import get_answer

st.title("Bitsy")

user_input = st.text_input("Ask a question:")

if user_input:
    response = get_answer(user_input)
    st.write(response)
