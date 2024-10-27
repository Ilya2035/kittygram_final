FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .
RUN mkdir -p /app/collected_static /app/media \
    && python manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8081", "kittygram_backend.wsgi"]
