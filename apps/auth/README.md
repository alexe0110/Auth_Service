

### Создать виртуальное окружение
    make init
    source .venv/bin/activate

> Описать энвы в `core/.env`

### Миграции
    ...

### Запуск 
    fastapi dev
или через gunicorn
    
    ./local_up.sh

### Создание суперпользователя
Для этого реализована cli команда `auth add-superuser`, 
которая создает пользователя со всеми имеющимися ролями<br>
_Пример использования:_

    auth add-superuser -e mymail@yandex.ru -p 123qwe --first_name Alexey --gender male --birthdate 01.10.1996

### Тесты
Поднять БД для тестов, она будет на порту 5434

    docker compose up auth-postgres-test auth-redis-test -d

Запустить pytest тесты любым удобным способом

    pytest ./tests -v

Чтобы оценить покрытие тестами 
    
    pytest --cov=. tests/

## Ссылка на репозиторий
https://github.com/NikFedoseev/Auth_sprint_2