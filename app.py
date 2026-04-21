    import streamlit as st
    import requests
    import json
    
    # --- CONFIGURATION ---
    st.set_page_config(page_title="Hermes Nihongo", page_icon="🇯🇵", layout="centered")
    
    st.markdown("""
        <style>
        .stApp { max-width: 600px; margin: 0 auto; }
        .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
        </style>
        """, unsafe_allow_html=True)
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'mode' not in st.session_state:
        st.session_state.mode = "Simulation"
    
    with st.sidebar:
        st.title("Sensei Settings")
        st.session_state.mode = st.selectbox("Training Mode", ["Simulation", "Correction", "Daily Challenge"])
        st.divider()
        st.info("🎙️ Tip: Use the iOS keyboard microphone for voice-to-text!")
    
    def get_local_ai_response(user_input, mode):
        try:
            base_url = st.secrets["LOCAL_AI_URL"]
        except KeyError:
            return "⚠️ Error: LOCAL_AI_URL not found in Streamlit Secrets."
    
        mode_prompts = {
            "Simulation": "You are a friendly Japanese conversation partner. Use format: 1. Japanese, 2. Romaji, 3. English. Ask a follow-up question.",
            "Correction": "You are a professional Japanese linguist. Use format: ✅ Corrected, 📖 Romaji, 🌍 English, 💡 Explanation, ✨ Natural Alternative.",
            "Daily Challenge": "You are a Japanese vocabulary coach. Give a daily word challenge and provide feedback with a gold star (⭐) if correct."
        }
        system_prompt = mode_prompts.get(mode, "You are a helpful Japanese teacher.")
        
        # --- THE FIX: Trying multiple common oMLX endpoints ---
        endpoints = ["/v1/chat/completions", "/chat/completions", "/generate"]
        
        for endpoint in endpoints:
            try:
                # Payload structure compatible with most local servers
                payload = {
                    "model": "gemma-4-31b",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    "temperature": 0.7
                }
                
                response = requests.post(f"{base_url}{endpoint}", json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    # Handle both OpenAI-style and simple lapped responses
                    if 'choices' in result:
                        return result['choices'][0]['message']['content']
                    elif 'response' in result:
                        return result['response']
                    elif 'text' in result:
                        return result['text']
                    else:
                        return str(result)
            except Exception:
                continue
    
        return "❌ Sensei is offline or using an unknown API endpoint. Please check your oMLX server logs!"
    
    st.title("🇯🇵 Hermes Nihongo")
    st.caption("Powered by Gemma 4 31B on M5 Pro")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Type or speak in Japanese..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Sensei is thinking..."):
                response = get_local_ai_response(prompt, st.session_state.mode)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
