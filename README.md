# Пример бота
Примеро бота в телеграме [тут](https://t.me/QuizHoffBot)

# Установка
Для запуска достаточно создать файл .env, в котором описаны переменные окружения.

Файл .env:
```
TELEGRAM_TOKEN=<токен телеграм бота>
VK_API_TOKEN=<токен сообщества vk>
TELEGRAM_TOKEN_LOGS=<бот для отправки логов>
TG_CHAT_ID=<идентификатор пользователя телеграма для получения логов>
REDIS_HOST=<адрес Redis>
REDIS_PASS=<пароль к Redis>
REDIS_PORT=<порт Redis>
QUESTIONS_DIR=<директория с файлами вопросов>
QUESTIONS_FILE=<опционально, если хочется задать конкретный файл>
```

## Токен telegram-бота
Для создания телеграм бота напишите боту [BotFather](https://t.me/BotFather), там вы создадите бота, и вам будет выдан токен бота.

## Токен бота сообщества вконтакте
Токен можно сгенерировать в меню управления сообщества на вкладке API

## Запуск
После заполнения файла с переменными можно запускать ботов с помощью команд
```
python3 telegram_bot.py
python3 vk_bot.py
```