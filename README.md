# Daily nasa bot
## Бот демонстрирующий работу API NASA
### Что можно увидеть в этом коде
1. Асинхронные запросы к API NASA
2. Базовые возможности API Telegram
3. Сохранение данных бота с использованием Picklepersistency
4. Выполнение регулярных задач через APSScheduler
5. Упаковку в Docker контейнер
### Использование
1. Установите docker
2. Создайте файл .env и пропиште в нем ключи окружения со своими токенами
```
token=your-own-token
superuser=your-chat-id
nasakey=DEMO_KEY
```
3. Выполните ```docker compose up```
