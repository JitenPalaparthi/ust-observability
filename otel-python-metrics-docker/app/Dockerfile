FROM python:3.12-slim

WORKDIR /app

# Faster, cleaner container logs
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
