
import streamlit as st
import requests
import json
import re
from streamlit.components.v1 import html

# --- CONFIGURATION ---
st.set_page_config(page_title="Hermes Nihongo", page_icon="🇯🇵", layout="centered")

# Mobile-app styling for a native iOS feel
st.markdown("""
    <style>
    .stApp { max-width: 600px; margin: 0 auto; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'mode' not in st.session_state:
    st.session_state.mode = "Simulation"

# --- SIDEBAR ---
with st.sidebar:
    st.title("Sensei Settings")
    st.session_state.mode = st.selectbox(
        "Training Mode", 
        ["Simulation", "Correction", "Daily Challenge"]
    )
    st.session_state.voice_enabled = st.checkbox("🔊 Enable Voice", value=True)
    st.divider()
    st.info("🎙️ Tip: Use the iOS keyboard microphone for voice-to-text!")

# --- AI LOGIC ---
def get_local_ai_response(user_input, mode):
    # Access the URL from Streamlit Secrets
    try:
        base_url = st.secrets["LOCAL_AI_URL"]
    except KeyError:
        return "⚠️ Error: LOCAL_AI_URL not found in Streamlit Secrets. Please add it in the app settings!"

    # Advanced System Prompts to turn Gemma 4 into a professional coach
    mode_prompts = {
        "Simulation": (
            "You are a friendly, natural Japanese conversation partner. "
            "Keep responses concise and conversational. For every response, strictly use this format:\n"
            "1. [Japanese text]\n"
            "2. [Romaji]\n"
            "3. [English translation]\n\n"
            "Then, ask a follow-up question to keep the conversation moving. Stay in character!"
        ),
        "Correction": (
            "You are a professional Japanese linguist and teacher. Analyze the user's Japanese input carefully. "
            "Your goal is to make them sound like a native speaker. Strictly use this format:\n"
            "✅ Corrected: [The corrected Japanese sentence]\n"
            "📖 Romaji: [Romaji of corrected sentence]\n"
            "🌍 English: [English translation]\n\n"
            "💡 Explanation: [Explain the grammar or nuance change. Why is the correction better?]\n"
            "✨ Natural Alternative: [How a native speaker would actually say this in a real-world setting]."
        ),
        "Daily Challenge": (
            "You are a Japanese vocabulary coach. Give the user a daily challenge: "
            "introduce one useful word or grammar point and ask them to use it in a sentence. "
            "Once they try it, provide a detailed critique, Romaji, and English translation. "
            "If they get it perfectly, give them a gold star (⭐)!"
        )
    }

    system_prompt = mode_prompts.get(mode, "You are a helpful Japanese teacher.")
    
    # Construct the payload for an OpenAI-compatible server (oMLX/SGLang/vLLM)
    payload = {
        "model": "Gemma-4-31B-it-4bit", 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "stream": False,
        "temperature": 0.7
    }

    # Attempt connectivity using a fallback loop to solve 404 errors
    endpoints = ["/v1/chat/completions", "/chat/completions", "/generate"]
    
    for endpoint in endpoints:
        try:
            full_url = f"{base_url.rstrip('/')}{endpoint}"
            response = requests.post(full_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                # Handle different response formats (OpenAI style vs raw generation)
                if 'choices' in result:
                    return result['choices'][0]['message']['content']
                elif 'content' in result:
                    return result['content']
                elif 'text' in result:
                    return result['text']
            
            # If it's not a 200, we try the next endpoint in the list
            continue
            
        except Exception:
            continue

    return "❌ Sensei is currently offline. I tried several connection paths, but couldn't reach your MacBook. Please check if Ngrok is running!"

# --- UI ---
st.title("🇯🇵 Hermes Nihongo")
st.caption("Powered by Gemma 4 31B on M5 Pro")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INPUT ---
if prompt := st.chat_input("Type or speak in Japanese..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Sensei is thinking..."):
            response = get_local_ai_response(prompt, st.session_state.mode)
            st.markdown(response)
            
            # --- Voice Synthesis ---
            if st.session_state.voice_enabled:
                # Extract Japanese characters for clean pronunciation
                jp_text = "".join(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]+', response))
                # Fallback to full response if no Japanese found
                speech_text = jp_text if jp_text else response
                # Trigger native iOS voice via JS
                html(f'''
                    <script>
                    var msg = new SpeechSynthesisUtterance("{speech_text}");
                    msg.lang = "ja-JP";
                    window.speechSynthesis.speak(msg);
                    </script>
                ''', height=0)
                
            st.session_state.messages.append({"role": "assistant", "content": response})
