---
name: bitrix-component-create
description: Создание нового компонента Bitrix с правильной структурой, используя современный подход на основе классов (class.php). Использовать, когда пользователь просит создать новый компонент, создать bitrix компонент или упоминает создание компонента.
---

# Создание компонента Bitrix (современный формат)

Когда пользователь просит создать новый компонент Bitrix:

## 1. Уточнение параметров

Спросите пользователя (если не указано):
- **Namespace компонента** (например, `aip_dev`, `custom`, `forumedia`)
- **Название компонента** (например, `my.component`, `news.list`)
- **Имя класса** (в PascalCase, например, `MyComponent`, `NewsList`)
- **Заголовок компонента** (человекочитаемое название на русском)
- **Описание компонента** (краткое описание функционала)
- **Группа компонента** (например, "AIP Components", "Custom Components")

## 2. Создание структуры

Создайте следующую структуру файлов в `local/components/{namespace}/{component.name}/`:

### Основные файлы:

#### `.description.php`
```php
<?php
if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();

$arComponentDescription = array(
    'NAME' => GetMessage('COMPONENT_NAME'),
    'DESCRIPTION' => GetMessage('COMPONENT_DESCRIPTION'),
    'ICON' => '/images/icon.gif',
    'PATH' => array(
        'ID' => '{namespace}',
        'NAME' => GetMessage('COMPONENT_GROUP'),
    )
);
```

#### `.parameters.php`
```php
<?php
if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();

$arComponentParameters = array(
    'GROUPS' => array(
    ),
    'PARAMETERS' => array(
        'CACHE_TIME' => array('DEFAULT' => 3600),
    ),
);
```

#### `class.php` (основной файл компонента)
```php
<?php

use Bitrix\Main\Localization\Loc;

if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();

Loc::loadMessages(__FILE__);

/**
 * Класс компонента {ComponentClassName}
 */
class {ComponentClassName}Component extends \CBitrixComponent
{
    /**
     * Проверка необходимых модулей
     * @return bool
     */
    protected function checkModules()
    {
        // Раскомментируйте если нужно
        // if (!CModule::IncludeModule('iblock'))
        // {
        //     ShowError(Loc::getMessage('MODULE_NOT_INSTALLED'));
        //     return false;
        // }

        return true;
    }

    /**
     * Обработка параметров компонента
     */
    protected function processParams()
    {
        // Обработка и нормализация параметров
        $this->arParams['CACHE_TIME'] = isset($this->arParams['CACHE_TIME'])
            ? (int)$this->arParams['CACHE_TIME']
            : 3600;
    }

    /**
     * Подготовка данных для вывода
     */
    protected function prepareResult()
    {
        // Основная логика компонента
        $this->arResult['ITEMS'] = array();
    }

    /**
     * Точка входа в компонент
     */
    public function executeComponent()
    {
        // Проверка модулей
        if (!$this->checkModules())
        {
            return;
        }

        // Обработка параметров
        $this->processParams();

        // Кэширование
        if ($this->startResultCache())
        {
            // Подготовка данных
            $this->prepareResult();

            // Подключение шаблона
            $this->includeComponentTemplate();
        }
    }
}
```

### Языковые файлы:

#### `lang/ru/.description.php`
```php
<?php
if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();

$MESS['COMPONENT_NAME'] = '{Заголовок компонента}';
$MESS['COMPONENT_DESCRIPTION'] = '{Описание компонента}';
$MESS['COMPONENT_GROUP'] = '{Группа компонента}';
```

#### `lang/ru/.parameters.php`
```php
<?php
if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();

$MESS['CACHE_TIME'] = 'Время кэширования (сек)';
```

#### `lang/ru/class.php`
```php
<?php
if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();

$MESS['MODULE_NOT_INSTALLED'] = 'Модуль не установлен';
```

### Шаблон по умолчанию:

