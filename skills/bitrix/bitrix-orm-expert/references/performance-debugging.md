# Производительность и диагностика

## Содержание

- Приоритет оптимизации
- N+1 и batch
- Кардинальность
- Кеш
- Диагностика ошибок

## Приоритет оптимизации

1. Убрать N+1.
2. Уменьшить select и число строк.
3. Исправить кардинальность joins.
4. Добавить/проверить индексы.
5. Выбрать batch/bulk API.
6. Только затем добавлять кеш.

Измеряй до и после: время, количество SQL, число гидратированных строк, память.

## N+1 и batch

Запрещенный паттерн:

```php
foreach ($items as $item)
{
    $item->fillProcess();
}
```

Предпочтительно:

- `Collection::fill(['PROCESS'])`;
- один query `whereIn('ID', $ids)`;
- repository batch method;
- preload в static cache с раскладкой по ID.

Для списковых компонентов сначала собери все foreign IDs, затем загрузи каждую зависимость одним запросом.

## Кардинальность

- Reference обычно не размножает базовую строку, если join уникален.
- OneToMany/ManyToMany в select/filter могут размножать строки.
- `DISTINCT` скрывает дубли, но может быть дорогим и маскировать ошибочную модель.
- Для фильтра существования связанной строки предпочитай `EXISTS`/`disableDataDoubling()`.
- Для выборки relation-коллекции часто лучше отдельный batch query, чем один огромный join.
- Pagination по размноженному набору может вернуть неверное число базовых сущностей.

## Select и hydration

- Выбирай только нужные поля.
- Не выбирай тяжелые text/array/UF/relations без необходимости.
- Для экспорта большого объема используй streaming `fetch()`, а не `fetchAll()/fetchCollection()`.
- Object hydration оправдана поведением и relations; массивы дешевле для плоских данных.
- `countTotal(true)` создает дополнительный запрос.

## Кеш

- `setCacheTtl($ttl)` полезен только для повторяемого стабильного запроса.
- Join-кеш выключен по умолчанию; `cacheJoins(true)` повышает риск устаревших данных.
- Обычный DataManager CRUD вызывает `cleanCache()` своей Entity.
- Прямой SQL, merge/deleteByFilter и изменение связанной Entity требуют отдельной проверки инвалидации.
- Не кешируй запрос, пока не устранены N+1, лишние строки и плохие индексы.

## Диагностика ошибок

### Unknown field definition

1. Проверь итоговую `Table::getEntity()->getFields()`.
2. Проверь alias/runtime registration до использования.
3. Для динамической iblock Entity добавляй relation через `getEntity()->addField(...)`.
4. Проверь порядок инициализации и сброс Entity cache.

### Дубли

1. Посмотри SQL.
2. Найди 1:N/N:M join.
3. Проверь уникальность join-условия.
4. Выбери `EXISTS`, отдельный batch query, group или distinct осознанно.

### Неверный boolean

1. Получи Field из Entity.
2. Убедись, что это `BooleanField`.
3. Используй `getValues()/normalizeValue()/booleanizeValue()`.
4. Не смешивай storage value и PHP bool.

### Не сработало событие

Проверь, не использовались ли:

- `ignoreEvents=true`;
- `MergeTrait::merge()`;
- `DeleteByFilterTrait::deleteByFilter()`;
- прямой SQL;
- изменение relation collection без object `save()`.

### Устаревшие данные

Проверь ORM query cache, join cache, static cache, managed cache и прямые записи в БД.

## Диагностические команды

```bash
rg -n "function methodName" bitrix/modules/main/lib/orm
rg -n "ClassName|FIELD_NAME" local/modules local/components
php -l path/to/file.php
```

На runtime-стенде дополнительно:

- `$query->getQuery()`;
- `\Bitrix\Main\ORM\Query\Query::getLastQuery()`;
- DB `EXPLAIN`;
- счетчик SQL проекта;
- точечный интеграционный сценарий create/read/update/delete.
