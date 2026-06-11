# Запросы и фильтры

## Содержание

- Выбор API
- Query
- Фильтры
- Runtime, expressions и relations
- Result
- UNION, подсчеты и кеш

## Выбор API

- `getRowById($id)`: одна строка по простому ID.
- `getRow($parameters)`: одна строка-массив с `limit=1`.
- `getByPrimary($primary, $parameters)`: Query Result по primary, включая составной.
- `getList($parameters)`: компактный declarative API.
- `query()`: предпочтителен для сложных, изменяемых и типизированных запросов.
- `getCount($filter)`: простой count без сложной группировки.

`getList()` поддерживает `select`, `filter`, `group`, `order`, `limit`, `offset`, `count_total`, `runtime`, `data_doubling`, `private_fields`, `cache`.

## Query

```php
$query = ItemsTable::query()
    ->setSelect(['ID', 'NAME', 'PROCESS.CODE'])
    ->where('ACTIVE', true)
    ->whereIn('PROCESS_ID', $processIds)
    ->addOrder('ID', 'DESC')
    ->setLimit(100);

$rows = $query->fetchAll();
```

Рекомендации:

- Явный `select` обязателен для списков и API.
- Сначала определи кардинальность результата, затем добавляй relations.
- Alias задавай осмысленно и не переиспользуй.
- `group/order/select` с агрегатами могут автоматически расширять `GROUP BY`; проверяй SQL.
- Private fields включай только осознанно.

## Фильтры

Массивный filter поддерживается, но для сложной динамической логики используй `ConditionTree`.

```php
$filter = Query::filter()
    ->logic('or')
    ->where('STATUS', 'NEW')
    ->where(
        Query::filter()
            ->where('STATUS', 'DONE')
            ->whereNotNull('FINISHED_AT')
    );
```

Основные методы:

- `where`, `whereNot`, `whereColumn`.
- `whereNull`, `whereNotNull`.
- `whereIn`, `whereNotIn`.
- `whereBetween`, `whereNotBetween`.
- `whereLike`, `whereNotLike`.
- `whereExists`, `whereNotExists`.
- `whereMatch`, `whereNotMatch`.
- `whereExpr`.

Правила:

- Пустой `whereIn('ID', [])` в этой версии не означает «ничего не найти»: условие пропускается. Проверяй пустой набор до построения запроса и возвращай пустой результат явно.
- Для сравнения колонок используй `whereColumn`, не передавай имя колонки как строковое значение.
- Пользовательские значения не вставляй в SQL expression строковой конкатенацией.
- Fulltext `MATCH` требует подходящего индекса и проверки DB-specific поведения.

## Runtime, expressions и relations

```php
$query->registerRuntimeField(
    new ExpressionField('CNT', 'COUNT(%s)', ['ID'])
);
```

- `ExpressionField` может быть scalar, aggregate, constant или содержать subquery.
- Все зависимости `buildFrom` должны разрешаться Query chain.
- Фильтр по aggregate попадет в HAVING.
- Runtime Reference удобен для запроса, но может размножить строки.
- Путь `RELATION.FIELD` строит цепочку joins автоматически.

При фильтрации через 1:N/N:M проверь:

- Нужны ли уникальные базовые строки.
- Нужен ли `disableDataDoubling()`, преобразующий часть фильтров в `EXISTS`.
- Не скрывает ли `DISTINCT` неправильную кардинальность и дорогой join.

## Result

- `fetch()`: следующая строка-массив.
- `fetchAll()`: все строки-массивы.
- `fetchObject()`: следующий EntityObject.
- `fetchCollection()`: коллекция объектов.
- `fetchRaw()`: сырые значения до части преобразований.

Не вызывай `fetchCollection()` дважды на одном Result: курсор уже изменен. Не используй object hydration, если нужен только плоский экспорт из миллионов строк.

## UNION, подсчеты и кеш

- `union()` создает UNION, `unionAll()` сохраняет дубли и обычно дешевле.
- Общие `order/limit/offset` для union задаются отдельными union-методами.
- `countTotal(true)` выполняет дополнительный count-запрос; не включай автоматически.
- `setCacheTtl()` включает ORM cache.
- По умолчанию запросы с join не кешируются; `cacheJoins(true)` включает это явно.
- ORM cache очищается обычными операциями DataManager своей Entity, но прямой SQL и изменения связанных таблиц могут оставить устаревшие результаты.

## Проверка запроса

1. Получи `$query->getQuery()` до исполнения или `Query::getLastQuery()` после.
2. Проверь joins, WHERE/HAVING, GROUP BY, LIMIT и aliases.
3. Проверь количество базовых ID и дублей.
4. Проверь индексы и EXPLAIN.
5. Для списка измерь количество запросов вместе с последующей обработкой.

## Ловушки локальной версии

- Не изменяй Query после первого `getQuery()`/`exec()`: собранные части кешируются внутри объекта.
- `LIKE` не добавляет `%` автоматически.
- `disableDataDoubling()` рассчитан на одиночный primary.
- Object fetch запрещен для агрегатного запроса.
- `fetchObject()` с back-reference может сначала загрузить весь result set.
- Relation collection считается полностью загруженной только без `LIMIT` и без фильтра по этой relation.
- `QueryHelper::getPrimaryFilter()` в локальной версии имеет дефект для составного primary; проверяй результат до использования.
- UNION не проверяет совместимость и количество колонок.
