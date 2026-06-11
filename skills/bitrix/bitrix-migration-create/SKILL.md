---
name: bitrix-migration-create
description: Создание миграций базы данных для Bitrix CMS с использованием Sprint\Migration. Использовать, когда пользователь просит создать миграцию, изменить структуру БД, добавить таблицу, создать HLBlock или изменить инфоблок в проекте lk.tpprf.ru.
---

# Миграций БД Bitrix

## Назначение

Создание миграций базы данных для Bitrix CMS с использованием Sprint\Migration.

## Когда использовать

Когда пользователю нужно создать миграцию для изменений структуры БД, создания таблиц или миграции данных.

## Шаги выполнения

### 1. Сбор параметров

Попросите пользователя предоставить:
- Описание миграции (на русском языке)
- Тип миграции (create, alter, data, drop)
- Целевую сущность (таблица, HLBlock, инфоблок)
- Операции (создание, изменение, удаление полей/индексов/данных)

### 2. Создание файла миграции

Создайте файл в `local/php_interface/migrations/{ОписательноеИмя}{ГГГГММДДЧЧММСС}.php`:

```php
<?php
namespace Sprint\Migration;

class {ОписательноеИмя}{ГГГГММДДЧЧММСС} extends Version
{
    protected $description = "Описание миграции";

    protected $moduleVersion = "4.6.1";

    public function up()
    {
        $helper = $this->getHelperManager();

        // Создание таблицы
        if ($this->isCreateType()) {
            $helper->Sql()->sql('
                CREATE TABLE IF NOT EXISTS fm_table_name (
                    ID INT(11) NOT NULL AUTO_INCREMENT,
                    UF_NAME VARCHAR(255) NOT NULL,
                    UF_CODE VARCHAR(50) NOT NULL,
                    PRIMARY KEY (ID),
                    INDEX IX_UF_CODE (UF_CODE)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
            ');
        }

        // Изменение таблицы
        if ($this->isAlterType()) {
            $helper->Sql()->sql('
                ALTER TABLE fm_table_name
                ADD COLUMN UF_NEW_FIELD INT(11) NULL,
                ADD INDEX IX_UF_NEW_FIELD (UF_NEW_FIELD);
            ');
        }

        // Миграция данных
        if ($this->isDataType()) {
            $helper->Sql()->sql('
                UPDATE fm_table_name
                SET UF_STATUS = "active"
                WHERE UF_STATUS IS NULL;
            ');
        }
    }

    public function down()
    {
        $helper = $this->getHelperManager();

        // Откат миграции
        if ($this->isCreateType()) {
            $helper->Sql()->sql('DROP TABLE IF EXISTS fm_table_name;');
        }

        if ($this->isAlterType()) {
            $helper->Sql()->sql('
                ALTER TABLE fm_table_name
                DROP COLUMN UF_NEW_FIELD,
                DROP INDEX IX_UF_NEW_FIELD;
            ');
        }
    }

    private function isCreateType()
    {
        return $this->getType() === 'create';
    }

    private function isAlterType()
    {
        return $this->getType() === 'alter';
    }

    private function isDataType()
    {
        return $this->getType() === 'data';
    }

    private function getType()
    {
        // Определение типа миграции по описанию
        return 'create';
    }
}
```

### 3. Создание HLBlock (если нужно)

```php
public function up()
{
    $helper = $this->getHelperManager();

    // Создание HLBlock
    $hlblockId = $helper->Hlblock()->saveHlblock([
        'NAME' => 'TableName',
        'TABLE_NAME' => 'fm_hl_table_name',
        'LANG' => [
            'ru' => 'Table Name',
        ],
    ]);

    // Создание полей
    $helper->Hlblock()->saveField($hlblockId, [
        'FIELD_NAME' => 'UF_NAME',
        'USER_TYPE_ID' => 'string',
        'SORT' => 10,
        'MANDATORY' => 'Y',
        'EDIT_FORM_LABEL' => ['ru' => 'Name'],
    ]);
}
```

### 4. Создание инфоблока (если нужно)

```php
public function up()
{
    $helper = $this->getHelperManager();

    // Создание инфоблока
    $iblockId = $helper->Iblock()->saveIblock([
        'NAME' => 'Infoblock Name',
        'CODE' => 'iblock_code',
        'IBLOCK_TYPE_ID' => 'content',
        'SITE_ID' => ['s1'],
        'GROUP_ID' => [
            '1' => 'X', // Администраторы - полный доступ
            '2' => 'R', // Пользователи - чтение
        ],
    ]);

    // Создание свойств
    $helper->Iblock()->saveProperty($iblockId, [
        'NAME' => 'Property Name',
        'CODE' => 'PROPERTY_CODE',
        'PROPERTY_TYPE' => 'S', // S - строка, N - число, L - список
        'ACTIVE' => 'Y',
    ]);
}
```

### 5. Тестирование

Проверьте:
- Миграция создана
- Метод up() выполняется без ошибок
- Метод down() откатывает изменения
- Структура БД соответствует ожиданиям

## Правила проекта

- **Имя файла**: ОписательноеИмя{ГГГГММДДЧЧММСС}.php
- **Описание**: На русском языке, краткое и понятное
- **Откат**: Обязательно реализовать метод down()
- **Безопасность**: Используйте IF NOT EXISTS при создании
- **Индексы**: Добавляйте индексы для полей в WHERE и JOIN
- **Кодировка**: UTF-8, collation utf8mb4_general_ci

## Кастомные типы полей

Проект lk.tpprf.ru использует кастомные типы полей:

### iblock_organization
Ссылка на организацию (инфоблок организаций)
```php
'USER_TYPE_ID' => 'iblock_organization',
'SETTINGS' => [
    'DISPLAY' => 'LIST',
    'LIST_HEIGHT' => 1,
    'IBLOCK_ID' => 145,
    'DEFAULT_VALUE' => '',
    'ACTIVE_FILTER' => 'N',
],
```

### iblock_element
Ссылка на элемент инфоблока (любой инфоблок)
```php
'USER_TYPE_ID' => 'iblock_element',
'SETTINGS' => [
    'DISPLAY' => 'LIST',
    'LIST_HEIGHT' => 1,
    'IBLOCK_ID' => 'module:iblockCode', // формат: module:iblockCode или числовой ID
    'DEFAULT_VALUE' => '',
    'ACTIVE_FILTER' => 'N',
],
```

### hlblock
Ссылка на другой HLBlock
```php
'USER_TYPE_ID' => 'hlblock',
'SETTINGS' => [
    'DISPLAY' => 'LIST',
    'LIST_HEIGHT' => 1,
    'HLBLOCK_ID' => 'HLBlockName', // имя HLBlock
    'HLFIELD_ID' => 0,
    'DEFAULT_VALUE' => 0,
],
```

## Примеры использования

Смотрите существующие миграции:
- `local/php_interface/migrations/DocflowHLApplications20241223130930.php`
- `local/php_interface/migrations/DocflowHLLog20241223130851.php`

## Типичные ошибки

1. Забывают реализовать метод down()
2. Не используют IF NOT EXISTS при создании
3. Не добавляют индексы для полей в WHERE
4. Не учитывают связи с другими таблицами
5. Забывают добавить права доступа

## Связанные скиллы

- bitrix-hlblock-create — создание HLBlock-таблиц
- performance-optimizer — оптимизация запросов
