# CA証明書基盤とHTTPSテストインタフェース

オンプレミスクローズド環境向けの自己署名認証局（CA）基盤と自動化された証明書生成、HTTPSテストサーバー。

## 概要

このプロジェクトは、SSL/TLS暗号化が必要だが自己署名証明書で認証エラーが発生するクローズドなオンプレミス環境向けに設計された完全な認証局基盤を提供します。以下の機能が含まれます：

- **自己署名CA証明書**（4096-bit RSA）
- **CAで署名されたサーバ証明書**（2048-bit RSA）
- **最小限のユーザー入力による自動化された証明書生成**
- **Dockerベースのテスト用HTTPSサーバ**（Nginxでポート5006）
- **他サーバでの使用のための証明書エクスポート**
- **IP制限なし** - 外部ネットワークからアクセス可能

## 機能

### 証明書生成
- OpenSSLベースのCAとサーバ証明書生成
- インテリジェントなデフォルト値による自動化ワークフロー
- 最小限のユーザー入力（サーバ名、有効期限）
- 強力な暗号化（CA: 4096-bit、サーバ: 2048-bit RSA）
- SHA-256署名アルゴリズム
- DNSとIPアドレスのSubjectAltName (SAN) サポート

### HTTPSテスト環境
- DockerコンテナでのNginxベースHTTPSサーバ
- TLS 1.2/1.3サポート
- ヘルスチェックと証明書情報エンドポイント
- 詳細な手順を含む美しいテストページ
- 制限なしの外部IPアクセス

### 証明書管理
- 証明書検証ユーティリティ
- 他サーバ用の証明書エクスポート
- 詳細なログ記録
- ファイル権限管理
- 証明書チェーンの検証

### セキュリティ
- 秘密鍵はバージョン管理にコミットされない
- 適切なファイル権限（鍵は600、証明書は644）
- SELinux互換のボリュームマウント
- 全体的にセキュアなデフォルト設定

## 必要要件

- OpenSSL
- Docker
- docker-compose
- sudo アクセス
- ポート5006が利用可能

## クイックスタート

5分間のセットアップガイドは [QUICKSTART.md](QUICKSTART.md) を参照してください。

### 基本的な使い方

```bash
# 1. 初期セットアップ
./scripts/setup-ca-environment.sh

# 2. 証明書生成
./scripts/create-ca.sh

# 3. HTTPSサーバ起動（sudoが必要）
sudo docker-compose up -d

# 4. 接続テスト
curl -k https://98.93.187.130:5006/
```

## ディレクトリ構造

```
CA/
├── README.md                           # このファイル
├── QUICKSTART.md                       # クイックスタートガイド
├── .env                                # 環境設定
├── .gitignore                          # セキュリティ設定
├── docker-compose.yml                  # HTTPSサーバ定義
│
├── scripts/
│   ├── setup-ca-environment.sh        # 初期セットアップスクリプト
│   ├── create-ca.sh                   # メイン証明書生成スクリプト
│   ├── export-certificates.sh         # 証明書エクスポートユーティリティ
│   ├── serve-cert.sh                  # 証明書配布サーバ
│   ├── install-cert-devops-server.ps1 # Azure DevOps Server用インストールスクリプト
│   └── utils/
│       └── verify-certificates.sh     # 証明書検証
│
├── config/
│   ├── openssl-ca.cnf                 # CA証明書OpenSSL設定
│   ├── openssl-server.cnf             # サーバ証明書OpenSSL設定
│   └── nginx/
│       ├── Dockerfile                 # Nginxコンテナ定義
│       ├── nginx.conf                 # HTTPS設定
│       └── index.html                 # テストページ
│
├── certs/                             # 生成された証明書（gitignore対象）
│   ├── ca/
│   │   ├── ca.key                     # CA秘密鍵
│   │   ├── ca.crt                     # CA証明書
│   │   ├── ca.srl                     # シリアル番号ファイル
│   │   ├── install-ca-windows.ps1     # Windowsクライアント用自動インストール
│   │   ├── install-ca-linux.sh        # Linuxクライアント用自動インストール
│   │   └── install-ca-macos.sh        # macOSクライアント用自動インストール
│   ├── server/
│   │   ├── server.key                 # サーバ秘密鍵
│   │   ├── server.csr                 # 証明書署名要求
│   │   ├── server.crt                 # サーバ証明書
│   │   └── server-chain.crt           # 証明書チェーン（サーバ + CA）
│   └── export/                        # エクスポートパッケージ
│       └── ca-bundle-*.tar.gz
│
└── logs/
    └── certificate-generation.log     # 操作ログ
```

## 詳細な使い方

### 1. 初期セットアップ

セットアップスクリプトを実行して依存関係を確認し、ディレクトリ構造を作成します：

```bash
chmod +x scripts/*.sh scripts/utils/*.sh
./scripts/setup-ca-environment.sh
```

このスクリプトは以下を実行します：
- OpenSSL、Docker、docker-composeの確認
- 必要なディレクトリの作成
- スクリプトへの実行権限の設定
- .envと.gitignoreファイルの確認

### 2. 証明書の生成

証明書生成スクリプトを実行します：

```bash
./scripts/create-ca.sh
```

**対話モード**（デフォルト）:
- サーバ名の入力を求められます（デフォルト: 98.93.187.130）
- 有効期限の入力を求められます（デフォルト: 730日）
- 組織名の入力を求められます（デフォルト: OnPremise-CA）

**自動モード**（入力プロンプトなし）:
```bash
./scripts/create-ca.sh --auto
```

スクリプトは以下を実行します：
1. CA証明書の生成（存在しない場合）
   - 4096-bit RSA秘密鍵
   - 指定された日数有効な自己署名証明書
2. サーバ証明書の生成
   - 2048-bit RSA秘密鍵
   - 証明書署名要求（CSR）
   - CAで署名されたサーバ証明書
   - 証明書チェーン（サーバ + CA）
3. 適切なファイル権限の設定
4. 証明書サマリーの表示

### 3. 証明書の検証

証明書が有効で適切に設定されていることを確認します：

