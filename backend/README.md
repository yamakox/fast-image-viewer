# fast-image-viewer backend

[Django](https://www.djangoproject.com/)と[Django REST framework](https://www.django-rest-framework.org/)を使ってバックエンドのREST APIを実装している。

## REST API仕様

`Accept`ヘッダーで取得したいコンテンツ型のMIMEタイプを指定できる。詳細は、[Django REST framework](https://www.django-rest-framework.org/)の[Content negotiation](https://www.django-rest-framework.org/api-guide/content-negotiation/)を参照。

Webブラウザ(Google ChromeとSafari)からAPIにアクセスすると、HTML形式のデータが返される。(`Accept`ヘッダーの先頭に`text/html`がいるため)

### データフォルダーAPI

#### データフォルダーの一覧取得

```http
GET /api/v1/folders HTTP/1.1
Accept: application/json

```

|クエリーパラメータ名|値|説明|
|---|---|---|
|rootonly|`yes`など、1文字以上の任意の文字列|親フォルダーの無い最上位階層のフォルダー一覧を取得する|
|parent|親フォルダーのID|指定された親フォルダー配下のフォルダー一覧を取得する|

`/api/v1/folders?parent=1`の応答例:

```json
[
  {
    "id": 4,
    "name": "E7系"
  },
  {
    "id": 2,
    "name": "W7系"
  }
]
```

#### データフォルダーの詳細情報の取得

```http
GET /api/v1/folders/<int:id> HTTP/1.1
Accept: application/json

```

`/api/v1/folders/2`の応答例:

```json
{
  "id": 2,
  "name": "W7系",
  "pathname": "新幹線/W7系",
  "parent": 1
}
```

### 画像データAPI

#### 画像データの一覧取得

```http
GET /api/v1/images HTTP/1.1
Accept: application/json

```

|クエリーパラメータ名|値|説明|
|---|---|---|
|rootonly|`yes`など|親フォルダーの無い最上位階層の画像データ一覧を取得する|
|favoriteonly|`yes`など|お気に入りとして登録されている画像データ一覧を取得する|
|parent|親フォルダーのID|指定された親フォルダー配下の画像データ一覧を取得する|
|ordering|`-favorite`, `favorite,name` など|フィールドの値で並べ替えを行う。降順(`-`で始まるフィールド名)の場合、`NULL`値は後ろ側に並ぶ。詳細は[DRFのOrderingFilter](https://www.django-rest-framework.org/api-guide/filtering/#orderingfilter)を参照。|
|page_size|1ページに表示する件数|ページネーションにおいて、1ページあたりの表示件数を指定できる。デフォルトは`.env`の`PAGINATION_SIZE`。|

`/api/v1/images?rootonly=yes&ordering=-favorite,-timestamp&page_size=5`の応答例:

```json
{
  "count": 184,
  "page": 1,
  "num_pages": 37,
  "page_size": 100,
  "results": [
    {
      "id": 10,
      "name": "20251019-DSC02528.jpeg",
      "favorite": "2026-06-05T16:00:01+09:00"
    },
    {
      "id": 21,
      "name": "20251206-DSC03670.jpeg",
      "favorite": "2026-06-05T16:00:00+09:00"
    },
    {
      "id": 11,
      "name": "20251019-DSC02800.jpeg",
      "favorite": "2026-06-05T16:00:00+09:00"
    },
    {
      "id": 20,
      "name": "20251219-DSC03771.jpeg",
      "favorite": "2026-06-05T15:00:01+09:00"
    },
    {
      "id": 583,
      "name": "20251219-DSC04081.jpeg",
      "favorite": null
    }
  ]
}
```

#### 画像データの詳細情報の取得

```http
GET /api/v1/images/<int:id> HTTP/1.1
Accept: application/json

```

`/api/v1/images/11`の応答例:

```json
{
  "id": 11,
  "name": "20251019-DSC02800.jpeg",
  "parent": null,
  "hash": "000000047fffffff",
  "timestamp": "2026-06-01T11:28:14.505976+09:00",
  "favorite": "2026-06-05T16:00:00+09:00"
}
```

#### 画像データの取得

```http
GET /api/v1/images/<int:id> HTTP/1.1
Accept: image/*

```

#### サムネイル画像データの取得

```http
GET /api/v1/images/<int:id>/thumbnail HTTP/1.1
Accept: image/*

```

## 開発メモ

### uvでプロジェクトを作成

```bash
uv init --python 3.13 fast-image-viewer
mv fast-image-viewer/ backend
```

### Djangoプロジェクトを作成

```bash
cd backend
uv add --dev debugpy ruff
uv add django uvicorn gunicorn python-dotenv
uv add h5py numpy pillow python-dateutil

uv run django-admin startproject fast_image_viewer .
uv run manage.py startapp api

# 動作確認: ブラウザで http://127.0.0.1:8000/ を開く
uv run manage.py runserver
```

### CORS対応

以下の[パッケージ](https://pypi.org/project/django-cors-headers/)を追加して、`fast_image_viewer/settings.py`にCORS設定を追加する。

```bash
uv add django-cors-headers
```

### Django REST frameworkを追加

以下の[パッケージ](https://www.django-rest-framework.org/)を追加して、`fast_image_viewer/settings.py`に設定を追加する。

```bash
uv add djangorestframework markdown django-filter
```

### モデルを作成

`api/models.py`にモデルを作成し、以下のコマンドを実行すると、`api/migrations/0001_initial.py`が生成される。

```bash
uv run manage.py makemigrations api
```

`id`列は自動的に作成されている。

```api/migrations/0001_initial.py
('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
```

DBにモデルのテーブルを作成する。

```bash
uv run manage.py migrate
```

モデルを変更するたび、`makemigrations`と`migrate`を実行する。

### データセットフォルダーをスキャンする

[コマンド](https://docs.djangoproject.com/ja/6.0/howto/custom-management-commands/)は`api/management/commands/scan_dataset.py`で実装している。

```bash
uv run manage.py scan_dataset
```

### REST APIを作成

`fast_image_viewer/settings.py`に[`django-filter`](https://www.django-rest-framework.org/api-guide/filtering/#djangofilterbackend)の設定を追加する。([Django REST frameworkを追加](#django-rest-frameworkを追加)したときの設定忘れ)

[Django REST frameworkを使って](https://www.django-rest-framework.org/tutorial/quickstart/)SerializersとViewSetsを実装して、routerにViewSetsを登録する。

### 静的ファイル(staticfiles)を配置・公開する

Django REST frameworkの`/api-auth`にアクセスすると、JavaScriptやCSSなどが404 Not Foundになってしまう。

対処方法は、開発時とデプロイ時で異なる。詳細は、Djangoの[静的ファイルの管理ドキュメント](https://docs.djangoproject.com/ja/6.0/howto/static-files/)を参照。

- 開発時の静的ファイルの公開
  
  [静的ファイル開発ビュー](https://docs.djangoproject.com/ja/6.0/ref/contrib/staticfiles/#django.contrib.staticfiles.views.serve)を使って、プロジェクトの`urls.py`の`urlpatterns`に`STATIC_URL`のURLパターンを追加する。

```fast_image_viewer/urls.py
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# settings.DEBUGがTrueの場合、'^static/(?P<path>.*)$'のURLパターンが追加される
urlpatterns += staticfiles_urlpatterns()
```

- デプロイ時の静的ファイルの配置と公開
  
  デプロイ時は`STATIC_ROOT`で静的ファイルの保存先フォルダーを設定して、以下のコマンドを実行して静的ファイルを収集する。
  
  `STATIC_ROOT`は、nginxなどのWebサーバを使って`STATIC_URL`のパスで公開する。

```bash
uv run manage.py collectstatic
```

### ページネーションを実装

`fast_image_viewer/settings.py`の`REST_FRAMEWORK`に[ページネーションの設定](https://www.django-rest-framework.org/api-guide/pagination/)を追加すると`Folder`にもページネーションの設定が加わってしまうので、[`Image`専用のページネーションクラス](https://www.django-rest-framework.org/api-guide/pagination/#custom-pagination-styles)を追加した。([参考](https://memory-lovers.blog/entry/2021/02/02/153345))
