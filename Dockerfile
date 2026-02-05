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

EXPOSE 8000

# Run migrations then start gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 --workers 3 talent_solutions.wsgi:application"]