```bash
./scripts/utils/verify-certificates.sh
```

以下をチェックします：
- 証明書の有効性
- 証明書チェーンの正確性
- ファイル権限
- 有効期限
- CA証明書のCA:TRUE拡張

### 4. HTTPSサーバの起動

**重要: すべてのdocker-composeコマンドはsudoを使用する必要があります**

```bash
# デタッチモードでコンテナを起動
sudo docker-compose up -d

# コンテナ状態の確認
sudo docker-compose ps

# ログの表示
sudo docker-compose logs -f ca-https-test

# コンテナの停止
sudo docker-compose down

# コンテナの再起動
sudo docker-compose restart
```

HTTPSサーバは以下を提供します：
- ポート5006（外部）→ 443（コンテナ）でリッスン
- `https://[SERVER]:5006/` でテストページを提供
- `https://[SERVER]:5006/health` でヘルスチェック
- `https://[SERVER]:5006/cert-info` で証明書情報

### 5. HTTPS接続のテスト

**ローカルテスト:**
```bash
# 証明書検証なしでテスト
curl -k https://localhost:5006/

# CA証明書を使用してテスト
curl --cacert certs/ca/ca.crt https://localhost:5006/

# ヘルスエンドポイントのテスト
curl -k https://localhost:5006/health
```

**外部テスト:**
```bash
# 別のマシンから
curl -k https://98.93.187.130:5006/

# CA証明書をインストール後の検証付きテスト
curl --cacert ca.crt https://98.93.187.130:5006/
```

**ブラウザテスト:**
```
https://98.93.187.130:5006/
```

### 6. 自動クライアントインストール（推奨）

クライアントマシンにCA証明書をインストールする最も簡単な方法は、自動インストールスクリプトを使用することです。

#### 6.0.1. 証明書ダウンロードサーバの起動（サーバ側）

CAサーバ上で、証明書ダウンロード用HTTPサーバを起動します：

```bash
# サーバ上で実行
cd /root/aws.git/container/claudecode/CA
./scripts/serve-cert.sh

# またはカスタムポートを指定
./scripts/serve-cert.sh 8080
```

サーバは以下を表示します：
```
==========================================
  CA Certificate Download Server
==========================================

Download URL:
  http://98.93.187.130:8080/ca.crt

Client Installation Scripts:
  Windows: http://98.93.187.130:8080/install-ca-windows.ps1
  Linux:   http://98.93.187.130:8080/install-ca-linux.sh
  macOS:   http://98.93.187.130:8080/install-ca-macos.sh
```

クライアントが証明書をダウンロードしてインストールする間、**このサーバを実行し続けてください**。

#### 6.0.2. 自動インストール - Windows

**Windowsクライアントマシン上で:**

1. **PowerShellスクリプトをダウンロード:**
   - ブラウザで `http://98.93.187.130:8080/install-ca-windows.ps1` にアクセス
   - またはPowerShellを使用:
   ```powershell
   Invoke-WebRequest -Uri "http://98.93.187.130:8080/install-ca-windows.ps1" -OutFile "install-ca-windows.ps1"
   ```

2. **管理者権限でスクリプトを実行:**
   - `install-ca-windows.ps1` を右クリック → **"PowerShellで実行"**
   - またはPowerShell（管理者）から:
   ```powershell
   powershell -ExecutionPolicy Bypass -File install-ca-windows.ps1
   ```

3. **スクリプトは自動的に以下を実行します:**
   - CA証明書（ca.crt）のダウンロード
   - 正しい証明書であることの確認
   - 古いOnPremise-CA証明書の削除
   - LocalMachine\Root（信頼されたルート）へのインストール
   - インストール確認の表示

4. **ブラウザを完全に再起動**して `https://98.93.187.130:5006/` にアクセス

#### 6.0.3. 自動インストール - Linux

**Linuxクライアントマシン上で:**

```bash
# インストールスクリプトをダウンロードして実行
curl -O http://98.93.187.130:8080/install-ca-linux.sh
chmod +x install-ca-linux.sh
sudo ./install-ca-linux.sh
```

スクリプトは自動的に以下を実行します：
- CA証明書のダウンロード
- 証明書の検証
- システムトラストストアへのインストール（Ubuntu/Debian/CentOS/RHEL/Fedora）
- 証明書ストアの更新
- インストール確認の表示

**サポートされているディストリビューション:**
- Ubuntu / Debian → `/usr/local/share/ca-certificates/`
- CentOS / RHEL / Fedora → `/etc/pki/ca-trust/source/anchors/`

#### 6.0.4. 自動インストール - macOS

**macOSクライアントマシン上で:**

```bash
# インストールスクリプトをダウンロードして実行
curl -O http://98.93.187.130:8080/install-ca-macos.sh
chmod +x install-ca-macos.sh
sudo ./install-ca-macos.sh
```

スクリプトは自動的に以下を実行します：
- CA証明書のダウンロード
- 証明書の検証
- trustRootでシステムキーチェーンへのインストール
- インストール確認の表示

**注意:** キーチェーンアクセスで手動で信頼を設定する必要がある場合があります：
1. キーチェーンアクセスアプリを開く
2. "システム"キーチェーンを選択
3. "OnPremise-CA-Root"を見つける
4. ダブルクリック → 信頼 → "常に信頼"に設定

#### 6.0.5. スクリプトが実行する処理

すべての自動インストールスクリプトは以下のステップを実行します：

1. **ダウンロード** - サーバからCA証明書を取得
2. **検証** - 証明書が正しいことを確認（CN=OnPremise-CA-Root）
3. **削除** - 既存のOnPremise-CA証明書を削除
4. **インストール** - システムトラストストアに証明書をインストール
5. **確認** - インストールが成功したことを検証
6. **表示** - 次のステップ（ブラウザ再起動、テストURL）を表示

**自動インストールの利点:**
- ✅ 手動でのファイル管理が不要
- ✅ 自動検証（正しい証明書であることを保証）
- ✅ 古い証明書の自動削除
- ✅ 正しいシステムストアにインストール（ユーザーストアではない）
- ✅ 明確なフィードバックとエラーメッセージ

---

