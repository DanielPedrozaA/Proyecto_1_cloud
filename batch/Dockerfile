
FROM python:3.11.4

WORKDIR /app    

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["celery", "-A", "BatchWorker.celery_app", "worker", "--loglevel=info", "--queues=allqueue"]
