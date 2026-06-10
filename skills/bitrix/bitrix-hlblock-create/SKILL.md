---
name: bitrix-hlblock-create
description: Создание HLBlock таблицы для Bitrix CMS с правильной структурой, миграцией и интеграцией с модулем. Использовать, когда пользователь просит создать HLBlock, создать новую таблицу в проекте lk.tpprf.ru, добавить HLBlock таблицу в модуль forumedia или создать ORM сущность для Highload-блока.
---

# Скилл: Создание HLBlock для Bitrix

## Назначение

Создание HLBlock таблицы для Bitrix CMS с правильной структурой, миграцией и интеграцией с модулем.

## Когда использовать

Когда пользователю нужно создать новую HLBlock таблицу в проекте lk.tpprf.ru.

## Шаги выполнения

### 1. Сбор параметров

Попросите пользователя предоставить:
- Название таблицы (описательное, на английском)
- Целевой модуль (например: forumedia.docflow)
- Список полей (необязательно)
- Связи с другими таблицами (необязательно)

### 2. Создание DataManager

Создайте файл в `local/modules/{module}/lib/entity/{TableName}Table.php`:

```php
<?php
namespace {ModuleNamespace};

use Bitrix\Main\ORM\Data\DataManager;
use Bitrix\Main\ORM\Fields\IntegerField;
use Bitrix\Main\ORM\Fields\StringField;
use Bitrix\Main\ORM\Fields\DatetimeField;
use Bitrix\Main\ORM\Fields\BooleanField;

class {TableName}Table extends DataManager
{
    public static function getTableName()
    {
        return 'fm_hl_{table_name}';
    }

    public static function getMap()
    {
        return [
            new IntegerField('ID', [
                'primary' => true,
                'autocomplete' => true,
            ]),
            new StringField('UF_NAME', [
                'required' => true,
                'title' => 'Название',
            ]),
            new StringField('UF_CODE', [
                'required' => true,
                'title' => 'Код',
            ]),
            new BooleanField('UF_ACTIVE', [
                'values' => ['N', 'Y'],
                'default_value' => 'Y',
                'title' => 'Активность',
            ]),
            new DatetimeField('UF_DATE_CREATE', [
                'default_value' => new \Bitrix\Main\Type\DateTime(),
                'title' => 'Дата создания',
            ]),
        ];
    }
}
```

### 3. Создание миграции

Создайте файл в `local/php_interface/migrations/{ОписательноеИмя}{timestamp}.php`:

```php
<?php
use Sprint\Migration\Version;
use Sprint\Migration\Builder;

class {ОписательноеИмя}{timestamp} extends Version
{
    protected $description = "Создание HLBlock таблицы {table_name}";

    protected $moduleVersion = "3.25.1";

    public function up()
    {
        $helper = $this->getHelperManager();

        // Создание HLBlock
        $hlblockId = $helper->Hlblock()->addIfNotExists([
            'NAME' => '{TableName}',
            'TABLE_NAME' => 'fm_hl_{table_name}',
            'LANG' => [
                'ru' => 'Table Name',
            ],
        ]);

        // Добавление полей
        $helper->Hlblock()->addFieldIfNotExists($hlblockId, [
            'FIELD_NAME' => 'UF_NAME',
            'USER_TYPE_ID' => 'string',
            'SORT' => 10,
            'MANDATORY' => 'Y',
            'EDIT_FORM_LABEL' => ['ru' => 'Название'],
        ]);

        // Добавление прав
        $helper->Hlblock()->addRights($hlblockId, [
            'U1' => 'R', // чтение
            'U2' => 'W', // запись
        ]);
    }

    public function down()
    {
        $helper = $this->getHelperManager();
        $hlblockId = $helper->Hlblock()->getHlblockId('{TableName}');

        if ($hlblockId) {
            $helper->Hlblock()->deleteHlblock($hlblockId);
        }
    }
}
```

### 4. Регистрация в include.php

Добавьте autoload в `local/modules/{module}/include.php`:

```php
Bitrix\Main\Loader::registerAutoLoadClasses(
    '{module}',
    [
        '{ModuleNamespace}\\{TableName}Table' => 'lib/entity/{TableName}Table.php',
    ]
);
```

### 5. Тестирование

Проверьте:
- Миграция создана и работает
- Таблица создана в БД
- DataManager работает через ORM
- Права доступа настроены

## Правила проекта

- **Именование**: TableNamePascalCase для классов, fm_hl_table_name для таблиц
- **Поля**: Все поля должны начинаться с UF_
- **Кодировка**: UTF-8, collation utf8mb4_general_ci
- **Индексы**: Добавляйте индексы для часто используемых полей в WHERE
- **Autoload**: Регистрируйте классы через include.php модуля

## Примеры использования

Смотрите существующие HLBlock таблицы:
- `local/modules/forumedia.docfloworm/lib/entity/ProcessesTable.php`
- `local/modules/forumedia.docfloworm/lib/entity/ApplicationsTable.php`
- `local/modules/forumedia.docfloworm/lib/entity/RolesTable.php`

## Типичные ошибки

1. Забывают зарегистрировать класс в include.php
2. Не добавляют индексы для полей в WHERE
3. Не учитывают связи с другими таблицами
4. Не добавляют права доступа

## Связанные скиллы

- bitrix-migration-create — создание миграций
- performance-optimizer — оптимизация запросов
