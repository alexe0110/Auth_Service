FROM python:3.12

WORKDIR /opt/app

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE 'config.settings'


RUN apt update && pip install --upgrade pip
COPY pyproject.toml poetry.lock /opt/app/

RUN pip install --no-compile poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["./run_gunicorn.sh"]