### 7. 手動クライアントインストール

自動スクリプトが機能しない場合や手動インストールを希望する場合は、以下の手順に従ってください：

#### 7.1. "保護されていない通信"警告が表示される理由

ブラウザからHTTPSサーバにアクセスすると、**"保護されていない通信"または"この接続ではプライバシーが保護されません"**という警告が表示されます。これは、ブラウザがまだ当社の自己署名CA証明書を信頼していないためです。

**これが発生する理由:**
- 当社のCA証明書は自己署名です（信頼された認証局から発行されたものではありません）
- ブラウザのトラストストアに当社のCA証明書がありません
- これは自己署名証明書の予想される動作です

**解決策:** クライアントマシンにCA証明書（`ca.crt`）をインストールします。

#### 7.2. CA証明書のダウンロード

まず、CA証明書ファイルをクライアントマシンに取得します：

**オプション1: エクスポートバンドルを使用**
```bash
# サーバ上で実行
./scripts/export-certificates.sh

# クライアントマシンにコピー
scp certs/export/ca-bundle-*.tar.gz user@client-machine:/tmp/

# クライアントマシン上で実行
cd /tmp
tar xzf ca-bundle-*.tar.gz
cd ca-bundle-*/
# これでca.crtファイルが手に入ります
```

**オプション2: CA証明書を直接コピー**
```bash
# サーバ上で実行
cd /root/aws.git/container/claudecode/CA

# クライアントマシンにコピー
scp certs/ca/ca.crt user@client-machine:/tmp/
```

**オプション3: ブラウザから証明書をエクスポート**

HTTPSサイトを表示している間に、ブラウザから直接CA証明書をエクスポートできます（セキュリティ警告が表示されていても可能）。

**重要: エクスポート形式**
- **推奨形式**: `.crt` または `.pem`（Base64エンコードX.509）
- **代替形式**: `.cer` または `.der`（DERエンコードバイナリ）
- **Linux/Mac向け**: `.crt` または `.pem` 形式を使用
- **Windows向け**: `.crt` と `.cer` の両方が機能しますが、`.crt` を推奨
- **避けるべき**: `.p7b` または `.pfx` 形式（これらは証明書チェーン用または秘密鍵を含みます）

**Chrome/Edge/Chromiumからのエクスポート:**

1. `https://98.93.187.130:5006/` にアクセス（警告が表示されても可）
2. アドレスバーの**"保護されていない通信"**または**警告アイコン**をクリック
3. **"証明書が無効です"**または**"証明書（無効）"**をクリック
4. 証明書ビューアが開きます
5. **"詳細"**タブに移動
6. **CA証明書**を探します: "OnPremise-CA-Root"（サーバ証明書ではありません）
   - 証明書パス/チェーンから選択する必要がある場合があります
7. **"エクスポート..."**または**"ファイルにコピー..."**ボタンをクリック
8. 形式を選択:
   - **Windows**: "Base64エンコードX.509 (.CER)"または"DERエンコードバイナリX.509 (.CER)"を選択
   - **Linux/Mac**: "Base64 (PEM)"形式を選択
9. `ca.crt`として保存（推奨ファイル名）
10. このファイルをインストールに使用（以下のセクション参照）

**Firefoxからのエクスポート:**

1. `https://98.93.187.130:5006/` にアクセス（警告が表示されても可）
2. アドレスバーの**ロックアイコン**または**警告アイコン**をクリック
3. **"接続は安全ではありません"** → **"詳細情報"**をクリック
4. **"証明書を表示"**ボタンをクリック
5. 証明書ビューアが新しいタブで開きます
6. スクロールダウンして"OnPremise-CA-Root"を表示している**発行者**セクションを見つけます
7. 証明書チェーンを探し、**ルートCA証明書**（OnPremise-CA-Root）をクリック
8. **"ダウンロード"**セクションをクリック
9. **"PEM (cert)"**形式を選択（これは`.crt`ファイルを作成します）
10. `ca.crt`として保存

**代替Firefox方法:**
1. サイトにアクセス（警告があっても）
2. **"詳細設定..."** → **"証明書を表示"**をクリック
3. 証明書ビューアで発行者証明書（OnPremise-CA-Root）を見つけます
4. **"ダウンロード"** → **"PEM (cert)"**をクリック
5. ファイルを保存

**Safari（Mac）からのエクスポート:**

1. `https://98.93.187.130:5006/` にアクセス（警告が表示されても可）
2. アドレスバーの**ロックアイコン**または**警告テキスト**をクリック
3. **"証明書を表示"**をクリック
4. 証明書チェーンを探します
5. **ルート証明書**を選択: "OnPremise-CA-Root"
6. 証明書アイコンをデスクトップまたはFinderにドラッグ
   - これにより`.cer`ファイルとして保存されます
7. 必要に応じて`ca.crt`にリネーム（オプション）

**ダウンロードした証明書の検証:**
```bash
# 証明書の詳細を確認
openssl x509 -in ca.crt -noout -text

# 以下が表示されるはずです:
# Subject: C=JP, ST=Tokyo, L=Tokyo, O=OnPremise-CA, OU=IT, CN=OnPremise-CA-Root
# Issuer: C=JP, ST=Tokyo, L=Tokyo, O=OnPremise-CA, OU=IT, CN=OnPremise-CA-Root
# (自己署名CAの場合、SubjectとIssuerは同じです)

# ファイル形式がDER（バイナリ）の場合、PEMに変換:
openssl x509 -inform der -in ca.cer -out ca.crt
```

**避けるべき一般的な誤り:**
- ❌ サーバ証明書（CN=98.93.187.130）をエクスポートしない - CA証明書（CN=OnPremise-CA-Root）をエクスポート
- ❌ `.pfx`または`.p12`形式で保存しない（これらはパスワードが必要で、異なる目的のためのものです）
- ❌ 証明書チェーン全体をエクスポートしない - ルートCA証明書のみ
- ✅ 証明書のサブジェクト/発行者に"OnPremise-CA-Root"があることを確認

**⚠️ 重要: サーバ証明書 vs CA証明書**

