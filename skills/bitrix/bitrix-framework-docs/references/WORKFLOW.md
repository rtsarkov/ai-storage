# Workflow

## 1. Создать или проверить модуль

1. Уточни `MODULE_ID`, namespace и расположение в `/local/modules/<module.id>/`.
2. Проверь наличие `install/index.php`, `install/version.php`, `include.php`, `.settings.php`, `lang/ru/...`.
3. В `DoInstall()` регистрируй модуль, БД, файлы, события. В `DoUninstall()` делай обратные операции.
4. Не копируй бизнес-логику в установщик; установщик только регистрирует структуру и артефакты.
5. После установки проверь `Loader::includeModule()` и автозагрузку ключевых классов.

## 2. Добавить controller action

1. Найди существующий controller style в модуле.
2. Выбери transport: AJAX action, route controller, rendered component/view или file response.
3. Опиши входные параметры типами PHP и/или validation rules.
4. Настрой `configureActions()` только для отличий от default filters.
5. Для read-only длинных действий добавь `CloseSession`, если сессия не изменяется.
6. Для write-действий оставь CSRF и authentication; добавь проверку прав доменного уровня.
7. Верни стабильный response shape и проверь frontend-контракт.

## 3. Спроектировать ORM DataManager

1. Зафиксируй таблицу, primary key, обязательные поля, default values, enum/boolean storage.
2. Опиши `getMap()` через field-классы. Для runtime-связей используй `ReferenceField`, `OneToMany`, `ManyToMany` только когда они реально поддержаны локальной версией.
3. Если есть пользовательские поля, добавь `getUfId()`.
4. Для сложных custom fields проверь, где проект добавляет поля: в `getMap()` или через `getEntity()->addField()`.
5. Добавь индексы и миграцию отдельно от runtime-кода.

## 4. Сделать выборку без N+1

1. Сначала собери root IDs одной выборкой.
2. Для 1:N/N:M связей оцени риск `LIMIT` и декартова произведения.
3. Если связей несколько или они множественные, используй batch preload: один запрос по всем root IDs на каждую группу данных.
4. Разложи результат по статическому кешу или map `rootId => rows`.
5. В компонент/сервис возвращай уже собранную структуру, а не callback с запросом на каждый элемент.

## 5. Добавить кеш

1. Определи зависимость результата: параметры, site, user, права, язык, таблицы.
2. Выбери механизм: static cache в рамках запроса, unmanaged cache с TTL, managed cache, component cache.
3. Сформируй ключ из всех влияющих параметров.
4. Добавь инвалидацию в write-путь: после ORM update/delete/add, события сохранения или доменного сервиса.
5. Проверь сценарий изменения данных: пользователь должен увидеть свежие данные после ожидаемой точки инвалидации.

## 6. Использовать raw SQL безопасно

1. Сначала проверь, нельзя ли выразить задачу через ORM или Query.
2. Если нужен SQL, получи connection через `Application::getConnection()`.
3. Для identifiers используй `SqlHelper::quote()`, для значений `forSql()` или `SqlExpression` с placeholder-логикой.
4. Batch insert/update делай через helper-методы, если они доступны.
5. Для отладки включи SQL tracker или локальный лог, затем убери шумные логи из production-кода.

## 7. Добавить JS-расширение

1. Размести расширение в `/local/js/<module>/<extension>/`.
2. Проверь `src`, `dist`, `bundle.config.js`, `config.php`.
3. Импортируй CSS и JS-зависимости из entrypoint.
4. Загрузи расширение в PHP через `Extension::load()`.
5. Для lazy UI используй `Runtime.loadExtension()`.
6. Собери bundle и проверь, что `config.php` не потерял зависимости.
