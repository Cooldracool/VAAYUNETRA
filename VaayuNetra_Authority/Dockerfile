# syntax=docker/dockerfile:1

FROM python:3.13-slim

# Keep Python snappy and logs unbuffered in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the full app (backend + frontend assets + uploads dir)
COPY backend ./backend
COPY css ./css
COPY js ./js
COPY index.html index.hmtl ./
COPY uploads ./uploads

EXPOSE 8000

# Healthcheck against the BFF health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=4)" || exit 1

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