**クライアントマシンにサーバ証明書をインストールしないでください！**

これが最も一般的な誤りです：

| 証明書 | ファイル | サブジェクト (CN) | 用途 | クライアントにインストール? |
|------------|------|--------------|---------|-------------------|
| ❌ サーバ証明書 | `server.crt` | CN=98.93.187.130 | HTTPSサーバで使用 | **NO - インストールしない!** |
| ✅ CA証明書 | `ca.crt` | CN=OnPremise-CA-Root | サーバ証明書に署名 | **YES - これをインストール!** |

**正しいファイルを持っているか確認する方法:**

```bash
# 証明書のサブジェクトを確認
openssl x509 -in your-file.crt -noout -subject

# 正しい（CA証明書）:
subject=C=JP, ST=Tokyo, L=Tokyo, O=OnPremise-CA, OU=IT, CN=OnPremise-CA-Root

# 誤り（サーバ証明書）:
subject=C=JP, ST=Tokyo, L=Tokyo, O=OnPremise-CA, OU=IT, CN=98.93.187.130
```

**誤ってサーバ証明書をインストールした場合:**
1. 証明書ストアから削除
2. 正しい`ca.crt`ファイルをダウンロード
3. `ca.crt`（CN=OnPremise-CA-Rootのファイル）をインストール

#### 7.3. CA証明書のインストール - Linux（Ubuntu/Debian）

```bash
# システムトラストストアにCA証明書をコピー
sudo cp ca.crt /usr/local/share/ca-certificates/onpremise-ca.crt

# 証明書ストアを更新
sudo update-ca-certificates

# インストールを確認
ls -l /etc/ssl/certs/ | grep onpremise-ca

# ブラウザを再起動（重要！）
# すべてのブラウザウィンドウを閉じて再度開く
```

**Linux上のChrome/Chromium向け:**
Chromeはシステム証明書ストアを使用するため、上記の手順で十分です。`update-ca-certificates`実行後にChromeを再起動してください。

**Linux上のFirefox向け:**
Firefoxは独自の証明書ストアを使用します（以下のセクション7.7を参照）。

#### 7.4. CA証明書のインストール - Linux（CentOS/RHEL/Fedora）

```bash
# トラストストアにCA証明書をコピー
sudo cp ca.crt /etc/pki/ca-trust/source/anchors/onpremise-ca.crt

# トラストストアを更新
sudo update-ca-trust extract

# インストールを確認
trust list | grep "OnPremise-CA"

# ブラウザを再起動
```

#### 7.5. CA証明書のインストール - Windows

**方法1: コマンドライン（管理者PowerShell）**
```powershell
# 管理者としてPowerShellを開く
# ca.crtを含むディレクトリに移動

# 信頼されたルート証明機関にインストール
certutil -addstore -f "ROOT" ca.crt

# インストールを確認
certutil -store ROOT | findstr "OnPremise-CA"
```

**方法2: GUI（ほとんどのユーザーにとって簡単）**

1. **ca.crt**をWindowsマシンにダウンロード
2. `ca.crt`ファイルを**ダブルクリック**
3. **"証明書のインストール..."**をクリック
4. **"ローカルコンピューター"**を選択（管理者権限が必要）または**"現在のユーザー"**
5. **"次へ"**をクリック
6. **"証明書をすべて次のストアに配置する"**を選択
7. **"参照"**をクリック
8. **"信頼されたルート証明機関"**を選択
9. **"OK"** → **"次へ"** → **"完了"**をクリック
10. セキュリティ警告で**"はい"**をクリック
11. **"インポートに成功しました"**が表示されるはずです
12. すべてのブラウザウィンドウを**閉じて再起動**

**Windows上のEdge/Chrome向け:**
- これらのブラウザはWindows証明書ストアを使用
- インストール後、ブラウザを再起動
- 警告が消えるはずです

**Windows上のFirefox向け:**
- Firefoxは独自の証明書ストアを使用（以下のセクション7.7を参照）

#### 7.6. CA証明書のインストール - macOS

**方法1: コマンドライン**
```bash
# ca.crtをMacにコピー
# ターミナルを開く

# システムキーチェーンにインストール（パスワードが必要）
sudo security add-trusted-cert \
    -d -r trustRoot \
    -k /Library/Keychains/System.keychain \
    ca.crt

# インストールを確認
security find-certificate -a -c "OnPremise-CA-Root" /Library/Keychains/System.keychain
```

**方法2: キーチェーンアクセスGUI**

1. **ca.crt**をMacにダウンロード
2. `ca.crt`を**ダブルクリック**（キーチェーンアクセスが開きます）
3. デフォルトで"ログイン"キーチェーンに追加されます
4. リストから**証明書を見つける** "OnPremise-CA-Root"
5. 証明書を**ダブルクリック**
6. **"信頼"**セクションを展開
7. **"この証明書を使用する場合"**を**"常に信頼"**に設定
8. ウィンドウを閉じる（パスワードを求められます）
9. **ブラウザを再起動**

**Safari向け:**
- システムキーチェーンを使用
- インストールとブラウザ再起動後に動作するはずです

**Mac上のChrome向け:**
- システムキーチェーンを使用
- インストールとブラウザ再起動後に動作するはずです

**Mac上のFirefox向け:**
- 独自の証明書ストアを使用（以下のセクション7.7を参照）

#### 7.7. CA証明書のインストール - Firefox（全プラットフォーム）

Firefoxは、オペレーティングシステムとは別の独自の証明書ストアを使用します。

**Firefox向けの手順:**

1. **Firefoxを開く**
2. **設定**に移動（またはアドレスバーに`about:preferences`と入力）
3. 検索ボックスで**"certificates"**を検索
4. **"証明書を表示..."**ボタンをクリック
5. **"認証局証明書"**タブに移動
6. **"インポート..."**ボタンをクリック
7. ダウンロードした**`ca.crt`**ファイルを選択
8. チェックボックスをオン: **"この認証局によるウェブサイトの識別を信頼する"**
9. **"OK"**をクリック
10. "OnPremise-CA"の下のリストに"OnPremise-CA-Root"が表示されるはずです
11. 設定を閉じる
12. **ページを更新**（F5）または`https://98.93.187.130:5006/`を再訪問

