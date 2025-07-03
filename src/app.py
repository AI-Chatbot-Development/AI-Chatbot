import streamlit as st
import datetime
import uuid
import time
import os
import json
from chatbot import load_faq
from nlp_agent import get_best_match
from database import init_db, log_interaction, log_feedback, log_escalation
from gtts import gTTS
import base64

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Bitsy - BITS College AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with college brand color #7EC143 - Light/Dark Mode Compatible
st.markdown("""
<style>
/* Main gradient background - Auto-adapts to theme */
.main > div {
    background: var(--background-color);
    color: var(--text-color);
    transition: all 0.3s ease;
}

/* CSS Variables for theme adaptation */
:root {
    --background-color: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    --text-color: #212529;
    --card-background: #ffffff;
    --border-color: #dee2e6;
    --sidebar-background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
    --sidebar-text: #495057;
}

@media (prefers-color-scheme: dark) {
    :root {
        --background-color: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        --text-color: #ffffff;
        --card-background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        --border-color: #4a5568;
        --sidebar-background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
        --sidebar-text: #ffffff;
    }
}

/* Header with brand color gradient */
.main-header {
    background: linear-gradient(135deg, #7EC143 0%, #5a9b32 50%, #4a7c28 100%);
    padding: 1.5rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    text-align: center;
    color: white;
    box-shadow: 0 8px 25px rgba(126, 193, 67, 0.3);
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
    0%, 100% { transform: rotate(0deg); }
    50% { transform: rotate(180deg); }
}

.main-header h1 {
    margin: 0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    position: relative;
    z-index: 1;
}

.main-header p {
    margin: 0.5rem 0 0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 1rem;
    opacity: 0.9;
    position: relative;
    z-index: 1;
}

/* Sidebar styling - Theme adaptive */
.css-1d391kg {
    background: var(--sidebar-background) !important;
}

.sidebar .sidebar-content {
    background: var(--sidebar-background) !important;
    color: var(--sidebar-text) !important;
}

/* Sidebar content styling */
section[data-testid="stSidebar"] {
    background: var(--sidebar-background) !important;
}

section[data-testid="stSidebar"] > div {
    background: var(--sidebar-background) !important;
    color: var(--sidebar-text) !important;
}

/* Sidebar text elements */
section[data-testid="stSidebar"] .stMarkdown {
    color: var(--sidebar-text) !important;
}

section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3 {
    color: #7EC143 !important;
    font-weight: 600;
}

/* Chat input styling - Theme adaptive */
.stChatFloatingInputContainer {
    bottom: 1rem;
    max-width: 65%;
    margin: 0 auto;
}

.stChatInputContainer > div {
    border-radius: 25px !important;
    border: 2px solid #7EC143 !important;
    background: var(--card-background) !important;
    box-shadow: 0 4px 15px rgba(126, 193, 67, 0.2) !important;
    transition: all 0.3s ease !important;
}

.stChatInputContainer > div:hover {
    box-shadow: 0 6px 20px rgba(126, 193, 67, 0.3) !important;
    transform: translateY(-1px);
}

.stChatInputContainer input {
    border: none !important;
    background-color: transparent !important;
    font-size: 14px !important;
    padding: 12px 20px !important;
    color: var(--text-color) !important;
}

.stChatInputContainer input:focus {
    box-shadow: 0 0 0 2px rgba(126, 193, 67, 0.4) !important;
    border-color: #7EC143 !important;
}

.stChatInputContainer input::placeholder {
    color: #6c757d !important;
    font-style: italic;
}

/* Send button styling */
.stChatInputContainer button {
    background: linear-gradient(135deg, #7EC143 0%, #6bb032 100%) !important;
    border: none !important;
    border-radius: 50% !important;
    width: 40px !important;
    height: 40px !important;
    margin-right: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 3px 10px rgba(126, 193, 67, 0.4) !important;
}

.stChatInputContainer button:hover {
    background: linear-gradient(135deg, #6bb032 0%, #5a9b32 100%) !important;
    transform: scale(1.05);
    box-shadow: 0 4px 15px rgba(126, 193, 67, 0.6) !important;
}

/* Microphone button styling */
.mic-button {
    background: linear-gradient(135deg, #ff6b6b 0%, #e63946 100%) !important;
    border: none !important;
    border-radius: 50% !important;
    width: 40px !important;
    height: 40px !important;
    margin-right: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 3px 10px rgba(255, 107, 107, 0.4) !important;
}

.mic-button:hover {
    background: linear-gradient(135deg, #e63946 0%, #d32f2f 100%) !important;
    transform: scale(1.05);
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.6) !important;
}

/* Chat messages styling - Theme adaptive */
.stChatMessage {
    background: var(--card-background) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    margin: 0.5rem 0 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    color: var(--text-color) !important;
}

.stChatMessage [data-testid="stMarkdownContainer"] {
    color: var(--text-color) !important;
}

.stChatMessage [data-testid="stMarkdownContainer"] p {
    color: var(--text-color) !important;
}

/* Sidebar buttons - Theme adaptive */
section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #7EC143 0%, #6bb032 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(126, 193, 67, 0.3) !important;
    width: 100% !important;
    margin-bottom: 0.5rem !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #6bb032 0%, #5a9b32 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(126, 193, 67, 0.4) !important;
}

/* Main content buttons */
.stButton > button {
    background: linear-gradient(135deg, #7EC143 0%, #6bb032 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 15px !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(126, 193, 67, 0.3) !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #6bb032 0%, #5a9b32 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(126, 193, 67, 0.4) !important;
}

/* Success and info messages - Theme adaptive */
.stSuccess {
    background: linear-gradient(135deg, #7EC143 0%, #6bb032 100%) !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
}

.stInfo {
    background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%) !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
}

/* Modern greeting section - Theme adaptive */
.greeting-container {
    background: var(--card-background);
    border-radius: 12px;
    padding: 1rem;
    margin: 1rem 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    border: 2px solid #7EC143;
    text-align: center;
}

.greeting-container h3 {
    color: #7EC143 !important;
    margin-bottom: 0.5rem;
    font-size: 1.2rem !important;
}

/* Spinner customization */
.stSpinner > div {
    border-top-color: #7EC143 !important;
}

/* Modern Chat Stats styling - Theme adaptive */
.metric-container {
    background: var(--card-background) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 16px !important;
    padding: 1.5rem 1rem !important;
    text-align: center !important;
    box-shadow: 0 6px 20px rgba(126, 193, 67, 0.15) !important;
    position: relative !important;
    overflow: hidden !important;
    transition: all 0.3s ease !important;
}

.metric-container::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 4px !important;
    background: linear-gradient(90deg, #7EC143 0%, #6bb032 50%, #7EC143 100%) !important;
}

.metric-container:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(126, 193, 67, 0.25) !important;
}

.metric-container h3 {
    color: #7EC143 !important;
    margin: 0 !important;
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    letter-spacing: -1px !important;
    line-height: 1 !important;
    text-shadow: none !important;
}

.metric-container p {
    color: var(--sidebar-text) !important;
    margin: 0.5rem 0 0 0 !important;
    opacity: 0.8 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    text-shadow: none !important;
}

/* Text input styling - Theme adaptive */
.stTextInput > div > div > input {
    background-color: var(--card-background) !important;
    color: var(--text-color) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
}

.stTextInput > div > div > input:focus {
    border-color: #7EC143 !important;
    box-shadow: 0 0 0 1px #7EC143 !important;
}

/* Fix for general text visibility - Theme adaptive */
.main .block-container {
    color: var(--text-color);
}

/* Ensure proper text color inheritance */
p, span, div {
    color: inherit !important;
}

.stMarkdown {
    color: var(--text-color) !important;
}

.stWrite {
    color: var(--text-color) !important;
}

/* Sidebar info box styling */
section[data-testid="stSidebar"] .stInfo {
    background: linear-gradient(135deg, #7EC143 0%, #6bb032 100%) !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
}

/* Ensure sidebar elements are visible in both themes */
section[data-testid="stSidebar"] * {
    color: var(--sidebar-text) !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {
    color: #7EC143 !important;
}

/* Light mode specific adjustments */
@media (prefers-color-scheme: light) {
    .stChatMessage {
        box-shadow: 0 2px 1px rgba(0,0,0,0.08) !important;
    }
    
    .greeting-container {
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
}

/* Dark mode specific adjustments */
@media (prefers-color-scheme: dark) {
    .stChatMessage {
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
    }
    
    .greeting-container {
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
}
</style>
""", unsafe_allow_html=True)

