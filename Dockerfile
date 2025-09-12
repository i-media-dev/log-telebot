FROM python:3.13-slim
WORKDIR /app
RUN pip install gunicorn
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "logger.main:app"]