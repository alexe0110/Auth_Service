

### Первый запуск

1. Запустить БД `docker compose up postgres -d` 
2. Миграции джанги `make migrate` или `python manage.py migrate`
4. Запустить остальные сервисы `docker compose up -d`
5. Для доступа к админке и методам сервиса авторизации, создать суперпользовател
`auth add-superuser -e name@ya.ru -p <password> --first_name Alexey --gender male --birthdate 01.10.1996`
