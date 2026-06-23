# AI Agent Instructions

## 1. 概要

本プロジェクトで開発する `fast-image-viewer` は、サーバ内のデータフォルダー内の画像データセットをサムネイルで一覧表示して、タップ・クリックするとその画像を表示する Web アプリケーションである。

フロントエンドは **Vue SPA**、バックエンドは **Django + Django REST framework** で構成される。

AI Agent は、自律的なリファクタラーではなく、**慎重なペアプログラマー**として機能する。

---

## 2. 技術スタック

### プラットフォーム

[nvm](https://github.com/nvm-sh/nvm) を使って Node.js のバージョンを管理する。[`frontend/.nvmrc`](https://github.com/nvm-sh/nvm#nvmrc) の設定に従う。

Python パッケージ管理には [uv](https://docs.astral.sh/uv/) を使う（`backend/`）。

### フロントエンド（`frontend/`）

- Vite + Vue 3
- Vue Router
- Tailwind CSS
  - Flowbite: Navbar と Sidebar を使う

### バックエンド（`backend/`）

- Django
- Django REST framework
- django-cors-headers
- django-filter
- SQLite（アプリデータ）

---

## 3. 想定するプロジェクト構造

```text
.
├─ AGENTS.md
├─ specs/                      # 仕様を記述したファイル (*.md)
├─ tasks/                      # AI Agent のタスクを記述したファイル (*.md)
├─ backend/
│  ├─ api/                     # Django アプリ（モデル、ビュー、シリアライザ）
│  ├─ fast_image_viewer/       # Django プロジェクト設定
│  └─ README.md                # バックエンド API 仕様
├─ frontend/
│  ├─ src/
│  │  ├─ components/           # Vue コンポーネント
│  │  ├─ pages/                # ページコンポーネント
│  │  ├─ router/               # Vue Router 定義
│  │  ├─ util.ts               # API 呼び出しユーティリティ
│  │  ├─ App.vue
│  │  ├─ main.ts
│  │  └─ style.css
│  └─ README.md
└─ README.md
```

### 仕様書（`./specs/*.md`）の書き方

仕様書には、システムが備える機能の説明を記述する。仕様書は Plan モードのチャットで作成され、実装タスクの前に完成する。

#### ファイル命名規則

- 仕様書ファイルは機能ごとに分割する（例: `login.md`, `frontend.md`）
- ファイル名は機能名を表すスネークケースまたはケバブケースを使用する

#### 記述内容

仕様書には以下の内容を含める:

- 機能の概要と技術スタック
- 画面遷移図（フロントエンド機能の場合）
- REST API のエンドポイント（バックエンド機能の場合）
- リクエスト/レスポンス形式
- エラーハンドリングの仕様
- 動作確認手順

### タスク（`./tasks/*.md`）の書き方

タスクはチェックボックス付きの箇条書きで記述する。

#### ファイル命名規則

- タスクファイルは機能ごとに分割する（例: `login.md`, `frontend.md`）
- ファイル名は対応する仕様書ファイル名と一致させることを推奨する（例: `specs/login.md` ↔ `tasks/login.md`）

#### 記述ルール

- 未実施のタスクは、チェックボックスはオフになっている (`- [ ]`)
- AI Agent がタスクを実行したら、チェックボックスをオンにする (`- [x]`)
- タスクは実装可能な粒度に分割する
- タスクの順序は依存関係を考慮して記述する
- 完了済みタスクをやり直す場合は、チェックボックスを手動でオフに戻すことができる（例: `- [x]` → `- [ ]`）

### AI Agent の動作ルール

#### タスクの実行フロー

1. **仕様書の確認**: 実装前に、対応する仕様書ファイル（`./specs/*.md`）を確認する
2. **タスクの確認**: ユーザーが指定したタスクファイル（`./tasks/*.md`）を確認する
3. **実装**: 仕様書に基づいて実装を行う
4. **タスクの更新**: タスクを完了したら、該当するチェックボックスをオンにする

#### タスクの実行方法

- ユーザーは Agent チャットからファイル名を指定してタスクを実行する（例: `tasks/login.mdを実施して`）
- AI Agent は指定されたタスクファイルを読み込み、チェックボックスがオフになっているタスク（`- [ ]`）を順次実行する
- 各タスクの完了ごとに、タスクファイルのチェックボックスを更新する

#### 仕様書が存在しない場合

- 仕様書が存在しない場合は、実装前にユーザーに確認する
- 仕様書の作成を提案するか、実装を進めるか判断を仰ぐ

---

## 4. バックエンドのルール

- Python コードは `backend/` 配下に実装する
- REST API は Django REST framework で実装する
- 認証は `django.contrib.auth` と `SessionAuthentication` を使う（詳細は [`specs/login.md`](./specs/login.md)）
- ユーザー登録は Django 管理画面で行い、自前の User モデルや登録 API は作らない
- HTTP ステータス定数は `from rest_framework import status` の `status.HTTP_*` を使う
- リンターには [ruff](https://docs.astral.sh/ruff/) を使う（`uv run ruff check`）
- マイグレーション: `uv run manage.py makemigrations` → `uv run manage.py migrate`
- API の詳細仕様は [`backend/README.md`](./backend/README.md) も参照する

---

## 5. フロントエンドのルール

- ページやコンポーネントは **Vue** で実装する
- Vue では、以下のルールに則る
  - Vue 3 Composition API を使う
  - Options API は使わない
  - `<script setup lang="ts">` で実装する
- コンポーネントは小さく、機能にフォーカスするように維持する
- UI デザインは **Tailwind CSS** を使い、シンプルな外見にする
- API 呼び出しは `src/util.ts` の共通関数を使う
- セッション Cookie を使う API 呼び出しには `credentials: 'include'` を設定する
- POST/PATCH には CSRF トークン（`X-CSRFToken` ヘッダー）を付与する

---

## 6. API 設計のルール

- REST API のベースパスは `/api/v1`
- URL 末尾のスラッシュは付けない（`trailing_slash=False`）
- 認証 API: `session`, `login`, `logout`（仕様は [`specs/login.md`](./specs/login.md)）
- フロントエンドとバックエンドは別オリジンで動作する（開発時: `localhost:5173` ↔ `localhost:8000`）
- 詳細な API 仕様は [`backend/README.md`](./backend/README.md) に記載する

---

## 7. 認証とセキュリティ

### 認証方式

- Django 標準認証（`django.contrib.auth`）+ セッション Cookie
- DRF の `SessionAuthentication`
- フロントエンドからのクロスオリジンリクエストには `CORS_ALLOW_CREDENTIALS` と `CSRF_TRUSTED_ORIGINS` を設定する

### 環境変数

- バックエンド: `backend/.env`（`backend/.env.example` をコピー）
- フロントエンド: `frontend/.env`（`frontend/.env.example` をコピー）
- 開発環境と本番環境で異なる値を設定できるようにする

---

## 8. コーディングスタイルと原則

### 全般

- 賢さよりも明快さを好む
- 最小限だが読みやすいコード
- 時期尚早な最適化を避ける
- リンターの検出した問題点は適切に修正する

### Python

- 型ヒントを適宜使う
- 既存の `views.py` のスタイル（ヘルパー関数、ViewSet）に合わせる

### TypeScript

- `strict` フレンドリなコード
- `any` は可能な限り避ける
- API バウンダリには明確な型が望ましい

---

## 9. AI はどのように働くべきか

- 大きなデザイン変更の前に尋ねる
- 複雑なコードを書く前に意図を説明する
- 差分を小さくして確認できるようにする
- 無断で依存関係を導入しない

---

## 10. 禁止事項

- 明示的な承認なしに大規模なリファクタリング
- カスタム User モデルや自前パスワードハッシュの導入
- 仕様書に無い API エンドポイントの追加

---

## 11. テストの方針

- テストは可能な限り実装するが、時期尚早なテストは避ける
- 統合テスト: バックエンドとの連携をテストする
- テストフレームワークは軽量なものを使用する（例: Vitest）

---

## 12. コミュニケーションスタイル

- 日本語を使う
- 決定を簡潔に説明する
- 回答を次のように構成する:
  - 結論
  - 理由
  - コード（必要な場合）
