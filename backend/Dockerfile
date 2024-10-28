FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/static /app/media

CMD sh -c "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8081 kittygram_backend.wsgi"
