# fast-image-viewer backend

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
