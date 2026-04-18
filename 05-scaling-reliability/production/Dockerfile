FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    uvicorn[standard]==0.30.0 \
    redis==5.0.1 \
    pydantic

# Copy app and utilities from production folder
COPY 05-scaling-reliability/production/app.py main.py
COPY 05-scaling-reliability/production/utils/ utils/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
