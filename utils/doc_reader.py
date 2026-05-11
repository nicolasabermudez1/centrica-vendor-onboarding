"""
Best-effort text extraction from an uploaded file.
The extracted text is sent to Gemini for field extraction; the file itself
is NEVER persisted to disk.
"""

import io


def extract_text(uploaded_file) -> str:
    """Returns up to ~8000 chars of plain text from the uploaded file.
    Handles txt/md/csv/pdf/docx. For unknown types, returns a metadata stub."""
    name = uploaded_file.name.lower()
    try:
        data = uploaded_file.getvalue()
    except Exception:
        data = uploaded_file.read()

    try:
        if name.endswith((".txt", ".md", ".csv", ".json", ".log")):
            return data.decode("utf-8", errors="ignore")[:8000]

        if name.endswith(".pdf"):
            try:
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(data))
                text = ""
                for page in reader.pages[:10]:
                    text += (page.extract_text() or "") + "\n"
                return text.strip()[:8000] or f"[PDF '{uploaded_file.name}' — no extractable text]"
            except Exception as e:
                return f"[PDF '{uploaded_file.name}' — text extraction failed: {e}]"

        if name.endswith(".docx"):
            try:
                from docx import Document
                doc = Document(io.BytesIO(data))
                text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
                return text[:8000] or f"[DOCX '{uploaded_file.name}' — no extractable text]"
            except Exception as e:
                return f"[DOCX '{uploaded_file.name}' — text extraction failed: {e}]"

        # Images, xlsx, etc. — pass filename + size; Gemini will hallucinate plausibly
        size_kb = len(data) // 1024
        return f"[File: {uploaded_file.name} · type: {uploaded_file.type or 'unknown'} · size: {size_kb}KB · binary content, fields inferred from filename and context]"
    except Exception as e:
        return f"[Could not read '{uploaded_file.name}': {e}]"