#### `templates/.default/template.php`
```php
<?php
if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();

use Bitrix\Main\Localization\Loc;

/**
 * @var array $arParams
 * @var array $arResult
 * @global CMain $APPLICATION
 * @global CUser $USER
 * @global CDatabase $DB
 * @var CBitrixComponentTemplate $this
 * @var string $templateName
 * @var string $templateFile
 * @var string $templateFolder
 * @var string $componentPath
 * @var {ComponentClassName}Component $component
 */

$this->setFrameMode(true);
?>

<div class="{component-name}">
    <!-- Разметка компонента -->
</div>
```

#### `templates/.default/style.css`
```css
/* Стили компонента */
.{component-name} {
    /* ... */
}
```

#### `templates/.default/script.js`
```javascript
/**
 * JavaScript для компонента {component.name}
 */
(function() {
    'use strict';

    // Код компонента

})();
```

#### `templates/.default/lang/ru/template.php`
```php
<?php
if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();

// Языковые константы шаблона
```

### Функционал AJAX (если требуется):

Если компоненту нужна функциональность AJAX, используйте **action-методы** через интерфейсы `Controllerable` и `Errorable`.

#### `class.php` с поддержкой AJAX:
```php
<?php

use Bitrix\Main\Engine\Contract\Controllerable;
use Bitrix\Main\Errorable;
use Bitrix\Main\ErrorCollection;
use Bitrix\Main\Localization\Loc;

if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();

Loc::loadMessages(__FILE__);

/**
 * Класс компонента {ComponentClassName} с поддержкой AJAX
 */
class {ComponentClassName}Component extends \CBitrixComponent implements Controllerable, Errorable
{
    /** @var ErrorCollection */
    protected $errorCollection;

    /**
     * Конструктор
     */
    public function __construct($component = null)
    {
        parent::__construct($component);
        $this->errorCollection = new ErrorCollection();
    }

    /**
     * Получить коллекцию ошибок
     * @return ErrorCollection
     */
    public function getErrors()
    {
        return $this->errorCollection->toArray();
    }

    /**
     * Получить объект ErrorCollection
     * @return ErrorCollection
     */
    public function getErrorByCode($code)
    {
        return $this->errorCollection->getErrorByCode($code);
    }

    /**
     * Настройка доступных action-методов
     * @return array
     */
    public function configureActions()
    {
        return [
            'exampleAction' => [
                'prefilters' => [],
                'postfilters' => []
            ],
        ];
    }

    /**
     * Пример AJAX action-метода
     * @param string $param1
     * @param int $param2
     * @return array
     */
    public function exampleActionAction($param1, $param2 = 0)
    {
        // Обработка данных
        if (empty($param1))
        {
            $this->errorCollection->setError(
                new \Bitrix\Main\Error(Loc::getMessage('ERROR_EMPTY_PARAM'))
            );
            return null;
        }

        // Бизнес-логика
        $result = [
            'success' => true,
            'data' => [
                'param1' => $param1,
                'param2' => $param2,
            ],
        ];

        return $result;
    }

    // ... остальные методы (checkModules, processParams, prepareResult, executeComponent)
}
```

#### `templates/.default/template.php` с AJAX:
```php
<?php
if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();

use Bitrix\Main\Localization\Loc;

/**
 * @var array $arParams
 * @var array $arResult
 * @var {ComponentClassName}Component $component
 */

$this->setFrameMode(true);

$componentId = $arResult['COMPONENT_ID'];
$signedParameters = $arResult['SIGNED_PARAMETERS'];
?>

<div class="{component-name}" id="<?= $componentId ?>">
    <button id="ajax-button">Выполнить AJAX запрос</button>
    <div id="result"></div>
</div>

<script>
BX.ready(function() {
    var componentId = '<?= CUtil::JSEscape($componentId) ?>';
    var signedParameters = '<?= CUtil::JSEscape($signedParameters) ?>';

    BX.bind(BX('ajax-button'), 'click', function() {
        BX.ajax.runComponentAction(
            '{namespace}:{component.name}', // Название компонента
            'exampleAction', // Название action-метода (без суффикса Action)
            {
                mode: 'class',
                data: {
                    param1: 'test',
                    param2: 123
                },
                signedParameters: signedParameters
            }
        ).then(function(response) {
            if (response.status === 'success') {
                console.log('Успех:', response.data);
                BX('result').innerHTML = JSON.stringify(response.data);
            }
        }).catch(function(response) {
            console.error('Ошибка:', response.errors);
        });
    });
});
</script>
```

