FROM python:3.12-slim

WORKDIR /app

COPY services/task-service/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/task-service/main.py main.py
COPY shared /app/shared

EXPOSE 8004

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
