# プロジェクト構成・起動仕様

Django 実装の [`../backend`](../../backend) を、FastAPI + SQLAlchemy で [`backend2`](../) 配下に再実装する。フロントエンド（[`../frontend`](../../frontend)）が利用する REST API 契約を維持し、既存の SQLite / HDF5 データを再利用できるようにする。

## ゴール

- `backend2/` に単独で起動できる FastAPI バックエンドを実装する
- API パス・レスポンス形は既存フロントと互換にする（末尾スラッシュなしの `/api/v1/...`）
- `{FIV_APPDATA_FOLDER_PATH}/dataset.sqlite3` と `thumbnail.hdf5` をそのまま使える
- 本フェーズでは Docker / VS Code tasks / Django `backend/` の削除・切替は行わない

## 技術スタック

| 役割 | 採用 |
|------|------|
| Web | FastAPI + uvicorn |
| ORM | SQLAlchemy 2.0（`Mapped` / `mapped_column`） |
| スキーマ検証 | Pydantic v2 |
| マイグレーション | Alembic |
| CORS | `CORSMiddleware` |
| 画像 / HDF5 | pillow / imagehash / h5py / numpy |
| Python | `>=3.13` |

Django / DRF / django-filter / django-cors-headers / gunicorn / markdown は使用しない。

## パッケージ化と CLI

Django 版は `manage.py` をコマンド起点にしていたため `[project.scripts]` を使わなかった。FastAPI 版では `manage.py` が無く、プロジェクトを **パッケージとしてインストール** し、CLI を `[project.scripts]` で公開する。

`pyproject.toml` の要点:

```toml
[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0", "poetry-dynamic-versioning>=1.0.0,<2.0.0"]
build-backend = "poetry_dynamic_versioning.backend"

[project]
name = "fast-image-viewer"
dynamic = ["version"]
# ... dependencies 等（version は静的に書かない）

[project.scripts]
scan_dataset = "cli.scan_dataset:main"

[tool.poetry]
version = "0.0.0"  # プレースホルダ（実バージョンは Git から解決）

[tool.poetry.requires-plugins]
poetry-dynamic-versioning = { version = ">=1.0.0,<2.0.0", extras = ["plugin"] }

[tool.poetry-dynamic-versioning]
enable = true
vcs = "git"
style = "pep440"

[tool.uv]
package = true
```

- **build backend** は Poetry（`poetry-core`）を使い、`poetry-dynamic-versioning` をプラグインとして追加する（バージョンは Git タグ等から動的に決定）
- 依存の管理・実行はこれまでどおり `uv`（`uv sync` / `uv run`）
- `uv sync` でエントリポイントが入る（別途 `uv pip install .` は不要）
- 実行: `uv run scan_dataset`
- `cli/scan_dataset.py` に `main()` を定義する（`module:callable` 形式）

## ディレクトリ構成

```text
backend2/
  pyproject.toml
  .env.example
  README.md
  main.py                 # uvicorn エントリ
  env.py / log.py
  ruff.toml
  alembic.ini
  alembic/
  app/
    main.py               # FastAPI app・CORS・ルータ登録
    db.py
    models.py
    schemas.py
    deps.py
    pagination.py
    routers/
      folders.py
      images.py
    services/
      dataset.py
      paths.py
  cli/
    scan_dataset.py
  specs/
  tasks/
```

## 環境変数

`.env.example` をコピーして `.env` を作成する。Django 版と互換のキーを維持する（FastAPI で未使用の `ALLOWED_HOSTS` / `STATIC_ROOT` は省略可）。

| 環境変数名 | 説明 |
|---|---|
| DEBUG | `True` の場合デバッグ（uvicorn reload 等）。本番は `False` |
| HOST | `main.py` 用ホスト。任意 IP 待ち受けは `0.0.0.0` |
| PORT | 待受ポート（デフォルト `8000`） |
| WORKERS | uvicorn ワーカー数 |
| PAGINATION_SIZE | 画像一覧のデフォルト件数（デフォルト `100`） |
| CORS_ALLOWED_ORIGINS | フロントオリジン。`;` 区切り（例: `http://localhost:5173`） |
| FIV_APPDATA_FOLDER_PATH | SQLite / HDF5 の格納先 |
| FIV_DATASET_FOLDER_PATH | 原画像データセットのルート |
| FIV_THUMBNAIL_SIZE | 正方形サムネの辺長（デフォルト `96`） |
| FIV_THUMBNAIL_QUALITY | JPEG 画質（デフォルト `60`） |

## データ配置

| 実体 | パス |
|---|---|
| SQLite | `{FIV_APPDATA_FOLDER_PATH}/dataset.sqlite3` |
| サムネイル HDF5 | `{FIV_APPDATA_FOLDER_PATH}/thumbnail.hdf5`（グループ `ThumbnailGroup`） |
| 原画像 | `{FIV_DATASET_FOLDER_PATH}/...` |

## 起動手順

```bash
cd backend2
cp .env.example .env   # 既存 APPDATA/DATASET を指す
uv sync
uv run alembic upgrade head           # 新規 DB の場合
# 既存 Django DB の場合は: uv run alembic stamp head
uv run scan_dataset                   # 未スキャン時
uv run main.py
```

フロントの `VITE_API_BASE_URL`（例: `http://localhost:8000`）はそのまま利用可能。Django `backend` と同時起動する場合は一方を止めるかポートを分ける。

## スコープ外（本再実装ではやらない）

- Docker Compose / `app.Dockerfile` / `.vscode/tasks.json` の切替
- Django [`backend/`](../../backend) の削除
- 認証の追加
- 自動テストスイートの新規追加（手動作動確認を優先）
- フロントエンドの変更

## 関連仕様

- [`database.md`](./database.md) — テーブル・ORM
- [`api.md`](./api.md) — REST API 契約
- [`dataset.md`](./dataset.md) — スキャンとサムネイル
