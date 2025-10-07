# app/ingestion/file_parser.py
import pandas as pd
import chardet
from PyPDF2 import PdfReader
import io

class FileTypeUnsupportedError(Exception):
    pass

def parse_file(file_obj: io.BytesIO, filename: str) -> pd.DataFrame:
    ext = filename.split(".")[-1].lower()

    if ext in ["csv"]:
        raw = file_obj.read()
        encoding = chardet.detect(raw)["encoding"] or "utf-8"
        file_obj.seek(0)
        df = pd.read_csv(file_obj, encoding=encoding, on_bad_lines="skip")
    elif ext in ["xlsx", "xls"]:
        df = pd.read_excel(file_obj)
    elif ext in ["xml"]:
        df = pd.read_xml(file_obj)
    elif ext in ["pdf"]:
        reader = PdfReader(file_obj)
        text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        df = pd.DataFrame({"text": text.splitlines()})
    else:
        raise FileTypeUnsupportedError(f"Unsupported file type: {ext}")

    df = df.dropna(how="all").reset_index(drop=True)
    return df