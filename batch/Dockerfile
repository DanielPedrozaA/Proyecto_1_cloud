FROM python:3.11.4

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Run the Pub/Sub worker
CMD ["python", "-u", "BatchWorker.py"]