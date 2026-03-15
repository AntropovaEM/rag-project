import os
from pypdf import PdfReader
from docx import Document


def load_document(file_path):
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = "\n\n".join(page.extract_text() for page in reader.pages)
        return {"content": text, "source": os.path.basename(file_path)}
    
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        text = "\n\n".join(para.text for para in doc.paragraphs)
        return {"content": text, "source": os.path.basename(file_path)}
    
    else:
        raise ValueError("Поддерживаются только PDF и DOCX файлы")

def split_text(text, chunk_size=1000, overlap=200):
    chunks = []
    for start in range(0, len(text), chunk_size - overlap):
        chunk = text[start:start + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks