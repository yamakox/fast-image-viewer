# REST API 仕様

既存フロント（[`../frontend`](../../frontend)）および Django 版 [`../backend/README.md`](../../backend/README.md) と互換の契約を維持する。

## 共通ルール

- ベースパス: `/api/v1`
- **末尾スラッシュなし**（例: `/api/v1/folders`、`/api/v1/images/1`）
- 認証なし（全匿名許可）
- CORS: `CORS_ALLOWED_ORIGINS` で許可したオリジンのみ
- JSON API の `Content-Type`: `application/json`
- admin / browsable API は実装しない
- `ordering` クエリ: DRF OrderingFilter 相当（カンマ区切り、`-` で降順）。許可フィールド外は `400`

## データフォルダー API

### 一覧取得

```http
GET /api/v1/folders HTTP/1.1
Accept: application/json
```

| クエリ | 説明 |
|---|---|
| rootonly | 1 文字以上あれば `parent IS NULL` |
| parent | 親フォルダ ID でフィルタ。存在しない親は `400` |
| ordering | 許可: `name`, `parent`。デフォルト `name` |

**200** — 配列（ページネーションなし）:

```json
[
  { "id": 4, "name": "E7系" },
  { "id": 2, "name": "W7系" }
]
```

### 詳細取得

```http
GET /api/v1/folders/<id> HTTP/1.1
Accept: application/json
```

**200**:

```json
{
  "id": 2,
  "name": "W7系",
  "pathname": "新幹線/W7系",
  "parent": 1
}
```

**404**: `{ "detail": "..." }`（文言は FastAPI 標準で可。フロントは主にステータスを見る）

## 画像データ API

### 一覧取得

```http
GET /api/v1/images HTTP/1.1
Accept: application/json
```

| クエリ | 説明 |
|---|---|
| rootonly | `parent IS NULL` |
| favoriteonly | `favorite IS NOT NULL` |
| parent | 親フォルダ ID。存在しない親は `400` |
| ordering | 許可: `name`, `parent`, `timestamp`, `favorite`。デフォルト `-timestamp` |
| page | ページ番号（1 始まり） |
| page_size | 1 ページ件数。未指定時は `PAGINATION_SIZE` |

**200**:

```json
{
  "count": 184,
  "page": 1,
  "num_pages": 37,
  "page_size": 5,
  "results": [
    {
      "id": 10,
      "name": "20251019-DSC02528.jpeg",
      "favorite": "2026-06-05T16:00:01+09:00"
    }
  ]
}
```

| 項目 | 説明 |
|---|---|
| count | 条件一致の総件数 |
| page | 現在ページ |
| num_pages | 総ページ数 |
| page_size | **実際に適用された 1 ページ件数**（Django 版のクラス属性固定バグは修正する） |
| results | `{ id, name, favorite }` の配列 |

### 詳細取得（メタ JSON）

```http
GET /api/v1/images/<id> HTTP/1.1
Accept: application/json
```

**200**:

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

### お気に入り更新

```http
PATCH /api/v1/images/<id> HTTP/1.1
Content-Type: application/json

{ "favorite": "<ISO8601>" | null }
```

- `favorite` は必須（`null` 可）
- **200**: `{ "id": <id>, "favorite": ... }`
- **404**: 画像が無い場合

### 原画像バイナリ

```http
GET /api/v1/images/<id>/image HTTP/1.1
Accept: image/*
```

- パス解決: 親あり → `{DATASET}/{parent.pathname}/{name}`、親なし → `{DATASET}/{name}`
- `Content-Type` は拡張子から決定（avif / gif / heic / jpg / jpeg / png / webp）
- **404**: DB レコード無し、またはファイル無し
- **500**: 未サポート形式 `{ "detail": "Unsupported image format: ..." }`

### サムネイルバイナリ

```http
GET /api/v1/images/<id>/thumbnail HTTP/1.1
Accept: image/*
```

- HDF5 `ThumbnailGroup` から JPEG を返す（常に `image/jpeg`）
- **404**: サムネ無し
- **500**: 読取例外時 `{ "id": <id>, "error": "..." }`

## エラーハンドリング方針

- フロントは非 200 でボディを厳密にパースしない想定があるため、ステータスコードの意味を Django 版と揃えることを優先する
- `parent` 不正は `400`、リソース無しは `404`
