import streamlit as st
import asyncio
import edge_tts
import PyPDF2
import os

# App Title
st.title("📄 PDF to Natural Voice MP3")
st.write("Upload a PDF and I'll convert it to a high-quality neural voice.")

# Sidebar for Voice Selection
voice_option = st.sidebar.selectbox(
    "Choose a Voice",
    ("en-US-GuyNeural (Male)", "en-US-AriaNeural (Female)", "en-GB-SoniaNeural (UK Female)")
)
voice_id = voice_option.split(" ")[0]

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # 1. Extract Text
    with st.spinner("Reading PDF..."):
        reader = PyPDF2.PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + " "
    
    if full_text.strip():
        st.success("Text extracted successfully!")
        
        # 2. Convert to Audio
        if st.button("Generate MP3"):
            output_file = "speech.mp3"
            
            async def make_audio():
                communicate = edge_tts.Communicate(full_text, voice_id)
                await communicate.save(output_file)

            with st.spinner("Synthesizing natural voice..."):
                asyncio.run(make_audio())
            
            # 3. Download Button
            with open(output_file, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
                st.download_button(
                    label="Download MP3",
                    data=f,
                    file_name="converted_audio.mp3",
                    mime="audio/mp3"
                )
    else:
        st.error("Could not find any text in that PDF.")