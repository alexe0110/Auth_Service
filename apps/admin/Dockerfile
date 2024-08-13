FROM python:3.11

WORKDIR /opt/app

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE 'config.settings'


COPY requirements requirements

RUN  pip install --upgrade pip \
     && pip install -r requirements

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["./run_gunicorn.sh"]