# Командная строка

Установка FastVK добавляет команду `fastvk`.

```console
$ fastvk --version
$ fastvk --help
```

## `fastvk new` — создать проект

```console
$ fastvk new mybot
Created mybot/
Next:
  cd mybot
  fastvk run mybot/main.py
```

Создаёт:

```
mybot/
  main.py          # рабочий бот: эхо + /start
  .env.example
  .gitignore
  README.md
```

Добавь `--package`, чтобы получить импортируемую раскладку
(`mybot/mybot/main.py` с `__init__.py`), запускаемую как `fastvk run mybot.main`.

## `fastvk run` — запустить бота

```console
$ fastvk run mybot/main.py        # путь к файлу
$ fastvk run mybot.main           # модуль через точку
$ fastvk run app:bot              # явный атрибут FastVK
```

Без `:attr` команда импортирует модуль и берёт первый найденный экземпляр
`FastVK`.

### Режим webhook

```console
$ fastvk run app:bot --webhook 0.0.0.0:8080 --confirmation abc123 --path /vk
```
