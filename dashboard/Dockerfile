FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY static ./static

EXPOSE 5000

ENV TARGET_HOST=http://target:8000
ENV LLAMA_HOST=http://llamafirewall:8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
