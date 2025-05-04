FROM python:3.11.4

WORKDIR /flask_app

# Copy requirements.txt to the container
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the application code to the container
COPY . .

# Copy the Google Cloud service account key to the container
COPY key.json /flask_app/key.json

# Set environment variable for Google Cloud credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=/flask_app/key.json

# Expose the port
EXPOSE 8080

# Use gevent or sync worker class for Gunicorn
CMD ["gunicorn", "-k", "eventlet", "-w", "1", "--timeout", "120", "-b", "0.0.0.0:8080", "app.wsgi:app"]