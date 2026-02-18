import os, sys, io, tempfile, subprocess, textwrap
import streamlit as st

SCRIPT = "interactive_glossary_builder.py"

def ensure_spacy():
    """Ensure spaCy small English model is present (first-run only on some hosts)."""
    try:
        import spacy
        spacy.load("en_core_web_sm")
    except Exception:
        try:
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
        except Exception as e:
            st.error("Could not download spaCy model automatically. Please install 'en_core_web_sm'.")
            st.stop()

st.set_page_config(page_title="Interactive Glossary Builder", layout="centered")
st.title("Interactive Glossary Builder")
st.caption("Upload a .docx or .txt, give the document a title, and download an interactive glossary (.docx).")

with st.expander("Options", expanded=True):
    title = st.text_input("Document title", value="My Lesson")
    extra = st.text_input("Always-include terms (comma-separated, optional)", value="")
    col1, col2 = st.columns(2)
    with col1:
        uploaded = st.file_uploader("Upload .docx or .txt", type=["docx", "txt"])
    with col2:
        st.write(" ")

st.divider()

build = st.button("Build Glossary", type="primary", disabled=uploaded is None or not title.strip())

# Run-time guard: make sure the builder exists
if not os.path.exists(SCRIPT):
    st.error(f"Cannot find '{SCRIPT}' next to app.py. Please upload it.")
    st.stop()

if build and uploaded:
    ensure_spacy()
    with tempfile.TemporaryDirectory() as td:
        in_path = os.path.join(td, uploaded.name)
        out_name = os.path.splitext(uploaded.name)[0] + "_glossary.docx"
        out_path = os.path.join(td, out_name)

        # Save the uploaded file
        with open(in_path, "wb") as f:
            f.write(uploaded.read())

        # Build command
        cmd = [sys.executable, SCRIPT, "--input", in_path, "--output", out_path, "--title", title]
        if extra.strip():
            cmd += ["--always-include", extra]

        with st.spinner("Building glossary... this can take ~15–45 seconds on first run."):
            proc = subprocess.run(cmd, capture_output=True, text=True)

        # Show diagnostics if something failed
        if proc.returncode != 0 or not os.path.exists(out_path):
            st.error("Something went wrong while generating the glossary.")
            with st.expander("Show error log"):
                st.code(proc.stdout + "\n" + proc.stderr)
        else:
            with open(out_path, "rb") as f:
                st.download_button("Download Glossary (.docx)", f, file_name=out_name, type="primary")
            st.success("Done! Your interactive glossary is ready.")
