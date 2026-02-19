FROM python:3.12-slim

WORKDIR /app

# Install system deps for Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Persistent dirs — db_data and media are volume-mounted at runtime,
# but create them here so the image is runnable standalone too.
RUN mkdir -p db_data media

# Collect static files so whitenoise can serve them
RUN python manage.py collectstatic --noinput

# Entrypoint: validates volumes are mounted, then migrates + starts gunicorn
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

CMD ["/entrypoint.sh"]