警告が消え、ロックアイコン🔒が表示されるはずです。

#### 7.8. インストールの確認

CA証明書をインストールした後、動作することを確認します：

**ブラウザで:**
1. `https://98.93.187.130:5006/`にアクセス
2. アドレスバーに**ロックアイコン**🔒が表示されるはずです（警告三角形ではありません）
3. ロックアイコンをクリック
4. **"接続は保護されています"**または**"証明書"**をクリック
5. 確認:
   - 発行先: `98.93.187.130`
   - 発行者: `OnPremise-CA-Root`
   - 有効期間の開始: （証明書開始日）
   - 有効期間の終了: （証明書有効期限）

**コマンドラインテスト:**
```bash
# Linux/Mac
curl https://98.93.187.130:5006/

# CA証明書がシステム全体にインストールされている場合、-kフラグなしで動作するはずです
# 証明書エラーで失敗する場合、CA証明書が正しくインストールされていません

# Windows PowerShell
Invoke-WebRequest -Uri https://98.93.187.130:5006/

# 証明書エラーなしで動作するはずです
```

#### 7.9. クライアントインストールのトラブルシューティング

**問題: インストール後もまだ"保護されていない通信"が表示される**

解決策:
1. **ブラウザを完全に再起動**（タブだけでなく、すべてのウィンドウを閉じる）
2. **ブラウザキャッシュをクリア**: 設定 → プライバシー → 閲覧データを削除
3. **証明書が正しいストアにあるか確認**:
   - Windows: "信頼されたルート証明機関"にある必要があります、"個人"ではありません
   - Linux: sudoで`update-ca-certificates`を実行
   - Mac: 証明書を"常に信頼"に設定する必要があります
4. **Firefox向け**: OS経由ではなく、Firefox独自の証明書マネージャーでインストール
5. **ページをハードリフレッシュ**: Ctrl+Shift+R（Windows/Linux）またはCmd+Shift+R（Mac）

**問題: "このCAルート証明書は信頼されていません"**

解決策:
1. `ca.crt`（`server.crt`ではない）をインストールしたことを確認
2. "信頼されたルート"ストアにインストール（中間または個人ではない）
3. Windowsでは、管理者としてcertutilを実行
4. Linuxでは、ca-certificatesディレクトリでファイル名が`.crt`で終わることを確認

**問題: Chromeが"NET::ERR_CERT_AUTHORITY_INVALID"と表示**

解決策:
1. CA証明書がシステムトラストストアにありません
2. Linuxで: `sudo update-ca-certificates`を実行してChromeを再起動
3. Windowsで: certutilまたはGUI経由でインストール、Chromeを再起動
4. シークレット/プライベートモードで開いてテスト

**問題: Firefoxはまだ警告を表示するが、Chromeは動作する**

解決策:
- Firefoxは別の証明書ストアを使用
- Firefox設定 → 証明書を通じてCA証明書をインポートする必要があります
- システムインストールはFirefoxに影響しません

### 8. 証明書のエクスポート

他サーバで使用するために証明書をエクスポートします：

```bash
./scripts/export-certificates.sh
```

これにより、以下を含む`certs/export/`にtarballが作成されます：
- `ca.crt` - クライアント信頼用のCA証明書
- `server.crt` - サーバ証明書
- `server.key` - サーバ秘密鍵（安全に保管してください！）
- `server-chain.crt` - 完全な証明書チェーン
- `README.txt` - インストール手順
- `verify.sh` - 検証スクリプト
- `CERTIFICATE_INFO.txt` - 証明書詳細

**別サーバへ転送:**
```bash
scp certs/export/ca-bundle-*.tar.gz user@other-server:/tmp/
```

## 9. 設定

### 環境変数（.env）

```bash
# サーバ設定
SERVER_NAME=98.93.187.130          # サーバホスト名またはIP
HTTPS_PORT=5006                    # 外部HTTPSポート
CERT_VALIDITY_DAYS=730             # 証明書有効期限（2年）

# 証明書サブジェクト情報
CERT_COUNTRY=JP                    # 国コード
CERT_STATE=Tokyo                   # 都道府県
CERT_LOCALITY=Tokyo                # 市区町村
CERT_ORGANIZATION=OnPremise-CA     # 組織名
CERT_ORG_UNIT=IT                   # 部門

# 外部アクセス
EC2_PUBLIC_IP=98.93.187.130        # パブリックIPアドレス

# 証明書ダウンロードサーバ
CERT_DOWNLOAD_PORT=8080            # 証明書配布サーバのポート
```

### OpenSSL設定

#### CA証明書（config/openssl-ca.cnf）
- 4096-bit RSA鍵
- 自己署名
- CA:TRUE拡張
- keyCertSignとcRLSign鍵使用

#### サーバ証明書（config/openssl-server.cnf）
- 2048-bit RSA鍵
- CAで署名
- serverAuthとclientAuth拡張鍵使用
- DNSとIPを含むSubjectAltName

### Nginx設定

#### SSL/TLS設定
- TLS 1.2とTLS 1.3のみ
- 強力な暗号スイート
- HTTP/2有効
- セキュリティヘッダー（HSTS、X-Frame-Optionsなど）

#### エンドポイント
- `/` - 手順付きテストページ
- `/health` - ヘルスチェック（"healthy"を返す）
- `/cert-info` - 証明書情報

## 10. 他サーバでの証明書使用

### Azure DevOps Server（オンプレミス）

Azure DevOps Serverには、CA証明書（クライアント信頼用）とサーバ証明書および秘密鍵（HTTPS動作用）の両方が必要です。

#### 前提条件

- Windows ServerにAzure DevOps Serverがインストール済み
- IISがインストールされ実行中
- OpenSSLが利用可能（Git for WindowsにはOpenSSLが含まれます）
- 管理者権限

#### 方法1: 自動インストール（PowerShellスクリプト）

**ステップ1: CAサーバから証明書をエクスポート**

