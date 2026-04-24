# Web-Shop

Django, Docker application

## Як отримати доступ до адмін-панелі

1. Відкрийте Docker. Після запуску та збору контейнерів (`docker-compose up --build`), відкрийте новий термінал.
2. Якщо ви запускаєте проект вперше, необхідно створити таблиці в БД (`docker-compose exec web python manage.py migrate`)
3. Створіть власного суперкористувача командою:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```
4. Дотримуйтесь інструкцій у терміналі (вкажіть логін, пошту та пароль).
5. Перейдіть за адресою http://localhost:8000/admin/ та увійдіть під своїми даними.
