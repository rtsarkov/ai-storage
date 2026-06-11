---
name: bitrix-vue-template-create
description: Создание Vue.js 3 SPA шаблона для существующего компонента Bitrix. Использовать, когда пользователь просит создать Vue шаблон, Vue SPA шаблон для компонента или упоминает создание фронтенда для Bitrix компонента с использованием Vue.
---

# Создание Vue.js 3 SPA шаблона для Bitrix компонента

Создание шаблона компонента Bitrix как одностраничного приложения Vue.js 3. Весь JS и CSS подключаются через `component_epilog.php`.

> **Важно**: Компонент (class.php) должен уже существовать и реализовать интерфейсы `Controllerable` и `Errorable`. Если компонента нет — предложите сначала использовать `/bitrix-component-create` с поддержкой AJAX.

## 1. Уточнение параметров

Спросите пользователя (если не указано):

- **Путь к компоненту** — например `local/components/forumedia/my.component/`
- **BX Namespace** — namespace JS-приложения (например `FM.MyModule.ComponentApp`)
- **Имя Vue приложения** — класс-обёртка (например `MyApp`)
- **Имя Vue компонента** — основной Vue компонент (например `MyAppComponent`)
- **ID расширения** — для `CJSCore::RegisterExt` (например `my_module_my_app`)

Если можно определить из контекста (название компонента, namespace) — определите автоматически и подтвердите с пользователем.

## 2. Создание структуры файлов

Создайте следующие файлы в `{component_path}/templates/.default/`:

### `template.php`

```php
<?php if (!defined("B_PROLOG_INCLUDED") || B_PROLOG_INCLUDED !== true) die(); ?>

<?php
$rootId = "{component-name}-" . rand(100, 1000);
$isAjax = $arParams['AJAX_CALL'] == 'Y';
$signedParameters = $this->getComponent()->getSignedParameters();
$componentName = $this->getComponent()->getName();
?>

<div class="<?= $isAjax ? 'p-3' : '' ?>" id="<?= $rootId ?>">
</div>

<script>
$(function() {
    var app = new BX.{BxNamespace}.{AppClassName}('#<?= $rootId; ?>', <?= CUtil::PhpToJSObject([
        'items' => $arResult['ITEMS'],
        'api' => [
            'controller' => $componentName,
            'signedParameters' => $signedParameters,
        ]
    ]) ?>);

    app.init();
});
</script>
```

**Ключевые моменты:**
- Случайный `rootId` — позволяет размещать несколько экземпляров на странице
- `signedParameters` — требуется для безопасных AJAX запросов
- Данные передаются из PHP в JS через `CUtil::PhpToJSObject()`
- Корневой `<div>` пустой — Vue монтируется в него

### `component_epilog.php`

```php
<?php
if (!defined("B_PROLOG_INCLUDED") || B_PROLOG_INCLUDED !== true) die();

\Bitrix\Main\UI\Extension::load("ui.vue3");
\Bitrix\Main\UI\Extension::load("ui.notification");

CJSCore::RegisterExt('{ext_id}', array(
    'skip_core' => true,
    'js' => $templateFolder . '/app.js',
    'css' => $templateFolder . '/style.css',
    'rel' => ['ui.vue3']
));

CJSCore::Init(array('{ext_id}'));
```

**Ключевые моменты:**
- `Extension::load("ui.vue3")` — загружает Vue 3 через Bitrix
- `Extension::load("ui.notification")` — система уведомлений (опционально)
- `CJSCore::RegisterExt` — регистрирует JS/CSS приложение как расширение
- `'rel' => ['ui.vue3']` — зависимость от Vue 3
- Добавляйте дополнительные расширения через `Extension::load()` по необходимости

### `app.js`