#### Правила для AJAX функциональности:

1. **Интерфейсы**:
   - `Controllerable` - для поддержки action-методов
   - `Errorable` - для обработки ошибок

2. **Метод configureActions()**:
   - Настраивает доступные action-методы
   - Определяет префильтры и постфильтры для каждого метода

3. **Action-методы**:
   - Название метода: `{actionName}Action()` (например, `exampleActionAction()`)
   - Вызов из JS: `BX.ajax.runComponentAction(..., 'exampleAction', ...)`
   - Возвращают массив с данными или null при ошибке

4. **Обработка ошибок**:
   - Используйте `ErrorCollection` для сбора ошибок
   - Методы `getErrors()` и `getErrorByCode()` из интерфейса `Errorable`

5. **Безопасность**:
   - Используйте подписанные параметры (`$this->getSignedParameters()`)
   - Передавайте `signedParameters` в AJAX запросе

6. **Вызов из JavaScript**:
   - Используйте `BX.ajax.runComponentAction()`
   - Указывайте `mode: 'class'`
   - Передавайте данные через `data: {...}`

## 3. Правила создания

- **Современный формат**: Используйте `class.php` вместо `component.php`
- **Класс компонента**: Наследуется от `\CBitrixComponent`, формат имени класса `{ComponentClassName}Component`
- **Метод executeComponent()**: Обязательная точка входа в компонент
- **Структура класса**: Разделяйте логику на методы (`checkModules()`, `processParams()`, `prepareResult()`)
- **Используйте use**: Импортируйте классы из пространств имён через `use` (например, `use Bitrix\Main\Localization\Loc;`)
- **Loc::loadMessages()**: Загружайте языковые файлы через `Loc::loadMessages(__FILE__)`
- **Проверки**: Все PHP файлы должны начинаться с `if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();`
- **Форматирование**: Используйте 4 пробела или таб для отступов
- **Заменители**: Замените `{namespace}`, `{component.name}`, `{ComponentClassName}`, `{Заголовок компонента}` на реальные значения
- **Локализация**: Создавайте только русскую локализацию, если не указано иное
- **Минимализм**: Не создавайте лишние файлы (images/, script.js, style.css и т.д. если не нужны). Добавляйте AJAX функционал только если явно запрошено

## 4. Преимущества class.php

- **OOP подход**: Чистая объектно-ориентированная архитектура
- **Переопределение методов**: Лёгкое расширение компонента через наследование
- **Инкапсуляция**: Логика изолирована в методах класса
- **Современный стандарт**: Рекомендуемый формат в документации Bitrix
- **Пространства имён**: Современная поддержка PHP (выражения use)

## 5. После создания

Сообщите пользователю:
- Путь к созданному компоненту: `local/components/{namespace}/{component.name}/`
- Структура созданных файлов
- Как включить компонент на странице:
  ```php
  <?$APPLICATION->IncludeComponent(
      "{namespace}:{component.name}",
      ".default",
      array(
          "CACHE_TIME" => 3600,
      )
  );?>
  ```

## 6. Заметки

- **AJAX функционал**: Всегда используйте action-методы через интерфейсы `Controllerable` и `Errorable`, не устаревший подход с `ajax.php`
- **Сложные компоненты**: Уточняйте детали с пользователем (нужен ли AJAX, дополнительные параметры, какие модули использовать)
- **Простые компоненты**: Создавайте минимальную базовую структуру с основными методами (без AJAX)
- **Расширяемость**: Можно добавлять дополнительные методы в класс компонента для разделения логики
- **Стандарты**: Следуйте PSR и стандартам кодирования Bitrix
- **Безопасность**: Всегда используйте подписанные параметры для AJAX запросов
- **Кэширование**: При использовании AJAX учитывайте, что данные могут быть кэшированы, используйте `$this->getSignedParameters()` вне блока кэша или отключите кэш для компонента
