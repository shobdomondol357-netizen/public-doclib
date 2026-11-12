import io, os, re, zipfile
from typing import Tuple

SUPPORTED = {
    "pdf","doc","docx","txt","rtf","odt","epub",
    "xls","xlsx","csv","ods",
    "ppt","pptx","odp",
    "md","html","htm","json","xml","jpg","jpeg","png","webp","gif",
}

def ext_of(name: str) -> str:
    return (name.rsplit(".",1)[-1].lower() if "." in name else "")

def extract_text(filename: str, data: bytes, mime: str = "") -> Tuple[str, str]:
    """Return (text, status). status in extracted/failed/none/unsupported."""
    ext = ext_of(filename)
    if ext not in SUPPORTED:
        return "", "unsupported"
    try:
        if ext == "pdf":
            return extract_pdf(data), "extracted"
        if ext in ("docx",):
            return extract_docx(data), "extracted"
        if ext in ("doc",):
            return extract_doc(data), "extracted"
        if ext in ("txt","md","csv","json","xml","html","htm","rtf"):
            return decode_text(data), "extracted"
        if ext in ("xlsx","xls","ods"):
            return extract_spreadsheet(filename, data), "extracted"
        if ext in ("pptx","ppt","odp"):
            return extract_presentation(filename, data), "extracted"
        if ext in ("odt",):
            return extract_odt(data), "extracted"
        if ext in ("epub",):
            return extract_epub(data), "extracted"
        if ext in ("jpg","jpeg","png","webp","gif"):
            return "", "none"  # image; no text unless OCR
    except Exception as e:
        return "", "failed:" + str(e)[:300]
    return "", "none"

def decode_text(data: bytes) -> str:
    for enc in ("utf-8","utf-16","latin-1"):
        try:
            return data.decode(enc)
        except Exception:
            continue
    return data.decode("utf-8", errors="replace")

def extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader
    r = PdfReader(io.BytesIO(data))
    out = []
    for p in r.pages:
        try:
            out.append(p.extract_text() or "")
        except Exception:
            out.append("")
    text = "\n".join(out)
    # OCR fallback if very little text
    if len(text.strip()) < 50:
        text = try_ocr_pdf(data)
    return text

def try_ocr_pdf(data: bytes) -> str:
    try:
        import pytesseract
        from pdf2image import convert_from_bytes
        imgs = convert_from_bytes(data, dpi=200)
        out = []
        for im in imgs:
            out.append(pytesseract.image_to_string(im))
        return "\n".join(out)
    except Exception:
        return ""

def extract_docx(data: bytes) -> str:
    import docx
    d = docx.Document(io.BytesIO(data))
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            parts.append(" | ".join(c.text for c in row.cells))
    return "\n".join(parts)

def extract_doc(data: bytes) -> str:
    # best-effort: try antiword? not available; return placeholder
    try:
        import subprocess, tempfile
        with tempfile.NamedTemporaryFile(suffix=".doc", delete=False) as f:
            f.write(data); path = f.name
        try:
            r = subprocess.run(["antiword", path], capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                return r.stdout
        except FileNotFoundError:
            pass
        finally:
            os.unlink(path)
    except Exception:
        pass
    return "[DOC binary format: text extraction not available on server]"

def extract_spreadsheet(filename, data) -> str:
    ext = ext_of(filename)
    if ext == "csv":
        return decode_text(data)
    if ext in ("xlsx","xls"):
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
        out = []
        for ws in wb.worksheets:
            out.append(f"## Sheet: {ws.title}")
            for row in ws.iter_rows(values_only=True):
                out.append(" | ".join("" if c is None else str(c) for c in row))
        return "\n".join(out)
    if ext == "ods":
        # use pandas if odfpy available
        try:
            import pandas as pd
            df = pd.read_excel(io.BytesIO(data), engine="odf")
            return df.to_string()
        except Exception:
            return "[ODS extraction unavailable]"
    return ""

def extract_presentation(filename, data) -> str:
    ext = ext_of(filename)
    if ext == "pptx":
        from pptx import Presentation
        prs = Presentation(io.BytesIO(data))
        out = []
        for i, slide in enumerate(prs.slides, 1):
            out.append(f"## Slide {i}")
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    out.append(shape.text)
        return "\n".join(out)
    return "[Presentation text extraction not available for this format]"

def extract_odt(data) -> str:
    try:
        import zipfile
        z = zipfile.ZipFile(io.BytesIO(data))
        xml = z.read("content.xml").decode("utf-8", errors="replace")
        # strip tags
        text = re.sub(r"<[^>]+>", " ", xml)
        return re.sub(r"\s+", " ", text)
    except Exception:
        return ""

def extract_epub(data) -> str:
    try:
        import ebooklib
        from ebooklib import epub
        book = epub.read_epub(io.BytesIO(data))
        out = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(item.get_content(), "html.parser")
                out.append(soup.get_text(" ", strip=True))
        return "\n".join(out)
    except Exception as e:
        return f"[EPUB extraction failed: {e}]"
