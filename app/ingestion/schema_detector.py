# app/ingestion/schema_detector.py
import re
import pandas as pd

def detect_schema(df: pd.DataFrame) -> dict:
    schema = {}
    for col in df.columns:
        col_lower = col.lower()

        if re.search(r"date", col_lower):
            schema[col] = "datetime"
        elif re.search(r"amount|amt|value|rs", col_lower):
            schema[col] = "float"
        elif re.search(r"dr|cr|debit|credit", col_lower):
            schema[col] = "category"
        else:
            schema[col] = "string"
    return schema