```bash
# CAサーバ上で実行
cd /root/aws.git/container/claudecode/CA
./scripts/export-certificates.sh

# Azure DevOps Serverに転送
# バンドルには以下が含まれます: ca.crt, server.crt, server.key, server-chain.crt
```

**ステップ2: 証明書バンドルをAzure DevOps Serverに転送**

```bash
# CAサーバからDevOpsサーバへ
scp certs/export/ca-bundle-*.tar.gz administrator@devops-server:C:\Temp\
```

**ステップ3: 展開してインストールスクリプトを実行**

Azure DevOps Server上で（PowerShellを管理者として）:

```powershell
# 証明書バンドルを展開
cd C:\Temp
tar -xzf ca-bundle-*.tar.gz

# CAサーバからインストールスクリプトをダウンロード
Invoke-WebRequest -Uri "http://98.93.187.130:8080/install-cert-devops-server.ps1" -OutFile "install-cert-devops-server.ps1"

# または展開されたバンドルから利用可能な場合はコピー
# scripts\install-cert-devops-server.ps1を現在のディレクトリにコピー

# インストールスクリプトを実行
powershell -ExecutionPolicy Bypass -File install-cert-devops-server.ps1 -CertificateBundle "C:\Temp\ca-bundle-20260120-013115"
```

**スクリプトが実行する処理:**
1. ✅ 信頼されたルート証明機関にCA証明書をインストール
2. ✅ 証明書と秘密鍵からPFXファイルを作成
3. ✅ 個人証明書ストアにサーバ証明書をインポート
4. ✅ IISのHTTPSバインディングを設定（ポート443）
5. ✅ Azure DevOps Server設定手順を表示

**ステップ4: Azure DevOps Serverの設定**

スクリプト完了後:

1. **Azure DevOps Server管理コンソールを開く**

2. **アプリケーション層** → **URLの変更**に移動

3. **パブリックURL**をHTTPSに更新:
   ```
   https://your-devops-server.domain.com/
   ```

4. **OK**をクリックして変更を適用

5. **Azure DevOps Serverサービスを再起動:**
   - サービス（`services.msc`）を開く
   - "Azure DevOps Server"および関連サービスを再起動
   - またはPowerShellを使用:
   ```powershell
   Restart-Service "Azure DevOps Server"
   Restart-Service "VSS*"
   ```

6. **HTTPSアクセスをテスト:**
   ```
   https://your-devops-server.domain.com/
   ```

#### 方法2: 手動インストール

手動インストールを希望する場合:

**ステップ1: CA証明書のインストール**

```powershell
# 信頼されたルートにCA証明書をインポート
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2("C:\Temp\ca-bundle-xxx\ca.crt")

$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root","LocalMachine")
$store.Open("ReadWrite")
$store.Add($cert)
$store.Close()

Write-Host "CA証明書がインストールされました"
```

**ステップ2: 証明書と鍵からPFXを作成**

```powershell
# OpenSSLを使用（Git for Windowsから）
cd "C:\Temp\ca-bundle-xxx"

# PFXを作成
& "C:\Program Files\Git\usr\bin\openssl.exe" pkcs12 -export `
  -out server.pfx `
  -inkey server.key `
  -in server.crt `
  -certfile ca.crt `
  -password pass:YourPassword

# またはGUIを使用: インポートウィザードはPFX形式が必要
```

**ステップ3: サーバ証明書のインポート**

```powershell
# 個人ストアにPFXをインポート
$pfxPassword = ConvertTo-SecureString -String "YourPassword" -AsPlainText -Force

$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2(
    "C:\Temp\ca-bundle-xxx\server.pfx",
    $pfxPassword,
    [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::MachineKeySet
)

$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("My","LocalMachine")
$store.Open("ReadWrite")
$store.Add($cert)
$store.Close()

Write-Host "サーバ証明書がインストールされました"
Write-Host "サムプリント: $($cert.Thumbprint)"
```

**ステップ4: IISのHTTPSバインディングを設定**

方法A: IISマネージャー（GUI）を使用

1. **IISマネージャー**（`inetmgr`）を開く
2. **Azure DevOps Serverサイト**（または"既定のWebサイト"）を選択
3. アクションペインの**"バインド..."**をクリック
4. HTTPSの**"追加..."**または**"編集..."**をクリック
5. **種類:** https
6. **ポート:** 443
7. **SSL証明書:** サーバ証明書を選択（サブジェクト/CNが表示されます）
8. **OK**をクリック

方法B: PowerShellを使用

```powershell
Import-Module WebAdministration

# 既存のHTTPSバインディングを削除（存在する場合）
Remove-WebBinding -Name "Default Web Site" -Protocol "https" -Port 443 -ErrorAction SilentlyContinue

# 新しいHTTPSバインディングを追加
New-WebBinding -Name "Default Web Site" -Protocol "https" -Port 443 -SslFlags 0

# 証明書のサムプリントを取得
$cert = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.Subject -like "*your-server-name*" }

# 証明書をバインド
$binding = Get-WebBinding -Name "Default Web Site" -Protocol "https" -Port 443
$binding.AddSslCertificate($cert.Thumbprint, "My")

Write-Host "HTTPSバインディングが設定されました"
```

**ステップ5: IIS設定のテスト**

```powershell
# HTTPSバインディングをテスト
netstat -an | findstr ":443"

# 以下が表示されるはずです:
# TCP    0.0.0.0:443            0.0.0.0:0              LISTENING

# ブラウザまたはcurlでテスト
curl https://localhost/ -k
```

**ステップ6: Azure DevOps Server設定の更新**

方法1のステップ4（Azure DevOps Server管理コンソール設定）に従ってください。

#### Azure DevOps Server HTTPSのトラブルシューティング

**問題: IISに証明書が表示されない**

解決策:
```powershell
# 個人ストアに証明書があることを確認
Get-ChildItem -Path Cert:\LocalMachine\My | Format-List Subject, Issuer, Thumbprint

