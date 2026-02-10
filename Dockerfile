FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY daily_ops_agent /app/daily_ops_agent
COPY pyproject.toml /app/pyproject.toml

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "daily_ops_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
