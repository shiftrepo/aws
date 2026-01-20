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
curl -k https://<SERVER_IP>:5006/
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
- サーバ名の入力を求められます（デフォルト: .envで設定されたサーバ名）
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
curl -k https://<SERVER_IP>:5006/

# CA証明書をインストール後の検証付きテスト
curl --cacert ca.crt https://<SERVER_IP>:5006/
```

**ブラウザテスト:**
```
https://<SERVER_IP>:5006/
```

### 6. クライアントへのCA証明書インストール

クライアントマシンからHTTPSサーバにアクセスする際、ブラウザが"保護されていない通信"警告を表示しないように、CA証明書（`ca.crt`）をインストールする必要があります。

**📖 詳細なクライアントインストール手順:**

クライアントへのCA証明書インストールに関する包括的なガイドは、専用ドキュメントを参照してください：

👉 **[CLIENT_INSTALLATION.md](CLIENT_INSTALLATION.md)**

このドキュメントには以下が含まれます：
- 自動インストールスクリプト（Windows/Linux/macOS）の使用方法
- 手動インストール手順（全OS向け）
- ブラウザ固有の設定（Chrome, Firefox, Safari, Edge）
- インストール確認方法
- トラブルシューティングガイド

**クイックリファレンス:**

```bash
# 証明書ダウンロードサーバを起動（サーバ側）
./scripts/serve-cert.sh

# クライアント側（自動インストール）
# Windows: http://<SERVER_IP>:8080/install-ca-windows.ps1 をダウンロードして実行
# Linux:   curl -O http://<SERVER_IP>:8080/install-ca-linux.sh && chmod +x install-ca-linux.sh && sudo ./install-ca-linux.sh
# macOS:   curl -O http://<SERVER_IP>:8080/install-ca-macos.sh && chmod +x install-ca-macos.sh && sudo ./install-ca-macos.sh
```

### 7. 証明書のエクスポート

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

## 8. 設定

### 環境変数（.env）

```bash
# サーバ設定
SERVER_NAME=your-server-name       # サーバホスト名またはIP
HTTPS_PORT=5006                    # 外部HTTPSポート
CERT_VALIDITY_DAYS=730             # 証明書有効期限（2年）

# 証明書サブジェクト情報
CERT_COUNTRY=JP                    # 国コード
CERT_STATE=Tokyo                   # 都道府県
CERT_LOCALITY=Tokyo                # 市区町村
CERT_ORGANIZATION=OnPremise-CA     # 組織名
CERT_ORG_UNIT=IT                   # 部門

# 外部アクセス
EC2_PUBLIC_IP=your-server-ip       # パブリックIPアドレス

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

## 9. 他サーバでの証明書使用

### Azure DevOps Server（オンプレミス）

Azure DevOps Serverに証明書をインストールしてHTTPSを有効化する詳細な手順については、専用ドキュメントを参照してください：

👉 **[AZURE_DEVOPS_SETUP.md](AZURE_DEVOPS_SETUP.md)**

このドキュメントには以下が含まれます：
- 前提条件と必要なファイル
- 自動インストール（PowerShellスクリプト）
- 手動インストール手順（6ステップ）
- IIS HTTPSバインディング設定（GUIとPowerShell）
- Azure DevOps Server管理コンソール設定
- トラブルシューティングガイド
- セキュリティベストプラクティス

**クイックリファレンス:**

```bash
# 1. CAサーバで証明書をエクスポート
./scripts/export-certificates.sh

# 2. Azure DevOps Serverに転送
scp certs/export/ca-bundle-*.tar.gz administrator@devops-server:C:\Temp\

# 3. DevOpsサーバ上で自動インストールスクリプトを実行
# 詳細はAZURE_DEVOPS_SETUP.mdを参照
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
curl https://<SERVER_IP>:5006/
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

## 10. セキュリティ上の考慮事項

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

## 11. トラブルシューティング

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
curl -k https://<SERVER_IP>:5006/
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

## 12. アーキテクチャ

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

## 13. メンテナンス

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
curl -k https://<SERVER_IP>:5006/

# 5. 他サーバ用にエクスポート
./scripts/export-certificates.sh
```

## 14. パフォーマンス

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

## 15. CICDプロジェクトとの統合

このCA基盤は、より大きなCICDプロジェクトの一部です：

- **独立**: 別個のdockerネットワーク（ca-network）
- **ポート割り当て**: ポート5006（CICDサービスと競合しない）
- **環境変数**: 親の.envからEC2_PUBLIC_IPを継承可能
- **ドキュメントパターン**: CICDプロジェクトと同じ構造に従う

## 16. FAQ

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

## 17. ライセンス

このプロジェクトは、オンプレミス環境向けCICD基盤の一部です。

## 18. サポート

問題や質問がある場合:
- このREADMEを徹底的に確認してください
- ログをレビュー: `logs/certificate-generation.log`
- コンテナログを確認: `sudo docker-compose logs ca-https-test`
- QUICKSTART.mdで一般的なタスクを参照してください
- 課題追跡: GitHub issues

## 19. バージョン

現在のバージョン: 1.0.0

## 20. 関連ドキュメント

- [QUICKSTART.md](QUICKSTART.md) - クイックスタートガイド
- [CLIENT_INSTALLATION.md](CLIENT_INSTALLATION.md) - クライアントへのCA証明書インストール手順
- [AZURE_DEVOPS_SETUP.md](AZURE_DEVOPS_SETUP.md) - Azure DevOps Server HTTPS設定ガイド
- [../CICD/README.md](../CICD/README.md) - 親CICDプロジェクトドキュメント
- [../CICD/CLAUDE.md](../CICD/CLAUDE.md) - Claude Codeプロジェクトガイド
