# Code Patterns

Оригинальные компактные примеры для применения правил навыка. Перед копированием адаптируй namespace, module id, права и response shape под проект.

## Controller: защищенный write-action

```php
use Bitrix\Main\Engine\Controller;
use Bitrix\Main\Engine\ActionFilter;

final class ApplicationController extends Controller
{
    public function configureActions(): array
    {
        return [
            'saveStatus' => [
                'prefilters' => [
                    new ActionFilter\HttpMethod([ActionFilter\HttpMethod::METHOD_POST]),
                    new ActionFilter\Authentication(),
                    new ActionFilter\Csrf(),
                ],
            ],
        ];
    }

    public function saveStatusAction(int $id, string $status): array
    {
        if (!$this->canEditApplication($id)) {
            $this->addError(new \Bitrix\Main\Error('Недостаточно прав'));
            return [];
        }

        $result = $this->statusService()->change($id, $status);
        if (!$result->isSuccess()) {
            foreach ($result->getErrors() as $error) {
                $this->addError($error);
            }
            return [];
        }

        return ['id' => $id, 'status' => $status];
    }
}
```

Decision: write-action keeps method/auth/CSRF filters and delegates domain rules to service-level permission checks.

## Controller: read-only action with closed session

```php
use Bitrix\Main\Engine\ActionFilter;

public function configureActions(): array
{
    return [
        'search' => [
            '+prefilters' => [
                new ActionFilter\CloseSession(),
            ],
        ],
    ];
}

public function searchAction(string $query): array
{
    return [
        'items' => $this->repository()->findPublicItems($query),
    ];
}
```

Decision: close the session only when the action does not write to session state.

## ORM: DataManager skeleton

```php
namespace Vendor\Module\Internals;

use Bitrix\Main\ORM\Data\DataManager;
use Bitrix\Main\ORM\Fields;

final class DocumentTable extends DataManager
{
    public static function getTableName(): string
    {
        return 'vendor_document';
    }

    public static function getUfId(): string
    {
        return 'VENDOR_DOCUMENT';
    }

    public static function getMap(): array
    {
        return [
            (new Fields\IntegerField('ID'))
                ->configurePrimary()
                ->configureAutocomplete(),
            (new Fields\IntegerField('OWNER_ID'))
                ->configureRequired(),
            (new Fields\StringField('TITLE'))
                ->configureRequired(),
            new Fields\DatetimeField('CREATED_AT'),
        ];
    }
}
```

Decision: table shape lives in DataManager; physical table/index creation belongs to migration/install code.

## Batch preload instead of N+1

```php
$rows = ApplicationTable::getList([
    'select' => ['ID', 'TITLE', 'PROCESS_ID'],
    'filter' => ['=PROCESS_ID' => $processIds],
    'order' => ['ID' => 'DESC'],
    'limit' => 50,
])->fetchAll();

$applicationIds = array_column($rows, 'ID');
$tagsByApplication = [];

if ($applicationIds) {
    $tagRows = ApplicationTagTable::getList([
        'select' => ['APPLICATION_ID', 'TAG_ID', 'TAG_TITLE' => 'TAG.TITLE'],
        'filter' => ['=APPLICATION_ID' => $applicationIds],
    ])->fetchAll();

    foreach ($tagRows as $tagRow) {
        $tagsByApplication[(int)$tagRow['APPLICATION_ID']][] = [
            'id' => (int)$tagRow['TAG_ID'],
            'title' => $tagRow['TAG_TITLE'],
        ];
    }
}

foreach ($rows as &$row) {
    $row['TAGS'] = $tagsByApplication[(int)$row['ID']] ?? [];
}
unset($row);
```

Decision: root rows and relation rows are loaded in bounded batches; no query is executed inside the render loop.

## Avoid multiple relation Cartesian product

```php
$query = BookTable::query()
    ->setSelect(['ID', 'TITLE'])
    ->where('ACTIVE', true)
    ->setLimit(20);

$books = $query->fetchAll();
$bookIds = array_column($books, 'ID');

$authors = $bookIds ? BookAuthorTable::getByBookIds($bookIds) : [];
$categories = $bookIds ? BookCategoryTable::getByBookIds($bookIds) : [];
```

Decision: do not select `AUTHORS`, `CATEGORIES`, and other many-valued relations in one limited root query unless query decomposition is explicitly used and verified.

## Managed cache with invalidation path

```php
use Bitrix\Main\Application;

final class DictionaryRepository
{
    private const CACHE_TTL = 3600;
    private const CACHE_KEY = 'vendor_dictionary_active_v1';
    private const CACHE_TABLE = 'vendor_dictionary';

    public function getActive(): array
    {
        $cache = Application::getInstance()->getManagedCache();

        if ($cache->read(self::CACHE_TTL, self::CACHE_KEY, self::CACHE_TABLE)) {
            return $cache->get(self::CACHE_KEY);
        }

        $items = DictionaryTable::getList([
            'select' => ['ID', 'TITLE', 'CODE'],
            'filter' => ['=ACTIVE' => 'Y'],
            'order' => ['SORT' => 'ASC'],
        ])->fetchAll();

        $cache->set(self::CACHE_KEY, $items);

        return $items;
    }

    public function clearCache(): void
    {
        DictionaryTable::cleanCache();
    }
}
```

Decision: read path and write invalidation path are designed together.

## Safe raw SQL

```php
use Bitrix\Main\Application;
use Bitrix\Main\DB\SqlExpression;

$connection = Application::getConnection();
$helper = $connection->getSqlHelper();

$table = $helper->quote('vendor_log');
$event = new SqlExpression('?', $eventName);
$payload = new SqlExpression('?', $jsonPayload);

$connection->queryExecute(
    "INSERT INTO {$table} (EVENT_NAME, PAYLOAD, CREATED_AT) VALUES ({$event}, {$payload}, NOW())"
);
```

Decision: raw SQL is isolated; identifiers and values are not concatenated directly from untrusted data.

## JS extension load

```php
\Bitrix\Main\UI\Extension::load([
    'fm.docflow.application-list',
    'main.core',
]);
```

```js
import {Runtime} from 'main.core';

export function openHeavyEditor(options)
{
    return Runtime.loadExtension('fm.docflow.editor').then(({Editor}) => {
        return new Editor(options).open();
    });
}
```

Decision: common UI loads upfront; heavy editor code loads only when the user opens it.
