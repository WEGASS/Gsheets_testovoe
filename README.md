# Тестовое задание для компании "Каналсервис"
Развертывание приложения осуществляется в следующей последовательности:
1. Клонировать репозиторий локально;
2. В файле docker-compose.yml изменить параметры BOT_TOKEN и CHAT_ID на собственный токен телеграм-бота и id чата соответственно;
3. При необходимости поменять параметр SCHEDULE_TIME на нужное кол-во минут (параметр отвечает за время обновления базы данных из GoogleSheets)
4. Открыть терминал в папке проекта и собрать приложение командой `docker-compose up`;
5. Дождаться конца сборки контейнеров (запуск может быть долгим, из-за запуска posgtres), запуска django и скрипта (в консоли после добавления всех записей в БД будет надпись вида "End syncing with GoogleSheets in YYYY-mm-dd HH:MM:DD"), а затем перейти на адрес localhost:8000


![image](https://user-images.githubusercontent.com/37272928/189197695-70a313f1-379d-443f-a18b-b65bccd06300.png)

Сам скрипт лежит в папке ./gsheets/script/

Ссылка на Google таблицу (доступ открыт):
https://docs.google.com/spreadsheets/d/1p3YOopCH996XAShh8Op7M6lb184rE7D5xjHJiYzmLNs/edit?usp=sharing


**Запуск приложения без Docker:**
1. Клонировать репозиторий
2. Установить необходимые библиотеки pip install -r requirements.txt
3. Изменить настройки БД в settings.py
4. Изменить настройки в ./gsheets/script/script.py (изменить в переменных данные url таблицы, название листа, токен бота, чат id и schedule time, везде где есть os.getenv)
5.  Применить миграции командой python manage.py migrate
6. Запустить скрипт python manage.py start_script
7. Открыть еще один терминал и запустить приложение python manage.py runserver
8. Перейти на localhost:8000
