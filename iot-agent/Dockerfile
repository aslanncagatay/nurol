FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt pika==1.3.2

COPY src/ ./src/
ENV PYTHONPATH=/app/src PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "-m", "iot_agent"]
CMD ["--consume"]
