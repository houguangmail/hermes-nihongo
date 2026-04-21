
import streamlit as st
import random

# --- CONFIGURATION ---
st.set_page_config(page_title="Hermes Nihongo", page_icon="🇯🇵", layout="centered")

# Custom CSS for a mobile-app feel
st.markdown("""
    <style>
    .stApp {
        max-width: 600px;
        margin: 0 auto;
    }
    .stChatMessage {
        border-radius: 15px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'mode' not in st.session_state:
    st.session_state.mode = "Simulation"

# --- SIDEBAR / SETTINGS ---
with st.sidebar:
    st.title("Settings")
    st.session_state.mode = st.selectbox(
        "Training Mode", 
        ["Simulation", "Correction", "Daily Challenge"]
    )
    st.write(f"Current Mode: **{st.session_state.mode}**")
    
    st.divider()
    st.info("Tip: Use the voice-to-text feature on your iOS keyboard for the best experience!")

# --- AI LOGIC (MOCKED FOR NOW, READY FOR API) ---
def get_ai_response(user_input, mode):
    # In a real scenario, this would call the LLM API.
    # We will simulate the 'Mix & Match' logic here.
    
    if mode == "Simulation":
        return f"【シミュレーション】\n\nこんにちは！ (Konnichiwa!)\n\nI'm acting as your conversation partner. You said: '{user_input}'.\n\nHow would you respond if we were in a cafe right now?"
    
    elif mode == "Correction":
        return f"【添削】\n\nYour sentence: '{user_input}'\n\nSuggested: '...\n\nExplanation: In this context, using 'desu' makes it sound more polite. Keep it up!"
    
    elif mode == "Daily Challenge":
        return f"【今日の挑戦】\n\nChallenge: Try to use the word '美味しい' (Oishii - Delicious) in a sentence related to your breakfast!"
    
    return "こんにちは！"

# --- UI ---
st.title("🇯🇵 Hermes Nihongo")
st.caption("Your personal AI Japanese Coach")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INPUT ---
if prompt := st.chat_input("Type or speak in Japanese..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI Response
    with st.chat_message("assistant"):
        response = get_ai_response(prompt, st.session_state.mode)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- VOICE Integration (Conceptual) ---
# For iOS, the most reliable way to get voice-to-text is via the native keyboard.
# For text-to-speech, we can embed a simple HTML5 audio element or use a TTS API.
