# fast-image-viewer frontend

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
