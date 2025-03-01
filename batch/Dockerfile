FROM python:3.11.4

WORKDIR /app

COPY requirements_batch.txt .
RUN pip install -r requirements_batch.txt

COPY . .

ENV REDISHOST=redis
ENV POSTGRES_HOST=db
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=rag_saas
ENV POSTGRES_PORT=5432

CMD ["celery", "-A", "batch_worker.celery_app", "worker", "--loglevel=info"]