# JavaScript for Web Speech API
st.markdown("""
<script>
const startRecognition = () => {
    if (!('webkitSpeechRecognition' in window)) {
        alert('Sorry, your browser does not support speech recognition.');
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('speech-input').value = transcript;
        document.getElementById('speech-input').dispatchEvent(new Event('input', { bubbles: true }));
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        alert('Error during speech recognition: ' + event.error);
    };

    recognition.onend = () => {
        console.log('Speech recognition ended.');
    };

    recognition.start();
};
</script>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = []
if 'history' not in st.session_state:
    st.session_state.history = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'pending_suggestion' not in st.session_state:
    st.session_state.pending_suggestion = None

# --- PERSISTENT BOOKMARK STORAGE ---
BOOKMARKS_FILE = 'bookmarks.json'

def load_bookmarks():
    if os.path.exists(BOOKMARKS_FILE):
        with open(BOOKMARKS_FILE, 'r') as file:
            return json.load(file)
    return []

def save_bookmarks(bookmarks):
    with open(BOOKMARKS_FILE, 'w') as file:
        json.dump(bookmarks, file, indent=4)

# Initialize bookmarks from file
if not st.session_state.bookmarks:
    st.session_state.bookmarks = load_bookmarks()

# --- INIT DB & FAQ ---
init_db()
faq = load_faq()
all_patterns = [pattern for item in faq for pattern in item.get("patterns", [])]
pattern_to_response = {pattern: item.get("response", "") for item in faq for pattern in item.get("patterns", [])}

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 📚 Quick Help")

    # Bookmarks section - only show if bookmarks exist
    if st.session_state.bookmarks:
        st.markdown("### 🔖 Bookmarked Answers")
        for i, bm in enumerate(st.session_state.bookmarks):
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"📌 {bm['label']}", key=f"bm_view_{i}"):
                    st.session_state.pending_suggestion = bm['query']
            with col2:
                if st.button("🗑️", key=f"bm_delete_{i}", help="Delete bookmark"):
                    st.session_state.bookmarks.pop(i)
                    save_bookmarks(st.session_state.bookmarks)
                    st.rerun()

        if st.button("🗑️ Clear All Bookmarks", key="clear_bms"):
            st.session_state.bookmarks = []
            save_bookmarks(st.session_state.bookmarks)
            st.rerun()

    st.markdown("### 🚀 Quick Actions")
    if st.button("📋 Course Registration", key="reg_btn"):
        st.session_state.pending_suggestion = "How do I register for classes?"
    if st.button("📊 Check Attendance Policy", key="attend_btn"):
        st.session_state.pending_suggestion = "What is the attendance requirement?"
    if st.button("💰 Payment Information", key="pay_btn"):
        st.session_state.pending_suggestion = "Can I pay tuition in installments?"
    if st.button("📜 Get Transcript", key="trans_btn"):
        st.session_state.pending_suggestion = "How do I get my transcript?"

    st.markdown("### 📋 Common Topics")
    for topic in [
        "Class Registration", "Attendance Policy", "Tuition Payment",
        "Academic Advising", "Course Exemptions", "Transcripts"
    ]:
        st.markdown(f"• {topic}")

    st.markdown("### 📞 Need Human Help?")
    st.info(
        "📧 **Email:** registrar@bits.edu.et\n\n"
        "📱 **Phone:** +251-11-xxx-xxxx\n\n"
        "🕒 **Office Hours:** 8AM-5PM"
    )

    if st.session_state.history:
        st.markdown("### 📈 Chat Stats")
        st.markdown(f"""
        <div class="metric-container">
            <h3>{len(st.session_state.history)}</h3>
            <p>Messages Exchanged</p>
        </div>
        """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🎓 Bitsy - BITS College AI Assistant</h1>
    <p>Your intelligent companion for college queries and support</p>
</div>
""", unsafe_allow_html=True)

