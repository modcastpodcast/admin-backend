FROM python:latest

ENV FLASK_APP=app.py

RUN pip install -r requirements.txt

CMD ["sh", "-c", "flask db upgrade && gunicorn --workers 2 --access-logfile - app:app"]