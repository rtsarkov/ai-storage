# Объекты и коллекции

## Содержание

- Когда использовать
- EntityObject
- Collection
- Relations
- Ловушки

## Когда использовать

Используй object API, когда нужны:

- доменные методы собственного object-класса;
- change tracking;
- типизация и преобразование полей;
- lazy/batch fill;
- сохранение relation changes.

Для плоского read-only отчета массивы обычно дешевле и проще.

## EntityObject

Создание и восстановление:

- `Table::createObject()` создает RAW object с defaults.
- `Table::wakeUpObject($primaryOrRow)` восстанавливает объект без полного запроса.
- `fetchObject()` гидратирует объект из Result.

Состояния:

- `RAW`: новый.
- `ACTUAL`: соответствует БД.
- `CHANGED`: содержит изменения.
- `DELETED`: удален.

Значения:

- Именованные методы: `getName()`, `setName()`, `remindActualName()`, `resetName()`.
- Универсальные методы: `get/set/require/remindActual/reset/unset`.
- `collectValues(Values::CURRENT|ACTUAL|ALL, FieldTypeMask::...)`.
- Runtime-значения читаются универсальным `get()`.
- Existing primary нельзя менять как обычное поле.

Загрузка:

- `fill($fieldsOrMask)` дозагружает незаполненные поля.
- `isFilled`, `isChanged`, `has` отвечают на разные вопросы; не подменяй один другим.
- Если объект нужен только как ссылка по primary, `wakeUpObject()` дешевле полного select.

Запись:

- `save()` выбирает add/update по состоянию и сохраняет relation changes.
- `delete()` удаляет объект и переводит его в DELETED.
- Всегда проверяй Result.

## Collection

Получение:

- `fetchCollection()`.
- `Table::createCollection()`.
- `Table::wakeUpCollection($rowsOrPrimaries)`.

Коллекция:

- реализует Iterator, ArrayAccess, Countable;
- индексирует объекты по serialized primary;
- умеет `getAll()`, `getByPrimary()`, `has()`, `isEmpty()`, `merge()`;
- поддерживает групповые `fill()` и `save()`;
- может собирать значения и relation-коллекции без ручного цикла запросов.

Для списка объектов:

```php
$items = ItemsTable::query()
    ->setSelect(['ID'])
    ->whereIn('ID', $ids)
    ->fetchCollection();

$items->fill(['NAME', 'PROCESS']);
```

Это предпочтительнее `fill()` каждого объекта в цикле.

## Relations

- Reference возвращает объект или `null`.
- OneToMany/ManyToMany возвращают Collection.
- Для изменения связи вызывай у владельца `addTo<Field>()`, `removeFrom<Field>()`, `removeAll<Field>()`, затем `save()`.
- Прямой `Collection::add/remove` меняет коллекцию, но не гарантирует фиксацию relation change.
- Relation changes сохраняются с учетом cascade policy и состояния объектов.

## Iblock object API

- Для элементов инфоблоков через `Bitrix\Iblock\Elements\Element*Table` сначала проверь API-код инфоблока и фактическую карту Entity.
- Обычные поля элемента читаются сгенерированными camelCase-getter'ами: `getId()`, `getName()`, `getDetailPicture()`.
- Свойства элемента также читаются через `get<Property>()`, но форма результата зависит от кратности и типа свойства.
- Одиночное свойство возвращает объект значения: `getArticle()->getValue()`, `getLatitude()->getValue()`, `getListProperty()->getValue()`.
- Множественное свойство возвращает Collection: `foreach ($element->getPhotos()->getAll() as $value) { $value->getValue(); }`.
- Для дополнительных данных используй явный select-путь: `PROPERTY.FILE` для файлов, `PROPERTY.ITEM` для списков, `PROPERTY.ELEMENT` для привязки к элементу, `PROPERTY.SECTION` для привязки к разделу.
- Не используй `method_exists()` как нормальный способ чтения iblock-свойств. Если код не знает кратность свойства, сначала получи/проверь схему, а не подбирай метод в runtime.

## Ловушки

- Lazy fill в цикле создает N+1.
- `wakeUpObject()` не доказывает существование строки в БД.
- Частично выбранный object имеет незаполненные поля; `get()` может вернуть `null`, а `require()` инициировать загрузку/ошибку в зависимости от контракта.
- `collectValues()` с relations может вернуть тяжелую структуру.
- Collection save не является заменой транзакции для сложного бизнес-сценария.
- Identity map действует в рамках гидрации/процесса, а не как общий application cache.
- Составные primary сериализуются внутренним алгоритмом; не изобретай собственный ключ без необходимости.
- В локальной версии Objectify не открывает общую транзакцию вокруг объекта и связей.
- Часть результатов каскадных save/delete может не попасть в итоговый Result; критичные связи проверяй отдельно.
- `configureCascadeSavePolicy()` не гарантирует ожидаемый контроль сохранения во всех ветках локальной реализации.
- `collectValues(..., recursive: true)` опасен на двунаправленных relations.
- У iblock-свойств одиночное и множественное значение имеют разные object-контракты; универсальный helper на `getValueList()` легко ломает одиночные строковые/числовые свойства.
