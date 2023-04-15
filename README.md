# cm-bootcamp-2023

## Деплой сервиса

Для каждого сервисы должна быть отдельный app во fly.io - для сервиса это `art-expert-collmach`, для бота - `art-expert-collmach-bot`.

Создается апа автоматически, но можно руками через `flyctl apps create <your-app-name>`.

По туториалу не получился деплой, поэтому предложили через docker и flyctl.

Команды `flyctl` выполняем из той директории, где находится `fly.toml`. Если это сервис, то заходим в `fastapi-deployement`. Если это бот, то заходим в `bot`.

```
cd fastapi-deployement
poetry run mlem build docker_dir -m nasnetmobile_2_dense_layers --target dockerdir --server fastapi --server.request_serializer pil_numpy --file_conf server=server.mlem
cd dockerdir
flyctl launch --auto-confirm --region ams --no-deploy --name art-expert-collmach
flyctl deploy # подождать пока все развернется
flyctl scale memory 2048 # после того как запустилось выполнить эту команду (не всегда нужно, но иногда без нее не работает)
```

Здесь в первой строке, когда билдим образ нужную модель указываем через `-m`.

## Деплой бота

Создаем новую app. Меняем название на новую апу в `fly.toml`, из директории `bot` запускаем `flyctl deploy`.

# art-expert-telegram-bot

Deploy something like https://t.me/AIArtExpertBot

- `bot/` folder: telegram bot (run locally or deploy to fly.io)
- `fastapi-deployment/` folder: fastapi and streamlit app to deploy to flyio

Read more about tools used:
- A simple solution for monitoring ML systems (FastAPI + Prometheus + Grafana) https://www.jeremyjordan.me/ml-monitoring/
- Python Telegram Bot https://python-telegram-bot.org
- 