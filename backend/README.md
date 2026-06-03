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
