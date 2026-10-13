FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

# Copy the dependency file first so this layer is cached until it changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Run as an unprivileged user.
RUN useradd --system --no-create-home appuser
USER appuser

EXPOSE 5000

# Bind to all interfaces so the container port can be published.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} app:app"]
