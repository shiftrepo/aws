# 職員保守システム (Employee Management System)

## 📚 目次

- [プロジェクトについて](#プロジェクトについて)
- [何ができるの？](#何ができるの)
- [準備するもの](#準備するもの)
- [インストール方法](#インストール方法)
- [使い方](#使い方)
- [プロジェクト構成](#プロジェクト構成)
- [テスト方法](#テスト方法)
- [トラブルシューティング](#トラブルシューティング)
- [用語解説](#用語解説)
- [よくある質問](#よくある質問)

---

## プロジェクトについて

このプロジェクトは、**職員（従業員）の情報を管理するWebアプリケーション**です。

### 特徴

- 🏗️ **綺麗な設計**: Javaの有名なビルドツール「Maven」の考え方を取り入れた、整理されたコード構成
- ✅ **テスト完備**: 自動テストが充実していて、バグが入りにくい
- 🔒 **ルール厳守**: コードの書き方にルールがあり、ESLintが自動でチェック
- 📊 **カバレッジ測定**: テストがどれだけコードをカバーしているか測定可能
- 🎯 **TypeScript**: 型があるので、間違いに気づきやすい

### このプロジェクトで学べること

1. **モジュール分割**: 大きなプロジェクトを小さな部品に分ける方法
2. **クリーンアーキテクチャ**: ビジネスロジックとUIを分離する設計
3. **自動テスト**: ユニットテスト（部品単位）とE2Eテスト（画面操作）
4. **TypeScript**: JavaScriptに型をつけたプログラミング言語
5. **React**: モダンなWebアプリケーションの作り方

---

## 何ができるの？

### 基本機能（CRUD操作）

このアプリでは、職員情報の**CRUD**操作ができます。

> **📝 CRUDとは？**
> - **C**reate（作成）: 新しい職員を登録
> - **R**ead（読取）: 職員の情報を見る
> - **U**pdate（更新）: 職員の情報を変更
> - **D**elete（削除）: 職員を削除

### 管理できる情報

各職員について、以下の情報を管理できます：

```
・名前 (Name)
・メールアドレス (Email)
・所属部署 (Department)
・役職 (Position)
・入社日 (Hire Date)
```

### 画面イメージ

実際の画面のスクリーンショットは `tests/coverage/screenshots/` フォルダにあります：

- `10-employee-list-with-data.png` - 職員一覧画面
- `11-create-form.png` - 新規登録フォーム
- `14-edit-form-loaded.png` - 編集フォーム
- `06-api-error.png` - エラー表示の例

---

## 準備するもの

### 必須ツール

このプロジェクトを動かすには、以下のツールが必要です：

#### 1. Node.js (バージョン 18以上)

**Node.jsとは？**
JavaScriptをブラウザ外で実行できる環境です。

**インストール確認:**
```bash
node --version
```

`v18.0.0` 以上が表示されればOKです。

**まだインストールしていない場合:**
- 公式サイト: https://nodejs.org/
- 推奨版（LTS）をダウンロードしてインストール

#### 2. pnpm (バージョン 8以上)

**pnpmとは？**
パッケージマネージャーの一種で、npmより高速です。

**インストール方法:**
```bash
npm install -g pnpm@8.10.0
```

**インストール確認:**
```bash
pnpm --version
```

`8.10.0` が表示されればOKです。

### 推奨ツール（あると便利）

- **Git**: コード管理ツール
- **VSCode**: 人気のコードエディタ
- **Chrome/Firefox**: ブラウザ（開発者ツール付き）

---

## インストール方法

### ステップ1: プロジェクトのダウンロード

すでにこのフォルダにいる場合は、この手順はスキップできます。

```bash
# Gitでクローンする場合（例）
git clone <リポジトリURL>
cd sampleJS
```

### ステップ2: 依存パッケージのインストール

プロジェクトに必要なライブラリをすべてダウンロードします。

```bash
pnpm install
```

**何が起こる？**
- `node_modules/` フォルダが作成される
- React、TypeScript、Viteなど、必要なライブラリがダウンロードされる
- 所要時間: 1〜3分程度

**エラーが出た場合:**
```bash
# キャッシュをクリアして再実行
pnpm store prune
pnpm install
```

### ステップ3: Playwrightのインストール（E2Eテスト用）

E2Eテスト（画面操作のテスト）を実行するためのブラウザをインストールします。

```bash
pnpm playwright:install
```

**何が起こる？**
- テスト専用のChromiumブラウザがダウンロードされる
- 所要時間: 2〜5分程度

**⚠️ 注意:**
- サーバー環境（GUI無し）では、追加の設定が必要な場合があります
- その場合は、Dockerを使った実行をおすすめします（後述）

---

## 使い方

### 🚀 開発サーバーの起動

アプリケーションを開発モードで起動します。

```bash
pnpm dev
```

**何が起こる？**
1. Viteが起動する
2. コードを監視して、変更を自動で反映
3. ブラウザで開けるURLが表示される

**表示例:**
```
VITE v5.4.21  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

**ブラウザで開く:**
```
http://localhost:3000
```

**停止方法:**
```
Ctrl + C を押す
```

### 📝 コードを編集する

1. `apps/web/src/` フォルダ内のファイルを編集
2. 保存すると自動でブラウザに反映される（ホットリロード）

**初心者におすすめの編集箇所:**
- `apps/web/src/pages/EmployeeListPage.tsx` - 一覧画面
- `apps/web/src/pages/EmployeeFormPage.tsx` - フォーム画面
- `apps/web/src/styles/global.css` - スタイル（色や大きさ）

### 🔍 コードの品質チェック

#### ESLintの実行（コードの間違いをチェック）

```bash
pnpm lint
```

**何がチェックされる？**
- コードの書き方のルール
- **アーキテクチャの依存関係**（重要！）
- 使われていない変数など

**エラーが出た場合:**
```bash
# 自動修正できるエラーを直す
pnpm lint:fix
```

#### TypeScriptの型チェック

```bash
pnpm type-check
```

**何がチェックされる？**
- 型の間違い（例: 数字を入れるべきところに文字列を入れている）
- 存在しない変数やプロパティの使用

### 🏗️ ビルド（本番用にコンパイル）

開発が終わったら、本番環境用にビルドします。

```bash
pnpm build:web
```

**何が起こる？**
- TypeScriptがJavaScriptに変換される
- ファイルが最適化・圧縮される
- `apps/web/dist/` フォルダに出力される

**ビルドされたものをプレビュー:**
```bash
pnpm preview
```

ブラウザで `http://localhost:3000` を開いて確認できます。

---

## テスト方法

### 🧪 ユニットテスト（部品単位のテスト）

個々の関数やコンポーネントが正しく動くかテストします。

```bash
pnpm test
```

**何がテストされる？**
- `modules/domain/` のビジネスロジック
- `modules/application/` のユースケース
- `modules/api/` のAPIクライアント
- `modules/ui/` のUIコンポーネント
- `modules/util/` のユーティリティ関数

**テスト結果の見方:**
```
✓ modules/domain/tests/models/Employee.test.ts (10)
  ✓ Employee (10)
    ✓ create (5)
      ✓ should create a valid employee
      ✓ should create employee with provided id
      ...
```

- ✓ = 成功
- ✗ = 失敗

### 🎭 E2Eテスト（画面操作のテスト）

実際にブラウザを動かして、ユーザーの操作をシミュレートします。

**⚠️ 事前準備: ビルドが必要**

E2Eテストは、ビルドされたアプリに対して実行されます。

```bash
# 1. まずビルド
pnpm build:web

# 2. E2Eテスト実行
pnpm test:e2e
```

**何がテストされる？**
- 職員一覧の表示
- 職員の新規作成
- 職員の編集
- 職員の削除
- フォームのバリデーション
- エラー表示

**テスト結果:**
```
Running 18 tests using 1 worker

✓ [chromium] › employee.spec.ts:87:7 › Employee Management › should display employee list page
✓ [chromium] › employee.spec.ts:95:7 › Employee Management › should navigate to create employee form
...

18 passed (45.5s)
```

### 📊 カバレッジ測定（テストの網羅率）

コードのどれだけの部分がテストされているか測定します。

```bash
# カバレッジ付きE2Eテスト実行
pnpm test:coverage

# レポート生成
pnpm coverage:report
```

**レポートの確認:**
```bash
# ブラウザで開く（macOS）
open coverage/index.html

# ブラウザで開く（Linux）
xdg-open coverage/index.html

# ブラウザで開く（Windows）
start coverage/index.html
```

**カバレッジの目標:**
- ライン: 80%以上
- ステートメント: 80%以上
- 関数: 80%以上
- 分岐: 80%以上

### 🐳 Dockerで実行（推奨）

サーバー環境など、GUIがない環境では、Dockerを使うと確実です。

```bash
# 1. Dockerイメージをビルド
docker build -f Dockerfile.playwright -t samplejs-playwright .

# 2. テスト実行（スクリーンショット付き）
docker run --rm \
  -v "$(pwd)/tests/coverage/screenshots:/app/tests/coverage/screenshots:z" \
  samplejs-playwright
```

**生成されたスクリーンショット:**
`tests/coverage/screenshots/` フォルダに18枚の画面キャプチャが保存されます。

---

## プロジェクト構成

### 📁 フォルダ構造

```
sampleJS/
├── apps/                        # アプリケーション
│   └── web/                     # Webアプリ
│       ├── src/
│       │   ├── main.tsx         # エントリーポイント
│       │   ├── App.tsx          # ルートコンポーネント
│       │   ├── pages/           # 画面コンポーネント
│       │   └── router/          # ルーティング設定
│       └── index.html           # HTMLテンプレート
│
├── modules/                     # モジュール（部品）
│   ├── domain/                  # ドメイン層
│   │   ├── src/
│   │   │   ├── models/          # データモデル
│   │   │   └── valueObjects/   # 値オブジェクト
│   │   └── tests/               # テスト
│   │
│   ├── application/             # アプリケーション層
│   │   ├── src/
│   │   │   ├── usecases/        # ユースケース
│   │   │   ├── ports/           # インターフェース
│   │   │   └── hooks/           # Reactフック
│   │   └── tests/
│   │
│   ├── api/                     # API層
│   │   ├── src/
│   │   │   ├── client/          # APIクライアント
│   │   │   └── repositories/   # リポジトリ
│   │   └── tests/
│   │
│   ├── ui/                      # UI層
│   │   ├── src/
│   │   │   └── components/      # 再利用可能なコンポーネント
│   │   └── tests/
│   │
│   └── util/                    # ユーティリティ層
│       ├── src/
│       │   ├── formatters/      # フォーマッター
│       │   └── validators/      # バリデーター
│       └── tests/
│
├── tests/                       # E2Eテスト
│   └── e2e/
│       ├── pages/               # Page Object
│       └── specs/               # テストシナリオ
│
├── scripts/                     # スクリプト
│   └── collect-coverage.js      # カバレッジ集計
│
├── package.json                 # プロジェクト設定
├── pnpm-workspace.yaml          # ワークスペース定義
├── tsconfig.base.json           # TypeScript設定
├── eslint.config.js             # ESLint設定（重要！）
├── playwright.config.ts         # Playwright設定
└── azure-pipelines.yml          # CI/CD設定
```

### 🏗️ アーキテクチャ（依存関係のルール）

このプロジェクトは、**依存方向が厳密に管理**されています。

```
        ┌─────┐
        │ web │  ← Webアプリケーション（すべてに依存OK）
        └──┬──┘
           │
    ┌──────┴──────┐
    ↓      ↓      ↓
┌────┐  ┌────┐  ┌────┐
│ ui │  │api │  │util│
└─┬──┘  └─┬──┘  └────┘
  │       │
  └───┬───┘
      ↓
┌─────────────┐
│ application │
└──────┬──────┘
       ↓
   ┌────────┐
   │ domain │  ← 一番下（依存なし）
   └────────┘
```

**ルール:**
- **domain**: 他のどこにも依存しない（純粋なビジネスロジック）
- **util**: 他のどこにも依存しない（汎用ツール）
- **application**: domainにのみ依存
- **api**: domainとapplicationに依存
- **ui**: domain、application、utilに依存
- **web**: すべてに依存OK

**違反すると？**
ESLintがエラーを出して、ビルドが失敗します。

**例:**
```typescript
// ❌ NG: domainがapplicationに依存
// modules/domain/src/models/Employee.ts
import { useEmployees } from '@samplejs/application';

// ESLintエラー:
// "domain cannot depend on application. Allowed dependencies: none"
```

---

## トラブルシューティング

### よくあるエラーと解決方法

#### ❌ `command not found: pnpm`

**原因:** pnpmがインストールされていない

**解決方法:**
```bash
npm install -g pnpm@8.10.0
```

#### ❌ `ERR_PNPM_NO_MATCHING_VERSION`

**原因:** 指定したバージョンが見つからない

**解決方法:**
```bash
# 最新のpnpmをインストール
npm install -g pnpm@latest

# または、バージョンを確認
pnpm --version
```

#### ❌ `Port 3000 is already in use`

**原因:** ポート3000が既に使われている

**解決方法:**
```bash
# 既存のプロセスを探す
lsof -ti:3000

# プロセスを停止
kill -9 $(lsof -ti:3000)

# または、別のポートを使う
PORT=3001 pnpm dev
```

#### ❌ E2Eテストが失敗する

**原因:** ビルドされていない、またはブラウザが起動できない

**解決方法:**
```bash
# 1. まずビルド
pnpm build:web

# 2. Dockerで実行（確実）
docker build -f Dockerfile.playwright -t samplejs-playwright .
docker run --rm samplejs-playwright
```

#### ❌ `Module not found`

**原因:** 依存パッケージが不足している

**解決方法:**
```bash
# 依存関係を再インストール
rm -rf node_modules
pnpm install
```

#### ❌ TypeScriptエラー

**原因:** 型の不一致

**解決方法:**
```bash
# 型チェックを実行して詳細を確認
pnpm type-check

# エラーメッセージを読んで、該当箇所を修正
```

### 🔄 完全リセット

どうしてもうまくいかない場合は、すべてクリーンにしてやり直します。

```bash
# 1. すべてのビルド成果物を削除
pnpm clean

# 2. node_modulesを削除
rm -rf node_modules apps/*/node_modules modules/*/node_modules

# 3. pnpmのキャッシュをクリア
pnpm store prune

# 4. 再インストール
pnpm install

# 5. Playwrightを再インストール
pnpm playwright:install

# 6. ビルド
pnpm build:web
```

---

## 用語解説

### プログラミング用語

| 用語 | 説明 |
|------|------|
| **Node.js** | JavaScriptをサーバー側で動かすための実行環境 |
| **pnpm** | パッケージマネージャー。npmより高速 |
| **TypeScript** | JavaScriptに型を追加した言語 |
| **React** | Facebookが作ったUI構築ライブラリ |
| **Vite** | 高速なビルドツール |
| **ESLint** | コードの品質をチェックするツール |
| **Playwright** | ブラウザを自動操作してテストするツール |
| **Vitest** | 高速なテストフレームワーク |

### アーキテクチャ用語

| 用語 | 説明 |
|------|------|
| **ドメイン層** | ビジネスロジックを書く場所（Reactなど不要） |
| **アプリケーション層** | ユースケース（機能）を書く場所 |
| **API層** | サーバーとの通信を担当 |
| **UI層** | 画面コンポーネント |
| **ユーティリティ層** | 汎用的な便利関数 |

### テスト用語

| 用語 | 説明 |
|------|------|
| **ユニットテスト** | 個々の関数やクラスをテストする |
| **E2Eテスト** | End-to-End。実際の画面操作をシミュレート |
| **カバレッジ** | テストがコードのどれだけをカバーしているかの割合 |
| **Page Object** | 画面の操作をクラスにまとめたパターン |
| **モック** | 本物の代わりに使う偽物（テスト用） |

### CRUD

| 文字 | 意味 | 操作 |
|------|------|------|
| **C** | Create | 新規作成 |
| **R** | Read | 読み取り（表示） |
| **U** | Update | 更新 |
| **D** | Delete | 削除 |

---

## よくある質問

### Q1. プログラミング初心者ですが、このプロジェクトを理解できますか？

**A:** はい、できます！ただし、以下の基礎知識があると理解しやすいです：

- HTML/CSSの基本
- JavaScriptの基本（変数、関数、if文など）
- Reactの基本（コンポーネント、propsなど）

わからない部分は、用語解説や各ファイルのコメントを参考にしてください。

### Q2. どこから読み始めればいいですか？

**A:** 以下の順番がおすすめです：

1. `modules/domain/src/models/Employee.ts` - データ構造を理解
2. `apps/web/src/pages/EmployeeListPage.tsx` - 一覧画面を見る
3. `apps/web/src/pages/EmployeeFormPage.tsx` - フォーム画面を見る
4. `modules/application/src/usecases/` - ビジネスロジックを理解

### Q3. 実際にコードを変更して試したいです

**A:** ぜひ試してください！以下がおすすめです：

```bash
# 1. 開発サーバーを起動
pnpm dev

# 2. ファイルを編集（例）
# apps/web/src/pages/EmployeeListPage.tsx
# - タイトルを「社員一覧」に変更してみる
# - ボタンの色を変えてみる

# 3. ブラウザで確認（自動で反映される）
```

### Q4. エラーが出たらどうすればいいですか？

**A:** 以下の手順で対処してください：

1. **エラーメッセージを読む**（何が問題か書いてある）
2. **トラブルシューティング**のセクションを確認
3. それでも解決しない場合は、`pnpm clean` して最初からやり直す

### Q5. 本番環境にデプロイするには？

**A:** ビルドしたファイルをサーバーにアップロードします：

```bash
# 1. ビルド
pnpm build:web

# 2. apps/web/dist/ フォルダをサーバーにアップロード

# 3. Webサーバー（Nginx、Apacheなど）で公開
```

Azure DevOps Pipelineを使った自動デプロイの設定は `azure-pipelines.yml` を参照してください。

### Q6. テストは必須ですか？

**A:** 開発中は必須ではありませんが、以下の理由で**強く推奨**します：

- バグの早期発見
- リファクタリング時の安心感
- コードの品質保証
- チーム開発での信頼性

### Q7. このプロジェクトを自分のプロジェクトに応用できますか？

**A:** もちろんです！このプロジェクトは学習用のテンプレートとして設計されています。

**応用のヒント:**
- `Employee` を `Product`、`User` などに置き換える
- 必要なフィールドを追加・削除する
- デザインをカスタマイズする

---

## 📚 さらに学ぶには

### 公式ドキュメント

- [React公式](https://react.dev/)
- [TypeScript公式](https://www.typescriptlang.org/)
- [Vite公式](https://vitejs.dev/)
- [Playwright公式](https://playwright.dev/)

### プロジェクト内のドキュメント

- `IMPLEMENTATION_SUMMARY.md` - 実装の詳細
- `QUICK_START.md` - クイックスタートガイド
- `TEST_EXECUTION_REPORT.md` - テスト実行レポート

### 次のステップ

1. ✅ このREADMEを読む
2. ✅ プロジェクトを動かす
3. ✅ コードを読んで理解する
4. ✅ 小さな変更を加えてみる
5. ✅ テストを書いてみる
6. ✅ 新しい機能を追加してみる

---

## 🤝 貢献・フィードバック

質問や提案があれば、Issue を作成してください。

---

## 📄 ライセンス

MIT License

---

## 🎉 楽しんで学習してください！

このプロジェクトは、モダンなWebアプリケーション開発のベストプラクティスを学ぶために作られました。

わからないことがあれば、焦らず一つずつ調べながら進めてください。

**Happy Coding! 🚀**
