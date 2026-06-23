# ログイン・ログアウト機能の実装

仕様: [`specs/login.md`](../specs/login.md)

## バックエンド

- [x] `settings.py` に `SessionAuthentication`、CORS、CSRF の設定を追加する
- [x] `api/views.py` に `session` ビュー（`GET /api/v1/session`）を実装する
- [x] `api/views.py` に `login` ビュー（`authenticate` + `auth_login`）を実装する
- [x] `api/views.py` に `logout` ビュー（`auth_logout`）を実装する
- [x] 認証 API に `@permission_classes([AllowAny])` を指定する
- [x] `_get_session_user()` を `request.user.is_authenticated` ベースで実装する
- [x] `api/urls.py` に `session`, `login`, `logout` の URL を登録する
- [x] `Favorite.user` を `settings.AUTH_USER_MODEL`（`auth.User`）へ参照する
- [x] マイグレーションを作成・適用する

## フロントエンド

- [x] `LoginPage.vue` にログインフォームを実装する
- [x] `MainPage.vue` にログアウトボタンを実装する
- [x] `router/index.ts` に `/login` ルートを追加する
- [x] `util.ts` に `getSession`, `checkSession`, `postData`, `ensureCsrfCookie` を実装する
- [x] API 呼び出しに `credentials: 'include'` を設定する
- [x] POST リクエストに `X-CSRFToken` ヘッダーを付与する
- [x] `MainPage.vue` で未ログイン時に `/login` へリダイレクトする
- [x] サイドバーにログイン中のユーザー名を表示する
- [x] ログイン成功後・ログアウト成功後は `location.href` でフルリロード遷移する
- [x] Flowbite Drawer 併用時のアクセシビリティ対応（`aria-hidden` 除去、フォーカス移動）

## 動作確認

- [x] 管理画面で作成したユーザーでログインできる
- [x] 未ログインで `/` にアクセスすると `/login` へ遷移する
- [x] ログアウト後に `/login` へ遷移し、バックドロップが残らない
- [x] ログイン後にサイドバーのメニューボタンが動作する
