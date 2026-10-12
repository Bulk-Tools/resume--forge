FROM python:3.11-slim

WORKDIR /app

# Engine (renderer + sample data) and the API code.
COPY engine/ /app/engine/
COPY api/requirements.txt /app/
COPY api/main.py /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
