# データベース・ORM の実装

仕様: [`../specs/database.md`](../specs/database.md)

依存: [`project.md`](./project.md) 完了後

- [ ] `app/db.py` を実装する（engine・Session・`get_db` Depends、SQLite パスは `FIV_APPDATA_FOLDER_PATH/dataset.sqlite3`）
- [ ] `app/models.py` に `Folder` / `Image`（テーブル名 `api_folder` / `api_image`）を定義する
- [ ] Image の `hash` 列を ORM 属性と JSON キーの両方で正しく扱えるようにする
- [ ] Alembic を初期化し、Django `0001_initial` 相当のマイグレーションを作成する
- [ ] 新規 DB で `alembic upgrade head` が通ることを確認する
- [ ] README に既存 Django DB 向け `alembic stamp head` の手順を書く（docs タスクでも可）
