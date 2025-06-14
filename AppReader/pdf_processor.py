import PyPDF2
import re
from typing import List, Tuple, Optional

class PDFProcessor:
    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """Extracts text from a PDF file with error handling."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text() or ''  #Handle None returns
                return text
        except Exception as e:
            raise RuntimeError(f"Failed to process PDF: {str(e)}")

    @staticmethod
    def clean_text(text: str) -> str:
        """Cleans extracted PDF text."""
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def smart_chunking(text: str, chunk_size: int = 1000) -> List[str]:
        """Splits text into coherent chunks preserving context."""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para)
            if current_size + para_size > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            current_chunk.append(para)
            current_size += para_size

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks