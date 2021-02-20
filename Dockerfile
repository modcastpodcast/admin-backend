FROM python:alpine

RUN apk add postgresql-libs git
RUN apk add --virtual .build-deps gcc musl-dev postgresql-dev

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

RUN apk --purge del .build-deps

CMD ["sh", "-c", "alembic upgrade head && uvicorn --port 80 --host 0.0.0.0 --workers 4 admin:app"]
