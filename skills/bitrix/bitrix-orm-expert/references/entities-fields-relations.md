# Сущности, поля и отношения

## Содержание

- DataManager и Entity
- Поля
- Relations
- Runtime и динамические сущности
- Практические проверки

## DataManager и Entity

Минимальная сущность определяет `getTableName()` и `getMap()`. Дополнительно проверь:

- `getConnectionName()` для нестандартного подключения.
- `getUfId()` для пользовательских полей.
- `setDefaultScope(Query $query)` для обязательного scope.
- `postInitialize(Entity $entity)` для динамических полей/relations после сборки карты.
- `getObjectClass()/getCollectionClass()` для собственных классов.
- `getEntity()->getFields()` для итоговой карты, включая UF и динамические поля.

Не путай:

- `getMap()` возвращает декларацию класса.
- `getEntity()->getFields()` возвращает реально инициализированную карту.
- `registerRuntimeField()` добавляет поле только конкретному Query.
- `getEntity()->addField()` меняет Entity текущего PHP-процесса.

## Поля

### Базовые настройки ScalarField

- `primary`: часть первичного ключа.
- `autocomplete`: DB-generated значение.
- `required`: ORM-проверка непустого значения.
- `unique`: добавляет UniqueValidator, но не заменяет уникальный индекс БД.
- `nullable`: разрешение `NULL`.
- `private`: скрыто от обычного select, пока private fields не включены.
- `column_name`: физическое имя колонки.
- `default_value`: значение или callback.

### Типы

- `IntegerField`: идентификаторы и целые числа.
- `FloatField`/`DecimalField`: числа; проверяй precision/scale и денежную семантику.
- `StringField`: строки ограниченной длины; имеет LengthValidator.
- `TextField`: длинный текст.
- `BooleanField`: хранилище задается парой значений. Используй `normalizeValue()`, `booleanizeValue()`, `getValues()`, а не hardcode `0/1` или `N/Y`.
- `EnumField`: значение из разрешенного списка.
- `DateField`/`DatetimeField`: используют Bitrix Date/DateTime; Datetime может учитывать timezone.
- `ArrayField`: сериализация JSON/PHP или callbacks.
- `ObjectField`: сериализация объекта через callbacks.
- `CryptoField`: шифрует значение при наличии crypto support/key.
- `SecretField`: предназначен для секретов с особым преобразованием.
- `ExpressionField`: только чтение; строится из SQL expression и `buildFrom`.

### Validators и modifiers

- Validators выполняются при обычных `add/update/save`.
- Fetch modifiers меняют данные после чтения.
- Save modifiers меняют данные перед SQL-записью.
- Modifier/validator должен быть чистым и предсказуемым; тяжелый запрос внутри него создает скрытый N+1.
- `UniqueValidator` и `ForeignValidator` выполняют дополнительные SQL-запросы; в batch-сценариях оцени их стоимость.
- Для инварианта, который должен гарантировать БД, используй также индекс/constraint.

## Relations

### Reference

Используй для N:1/1:1 со стороны таблицы, содержащей внешний ключ.

```php
new Reference(
    'PROCESS',
    ProcessesTable::class,
    Join::on('this.PROCESS_ID', 'ref.ID')
)
```

- `this` относится к текущей Entity, `ref` к связанной.
- Явно оцени `LEFT` против `INNER`.
- Для составного join собирай условия через `Join::on(...)->where(...)`.
- Relation в select может влиять на количество строк и кеширование.

### OneToMany

Обратная коллекция через имя `Reference` в дочерней Entity:

```php
new OneToMany('APPLICATIONS', ApplicationsTable::class, 'PROCESS')
```

Имя третьего аргумента должно совпадать с Reference дочерней сущности. Это не физическое поле.

### ManyToMany

Работает через mediator entity/table. Предпочитай явную mediator entity, если у связи есть дополнительные поля или важна прозрачность.

- Для простой связи можно настроить mediator table и имена local/remote primary.
- Для дополнительных данных моделируй mediator как полноценную сущность и работай с ней явно.
- Проверь составные primary, уникальный индекс пары FK и cascade policy.

### Cascade policies

- `NO_ACTION`: ORM не меняет связанную сущность.
- `SET_NULL`: обнуляет связь, если контракт допускает nullable.
- `FOLLOW`: следует за связанными объектами.
- `FOLLOW_ORPHANS`: удаляет оставшиеся без владельца записи; высокий риск потери данных.

Перед cascade проверь реальное владение записью, DB constraints и транзакцию.

## Runtime и динамические сущности

- Runtime `Reference`/`ExpressionField` хорош для одного запроса и не загрязняет глобальную Entity.
- `Entity::compileEntity()` полезен для динамических таблиц, но усложняет типизацию и диагностику.
- Для Bitrix iblock ORM relation может требовать `getEntity()->addField(...)`, потому что итоговая Entity формируется динамически.
- После изменения UF/map в долгоживущем процессе может потребоваться сброс Entity/runtime-кеша.

## Практические проверки

- Физическая колонка существует и совместима с Field.
- Primary и autocomplete соответствуют таблице.
- Boolean storage values соответствуют данным.
- Nullable/required/default не противоречат друг другу.
- Join использует индексированные поля.
- OneToMany ссылается на существующий Reference.
- ManyToMany mediator имеет уникальность пары и нужные индексы.
- Runtime alias не конфликтует с map/select alias.
- `StringField::size` в локальной версии может молча обрезать значение; для строгого контракта добавь явный LengthValidator.
- `ObjectField` требует корректные serialize/unserialize callbacks.
- Поведение границ `RangeValidator` проверяй по локальному исходнику, не только по PHPDoc.