# --- CENTER GREETING UI - Modern and compact ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if not st.session_state.user_name:
        st.markdown("""
        <div class="greeting-container">
            <h3>👋 Let's get started!</h3>
        </div>
        """, unsafe_allow_html=True)
        name_input = st.text_input("", placeholder="What should I call you?")
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
        cols = st.columns(3)
        suggestions = [
            "How do I register for classes?",
            "What's the attendance policy?", 
            "Can I pay tuition in installments?"
        ]
        for i, suggestion in enumerate(suggestions):
            with cols[i]:
                if st.button(suggestion, key=f"suggestion_{i}"):
                    st.session_state.pending_suggestion = suggestion

# --- CHAT HISTORY ---
for i, message in enumerate(st.session_state.history):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("type") == "answer":
            if st.button("🔖 Bookmark", key=f"bookmark_{i}"):
                user_msg = st.session_state.history[i-1]["content"] if i > 0 else "Query"
                st.session_state.bookmarks.append({
                    "query": user_msg,
                    "label": user_msg[:40] + ("..." if len(user_msg) > 40 else ""),
                    "answer": message["content"],
                    "timestamp": datetime.datetime.now().isoformat()
                })
                save_bookmarks(st.session_state.bookmarks)
                st.success("🔖 Bookmarked!")

        # Display audio for assistant responses
        if message["role"] == "assistant" and message.get("type") == "answer" and "audio_file" in message:
            st.audio(message["audio_file"], format="audio/mp3")

        # Handle feedback for answers
        if message.get("type") == "answer" and "interaction_id" in message:
            interaction_id = message['interaction_id']
            feedback_state_key = f"feedback_given_{interaction_id}"
            feedback_type_key = f"feedback_type_{interaction_id}"
            
            if not st.session_state.get(feedback_state_key, False):
                col1, col2, _ = st.columns([1, 1, 8])
                with col1:
                    if st.button("👍", key=f"up_{interaction_id}", help="This answer was helpful"):
                        log_feedback(interaction_id, 1)
                        st.session_state[feedback_state_key] = True
                        st.session_state[feedback_type_key] = "positive"
                        st.rerun()
                with col2:
                    if st.button("👎", key=f"down_{interaction_id}", help="This answer was not helpful"):
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
                    
                    # Generate audio for the response
                    tts = gTTS(text=response, lang='en')
                    audio_file = f"response_{uuid.uuid4()}.mp3"
                    tts.save(audio_file)
                    
                    st.session_state.history.append({"role": "user", "content": option})
                    interaction_id = log_interaction(st.session_state.session_id, original_prompt, response, 0.85)
                    st.session_state.history.append({
                        "role": "assistant",
                        "content": response,
                        "type": "answer",
                        "interaction_id": interaction_id,
                        "audio_file": audio_file
                    })
                    
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
    
    with st.spinner("🤔 Thinking..."):
        best_q, best_score = get_best_match(prompt, all_patterns)

        if best_q and best_score >= 0.5:  # Reduced from 0.75
            response = pattern_to_response[best_q]
            # Generate audio for the response
            tts = gTTS(text=response, lang='en')
            audio_file = f"response_{uuid.uuid4()}.mp3"
            tts.save(audio_file)
            
            interaction_id = log_interaction(st.session_state.session_id, prompt, response, best_score)
            st.session_state.history.append({
                "role": "assistant",
                "content": response,
                "type": "answer",
                "interaction_id": interaction_id,
                "audio_file": audio_file
            })
        else:
            scored = []
            for p in all_patterns:
                _, score = get_best_match(prompt, [p])
                scored.append((p, score))
            
            scored.sort(key=lambda x: x[1], reverse=True)
            options = [q for q, s in scored[:3] if s > 0.3]

            if options:
                response = "I'm not sure I understood. Did you mean one of these?"
                st.session_state.history.append({"role": "assistant", "content": response, "type": "options", "options": options})
            else:
                response = "I'm not sure how to answer that. This query has been escalated to a human agent."
                st.session_state.history.append({"role": "assistant", "content": response, "type": "escalated"})
                log_escalation(prompt)
    
    st.rerun()

