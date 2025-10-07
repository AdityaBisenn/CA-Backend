# app/ingestion/service.py
from io import BytesIO
import pandas as pd
from app.ingestion.file_parser import parse_file
from app.ingestion.schema_detector import detect_schema
from app.core.logger import log_error

async def process_file(file):
    file_bytes = await file.read()
    file_path = file.filename

    try:
        df = parse_file(BytesIO(file_bytes), file_path)
        schema = detect_schema(df)
        response = {
            "file_name": file_path,
            "records_ingested": len(df),
            "schema": schema,
            "errors": []
        }
        return response

    except Exception as e:
        log_error("IngestionPipeline", type(e).__name__, str(e))
        raise e