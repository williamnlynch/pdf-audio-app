import streamlit as st
import asyncio
import edge_tts
import PyPDF2
import os
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="PDF to Natural MP3", page_icon="🎙️")

st.title("📄 PDF to Natural Voice MP3")
st.write("Upload a PDF and I'll convert it to a high-quality neural voice without the 'robotic' pauses.")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("Voice Settings")
voice_map = {
    "Male (US)": "en-US-GuyNeural",
    "Female (US)": "en-US-AriaNeural"
}

selection = st.sidebar.selectbox("Choose a Voice Persona", list(voice_map.keys()))
voice_id = voice_map[selection]

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload your PDF here", type="pdf")

if uploaded_file is not None:
    # 1. EXTRACT AND CLEAN TEXT
    with st.spinner("Processing PDF and smoothing line breaks..."):
        reader = PyPDF2.PdfReader(uploaded_file)
        raw_lines = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                # Split by lines to handle each line individually
                raw_lines.extend(text.splitlines())
        
        # Join lines with a single space to remove 'hard returns' from the PDF
        clean_text = " ".join(raw_lines)
        
        # REPAIR HYPHENATION: Fix words split across lines (e.g., "en- vironment")
        clean_text = clean_text.replace("- ", "")
        
        # REMOVE EXCESS WHITESPACE: Fix double or triple spaces
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    if clean_text:
        st.success(f"Successfully processed {len(clean_text)} characters!")
        
        # Preview the text so you can see it's smooth
        with st.expander("Preview Cleaned Text"):
            st.write(clean_text[:1000] + "..." if len(clean_text) > 1000 else clean_text)

        # 2. GENERATE AUDIO
        if st.button("Generate MP3 Audio"):
            output_file = "speech_output.mp3"
            
            async def generate_speech():
                # We use edge_tts to create a high-quality stream
                communicate = edge_tts.Communicate(clean_text, voice_id)
                await communicate.save(output_file)

            with st.spinner("Synthesizing neural voice... this may take a moment for long files."):
                try:
                    asyncio.run(generate_speech())
                    
                    # 3. DISPLAY AND DOWNLOAD
                    with open(output_file, "rb") as f:
                        audio_data = f.read()
                        st.audio(audio_data, format="audio/mp3")
                        st.download_button(
                            label="📥 Download MP3 File",
                            data=audio_data,
                            file_name="converted_audio.mp3",
                            mime="audio/mp3"
                        )
                except Exception as e:
                    st.error(f"An error occurred during synthesis: {e}")
    else:
        st.error("We couldn't find any readable text in that PDF. It might be a scanned image.")

# --- FOOTER ---
st.divider()
st.caption("Powered by Microsoft Edge Neural TTS and Streamlit.")