# --- CHAT INPUT WITH MICROPHONE ---
col1, col2, col3 = st.columns([1, 10, 1])
with col1:
    if st.button("🎙️", key="mic_button", help="Speak your question"):
        st.markdown("""
        <input type="hidden" id="speech-input" />
        <script>startRecognition();</script>
        """, unsafe_allow_html=True)
with col2:
    prompt = st.chat_input("💬 Ask me anything about BITS College...", key="speech-input")
with col3:
    pass

if prompt:
    # Add user message
    st.session_state.history.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("🤔 Thinking..."):
        best_q, best_score = get_best_match(prompt, all_patterns)

        if best_q and best_score >= 0.5:
            response = pattern_to_response[best_q]
            # Generate audio for the response
            tts = gTTS(text=response, lang='en')
            audio_file = f"response_{uuid.uuid4()}.mp3"
            tts.save(audio_file)
            
            interaction_id = log_interaction(st.session_state.session_id, prompt, response, best_score)
            st.session_state.history.append({
                "role": "assistant",
                "content": response,
                "type": "answer",
                "interaction_id": interaction_id,
                "audio_file": audio_file
            })
        else:
            # Generate options for unclear queries with more lenient scoring
            scored = []
            for p in all_patterns:
                _, score = get_best_match(prompt, [p])
                scored.append((p, score))
            
            scored.sort(key=lambda x: x[1], reverse=True)
            options = [q for q, s in scored[:3] if s > 0.3] 

            if options:
                response = "I'm not sure I understood. Did you mean one of these?"
                st.session_state.history.append({"role": "assistant", "content": response, "type": "options", "options": options})
            else:
                response = "I'm not sure how to answer that. This query has been escalated to a human agent."
                st.session_state.history.append({"role": "assistant", "content": response, "type": "escalated"})
                log_escalation(prompt)
    
    st.rerun()