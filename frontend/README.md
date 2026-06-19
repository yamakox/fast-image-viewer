# fast-image-viewer frontend

Vite + Vueを使ってフロントエンドを実装している。

## 使い方

### nvmの準備

Googleで検索すると、最初に公式ではないサイトが表示されるので要注意。[https://github.com/nvm-sh/nvm](https://github.com/nvm-sh/nvm)が公式サイトである。

[インストールスクリプト](https://github.com/nvm-sh/nvm#installing-and-updating)を実行して`nvm`をインストールする。
`.nvmrc`を作成し、以下のコマンドを実行してnodeをインストールする。

```bash
nvm install
```

次回以降は、`.nvmrc`のあるフォルダーに移動して以下のコマンドを実行すると、適切なバージョンのnodeが動作する。

```bash
nvm use
```

### プロジェクトの準備

`npm`を使って、依存関係パッケージをインストールする。

```bash
npm install
```

`.env.example`をコピーして`.env`ファイルを作成する。

### Viteの開発サーバによる実行

以下のコマンドを実行し、ブラウザで`http://localhost:5173`を開く。

```bash
npm run dev
```

### ビルド

`dist`フォルダーにビルド成果物が作成される。

```bash
npm run build
```

## 開発メモ

### viteでプロジェクトを作成

```bash
npm create vite@latest
```

- Project name: fast-image-viewer
- Select a framework: Vue
- Select a variant: TypeScript

```bash
mv fast-image-viewer/ frontend
```

[`.env`](https://ja.vite.dev/guide/env-and-mode)はAPIのBASE URL設定に使用する。

### プロジェクトのセットアップ

[レスポンシブデザイン](https://tailwindcss.com/docs/responsive-design)はTailwind CSSを使う。

```bash
cd frontend
npm i -D @tsconfig/node24 oxfmt oxlint
npm i tailwindcss @tailwindcss/vite
```

サイドバー用に[*Flowbite*](https://flowbite.com/docs/getting-started/vue/)をインストールする。
[アイコン](https://flowbite.com/icons/)もFlowbiteを使用している。

```bash
npm i flowbite
```

~~サブフォルダー表示用~~クエリーパラメータ取得用に[*Vue Router*](https://router.vuejs.org/guide/essentials/dynamic-matching.html)をインストールする。

```bash
npm i vue-router
```

画像ビューアの拡大・縮小用に[panzoom](https://github.com/anvaka/panzoom)をインストールする。

```bash
npm i panzoom
```
