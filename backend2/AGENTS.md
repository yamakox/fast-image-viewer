# AI Agent Instructions

## 1. 概要

本ディレクトリ（`backend2`）では、既存の Django 実装（[`../backend`](../backend)）を **FastAPI + SQLAlchemy** で再実装する。

ゴールは、フロントエンド（[`../frontend`](../frontend)）が利用する REST API 契約を維持しつつ、単独で起動できるバックエンドを `backend2/` に完成させることである。既存の SQLite（`api_folder` / `api_image`）と `thumbnail.hdf5` を再利用できるようにする。

AI Agent は、自律的なリファクタラーではなく、**慎重なペアプログラマー**として機能する。

---

## 2. 技術スタック

### プラットフォーム

- Python `>=3.13`
- パッケージ管理・実行は [uv](https://github.com/astral-sh/uv) を使う

```bash
uv sync
uv run main.py
uv run alembic upgrade head
uv run scan_dataset
```

プロジェクトはパッケージ化し、CLI は `[project.scripts]` で公開する（Django 版の `manage.py` 相当）。詳細は [`specs/project.md`](./specs/project.md)。

### バックエンド（本ディレクトリの対象）

- FastAPI + uvicorn
- SQLAlchemy 2.0（`Mapped` / `mapped_column`）
- Pydantic v2
- Alembic
- CORS: FastAPI `CORSMiddleware`
- 画像 / HDF5: pillow / imagehash / h5py / numpy

### 使わないもの

- Django / Django REST framework / django-filter / django-cors-headers
- gunicorn / markdown（Django 版で使っていたが本実装では不要）
- 認証ミドルウェア・ユーザー管理

### フロントエンド・既存 Django backend

- [`../frontend`](../frontend) と [`../backend`](../backend) は **原則として変更しない**
- API 契約の変更が必要な場合は、実装前にユーザーに確認する
- Docker Compose / `app.Dockerfile` / `.vscode/tasks.json` の切替は、明示的に依頼されるまで行わない

---

## 3. 想定するプロジェクト構造

```text
.
├─ AGENTS.md
├─ pyproject.toml
├─ .env.example
├─ README.md
├─ main.py                 # uvicorn エントリ
├─ env.py / log.py
├─ ruff.toml
├─ alembic.ini
├─ alembic/
├─ app/
│  ├─ main.py              # FastAPI app・CORS・ルータ登録
│  ├─ db.py
│  ├─ models.py
│  ├─ schemas.py
│  ├─ deps.py
│  ├─ pagination.py
│  ├─ routers/
│  │  ├─ folders.py
│  │  └─ images.py
│  └─ services/
│     ├─ dataset.py
│     └─ paths.py
├─ cli/
│  └─ scan_dataset.py
├─ specs/                  # 仕様 (*.md)
└─ tasks/                  # AI Agent のタスク (*.md)
```

### 仕様書（`./specs/*.md`）の書き方

仕様書には、システムが備える機能の説明を記述する。仕様書は Plan モードのチャットで作成され、実装タスクの前に完成する。

#### ファイル命名規則

- 仕様書ファイルは機能ごとに分割する
- ファイル名は機能名を表すスネークケースまたはケバブケースを使用する

#### 現行の仕様書

| ファイル | 内容 |
|---|---|
| [`specs/project.md`](./specs/project.md) | ゴール・スタック・構成・env・起動・スコープ外 |
| [`specs/database.md`](./specs/database.md) | テーブル・ORM・Alembic・既存 DB 互換 |
| [`specs/api.md`](./specs/api.md) | REST API のパス・入出力・エラー |
| [`specs/dataset.md`](./specs/dataset.md) | スキャン・HDF5・パス/MIME |

仕様の追加・変更が必要な場合は、実装前に仕様書を更新してからタスクを進める。

### タスク（`./tasks/*.md`）の書き方

タスクはチェックボックス付きの箇条書きで記述する。

#### ファイル命名規則

- タスクファイルは機能ごとに分割する
- ファイル名は対応する仕様書ファイル名と一致させることを推奨する（例: `specs/api.md` ↔ `tasks/api.md`）
- 横断的な確認は `tasks/docs.md` のように別ファイルにしてよい

#### 記述ルール

- 未実施のタスクは、チェックボックスはオフになっている (`- [ ]`)
- AI Agent がタスクを実行したら、チェックボックスをオンにする (`- [x]`)
- タスクは実装可能な粒度に分割する
- タスクの順序は依存関係を考慮して記述する
- 完了済みタスクをやり直す場合は、チェックボックスを手動でオフに戻すことができる（例: `- [x]` → `- [ ]`）

#### 推奨実施順

1. [`tasks/project.md`](./tasks/project.md)
2. [`tasks/database.md`](./tasks/database.md)
3. [`tasks/api.md`](./tasks/api.md) と [`tasks/dataset.md`](./tasks/dataset.md)（並行可）
4. [`tasks/docs.md`](./tasks/docs.md)

#### タスクの例

```./tasks/database.md
# データベース・ORM の実装

- [x] app/db.py を実装する
- [ ] app/models.py に Folder / Image を定義する
- [ ] Alembic 初期リビジョンを作成する
```

### AI Agent の動作ルール

#### タスクの実行フロー

1. **仕様書の確認**: 実装前に、対応する仕様書ファイル（`./specs/*.md`）を確認する
2. **タスクの確認**: ユーザーが指定したタスクファイル（`./tasks/*.md`）を確認する
3. **実装**: 仕様書に基づいて実装を行う
4. **タスクの更新**: タスクを完了したら、該当するチェックボックスをオンにする

#### タスクの実行方法

- ユーザーは Agent チャットからファイル名を指定してタスクを実行する（例: `tasks/project.mdを実施して`）
- AI Agent は指定されたタスクファイルを読み込み、チェックボックスがオフになっているタスク（`- [ ]`）を順次実行する
  - 新規の未完了タスクだけでなく、ユーザーが手動でオフに戻した完了済みタスクも実行対象となる
- 各タスクの完了ごとに、タスクファイルのチェックボックスを更新する
- 複数のタスクファイルが指定された場合は、指定された順序で実行する

#### 仕様書が存在しない場合

- 仕様書が存在しない場合は、実装前にユーザーに確認する
- 仕様書の作成を提案するか、実装を進めるか判断を仰ぐ

---

## 4. バックエンドのルール

- プロジェクトをパッケージ化する（build backend は Poetry + `poetry-dynamic-versioning`、`tool.uv.package = true`）。CLI は `[project.scripts]` で公開する（例: `uv run scan_dataset`）
- パッケージバージョンは `poetry-dynamic-versioning` で Git から動的に決める（`project.version` は静的に書かない）
- FastAPI の APIRouter でエンドポイントを分割する（`folders` / `images`）
- 末尾スラッシュなしのパスにする（`/api/v1/folders` など）
- ORM は SQLAlchemy 2.0 スタイル（`select()` / `session.scalars()` など）を使う
- テーブル名は Django 互換のため `api_folder` / `api_image` に固定する
- 画像 list のレスポンス `page_size` は、**実際に適用された件数**を返す（Django 版のクラス属性固定は踏襲しない）
- スキャン意味（cleanup → 再帰 → 既存スキップ → サムネ生成）を勝手に変えない
- admin / browsable API は実装しない

---

## 5. フロントエンドのルール

本ディレクトリではフロントエンドは対象外のため、本章は省略する。フロントの変更が必要に見える場合は提案のみ行い、実装しない。

---

## 6. API 設計のルール

- 契約の正本は [`specs/api.md`](./specs/api.md) とする
- 既存フロント（`VITE_API_BASE_URL` + `/api/v1/...`）との互換を最優先する
- 認証なし・匿名フルアクセス（現状どおり）
- CORS は `CORS_ALLOWED_ORIGINS`（`;` 区切り）のみ許可する
- 破壊的なレスポンス形の変更は、仕様書更新とユーザー承認なしに行わない

参考: Django 版の詳細記述は [`../backend/README.md`](../backend/README.md)

---

## 7. 認証とセキュリティ

### 認証方式

本プロジェクトでは認証を使わないため、本章は省略する。

### 環境変数

- 環境変数は `.env` ファイルで定義する
  - `.env.example` ファイルも準備する
- 開発環境と本番環境で異なる値を設定できるようにする
- キー定義の正本は [`specs/project.md`](./specs/project.md)

---

## 8. コーディングスタイルと原則

### 全般

- 賢さよりも明快さを好む
- 最小限だが読みやすいコード
- 時期尚早な最適化を避ける
- リンター（ruff）の検出した問題点は適切に修正する

### Python

- 型ヒントを付ける（関数シグネチャ・公開 API）
- SQLAlchemy 2.0 / Pydantic v2 の書き方に揃える
- Django 版のロジックを移植するときは、挙動を変えず ORM / フレームワーク差分だけ置き換える

---

## 9. AI はどのように働くべきか

- 大きなデザイン変更の前に尋ねる
- 複雑なコードを書く前に意図を説明する
- 差分を小さくして確認できるようにする
- 無断で依存関係を導入しない
- 仕様とタスクにない機能追加（認証、テストフレームワーク一式、Docker 切替など）を勝手に始めない

---

## 10. 禁止事項

- Django 依存の再導入
- 明示的な承認なしに大規模なリファクタリング
- 明示的な承認なしの API 契約破壊
- 既存 `../backend` / `../frontend` / Docker 関連の無断変更・削除
- 既存 DB スキーマの無断変更（テーブル名・列の破壊的変更）

---

## 11. テストの方針

- テストは可能な限り実装するが、時期尚早なテストは避ける
- 当面は `test.http` とフロント通し確認を優先する
- 自動テストを追加する場合は軽量なものを使い、導入前にユーザーに確認する

---

## 12. コミュニケーションスタイル

- 日本語を使う
- 決定を簡潔に説明する
- 回答を次のように構成する:
  - 結論
  - 理由
  - コード (必要な場合)
