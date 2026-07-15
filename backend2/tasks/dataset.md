# データセットスキャン・CLI の実装

仕様: [`../specs/dataset.md`](../specs/dataset.md)

依存: [`database.md`](./database.md) 完了後。API thumbnail と同時に使うため [`api.md`](./api.md) と並行可。

- [ ] `app/services/dataset.py` に `Hdf5File` を移植する
- [ ] `_to_rgb` / `_create_image_data` / `_scan_dataset_folder` / `_cleanup_database` / `scan_dataset` を SQLAlchemy セッション向けに移植する
- [ ] `cli/scan_dataset.py` に `main()` を実装し、`uv run scan_dataset` で実行できるようにする（`[project.scripts]` 経由）
- [ ] 既存またはサンプルデータセットでスキャンが完了し、DB・HDF5 が更新されることを確認する
