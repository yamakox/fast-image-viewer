# fast-image-viewer

サーバ内の画像データフォルダを閲覧するWebアプリケーションです。Dockerで動きます。

## 使い方

### 環境変数の準備とコンテナイメージのビルド

`.env.example`をコピーして`.env`を作り、設定値をカスタマイズしてください。

|環境変数名|値の説明|
|---|---|
|PROTOCOL|現状は`http`のみ指定可能|
|HOST|Webアプリを公開するホストのホスト名またはIPアドレス|
|PORT_WEB|Webアプリを公開するポート番号|
|PORT_API|WebアプリのAPIを公開するポート番号|
|DATASET_PATH|画像データを格納しているフォルダーのフルパス名|

`http://myserver.local:12345/`でWebアプリを公開する場合、以下のようになります。

```.env
PROTOCOL=http
HOST=myserver.local
PORT_WEB=12345
PORT_API=12346
DATASET_PATH=/path/to/dataset
```

以下のコマンドを実行して、コンテナイメージをビルドします。
`HOST`や`PORT_API`はコンテナイメージの中に格納されるため、これらの環境変数を変更したときはビルドをやり直します。

```bash
docker compose build
```

### 画像データのスキャン

すでにWebアプリケーションが起動している場合は、事前に[停止](#アプリの停止)しておいてください。

`docker-compose.yml`ファイルのあるフォルダーで以下のコマンドを実行してください。

```bash
docker compose run -i --rm app uv run manage.py migrate
docker compose run -i --rm app uv run manage.py scan_dataset
```

### アプリの起動

```bash
docker compose up -d
```

### アプリの停止

```bash
docker compose down
```

コンテナイメージや、Webアプリケーションで作成したデータベースやサムネイル画像を消去したい場合は、以下のコマンドを実行してください。

```bash
docker compose down --volumes --rmi all
```

### データベース・サムネイルの削除

アプリの停止後、以下のコマンドを実行してください。

```bash
docker volume rm fast-image-viewer_appdata
```

### ユーザーの作成

まず、管理者ユーザーを以下のコマンドで作成してください。

```bash
docker compose run -i --rm app uv run manage.py createsuperuser
```

`http://{HOST}:{PORT_API}/admin`で管理画面を開き、管理者ユーザーでログインして、ユーザーを作成してください。

## 各フォルダーの説明

詳細はそれぞれのREADME.mdを参照してください。

- `backend`の[README.md](./backend/README.md)
- `frontend`の[README.md](./frontend/README.md)
- `nginx`の[README.md](./nginx/README.md)
