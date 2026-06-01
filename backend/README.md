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
