import os
from pypdf import PdfReader
from fpdf import FPDF
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class PDFTranslator:
    """A class that translates PDF documents."""

    def __init__(self, api_key=None):
        """Initialize the PDFTranslator with an API key."""

        # Gets API key from parameter or environment variables
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')

        # Checks if there is an API key
        if not self.api_key:
            raise Exception('API key is not found. Set it in .env file.')

        # Creates OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"
        print("Translator Successfully Initialized.")

    def extract_text(self, pdf_path):
        """Extract text from PDF."""
        print(f"Extracting text from PDF: {pdf_path}")

        reader = PdfReader(pdf_path)

        text = ''

        for page_num, page in enumerate(reader.pages, 1):
            print(f" Reading page: {page_num}/{len(reader.pages)}")

            page_text = page.extract_text()

            text += page_text + "\n\n"

        return text.strip()

    def translate_text(self, text, target_language):
        """Translate text using OpenAI API."""
        print(f"🌐 Translating to {target_language}...")

        # Split text into chunks
        words = text.split()
        chunk_size = 15000  # characters instead of words
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)

        print(f"  ➤ Split into {len(chunks)} chunk(s)")

        # Translate each chunk WITH NUMBERING for order preservation
        translated_chunks = []
        for i, chunk in enumerate(chunks, 1):
            print(f"  ➤ Translating chunk {i}/{len(chunks)}")

            # Add chunk number to help preserve order
            prompt = f"Translate the following text to {target_language}. This is part {i} of {len(chunks)}. Maintain the original formatting and do NOT add any introductory text:\n\n{chunk}"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": f"You are a professional translator. Translate text accurately to {target_language}. Output ONLY the translation, no explanations or notes."
                     },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            translated_text = response.choices[0].message.content
            translated_chunks.append(translated_text)

            # Debug: Show preview of what was translated
            print(f"      Preview: {translated_text[:50]}...")

        # Combine chunks in order
        full_translation = '\n\n'.join(translated_chunks)
        print("✓ Translation complete!")

        return full_translation

    def create_pdf(self, text, output_path):
        """Create a PDF file with the translated text."""
        print(f"📄 Creating PDF: {output_path}")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", size=11)

        paragraphs = text.split('\n\n')

        lines_added = 0
        lines_skipped = 0

        for para in paragraphs:
            if not para.strip():
                continue

            try:
                # Clean problematic characters using Unicode escapes
                clean_para = (para
                              .replace('\u2018', "'")  # '
                              .replace('\u2019', "'")  # '
                              .replace('\u201c', '"')  # "
                              .replace('\u201d', '"')  # "
                              .replace('\u2014', '-')  # —
                              .replace('\u2026', '...'))  # …

                # Add paragraph
                pdf.multi_cell(0, 6, text=clean_para)
                pdf.ln(4)
                lines_added += 1

            except Exception as e:
                lines_skipped += 1
                print(f"  ⚠ Skipped paragraph: {str(e)}")
                continue

        pdf.output(output_path)

        print(f"✓ PDF created successfully!")
        print(f"  ➤ Paragraphs added: {lines_added}")
        if lines_skipped > 0:
            print(f"  ⚠ Paragraphs skipped: {lines_skipped}")

    def translate_pdf(self, input_path, output_path, target_language):
        """Main function: translate a complete PDF file."""
        print("=" * 60)
        print("PDF TRANSLATION STARTING")
        print("=" * 60)

        # Step 1: Extract text
        text = self.extract_text(input_path)
        print(f"\n✓ Extracted {len(text)} characters\n")

        # Check if we got any text
        if not text:
            raise ValueError("No text found in PDF!")

        # Step 2: Translate
        translated_text = self.translate_text(text, target_language)

        # Step 3: Create new PDF
        print()  # Add blank line
        self.create_pdf(translated_text, output_path)

        print("\n" + "=" * 60)
        print("TRANSLATION COMPLETE!")
        print("=" * 60)

        return translated_text


# if __name__ == "__main__":
#     translator = PDFTranslator()
#
#     # Extract text
#     text = translator.extract_text("test.pdf")
#     print(f"\n📝 First 100 chars of original:")
#     print(text[:100])
#     print(f"\n📝 Last 100 chars of original:")
#     print(text[-100:])
#
#     # Translate
#     translated = translator.translate_text(text, "Spanish")
#
#     # Verify order
#     print(f"\n🌐 First 100 chars of translation:")
#     print(translated[:100])
#     print(f"\n🌐 Last 100 chars of translation:")
#     print(translated[-100:])
#
#     # Create PDF
#     translator.create_pdf(translated, "test_spanish.pdf")

if __name__ == "__main__":
    # Create translator
    translator = PDFTranslator()

    # Translate a PDF file
    translator.translate_pdf(
        input_path="test.pdf",
        output_path="test_spanish.pdf",
        target_language="Spanish"
    )

    print("\n✓ Check your folder for 'test_spanish.pdf'!")