# ドキュメント・動作確認

仕様: [`../specs/project.md`](../specs/project.md)、[`../specs/api.md`](../specs/api.md)

依存: [`project.md`](./project.md)、[`database.md`](./database.md)、[`api.md`](./api.md)、[`dataset.md`](./dataset.md) の実装完了後

- [x] `README.md` に起動手順・環境変数・migrate / stamp / `uv run scan_dataset` / 起動を記載する
- [x] 既存 Django DB 利用時の `alembic stamp head` 手順を README に明記する
- [x] API 仕様の要約または `backend/README.md` への互換である旨を記載する
- [x] `.env` で既存 `FIV_APPDATA_FOLDER_PATH` / `FIV_DATASET_FOLDER_PATH` を指し、フロントから通し確認する手順を README に書く
- [ ] Django backend を止めた状態で frontend から folders / サムネ一覧 / 画像表示 / お気に入り PATCH を確認する
