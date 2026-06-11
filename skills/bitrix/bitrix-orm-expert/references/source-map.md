# Карта пакета ORM

## Содержание

- Приоритет источников
- Подсистемы пакета
- Как искать контракт
- Совместимость

## Приоритет источников

1. Исходники установленного `bitrix/modules/main/lib/orm/`.
2. Реальные ORM-сущности и запросы текущего проекта.
3. Современная официальная документация `docs.1c-bitrix.ru`.
4. Учебный курс `dev.1c-bitrix.ru`.

Документация может содержать методы из более новой версии. Старый namespace `Bitrix\Main\Entity` обычно является слоем обратной совместимости; для нового кода предпочитай `Bitrix\Main\ORM`.

## Подсистемы пакета

### Корень

- `entity.php`: инициализация Entity, поля, primary, runtime compile, object/collection-классы, кеш.
- `event.php`, `eventresult.php`, `eventmanager.php`: ORM lifecycle events и модификация данных.
- `entityerror.php`: ошибки уровня сущности.
- `loader.php`: автозагрузка сгенерированных object/collection-классов.
- `annotations/*`: генерация аннотаций для DataManager, объектов, коллекций и relations.

### `data/`

- `datamanager.php`: основной facade чтения/записи и lifecycle.
- `result.php`, `addresult.php`, `updateresult.php`, `deleteresult.php`: результаты операций.
- `internal/mergetrait.php`: DB-specific upsert без стандартных событий/валидации.
- `internal/deletebyfiltertrait.php`: прямой delete по непустому фильтру без стандартных delete-событий.

### `fields/`

- `field.php`: validators, fetch/save modifiers, serialization, title, entity/connection.
- `scalarfield.php`: primary, required, unique, autocomplete, private, nullable, binary, column/default.
- Скалярные типы: integer, float/decimal, string/text, boolean, enum, date/datetime.
- Сериализуемые/специальные: array, object, crypto, secret.
- `expressionfield.php`: вычисляемые и агрегатные runtime/map-поля.
- `usertypefield.php`, `usertypeutsmultiplefield.php`: пользовательские поля.
- `fieldtypemask.php`: маски для object/collection fill и collectValues.

### `fields/relations/`

- `reference.php`: N:1 и 1:1 в направлении владельца внешнего ключа.
- `onetomany.php`: обратная коллекция через существующий Reference.
- `manytomany.php`: связь через mediator entity/table.
- `relation.php`: join type и cascade policies.
- `cascadepolicy.php`: `NO_ACTION`, `SET_NULL`, `FOLLOW`, `FOLLOW_ORPHANS`.

### `fields/validators/`

- `BooleanValidator`, `DateValidator`, `EnumValidator`.
- `ForeignValidator`, `UniqueValidator`.
- `LengthValidator`, `RangeValidator`, `RegExpValidator`.
- `IValidator`/`Validator`: контракт и базовая обработка ошибок.

### `query/`

- `query.php`: Query builder, select/filter/group/order/runtime/union/cache/exec.
- `result.php`: array/object/collection hydration.
- `filter/*`: `ConditionTree`, conditions, operators и expressions.
- `join.php`: построитель join-условий.
- `chain.php`, `chainelement.php`: разрешение путей вида `RELATION.FIELD`.
- `expression.php`: SQL expressions для filter/join.
- `union.php`, `unioncondition.php`: UNION/UNION ALL и общие limit/order.
- `queryhelper.php`: вспомогательные преобразования сложных запросов.
- `nosqlprimaryselector.php`: интерфейс альтернативного выбора primary.

### `objectify/`

- `entityobject.php`: состояния, значения, fill/save/delete, relation changes.
- `collection.php`: identity по primary, batch fill/save, групповые значения.
- `identitymap.php`: повторное использование объектов в пределах hydration.
- `state.php`: `RAW`, `ACTUAL`, `CHANGED`, `DELETED`.
- `values.php`: выбор CURRENT/ACTUAL/ALL значений.

## Как искать контракт

```bash
# Сигнатура и реализация метода
rg -n "function methodName" bitrix/modules/main/lib/orm

# Доступные методы подсистемы
rg -n "public (static )?function" bitrix/modules/main/lib/orm/query

# Реальные примеры проекта
rg -n "registerRuntimeField|fetchCollection|new OneToMany" local/modules local/components
```

Для неизвестного поведения читай вызывающий и вызываемый код до места SQL/события/гидрации. Не делай вывод только по PHPDoc.

## Совместимость

- Проверяй наличие метода через локальный исходник до использования.
- Учитывай PHP-версию проекта.
- Не переноси примеры с `Bitrix\Main\Entity` в новый код без проверки современного аналога.
- Runtime-расширения Entity живут в процессе PHP и зависят от порядка инициализации.
- Сгенерированные object/collection-классы зависят от корректной карты Entity и автозагрузчика.
