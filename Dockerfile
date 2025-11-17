# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Create a startup script to run DB init ONCE, then start Gunicorn
RUN echo '#!/bin/bash\n\
# Initialize DB (This runs in a single process)\n\
python -c "from app import app, db; app.app_context().push(); db.create_all()"\n\
\n\
# Start Gunicorn\n\
exec gunicorn -c gunicorn_config.py app:app\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 5000

# Use the new entrypoint script
CMD ["/app/entrypoint.sh"]