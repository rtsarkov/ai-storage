---
name: bitrix-orm-expert
description: Проектирование, реализация, отладка и оптимизация решений на Bitrix D7 ORM. Использовать при работе с DataManager, Entity, ORM-полями, Reference/OneToMany/ManyToMany, Query/getList/ConditionTree, ExpressionField, EntityObject/Collection, ORM-событиями, batch-операциями, пользовательскими полями, runtime-связями, кешированием и проблемами производительности/N+1.
---

# Bitrix ORM Expert

## Назначение

Находить корректное и производительное решение на Bitrix D7 ORM с учетом реально установленной версии ядра и паттернов проекта.

## Главный принцип

Локальные исходники `bitrix/modules/main/lib/orm/` являются источником истины для доступного API и поведения. Официальная документация объясняет контракт, но может описывать другую версию.

Перед нетривиальным решением:

1. Найди корень сайта и локальный ORM-пакет.
2. Запусти `scripts/inspect-orm.sh <site-root>`.
3. Проверь сигнатуры и реализацию нужных методов в исходниках.
4. Найди 1-3 близких примера в проекте.
5. Только после этого проектируй изменение.

## Обязательный рабочий процесс

### 1. Определи форму задачи

- Описание новой таблицы/сущности: читай `references/entities-fields-relations.md`.
- Выборка, фильтр, join, агрегат, подзапрос: читай `references/queries-filters.md`.
- Объекты, коллекции, загрузка и сохранение связей: читай `references/objects-collections.md`.
- Элементы инфоблоков через `Bitrix\Iblock\Elements\Element*Table`, свойства, `fetchObject()/fetchCollection()`: читай `references/iblock-elements.md`.
- Add/update/delete, события, bulk/upsert: читай `references/writes-events-bulk.md`.
- Медленный запрос, N+1, дубли, кеш, непонятный SQL: читай `references/performance-debugging.md`.
- Выбор между несколькими подходами: читай `references/decision-recipes.md`.
- Поиск нужного внутреннего класса: читай `references/source-map.md`.

### 2. Проверь контракт сущности

- Изучи `DataManager::getTableName()`, `getMap()`, `getUfId()`, `setDefaultScope()` и `postInitialize()`.
- Получай инициализированные поля через `Table::getEntity()->getFields()/getField()`, а не только через `getMap()`.
- Учитывай runtime-поля, динамически добавленные поля, пользовательские поля и relation-поля.
- Проверяй фактические типы полей перед нормализацией значений. Не считай, что все boolean хранятся как `0/1`.

### 3. Выбери минимальный корректный API

- Одна простая строка-массив: `getRow()`/`getRowById()`.
- Массивы: `getList()->fetch()/fetchAll()`.
- Объект с поведением или связями: `query()->fetchObject()`.
- Набор объектов и batch-fill/save: `fetchCollection()`.
- Сложный динамический фильтр: `Query::filter()` / `ConditionTree`.
- Агрегат или вычисление: `ExpressionField`.
- Динамическая связь только для запроса: `registerRuntimeField()`.
- Массовая предзагрузка: один запрос по списку ID и раскладка по ключу.

### 4. Проверь корректность и стоимость

- Явно задай `select`; не загружай `*` и тяжелые relations без необходимости.
- Для списков исключи запросы внутри цикла.
- Проверь кардинальность relation и возможность размножения строк.
- Для фильтра по 1:N/N:M оцени `disableDataDoubling()` и `EXISTS`.
- Не включай `cacheJoins(true)` без анализа изменяемости связанных таблиц и инвалидации.
- Проверь индексы для `WHERE`, `JOIN`, `ORDER BY`, уникальных ограничений.
- Получи SQL через `$query->getQuery()` или `Query::getLastQuery()` и оцени план выполнения, когда это возможно.

### 5. Проверь запись

- Всегда проверяй `Result::isSuccess()` и `getErrorMessages()/getErrors()`.
- Учитывай validators, save modifiers, user fields, события и очистку ORM-кеша.
- `addMulti()/updateMulti()` применяй только после проверки их ограничений по событиям, auto-increment и одинаковому набору полей.
- `MergeTrait::merge()` и `DeleteByFilterTrait::deleteByFilter()` обходят обычный CRUD lifecycle; применяй осознанно.
- При нескольких зависимых записях используй транзакцию уровня connection/service.

### 6. Верифицируй

- Проверь синтаксис измененных PHP-файлов.
- Для запросов проверь SQL, количество строк, отсутствие дублей и корректность пустых наборов.
- Для записи проверь create/update/delete, ошибки валидаторов, события, связи и очистку кеша.
- Для оптимизации сравни количество SQL-запросов и время до/после.

## Жесткие правила

- Не редактируй ядро `bitrix/modules/main/lib/orm/`.
- Не используй сырой SQL, пока ORM выражает задачу без потери корректности или существенной производительности.
- Не создавай N+1: relation-fill коллекции или batch preload предпочтительнее запросов в цикле.
- Не изменяй relation-коллекцию напрямую для сохранения связи; используй `addTo/removeFrom/removeAll` и `save()`.
- Не полагайся на `getMap()` для динамических полей Bitrix iblock/HLBlock; проверяй инициализированную Entity.
- Для iblock-свойств не заменяй знание схемы `method_exists()`-fallback'ами: сначала определи тип, кратность и нужные дополнительные поля (`VALUE`, `FILE`, `ITEM`, `ELEMENT`, `SECTION`), затем используй соответствующий сгенерированный getter.
- Не читай одиночные и множественные iblock-свойства одним универсальным `getValueList()`: одиночное свойство читает `get<Property>()->getValue()`, множественное возвращает коллекцию и читается через `get<Property>()->getAll()`.
- Не считай `php -l` доказательством runtime-корректности.
- Для API, которого нет в локальной версии, предложи совместимый вариант, а не код из более новой документации.

## Формат результата

При объяснении решения укажи:

1. Почему выбран этот ORM API.
2. Какой SQL-паттерн он создаст и где риск N+1/дублей.
3. Какие lifecycle-события, валидаторы, relations и кеши затронуты.
4. Как решение проверено.

## Официальные источники

- Современная документация: <https://docs.1c-bitrix.ru/pages/orm/orm-concepts.html>
- Учебный курс и оглавление ORM: <https://dev.1c-bitrix.ru/learning/course/index.php?COURSE_ID=43&CHAPTER_ID=05748&LESSON_PATH=3913.3516.5748>
- Практическая статья по `Bitrix\Iblock\Elements\Element*Table` и свойствам: <https://mrcappuccino.ru/blog/post/iblock-elements-bitrix-d7>

Используй их для уточнения концепций. При расхождении следуй локальным исходникам.
