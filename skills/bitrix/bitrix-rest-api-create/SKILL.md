---
name: bitrix-rest-api-create
description: Создание REST API контроллера для Bitrix CMS с валидацией, обработкой ошибок и интеграцией с модулем. Использовать, когда пользователь просит создать REST API, создать endpoint, добавить API контроллер, настроить API в проекте lk.tpprf.ru или создать обработчик HTTP-запросов.
---

# Скилл: Создание REST API для Bitrix

## Назначение

Создание REST API контроллера для Bitrix CMS с валидацией, обработкой ошибок и интеграцией с модулем.

## Когда использовать

Когда пользователю нужно создать REST API endpoint в проекте lk.tpprf.ru.

## Шаги выполнения

### 1. Сбор параметров

Попросите пользователя предоставить:
- Название модуля (например: forumedia.docflow)
- Название контроллера (например: Application)
- Список методов (например: get, list, create, update, delete)
- Права доступа (например: read, write, admin)

### 2. Создание контроллера

Создайте файл в `local/modules/{module}/lib/controller/{ControllerName}.php`:

```php
<?php
namespace {ModuleNamespace}\Controller;

use Bitrix\Main\Engine\Controller;
use Bitrix\Main\Error;
use Bitrix\Main\Loader;
use Bitrix\Main\Localization\Loc;

Loader::includeModule('{module}');

class {ControllerName} extends Controller
{
    // Настройка прав доступа
    public function configureActions()
    {
        return [
            'get' => [
                'prefilters' => [
                    // Проверка CSRF для изменяющих операций
                    // new \Bitrix\Main\Engine\ActionFilter\HttpMethod(['POST']),
                    // new \Bitrix\Main\Engine\ActionFilter\Csrf(),
                ],
                'postfilters' => [],
            ],
            'list' => [
                'prefilters' => [],
            ],
            'create' => [
                'prefilters' => [
                    new \Bitrix\Main\Engine\ActionFilter\HttpMethod(['POST']),
                    new \Bitrix\Main\Engine\ActionFilter\Csrf(),
                ],
            ],
            'update' => [
                'prefilters' => [
                    new \Bitrix\Main\Engine\ActionFilter\HttpMethod(['POST']),
                    new \Bitrix\Main\Engine\ActionFilter\Csrf(),
                ],
            ],
            'delete' => [
                'prefilters' => [
                    new \Bitrix\Main\Engine\ActionFilter\HttpMethod(['POST']),
                    new \Bitrix\Main\Engine\ActionFilter\Csrf(),
                ],
            ],
        ];
    }

    // Параметры передаются через signedParameters
    public function listKeysSignedParameters()
    {
        return [
            'PARAM1',
            'PARAM2',
        ];
    }

    /**
     * Получить запись
     *
     * @param int $id
     * @return array
     */
    public function getAction($id)
    {
        global $USER;

        if (!$USER->IsAuthorized()) {
            $this->addError(new Error('Требуется авторизация', 401));
            return [];
        }

        // Проверка прав
        if (!$this->checkReadAccess()) {
            $this->addError(new Error('Недостаточно прав', 403));
            return [];
        }

        // Валидация
        if (empty($id)) {
            $this->addError(new Error('ID не указан', 400));
            return [];
        }

        // Получение данных
        $data = $this->getRecord($id);

        if (!$data) {
            $this->addError(new Error('Запись не найдена', 404));
            return [];
        }

        return [
            'success' => true,
            'data' => $data,
        ];
    }

    /**
     * Получить список записей
     *
     * @param array $filter
     * @param int $limit
     * @param int $offset
     * @return array
     */
    public function listAction(array $filter = [], $limit = 50, $offset = 0)
    {
        global $USER;

        if (!$USER->IsAuthorized()) {
            $this->addError(new Error('Требуется авторизация', 401));
            return [];
        }

        // Проверка прав
        if (!$this->checkReadAccess()) {
            $this->addError(new Error('Недостаточно прав', 403));
            return [];
        }

        // Получение списка
        $result = $this->getList($filter, $limit, $offset);

        return [
            'success' => true,
            'data' => $result['items'],
            'total' => $result['total'],
        ];
    }

    /**
     * Создать запись
     *
     * @param array $fields
     * @return array
     */
    public function createAction(array $fields)
    {
        global $USER;

        if (!$USER->IsAuthorized()) {
            $this->addError(new Error('Требуется авторизация', 401));
            return [];
        }

        // Проверка прав
        if (!$this->checkWriteAccess()) {
            $this->addError(new Error('Недостаточно прав', 403));
            return [];
        }

        // Валидация
        $validation = $this->validateFields($fields);
        if (!$validation['valid']) {
            foreach ($validation['errors'] as $error) {
                $this->addError(new Error($error, 400));
            }
            return [];
        }

        // Создание записи
        $id = $this->createRecord($fields);

        if (!$id) {
            $this->addError(new Error('Ошибка создания записи', 500));
            return [];
        }

        return [
            'success' => true,
            'data' => ['id' => $id],
        ];
    }

    /**
     * Обновить запись
     *
     * @param int $id
     * @param array $fields
     * @return array
     */
    public function updateAction($id, array $fields)
    {
        global $USER;

        if (!$USER->IsAuthorized()) {
            $this->addError(new Error('Требуется авторизация', 401));
            return [];
        }

        // Проверка прав
        if (!$this->checkWriteAccess()) {
            $this->addError(new Error('Недостаточно прав', 403));
            return [];
        }

        // Валидация
        if (empty($id)) {
            $this->addError(new Error('ID не указан', 400));
            return [];
        }

        // Обновление записи
        $result = $this->updateRecord($id, $fields);

        if (!$result) {
            $this->addError(new Error('Ошибка обновления записи', 500));
            return [];
        }

        return [
            'success' => true,
            'data' => [],
        ];
    }

    /**
     * Удалить запись
     *
     * @param int $id
     * @return array
     */
    public function deleteAction($id)
    {
        global $USER;

        if (!$USER->IsAuthorized()) {
            $this->addError(new Error('Требуется авторизация', 401));
            return [];
        }

        // Проверка прав
        if (!$this->checkDeleteAccess()) {
            $this->addError(new Error('Недостаточно прав', 403));
            return [];
        }

        // Валидация
        if (empty($id)) {
            $this->addError(new Error('ID не указан', 400));
            return [];
        }

        // Удаление записи
        $result = $this->deleteRecord($id);

        if (!$result) {
            $this->addError(new Error('Ошибка удаления записи', 500));
            return [];
        }

        return [
            'success' => true,
            'data' => [],
        ];
    }

    // ========== Вспомогательные методы ==========

    /**
     * Проверить права на чтение
     */
    private function checkReadAccess()
    {
        global $USER;

        // Администраторы имеют все права
        if ($USER->IsAdmin()) {
            return true;
        }

        // TODO: Добавить логику проверки прав
        return true;
    }

    /**
     * Проверить права на запись
     */
    private function checkWriteAccess()
    {
        global $USER;

        if ($USER->IsAdmin()) {
            return true;
        }

        // TODO: Добавить логику проверки прав
        return true;
    }

    /**
     * Проверить права на удаление
     */
    private function checkDeleteAccess()
    {
        return $this->checkWriteAccess();
    }

    /**
     * Валидировать поля
     */
    private function validateFields(array $fields)
    {
        $errors = [];

        // TODO: Добавить логику валидации

        return [
            'valid' => empty($errors),
            'errors' => $errors,
        ];
    }

    /**
     * Получить запись
     */
    private function getRecord($id)
    {
        // TODO: Реализовать получение записи через ORM
        return [];
    }

    /**
     * Получить список записей
     */
    private function getList(array $filter, $limit, $offset)
    {
        // TODO: Реализовать получение списка через ORM
        return [
            'items' => [],
            'total' => 0,
        ];
    }

    /**
     * Создать запись
     */
    private function createRecord(array $fields)
    {
        // TODO: Реализовать создание записи через ORM
        return 0;
    }

    /**
     * Обновить запись
     */
    private function updateRecord($id, array $fields)
    {
        // TODO: Реализовать обновление записи через ORM
        return false;
    }

    /**
     * Удалить запись
     */
    private function deleteRecord($id)
    {
        // TODO: Реализовать удаление записи через ORM
        return false;
    }
}
```

### 3. Тестирование

Проверьте:
- Контроллер создан
- Методы работают корректно
- Валидация работает
- Проверка прав работает
- Формат ответа соответствует спецификации

## Правила проекта

- **Namespace**: `{ModuleNamespace}\Controller`
- **Путь**: `local/modules/{module}/lib/controller/{ControllerName}.php`
- **Формат ответа**: `{ success: bool, data: [], errors: [] }`
- **CSRF**: Обязательно проверять CSRF для изменяющих операций
- **Права**: Проверять права доступа для каждого метода
- **Валидация**: Валидировать все входные данные

## Примеры использования

Смотрите существующие контроллеры:
- `local/modules/forumedia.docflow/lib/controller/Application.php`
- `local/modules/forumedia.organizations/lib/controller/Organization.php`

## Типичные ошибки

1. Забывают проверить CSRF для изменяющих операций
2. Не проверяют права доступа
3. Не валидируют входные данные
4. Не возвращают корректный формат ответа
5. Неправильно обрабатывают ошибки

## Связанные скиллы

- performance-optimizer — оптимизация запросов
- bitrix-hlblock-create — создание HLBlock-таблиц