# 証明書に秘密鍵があることを確認
Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.HasPrivateKey } | Format-List Subject
```

**問題: IISが"指定されたネットワークパスワードが正しくありません"と表示**

解決策: 証明書がマシンストアではなくユーザーストアにインポートされました
```powershell
# MachineKeySetフラグで再インポート
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2(
    "server.pfx",
    $password,
    [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::MachineKeySet
)
```

**問題: Azure DevOps ServerがまだHTTPを使用している**

解決策:
1. 管理コンソールでアプリケーション層URLを確認
2. IISバインディングがアクティブであることを確認: `Get-WebBinding -Name "Default Web Site"`
3. Azure DevOpsサービスを再起動
4. ブラウザキャッシュをクリア

**問題: クライアントがまだ証明書警告を表示する**

解決策: クライアントはCA証明書（ca.crt）をインストールする必要があります - クライアントインストールについてはセクション6を参照してください。

#### Azure DevOps Serverのセキュリティベストプラクティス

1. **強力なPFXパスワードを使用** - 安全に保管し、ソース管理にコミットしない
2. **証明書秘密鍵のアクセスを制限** - サービスアカウントのみがアクセスする必要があります
3. **HTTPS専用を有効化** - IISでHTTPをHTTPSにリダイレクト
4. **ファイアウォールルールを更新** - ポート443を許可、必要に応じてポート80をブロック
5. **証明書の有効期限を監視** - 証明書の期限が切れる前にリマインダーを設定（730日）
6. **証明書をバックアップ** - PFXとパスワードを安全な場所に保管

#### ファイアウォール設定

```powershell
# HTTPS（ポート443）を許可
New-NetFirewallRule -DisplayName "Azure DevOps HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# オプション: HTTPSが動作した後にHTTP（ポート80）をブロック
New-NetFirewallRule -DisplayName "Block Azure DevOps HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Block
```

---

### Linux（Ubuntu/Debian）

```bash
# 証明書バンドルを展開
tar xzf ca-bundle-*.tar.gz
cd ca-bundle-*/

# CA証明書をインストール
sudo cp ca.crt /usr/local/share/ca-certificates/onpremise-ca.crt
sudo update-ca-certificates

# 接続をテスト
curl https://98.93.187.130:5006/
```

### Linux（CentOS/RHEL）

```bash
# CA証明書をインストール
sudo cp ca.crt /etc/pki/ca-trust/source/anchors/onpremise-ca.crt
sudo update-ca-trust
```

### Windows

**コマンドライン（管理者）:**
```cmd
certutil -addstore -f "ROOT" ca.crt
```

**GUI:**
1. `ca.crt`をダブルクリック
2. "証明書のインストール"をクリック
3. "ローカルコンピューター"を選択
4. "信頼されたルート証明機関"を選択
5. "完了"をクリック

### macOS

```bash
sudo security add-trusted-cert -d -r trustRoot \
    -k /Library/Keychains/System.keychain ca.crt
```

### Webサーバ

#### Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name your-server.com;

    ssl_certificate /etc/nginx/certs/server-chain.crt;
    ssl_certificate_key /etc/nginx/certs/server.key;

    # ... その他の設定
}
```

#### Apache

```apache
<VirtualHost *:443>
    ServerName your-server.com

    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/server.crt
    SSLCertificateKeyFile /etc/ssl/private/server.key
    SSLCertificateChainFile /etc/ssl/certs/ca.crt

    # ... その他の設定
</VirtualHost>
```

## 11. セキュリティ上の考慮事項

### 秘密鍵の保護

**秘密鍵は保護する必要があります:**
- バージョン管理にコミットしない（gitignore済み）
- 権限を600に設定（所有者のみ読み書き可能）
- バックアップは暗号化されたストレージに保管
- 定期的にローテーション

```bash
# 適切な権限
chmod 600 certs/ca/ca.key
chmod 600 certs/server/server.key
```

### 証明書の有効期限

- デフォルト有効期限: 730日（2年）
- 有効期限を監視
- 有効期限前に更新
- デプロイ前に更新された証明書をテスト

```bash
# 有効期限を確認
openssl x509 -in certs/server/server.crt -noout -dates
```

### アクセス制御

- HTTPSサーバは外部IPからアクセス可能（IP制限なし）
- 本番環境向け: ファイアウォールでIPホワイトリストを実装
- 強力なTLS設定を使用（TLS 1.2以降）
- OpenSSLとDockerを最新に保つ

## 12. トラブルシューティング

### 証明書生成の問題

**エラー: OpenSSLが見つかりません**
```bash
# OpenSSLをインストール
sudo yum install openssl          # CentOS/RHEL
sudo apt-get install openssl      # Ubuntu/Debian
```

**エラー: .envファイルが見つかりません**
```bash
# セットアップスクリプトを実行
./scripts/setup-ca-environment.sh
```

**エラー: 権限が拒否されました**
```bash
# 実行権限を設定
chmod +x scripts/*.sh scripts/utils/*.sh
```

### Dockerの問題

**エラー: 権限が拒否されました（dockerソケット）**
```bash
# sudoを使用
sudo docker-compose up -d
```

**エラー: ポート5006が既に使用中です**
```bash
# ポートを使用しているものを確認
sudo netstat -tlnp | grep 5006

# .envとdocker-compose.ymlでポートを変更
# または競合するサービスを停止
```

**エラー: コンテナがヘルスチェックに失敗します**
```bash
# ログを確認
sudo docker-compose logs ca-https-test

# 証明書が正しくマウントされているか確認
sudo docker-compose exec ca-https-test ls -la /etc/nginx/certs/

# コンテナを再起動
sudo docker-compose restart
```

### 接続の問題

**エラー: 接続が拒否されました**
```bash
# コンテナが実行中か確認
sudo docker-compose ps

# ファイアウォールを確認
sudo firewall-cmd --list-ports
sudo firewall-cmd --add-port=5006/tcp --permanent
sudo firewall-cmd --reload
```

**エラー: 証明書の検証に失敗しました**
```bash
# クライアントマシンにCA証明書をインストール
# またはテスト用に-kフラグを使用して検証をスキップ
curl -k https://98.93.187.130:5006/
```

**ブラウザがセキュリティ警告を表示**
- ブラウザにCA証明書をインポート（"証明書の使用"セクション参照）
- Firefox向け: 組み込みの証明書マネージャーを使用
- Chrome/Edge向け: OSトラストストアにCA証明書をインストール

### 証明書の問題

**エラー: 証明書の有効期限が切れています**
```bash
# 証明書を再生成
rm -rf certs/ca/* certs/server/*
./scripts/create-ca.sh
sudo docker-compose restart
```

**エラー: 証明書チェーンの検証に失敗しました**
```bash
# 証明書チェーンを検証
./scripts/utils/verify-certificates.sh

# CA証明書がサーバ証明書に署名したか確認
openssl verify -CAfile certs/ca/ca.crt certs/server/server.crt
```

## 13. アーキテクチャ

### 証明書階層

```
OnPremise-CA-Root（CA証明書）
  └── 自己署名、4096-bit RSA
      └── 730日間有効
          └── サーバ証明書に署名
              │
              └── サーバ証明書（server.crt）
                  └── 2048-bit RSA
                  └── 730日間有効
                  └── SubjectAltName: DNS + IP
```

### 証明書チェーン

```
クライアント ←→ HTTPSサーバ
          │
          └── 提示: server-chain.crt
              │
              ├── サーバ証明書（server.crt）
              │   └── CAで署名
              │
              └── CA証明書（ca.crt）
                  └── 自己署名
```

### Dockerアーキテクチャ

```
Host:5006 ←→ Dockerブリッジ ←→ Container:443
              (ca-network)
                  │
                  └── Nginx HTTPSサーバ
                      ├── マウント: server.crt
                      ├── マウント: server.key
                      ├── マウント: server-chain.crt
                      ├── マウント: nginx.conf
                      └── マウント: index.html
```

## 14. メンテナンス

### 定期的なタスク

**証明書有効期限の確認**（月次）
```bash
# 有効期限を確認
openssl x509 -in certs/ca/ca.crt -noout -enddate
openssl x509 -in certs/server/server.crt -noout -enddate

# 有効期限までの日数を取得
openssl x509 -in certs/server/server.crt -noout -checkend 2592000
```

**証明書の検証**（月次）
```bash
./scripts/utils/verify-certificates.sh
```

**コンテナヘルスの確認**（週次）
```bash
sudo docker-compose ps
sudo docker-compose logs --tail=100 ca-https-test
```

**ログのレビュー**（週次）
```bash
cat logs/certificate-generation.log
sudo docker-compose logs ca-https-test
```

### 証明書の更新

証明書の有効期限が近い場合:

```bash
# 1. 既存の証明書をバックアップ
tar czf certs-backup-$(date +%Y%m%d).tar.gz certs/

# 2. 新しい証明書を生成
./scripts/create-ca.sh

# 3. HTTPSサーバを再起動
sudo docker-compose restart

# 4. 新しい証明書を検証
./scripts/utils/verify-certificates.sh
curl -k https://98.93.187.130:5006/

# 5. 他サーバ用にエクスポート
./scripts/export-certificates.sh
```

## 15. パフォーマンス

### リソース使用量

- **CPU**: 最小限（Nginxは軽量）
- **メモリ**: 約10-20MB（Alpineベースのコンテナ）
- **ディスク**: 約50MB（コンテナイメージ + 証明書）
- **ネットワーク**: 無視できる（テストサーバのみ）

### スケーリング

本番環境での使用:
- 複数のHTTPSサーバでロードバランサーを使用
- 証明書配布の自動化を実装
- 証明書有効期限の監視とアラートを設定
- 公開サービス向けにLet's Encryptの使用を検討

## 16. CICDプロジェクトとの統合

このCA基盤は、より大きなCICDプロジェクトの一部です：

- **独立**: 別個のdockerネットワーク（ca-network）
- **ポート割り当て**: ポート5006（CICDサービスと競合しない）
- **環境変数**: 親の.envからEC2_PUBLIC_IPを継承可能
- **ドキュメントパターン**: CICDプロジェクトと同じ構造に従う

## 17. FAQ

**Q: 本番環境でこれらの証明書を使用できますか？**
A: これらはオンプレミスクローズド環境に適した自己署名証明書です。公開サービス向けには、信頼されたCA（例: Let's Encrypt）からの証明書を使用してください。

**Q: 証明書生成後にサーバ名を変更するにはどうすればよいですか？**
A: 新しいサーバ名で証明書を再生成します：
```bash
rm -rf certs/server/*
./scripts/create-ca.sh
sudo docker-compose restart
```

**Q: 同じCAを使用して複数のサーバ証明書に署名できますか？**
A: はい！CA証明書と鍵は再利用できます。異なるサーバ名でcreate-ca.shを実行するだけです。スクリプトは既に存在する場合、CA生成をスキップします。

**Q: docker-composeにsudoが必要なのはなぜですか？**
A: これはissue #119で指定された要件です。Dockerは、Dockerソケットにアクセスしてコンテナを管理するために管理者権限が必要です。

**Q: ポート5006から変更できますか？**
A: はい。`.env`の`HTTPS_PORT`と`docker-compose.yml`のポートマッピングを更新してください。

**Q: ブラウザのセキュリティ警告を削除するにはどうすればよいですか？**
A: CA証明書（ca.crt）をブラウザまたはシステムトラストストアにインポートしてください。"他サーバでの証明書使用"セクションを参照してください。

## 18. ライセンス

このプロジェクトは、オンプレミス環境向けCICD基盤の一部です。

## 19. サポート

問題や質問がある場合:
- このREADMEを徹底的に確認してください
- ログをレビュー: `logs/certificate-generation.log`
- コンテナログを確認: `sudo docker-compose logs ca-https-test`
- QUICKSTART.mdで一般的なタスクを参照してください
- 課題追跡: GitHub issues

## 20. バージョン

現在のバージョン: 1.0.0

## 21. 関連ドキュメント

- [QUICKSTART.md](QUICKSTART.md) - クイックスタートガイド
- [../CICD/README.md](../CICD/README.md) - 親CICDプロジェクトドキュメント
- [../CICD/CLAUDE.md](../CICD/CLAUDE.md) - Claude Codeプロジェクトガイド
