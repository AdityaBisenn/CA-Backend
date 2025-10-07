#!/bin/bash
# Activate virtual environment and run the server
source .venv/bin/activate
python -m uvicorn app.main:app --reload --port 8001 --host 0.0.0.0