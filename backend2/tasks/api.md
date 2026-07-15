# REST API の実装

仕様: [`../specs/api.md`](../specs/api.md)

依存: [`database.md`](./database.md) 完了後。バイナリ配信は [`dataset.md`](./dataset.md) の paths / HDF5 と合わせて完成させる。

## 共通

- [x] `app/schemas.py` に Folder / Image の Pydantic モデルを定義する
- [x] ordering / parent / rootonly / favoriteonly 用の共通クエリヘルパを実装する
- [x] `app/pagination.py` で画像一覧用ページネーション（count / page / num_pages / page_size / results）を実装する（`page_size` は適用済み件数を返す）

## Folders

- [x] `GET /api/v1/folders`（list: `{id,name}`、フィルタ・ordering）
- [x] `GET /api/v1/folders/{id}`（retrieve: `{id,name,pathname,parent}`）
- [x] 不正な `parent` で `400` を返す

## Images（JSON）

- [x] `GET /api/v1/images`（list + ページネーション + フィルタ・ordering）
- [x] `GET /api/v1/images/{id}`（メタ JSON）
- [x] `PATCH /api/v1/images/{id}`（`favorite` 更新、応答 `{id,favorite}`）

## Images（バイナリ）

- [x] `app/services/paths.py` で原画像パス解決と MIME 判定を実装する
- [x] `GET /api/v1/images/{id}/image` を実装する
- [x] `GET /api/v1/images/{id}/thumbnail` を実装する（HDF5 読取）

## 手動確認

- [x] `test.http` を配置し、folders / images / PATCH / image / thumbnail を確認する
