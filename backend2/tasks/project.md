# プロジェクト骨格の実装

仕様: [`../specs/project.md`](../specs/project.md)

依存: なし（最初に実施する）

- [x] `pyproject.toml` を作成する（Python >=3.13、FastAPI / uvicorn / SQLAlchemy / Alembic / pydantic / pillow / imagehash / h5py / numpy / python-dotenv / python-dateutil、dev に ruff / debugpy）
- [x] `pyproject.toml` でパッケージ化する（build backend は `poetry_dynamic_versioning.backend`、`poetry-dynamic-versioning` プラグイン、`tool.uv.package = true`、`[project.scripts]` に `scan_dataset = "cli.scan_dataset:main"`）
- [x] `uv sync` で依存とエントリポイントをインストールできることを確認する
- [x] `env.py` を実装する（`.env` 読込と計画どおりの環境変数）
- [x] `.env.example` を作成する
- [x] `log.py` を実装する
- [x] `ruff.toml` を backend 相当で配置する
- [x] `app/main.py` で FastAPI アプリを生成し、`CORSMiddleware` を設定する
- [x] ルータ登録用のプレースホルダ（空の folders / images でも可）を用意する
- [x] `main.py` で uvicorn 起動できるようにする（`app.main:app`）
- [x] 起動してヘルスチェック相当（OpenAPI `/docs` が開く等）を確認する
