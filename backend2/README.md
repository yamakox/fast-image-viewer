# fast-image-viewer backend2

[FastAPI](https://fastapi.tiangolo.com/) と [SQLAlchemy](https://www.sqlalchemy.org/) によるバックエンド実装。Django 版（[`../backend`](../backend)）と REST API 契約・SQLite / HDF5 データ形式を互換にする。

## .env 設定

`.env.example` をコピーして `.env` を作成する。

| 環境変数名 | 説明 |
|---|---|
| DEBUG | `True` の場合デバッグモード（uvicorn reload 等）。本番は `False` |
| HOST | `main.py` 用ホスト。任意 IP 待ち受けは `0.0.0.0` |
| PORT | 待受ポート |
| WORKERS | uvicorn ワーカー数（DEBUG 時は 1） |
| PAGINATION_SIZE | 画像一覧のデフォルト件数 |
| CORS_ALLOWED_ORIGINS | フロントオリジン。`;` 区切り |
| FIV_APPDATA_FOLDER_PATH | SQLite / HDF5 の格納先 |
| FIV_DATASET_FOLDER_PATH | 原画像データセットのルート |
| FIV_THUMBNAIL_SIZE | 正方形サムネの辺長 |
| FIV_THUMBNAIL_QUALITY | JPEG 画質 |

## 使い方

```bash
cd backend2
cp .env.example .env   # 既存 APPDATA/DATASET を指す
uv sync
```

### データベースのマイグレーション

**新規 DB:**

```bash
uv run alembic upgrade head
```

**既存 Django DB**（`api_folder` / `api_image` 済み）はスキーマ変更せず履歴だけ揃える:

```bash
uv run alembic stamp head
```

### 画像データのスキャン

```bash
uv run scan_dataset
```

### バックエンドの起動

```bash
uv run main.py
```

フロントの `VITE_API_BASE_URL`（例: `http://localhost:8000`）はそのまま利用できる。Django `backend` と同時に動かないよう、片方を止めるかポートを分ける。

## REST API

パス・レスポンス形は Django 版と互換（末尾スラッシュなしの `/api/v1/...`）。詳細は [`specs/api.md`](./specs/api.md) および [`../backend/README.md`](../backend/README.md)。

画像一覧の `page_size` レスポンスは、適用済み件数を返す（Django 版のクラス属性固定は修正）。

## フロントからの通し確認

1. Django backend を停止する
2. 上記のとおり `.env` で既存 `FIV_APPDATA_FOLDER_PATH` / `FIV_DATASET_FOLDER_PATH` を指す
3. `uv run main.py` で起動
4. フロントから folders / サムネ一覧 / 画像表示 / お気に入り PATCH を確認する
