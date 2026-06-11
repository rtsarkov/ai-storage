# Выбор решения

## Содержание

- Быстрые решения
- Антипаттерны
- Review checklist

## Быстрые решения

### Получить справочник по ID

Один query с `whereIn()`, явный select, затем ассоциативная раскладка. Не вызывай `getById()` в цикле.

### Проверить наличие связи

Фильтр по relation с `EXISTS`/`disableDataDoubling()` или отдельный query mediator-таблицы. Не выбирай всю relation-коллекцию только ради boolean.

### Посчитать связанные записи

`ExpressionField('CNT', 'COUNT(%s)', [...])` + корректная group/having либо отдельный агрегатный query. Проверь дубли от других joins.

### Добавить динамическую связь

Для одного запроса используй runtime Reference. Для общесистемного контракта добавь relation в Entity map/postInitialize. Для динамической iblock Entity используй `getEntity()->addField()`.

### Сохранить граф объектов

Используй EntityObject relations и cascade только при ясном владении. Для сложного сценария предпочитай service + явную транзакцию.

### Массово записать технические данные

Выбирай `addMulti/updateMulti/merge` только после ответа на вопрос: нужны ли validators, modifiers, UF, events, audit и per-row IDs?

### Удалить много строк

Если обязательны delete events/cascade/audit, удаляй через обычный lifecycle в chunks. Если это чистая техническая таблица и lifecycle не нужен, допустим `deleteByFilter()` с непустым фильтром.

## Антипаттерны

- `getList()` внутри `foreach`.
- `select => ['*', 'RELATION.*']` для списка.
- `DISTINCT` без понимания источника дублей.
- `cacheJoins(true)` как первая оптимизация.
- Hardcode boolean `0/1` или `N/Y`.
- Динамический SQL через конкатенацию пользовательского ввода.
- Save relation через прямое изменение Collection.
- Bulk с `ignoreEvents=true` без проверки бизнес-семантики.
- Runtime field с глобальным alias-конфликтом.
- `getMap()` как единственный источник итоговых полей.
- `php -l` как единственная проверка ORM-изменения.

## Review checklist

### Модель

- Field соответствует колонке и данным.
- Primary/unique/indexes определены корректно.
- Relation direction и cardinality корректны.
- Cascade отражает владение.

### Чтение

- Явный select.
- Нет N+1.
- Нет неожиданных дублей.
- Pagination/count корректны.
- SQL и индексы проверены.

### Запись

- Result проверен.
- Lifecycle и события сохранены либо обход обоснован.
- Типы нормализованы через Field.
- Есть транзакция для зависимых операций.
- Кеши инвалидируются.

### Совместимость

- API существует в локальном ядре.
- Используется `Bitrix\Main\ORM`, если legacy namespace не обязателен.
- Решение соответствует PHP-версии и паттернам проекта.
