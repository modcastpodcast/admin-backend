FROM python:latest

WORKDIR /app
COPY . .

ENV FLASK_APP=app.py

RUN pip install -r requirements.txt

CMD ["sh", "-c", "flask db upgrade && gunicorn --bind 0.0.0.0:80 --access-logfile - app:app"]