```javascript
(function () {
    BX.namespace('{BxNamespace}');

    /**
     * Класс для работы с контроллером компонента (AJAX запросы)
     */
    class Api {
        setController(controller) {
            this.controller = controller;
        }

        setSignedParameters(signedParameters) {
            this.signedParameters = signedParameters;
        }

        /**
         * Базовый метод запроса к контроллеру
         */
        request(action, data) {
            return BX.ajax.runComponentAction(this.controller, action, {
                signedParameters: this.signedParameters,
                data,
                mode: 'class',
                method: 'POST',
            });
        }

        // Добавьте методы для каждого action из class.php:
        // getData(params) {
        //     return this.request('getData', { params });
        // }
    }

    /**
     * Vue 3 компонент приложения
     */
    const {ComponentName} = {
        data() {
            return {
                loading: false,
                items: [],
            }
        },

        props: {
            initialItems: {
                type: Array,
                default: () => []
            }
        },

        created() {
            this.items = this.initialItems;
        },

        computed: {
            // Вычисляемые свойства
        },

        methods: {
            // Методы компонента
        },

        template: `
            <div ref="root">
                <div class="card">
                    <div class="card-header">
                        <span>Заголовок</span>
                    </div>
                    <div class="card-body">
                        <!-- Разметка приложения -->
                    </div>
                </div>
            </div>
        `
    };

    /**
     * Класс-обёртка Vue 3 приложения
     */
    class {AppClassName} {
        #application;

        constructor(rootNode, data) {
            this.rootNode = document.querySelector(rootNode);
            this.items = data.items || [];
            this.apiData = data.api;
        }

        init() {
            this.attachTemplate();
        }

        attachTemplate() {
            const context = this;

            this.#application = BX.Vue3.BitrixVue.createApp({
                data() {
                    return {
                        items: context.items,
                    }
                },
                name: '{AppClassName}',
                components: {
                    {ComponentName}
                },
                beforeCreate() {
                    this.$bitrix.Application.set(context);

                    const api = new Api();
                    api.setSignedParameters(context.apiData.signedParameters);
                    api.setController(context.apiData.controller);
                    this.$bitrix.Api = api;
                },

                template: `<{ComponentName}
                                ref="component"
                                :initial-items="items"
                            />`
            });

            this.#application.mount(this.rootNode);
        }

        detachTemplate() {
            if (this.#application) {
                this.#application.unmount();
            }
        }
    }

    BX.{BxNamespace}.{AppClassName} = {AppClassName};
}());
```

**Архитектура app.js (3 уровня):**

1. **Api** — класс для AJAX запросов к контроллеру компонента через `BX.ajax.runComponentAction`. Метод `request()` — базовый, остальные методы вызывают его для конкретных actions.

2. **{ComponentName}** — Vue 3 компонент с UI логикой. Содержит `data`, `props`, `computed`, `methods` и встроенный `template`. Доступ к Api через `this.$Bitrix.Api`.

3. **{AppClassName}** — класс-обёртка, создаёт Vue 3 приложение через `BX.Vue3.BitrixVue.createApp()`. Передаёт данные из PHP в Vue через props. Регистрирует Api в `this.$bitrix`.

### `style.css`

```css
/* Стили компонента {component-name} */
```

## 3. Правила создания

- **Подключение ресурсов**: Весь JS и CSS подключаются ТОЛЬКО через `component_epilog.php`, никогда напрямую в `template.php`
- **Передача данных**: PHP → JS через `CUtil::PhpToJSObject()` в `template.php`
- **AJAX**: Через класс `Api` и `BX.ajax.runComponentAction()` с `mode: 'class'`
- **Безопасность**: Всегда передавайте `signedParameters` в AJAX запросы
- **Vue шаблон**: Встроенный шаблон в свойстве `template` компонента (не отдельный .html файл)
- **Namespace**: Регистрируйте приложение в `BX.{BxNamespace}` через `BX.namespace()`
- **Минимализм**: Не создавайте лишние файлы. Всё приложение в одном `app.js`. При росте — выделяйте компоненты в отдельные файлы и подключайте через `CJSCore::RegisterExt`

## 4. Дополнительные расширения (если нужно)

Если пользователю нужны дополнительные возможности, добавьте в `component_epilog.php`:

```php
// Уведомления
\Bitrix\Main\UI\Extension::load("ui.notification");

// Диалоги
\Bitrix\Main\UI\Extension::load("ui.dialogs.messagebox");

// Иконки
\Bitrix\Main\UI\Extension::load("ui.icons");
```

## 5. После создания

Сообщите пользователю:
- Список созданных файлов
- Напомните, что `class.php` должен иметь интерфейсы `Controllerable` и `Errorable`
- Напомните добавить методы в класс `Api` для каждого action из `class.php`
- Напомните заполнить `$arResult` нужными данными в `class.php` и обновить передачу в `template.php`
