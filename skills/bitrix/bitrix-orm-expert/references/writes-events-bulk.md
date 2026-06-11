# Запись, события и массовые операции

## Содержание

- Обычный lifecycle
- Result и ошибки
- Events
- Bulk API
- Прямые операции
- Транзакции

## Обычный lifecycle

Для `DataManager::add/update/delete` ядро координирует:

- нормализацию primary и данных;
- field validation;
- before/on/after events;
- save modifiers и преобразование в DB;
- user fields;
- SQL;
- очистку ORM cache;
- Result.

Используй обычный lifecycle по умолчанию, особенно когда сущность имеет события, UF, modifiers, relations или бизнес-инварианты.

## Result и ошибки

```php
$result = ItemsTable::add($data);
if (!$result->isSuccess())
{
    throw new \RuntimeException(implode('; ', $result->getErrorMessages()));
}
```

- `AddResult` содержит добавленный primary/ID.
- Ошибки могут быть `EntityError` или `FieldError` с кодом.
- Проверяй конкретные коды, когда ошибка имеет бизнес-смысл.
- Исключение и unsuccessful Result являются разными каналами ошибок.

## Events

Стандартные события:

- `OnBeforeAdd`, `OnAdd`, `OnAfterAdd`.
- `OnBeforeUpdate`, `OnUpdate`, `OnAfterUpdate`.
- `OnBeforeDelete`, `OnDelete`, `OnAfterDelete`.

`EventResult` позволяет:

- добавить ошибки;
- изменить поля;
- удалить поля из операции.

Правила:

- Before event валидирует/модифицирует до SQL.
- After event не должен предполагать, что внешний побочный эффект откатится вместе с DB.
- Избегай рекурсивного вызова той же операции из ее обработчика.
- Тяжелые запросы в events размножают стоимость каждой записи.

## Bulk API

### `addMulti($rows, $ignoreEvents = false)`

- Эффективнее цикла add.
- Строки должны иметь совместимый набор полей.
- События и auto-increment ограничивают multi-insert: ядру нужны ID для событий.
- `ignoreEvents=true` меняет семантику, а не только скорость.
- `ignoreEvents=true` не отключает validation, modifiers, UF и очистку кеша в локальной версии.
- При events + auto-increment настоящий multi-insert может превратиться в отдельные INSERT.
- Проверь validators, UF и Result локальной версии.

### `updateMulti($primaries, $data, $ignoreEvents = false)`

- Обновляет много primary одинаковыми данными.
- Не подходит, когда каждой строке нужны разные значения.
- Events и проверки могут сделать операцию существенно дороже.
- Если event handlers модифицируют строки по-разному, локальная реализация может перейти к отдельным UPDATE.

Для разных данных по строкам часто лучше:

- специализированный repository/service batch;
- DB-specific upsert после проверки контракта;
- chunked обычные операции в транзакции, если события обязательны.

## Прямые операции

### `MergeTrait::merge()`

- Использует SQL helper `prepareMerge()`.
- Выполняет upsert по primary или переданным unique fields.
- Очищает ORM cache.
- Не запускает обычную валидацию, modifiers, UF и CRUD events.
- Не возвращает стандартный Add/Update Result.

Применяй для технических таблиц и идемпотентной синхронизации, когда обход lifecycle доказанно допустим.

### `DeleteByFilterTrait::deleteByFilter()`

- Строит SQL filter и запрещает пустой фильтр.
- Выполняет прямой DELETE.
- Вызывает только optional `onBeforeDeleteByFilter()`.
- Не запускает обычные per-row delete events/cascade/object logic.
- Не удаляет UF-данные через обычный UF lifecycle.
- Очищает ORM cache своей Entity.

Не применяй, если delete events, cascade или аудит обязательны.

## Транзакции

- ORM-операция может использовать внутреннюю транзакцию, но бизнес-сценарий из нескольких операций требует внешней транзакции.
- Получай connection у Entity/ConnectionPool и оборачивай зависимые записи.
- Внешние API, файлы и сообщения не откатываются DB-транзакцией; проектируй компенсацию/outbox.
- После rollback не считай in-memory EntityObject автоматически синхронизированным с БД.
- Обычный DataManager CRUD не дает общей транзакции для SQL, UF и внешних after-event side effects.

## Checklist записи

- Нормализованы типы, особенно boolean/date/array.
- Required/nullable/default согласованы.
- Проверен Result.
- Известно, какие события запускаются.
- Известно, какие кеши очищаются.
- Для bulk явно подтвержден допустимый обход lifecycle.
- Для нескольких таблиц есть транзакционная стратегия.
