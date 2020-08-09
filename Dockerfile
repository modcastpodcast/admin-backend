FROM python:latest

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["sh", "-c", "alembic upgrade head && uvicorn --port 80 --host 0.0.0.0 --workers 4 admin:app"]