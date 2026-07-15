# データセットスキャン・サムネイル仕様

Django 版 [`backend/api/dataset.py`](../../backend/api/dataset.py) の挙動を SQLAlchemy セッション対応で移植する。スキャン意味（cleanup → 再帰スキャン → 既存スキップ → サムネ生成）は変更しない。

## HDF5（`thumbnail.hdf5`）

| 項目 | 値 |
|---|---|
| ファイルパス | `{FIV_APPDATA_FOLDER_PATH}/thumbnail.hdf5` |
| グループ名 | `ThumbnailGroup` |
| データセット名 | Image `id` の文字列 |
| 格納形式 | JPEG バイナリ（numpy 配列として作成） |

### `Hdf5File` 操作

| メソッド | 挙動 |
|---|---|
| `set_data(id, data)` | 同一 id が既にある場合は例外 |
| `get_data(id)` | 無い場合は例外 |
| `has_data(id)` | 存在確認 |
| コンテキストマネージャ | `__enter__` / `__exit__` で open/close |

スキャン時は mode `'a'`、API の thumbnail 読取時は mode `'r'`。

## スキャン処理 `scan_dataset`

CLI: `uv run scan_dataset`

Django 版は `manage.py` 起点だったが、FastAPI 版ではパッケージ化し `[project.scripts]` で CLI を公開する（詳細は [`project.md`](./project.md)）。

### 1. クリーンアップ `_cleanup_database`

ルートから再帰的に:

1. 子 Folder: ディスク上の `pathname` が無ければ DB 行を削除（CASCADE で子孫も対象になりうる）。存在すれば再帰
2. Image: `{parent_path}/{name}` が無ければ DB 行のみ削除

**注意**: HDF5 エントリは削除しない（del してもファイルサイズが減らないため。Django 版コメントと同じ方針）。

### 2. 再帰スキャン `_scan_dataset_folder`

`FIV_DATASET_FOLDER_PATH` 直下から:

- **ディレクトリ**: `pathname = relative_to(root)` で Folder を lookup。無ければ作成して再帰
- **ファイル**: ドット始まりは無視。それ以外は `_create_image_data`

### 3. 画像登録 `_create_image_data`

1. 同一 `(name, parent)` が既にあれば **スキップ（更新しない）**
2. Pillow で開き、中央正方形に crop
3. `FIV_THUMBNAIL_SIZE` に LANCZOS リサイズ
4. RGB 化して JPEG（`FIV_THUMBNAIL_QUALITY`）をバッファに保存
5. `imagehash.average_hash` で hash、mtime（ローカル TZ）で `timestamp`
6. Image 行を INSERT 後、HDF5 に JPEG を `set_data`

エラーはログに出し、スキャン全体は継続する。

## 原画像パス・MIME（`services/paths.py`）

API の `/image` 配信で使用する。

| 拡張子 | MIME |
|---|---|
| `.avif` | `image/avif` |
| `.gif` | `image/gif` |
| `.heic` | `image/heic` |
| `.jpg` / `.jpeg` | `image/jpeg` |
| `.png` | `image/png` |
| `.webp` | `image/webp` |

未対応拡張子は `/image` で HTTP 500（[`api.md`](./api.md) 参照）。
