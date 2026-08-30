# Command line

Installing FastVK adds a `fastvk` command.

```console
$ fastvk --version
$ fastvk --help
```

## `fastvk new` — scaffold a project

```console
$ fastvk new mybot
Created mybot/
Next:
  cd mybot
  fastvk run mybot/main.py
```

Creates:

```
mybot/
  main.py          # a working echo + /start bot
  .env.example
  .gitignore
  README.md
```

Add `--package` to get an importable layout (`mybot/mybot/main.py` with an
`__init__.py`), runnable as `fastvk run mybot.main`.

## `fastvk run` — run a bot

```console
$ fastvk run mybot/main.py        # path to a file
$ fastvk run mybot.main           # dotted module
$ fastvk run app:bot              # explicit FastVK attribute
```

Without `:attr` the command imports the module and picks the first `FastVK`
instance it finds.

### Webhook mode

```console
$ fastvk run app:bot --webhook 0.0.0.0:8080 --confirmation abc123 --path /vk
```
