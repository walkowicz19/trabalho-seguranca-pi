FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY autonomous_agent.py .
COPY crewai_attacker.py .

CMD ["python", "autonomous_agent.py", "--target", "http://llamafirewall:8080"]
