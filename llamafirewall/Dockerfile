FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rules_and_scanners.py .
COPY proxy_firewall.py .

RUN mkdir -p /var/log/llamafirewall

ENV LLAMAFIREWALL_LOG_DIR=/var/log/llamafirewall
ENV TARGET_HOST=http://target:8000

EXPOSE 8080

CMD ["uvicorn", "proxy_firewall:app", "--host", "0.0.0.0", "--port", "8080"]
