"""
Streamlit Web Interface for PDF Translator
A user-friendly web app for translating PDFs between English and Spanish.
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
from translator import PDFTranslator

# Page configuration
st.set_page_config(
    page_title="PDF Translator",
    page_icon="📄",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        padding: 1rem 0;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📄 PDF Translator</h1>', unsafe_allow_html=True)
st.markdown(
    '<p style="text-align: center; color: #666;">Translate PDF documents between English and Spanish using AI</p>',
    unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    This tool uses OpenAI's GPT-4o-mini to translate PDF documents.

    **Features:**
    - English ↔ Spanish translation
    - Preserves document structure
    - Handles large documents
    - Fast and accurate
    """)

    st.header("⚙️ Settings")
    show_cost = st.checkbox("Show estimated cost", value=False)

    st.markdown("---")
    st.caption("Built with Python, OpenAI API, and Streamlit")

# Main content
col1, col2 = st.columns(2)

with col1:
    source_lang = st.selectbox(
        "From:",
        ["English", "Spanish"],
        key="source"
    )

with col2:
    target_lang = st.selectbox(
        "To:",
        ["Spanish", "English"],
        key="target"
    )

# Validation
if source_lang == target_lang:
    st.error("⚠️ Please select different source and target languages!")
    st.stop()

# File upload
uploaded_file = st.file_uploader(
    "Upload PDF to translate",
    type=['pdf'],
    help="Maximum file size: 200MB"
)

if uploaded_file:
    # Show file info
    file_size = uploaded_file.size / (1024 * 1024)  # Convert to MB
    st.info(f"📎 **{uploaded_file.name}** ({file_size:.2f} MB)")

    # Estimate cost
    if show_cost:
        # Rough estimation: ~$0.01 per MB
        estimated_cost = file_size * 0.01
        st.caption(f"💰 Estimated cost: ${estimated_cost:.3f}")

    # Translate button
    if st.button("🚀 Translate", type="primary", use_container_width=True):
        try:
            # Check for API key
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                st.error("❌ OpenAI API key not found! Please set OPENAI_API_KEY environment variable.")
                st.stop()

            # Create temporary files
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
                tmp_input.write(uploaded_file.read())
                input_path = tmp_input.name

            output_path = tempfile.mktemp(suffix='.pdf')

            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Initialize translator
            status_text.text("Initializing translator...")
            progress_bar.progress(10)
            translator = PDFTranslator()

            # Extract text
            status_text.text("📄 Extracting text from PDF...")
            progress_bar.progress(25)
            text = translator.extract_text(input_path)

            # Show extraction info
            char_count = len(text)
            status_text.text(f"✓ Extracted {char_count:,} characters")
            progress_bar.progress(40)

            # Translate
            status_text.text(f"🌐 Translating to {target_lang}...")
            progress_bar.progress(50)
            translated_text = translator.translate_text(text, target_lang)
            progress_bar.progress(85)

            # Create PDF
            status_text.text("📝 Creating translated PDF...")
            translator.create_pdf(translated_text, output_path)
            progress_bar.progress(100)

            status_text.text("✅ Translation complete!")

            # Success message
            st.success("🎉 Translation completed successfully!")

            # Download button
            with open(output_path, 'rb') as f:
                pdf_bytes = f.read()

            original_name = Path(uploaded_file.name).stem
            download_name = f"{original_name}_{target_lang.lower()}.pdf"

            st.download_button(
                label="📥 Download Translated PDF",
                data=pdf_bytes,
                file_name=download_name,
                mime="application/pdf",
                use_container_width=True
            )

            # Show preview
            with st.expander("📖 Preview Translation"):
                preview_length = min(500, len(translated_text))
                st.text_area(
                    "First 500 characters:",
                    translated_text[:preview_length] + "...",
                    height=200
                )

            # Cleanup
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except:
                pass

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

else:
    # Instructions when no file uploaded
    st.markdown("""
    <div class="info-box">
        <h3>🚀 How to use:</h3>
        <ol>
            <li>Select source and target languages</li>
            <li>Upload your PDF file</li>
            <li>Click "Translate"</li>
            <li>Download the translated PDF</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <h3>✨ Features:</h3>
        <ul>
            <li>🔄 Bidirectional translation (English ↔ Spanish)</li>
            <li>📊 Handles multi-page documents</li>
            <li>🎯 Preserves document structure</li>
            <li>⚡ Fast processing with GPT-4o-mini</li>
            <li>💰 Cost-effective (~$0.01-0.05 per document)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("⚠️ Note: Translation quality depends on document complexity. API costs apply.")