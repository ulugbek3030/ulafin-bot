FROM python:3.11-slim AS base

# System deps for Pillow, matplotlib, tesseract
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY pyproject.toml .
RUN pip install --no-cache-dir . && pip cache purge

# Copy app code
COPY . .

# Non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "-m", "app.main"]
