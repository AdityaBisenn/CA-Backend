# app/ingestion/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.ingestion.service import process_file

router = APIRouter(tags=["Ingestion"])

@router.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    try:
        result = await process_file(file)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))