# Router

`Router` регистрирует хэндлеры и объединяет суб-роутеры. `Bot` / `FastVK` наследует его.

## Декораторы хэндлеров

### @router.message

```python
@router.message(*filters)
async def handler(message: Message, ...) -> None: ...
```

Регистрирует хэндлер для событий `message_new`.

### @router.callback

```python
@router.callback(*filters)
async def handler(callback: CallbackQuery, ...) -> None: ...
```

Регистрирует хэндлер для событий `message_event` (нажатие callback кнопки).

### @router.error

```python
@router.error()
async def handler(error: Exception, ...) -> None: ...
```

Регистрирует глобальный обработчик ошибок. Вызывается когда любой другой хэндлер выбрасывает исключение.

## Фильтры уровня роутера

```python
router = Router()
router.message.filter(IsAdmin())
router.callback.filter(IsAdmin())
```

Все хэндлеры этого роутера получат события только если `IsAdmin()` вернёт `True`.

## include_router

```python
router.include_router(other_router: Router) -> None
```

Объединить все хэндлеры из `other_router` в этот роутер (хэндлеры разрешаются в порядке регистрации).

## Dependency injection

Параметры хэндлера разрешаются по типу:

```python
async def handler(
    message: Message,      # объект события
    user: User,            # автоматически получен для message_new
    state: FSMContext,     # FSM контекст для этого пользователя+чата
    bot: Bot,              # экземпляр бота
) -> None: ...
```

Кастомные типы можно внедрить через middleware добавив их в словарь `data`.

## Порядок разрешения хэндлеров

1. Хэндлеры зарегистрированные первыми имеют приоритет.
2. Если фильтры хэндлера прошли, он обрабатывает событие и останавливает обработку.
3. Фильтры уровня роутера проверяются перед фильтрами уровня хэндлера.
4. Хэндлеры суб-роутеров проверяются после хэндлеров родительского роутера.
