# fast-image-viewer backend

[Django](https://www.djangoproject.com/)と[Django REST framework](https://www.django-rest-framework.org/)を使ってバックエンドのREST APIを実装している。

## .env設定

`.env.example`をコピーして`.env`を作成する。

|環境変数名|説明|
|---|---|
|DEBUG|`True`の場合デバッグモードで起動する。本番では`False`にする。|
|STATIC_ROOT|Djangoの静的ファイルの格納先フォルダーを指定する。詳細は[こちらの説明](#静的ファイルstaticfilesを配置公開する)を参照。|
|PAGINATION_SIZE|サムネイル画像一覧のページネーションにおいて、1ページあたりの画像数を指定する。|
|CORS_ALLOWED_ORIGINS|`http://localhost:5173`など、フロントエンドのオリジンを指定する。`;`で複数指定できる。|
|FIV_APPDATA_FOLDER_PATH|`db.sqlite3`や`thumbnail.hdf5`などのアプリデータの格納先フォルダーを指定する。|
|FIV_DATASET_FOLDER_PATH|画像データの格納先フォルダーを指定する。|
|FIV_THUMBNAIL_SIZE|正方形にクロップした画像の縮小サイズ(サムネイル画像のサイズ)を指定する。|
|FIV_THUMBNAIL_QUALITY|サムネイル画像をJPEGで保存するときの画質(〜100)を指定する。|

## 起動

```bash
uv run -m uvicorn --host=localhost --port=8000 fast_image_viewer.asgi:application
```

## REST API仕様

`Accept`ヘッダーで取得したいコンテンツ型のMIMEタイプを指定できる。詳細は、[Django REST framework](https://www.django-rest-framework.org/)の[Content negotiation](https://www.django-rest-framework.org/api-guide/content-negotiation/)を参照。

Webブラウザ(Google ChromeとSafari)からAPIにアクセスすると、HTML形式のデータが返される。(`Accept`ヘッダーの先頭に`text/html`がいるため)

Django REST frameworkで実装したREST APIは、原則として、`application/json`または`image/jpeg`などの画像タイプのデータを返す。

しかし、Djangoに登録しているURLパターンに一致しない(つまり本仕様に無い)URLパス名など、想定外のAPI呼び出しが行われた場合、`text/html`のHTMLデータでHTTPステータスコード`404`・`500`などを返す場合がある。`200`以外のHTTPステータスコードで返ってきた場合、ブラウザの開発者ツールでレスポンスのボディを閲覧すればよいので、フロントエンドではレスポンスのボディをハンドリングする必要はない。

### データフォルダーAPI

#### データフォルダーの一覧取得

##### リクエストの形式

```http
GET /api/v1/folders HTTP/1.1
Accept: application/json

```

|クエリーパラメータ名|値|説明|
|---|---|---|
|rootonly|`yes`など、1文字以上の任意の文字列|親フォルダーの無い最上位階層のフォルダー一覧を取得する|
|parent|親フォルダーのID|指定された親フォルダー配下のフォルダー一覧を取得する|
|ordering|`-name`, `parent,name` など|フィールドの値で並べ替えを行う。降順(`-`で始まるフィールド名)の場合、`NULL`値は後ろ側に並ぶ。詳細は[DRFのOrderingFilter](https://www.django-rest-framework.org/api-guide/filtering/#orderingfilter)を参照。|

##### レスポンスの形式

- HTTPステータスコード: `200`:
  
  `/api/v1/folders?parent=1`の応答例(クエリーパラメータが適切な場合)

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

- HTTPステータスコード: `400`:
  
  `/api/v1/folders?parent=99`の応答例(クエリーパラメータが不適切な場合)

```json
{
    "parent": [
        "正しく選択してください。選択したものは候補にありません。"
    ]
}
```

#### データフォルダーの詳細情報の取得

##### リクエストの形式

```http
GET /api/v1/folders/<int:id> HTTP/1.1
Accept: application/json

```

##### レスポンスの形式

- HTTPステータスコード: `200`:
  
  `/api/v1/folders/2`の応答例(idが適切な場合)

```json
{
  "id": 2,
  "name": "W7系",
  "pathname": "新幹線/W7系",
  "parent": 1
}
```

- HTTPステータスコード: `404`:
  
  `/api/v1/folders/99`の応答例(idが不適切な場合)

```json
{
    "detail": "No Folder matches the given query."
}
```

### 画像データAPI

#### 画像データの一覧取得

##### リクエストの形式

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

##### レスポンスの形式

- HTTPステータスコード: `200`:
  
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

|項目名|値の説明|
|---|---|
|count|クエリーパラメータに一致する画像データの総数。全ページの画像データの合計になる。|
|page|ページネーションのページ番号。|
|num_pages|ページネーションのページ総数。|
|page_size|1ページあたりの画像データの数。上記の例のように、クエリーパラメータの値ではなく、`.env`の`PAGINATION_SIZE`の値が返る。|
|results|クエリーパラメータに一致する画像データの配列。|

- HTTPステータスコード: `400`:
  
  `/api/v1/images?parent=99`の応答例:

```json
{
    "parent": [
        "正しく選択してください。選択したものは候補にありません。"
    ]
}
```

#### 画像データの詳細情報の取得

##### リクエストの形式

```http
GET /api/v1/images/<int:id> HTTP/1.1
Accept: application/json

```

##### レスポンスの形式

- HTTPステータスコード: `200`:
  
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

- HTTPステータスコード: `404`:
  
  `/api/v1/images/1000`の応答例(idが不適切な場合)

```json
{
    "detail": "No Image matches the given query."
}
```

#### お気に入りの設定

##### リクエストの形式

```http
PATCH /api/v1/images/<int:id> HTTP/1.1
Accept: application/json
Content-Type: application/json

{
    "favorite": <お気に入りに登録する日時文字列>|null
}
```

|項目名|値の説明|
|---|---|
|favorite|お気に入りから外す場合は`null`、お気に入りにする場合はISO8601形式の現在日時を指定する。|

##### レスポンスの形式

- HTTPステータスコード: `200`:
  
  `/api/v1/images/300`の応答例:

```json
{
  "id": 300,
  "favorite": "2026-06-08T10:00:00+09:00"
}
```

- HTTPステータスコード: `404`:
  
  `/api/v1/images/1000`の応答例(idが不適切な場合)

```json
{
  "detail": "Image data not found."
}
```

#### 画像データの取得

##### リクエストの形式

```http
GET /api/v1/images/<int:id>/image HTTP/1.1
Accept: image/*

```

##### レスポンスの形式

- HTTPステータスコード: `200`:
  
  `/api/v1/images/300/image`の応答例

```text
Content-Type: image/jpeg

...画像ファイルのバイナリデータ...
```

- HTTPステータスコード: `404`:
  
  `/api/v1/images/1000/image`の応答例(idが不適切な場合)

```json
{
  "detail": "Image data not found."
}
```

- HTTPステータスコード: `500`:
  
  `/api/v1/images/300/image`の応答例(画像ファイルが未サポート形式の場合)

```json
{
  "detail": "Unsupported image format: test.svg"
}
```

#### サムネイル画像データの取得

##### リクエストの形式

```http
GET /api/v1/images/<int:id>/thumbnail HTTP/1.1
Accept: image/*

```

##### レスポンスの形式

- HTTPステータスコード: `200`:
  
  `/api/v1/images/300/thumbnail`の応答例

```text
Content-Type: image/jpeg

...画像ファイルのバイナリデータ...
```

- HTTPステータスコード: `404`:
  
  `/api/v1/images/1000/image`の応答例(idが不適切な場合)

```json
{
  "detail": "Thumbnail image not found."
}
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

[Django REST frameworkを使って](https://www.django-rest-framework.org/tutorial/quickstart/)SerializersとViewSetsを実装して、router(`DefaultRouter`)にViewSetsを登録する。

デフォルトの`DefaultRouter`の場合、`PUT`や`PATCH`では、URL末尾の`/`を省略すると以下のエラーが発生する。

```text
RuntimeError: You called this URL via PUT, but the URL doesn't end in a slash and you have APPEND_SLASH set. Django can't redirect to the slash URL while maintaining PUT data.
```

しかし、`DefaultRouter`のパラメータに[`trailing_slash=False`](https://www.django-rest-framework.org/api-guide/routers/#defaultrouter)を与えると、末尾の`/`を省略したURLパターンになる。

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

### ~~PUT~~ PATCHを実装

本アプリは[認証](https://www.django-rest-framework.org/api-guide/authentication/)による[許可](https://www.django-rest-framework.org/api-guide/permissions/)は使用しないため、~~PUT~~ PATCH可能な`ModelViewSet`派生クラスには以下の行を追加している。

```api/views.py
from rest_framework.permissions import AllowAny

    permission_classes = [AllowAny]
```

一部のフィールドだけを更新する場合は、[`partial=True`](https://www.django-rest-framework.org/api-guide/serializers/#accessing-the-initial-data-and-instance)を指定してSerializerのインスタンスを作り、`ModelViewSet`の`partial_update`メソッドを実装して、`PATCH`メソッドでリクエストを受ける。

nullで更新できるようにするときは、Serializerクラス.Metaに[以下の属性](https://www.django-rest-framework.org/api-guide/fields/#allow_null)を追加する。`required`は`blank=True, null=True`のフィールドでは`False`となる。

```serializers.py
        extra_kwargs = {
            'favorite': {'allow_null': True, required=False}
        }
```

### 画像データを取得するためのルーティングを追加

[`ModelViewSet`派生クラス](https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset)はデフォルトで`list`や`retrieve`、`partial_update`などのアクションを提供するが、`@action`デコレータ付きのメソッドを実装してアクションを追加することができる。

`detail=True`で`pk`ありのURLパターンになり、`detail=False`で`pk`なしのURLパターンになる。`SimpleRouter`や`DefaultRouter`によって[URLパターンが決定する](https://www.django-rest-framework.org/api-guide/routers/#api-guide)。

```views.py
class ImageViewSet(viewsets.ModelViewSet):
    ...中略...

    @action(detail=True)
    def thumbnail(self, request, pk=None):
        ...サムネイル画像を返す処理...

    @action(detail=False):
    def favorites(self, request):
        ...お気に入り画像のリストを返す処理...
```

### `Image/*`形式データの応答

Django REST frameworkの[Custom renderers](https://www.django-rest-framework.org/api-guide/renderers/#custom-renderers)を使って、リクエストの`Accept`ヘッダーのコンテンツ型に応じたデータ(つまり画像データ)を返すことができる。

`ModelViewSet`派生クラスの`renderer_classes`にコンテンツ型に対応したrendererクラスのリストを設定する。(省略時はsettings.pyの`DEFAULT_RENDERER_CLASSES`に従う)

```views.py
    renderer_classes = [
        image_renderers.JPEGRenderer, 
        renderers.JSONRenderer, 
        renderers.BrowsableAPIRenderer
    ]
```

あるいは、~~[デコレータ](https://www.django-rest-framework.org/api-guide/renderers/#setting-the-renderers)を使ってrendererを設定する~~ [`@action`の`renderer_classes`パラメータ](https://www.django-rest-framework.org/tutorial/6-viewsets-and-routers/)を指定する。

```views.py
    @action(methods=['get'], detail=True, renderer_classes=[image_renderers.JPEGRenderer, ])
    def image(self, request, pk=None):
        ...以下略...
```

リクエストが`Accept: image/*`の場合、`image/jpeg`などのrendererクラスが登録されていないと`ModelViewSet`派生クラスは呼ばれずに`406 Not Acceptable`エラーが返る。

要求されたコンテンツ型のmedia typeは`request.accepted_media_type`で取得できる。

```views.py
    def retrieve(self, request, pk=None):
        logger.debug(f'retrieve: {pk=} {request=}')
        if request.accepted_media_type.startswith('image/'):
            return self.__retrieve_image(request, pk)
        return super().retrieve(request, pk)
```

### ruffによるチェックと整形

```bash
uv run ruff check
```

```bash
uv run ruff format
```
