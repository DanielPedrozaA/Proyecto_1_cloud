
FROM python:3.11.4

WORKDIR /flask_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "--worker-class", "eventlet", "-b", "0.0.0.0:8080", "app.wsgi:app"]

