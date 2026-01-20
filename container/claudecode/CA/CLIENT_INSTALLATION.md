# クライアント側CA証明書インストールガイド

このドキュメントでは、自己署名CA証明書をクライアントマシンにインストールして、HTTPSサーバへの接続時にブラウザの警告を解消する方法を説明します。

## 目次

1. [概要](#概要)
2. [自動インストール（推奨）](#自動インストール推奨)
3. [手動インストール](#手動インストール)
4. [必要なファイル](#必要なファイル)

## 概要

### "保護されていない通信"警告が表示される理由

ブラウザからHTTPSサーバにアクセスすると、**"保護されていない通信"または"この接続ではプライバシーが保護されません"**という警告が表示されます。これは、ブラウザがまだ当社の自己署名CA証明書を信頼していないためです。

**これが発生する理由:**
- 当社のCA証明書は自己署名です（信頼された認証局から発行されたものではありません）
- ブラウザのトラストストアに当社のCA証明書がありません
- これは自己署名証明書の予想される動作です

**解決策:** クライアントマシンにCA証明書（`ca.crt`）をインストールします。

## 自動インストール（推奨）

クライアントマシンにCA証明書をインストールする最も簡単な方法は、自動インストールスクリプトを使用することです。

### ステップ1: 証明書ダウンロードサーバの起動（サーバ側）

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
  http://<SERVER_IP>:8080/ca.crt

Client Installation Scripts:
  Windows: http://<SERVER_IP>:8080/install-ca-windows.ps1
  Linux:   http://<SERVER_IP>:8080/install-ca-linux.sh
  macOS:   http://<SERVER_IP>:8080/install-ca-macos.sh
```

クライアントが証明書をダウンロードしてインストールする間、**このサーバを実行し続けてください**。

### ステップ2-A: 自動インストール - Windows

**Windowsクライアントマシン上で:**

1. **PowerShellスクリプトをダウンロード:**
   - ブラウザで `http://<SERVER_IP>:8080/install-ca-windows.ps1` にアクセス
   - またはPowerShellを使用:
   ```powershell
   Invoke-WebRequest -Uri "http://<SERVER_IP>:8080/install-ca-windows.ps1" -OutFile "install-ca-windows.ps1"
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

4. **ブラウザを完全に再起動**して `https://<SERVER_IP>:5006/` にアクセス

### ステップ2-B: 自動インストール - Linux

**Linuxクライアントマシン上で:**

```bash
# インストールスクリプトをダウンロードして実行
curl -O http://<SERVER_IP>:8080/install-ca-linux.sh
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

### ステップ2-C: 自動インストール - macOS

**macOSクライアントマシン上で:**

```bash
# インストールスクリプトをダウンロードして実行
curl -O http://<SERVER_IP>:8080/install-ca-macos.sh
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

### 自動インストールスクリプトの動作

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

## 手動インストール

自動スクリプトが機能しない場合や手動インストールを希望する場合は、以下の手順に従ってください：

### 1. CA証明書のダウンロード

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

#### Chrome/Edge/Chromiumからのエクスポート

1. `https://<SERVER_IP>:5006/` にアクセス（警告が表示されても可）
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

#### Firefoxからのエクスポート

1. `https://<SERVER_IP>:5006/` にアクセス（警告が表示されても可）
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

#### Safari（Mac）からのエクスポート

1. `https://<SERVER_IP>:5006/` にアクセス（警告が表示されても可）
2. アドレスバーの**ロックアイコン**または**警告テキスト**をクリック
3. **"証明書を表示"**をクリック
4. 証明書チェーンを探します
5. **ルート証明書**を選択: "OnPremise-CA-Root"
6. 証明書アイコンをデスクトップまたはFinderにドラッグ
   - これにより`.cer`ファイルとして保存されます
7. 必要に応じて`ca.crt`にリネーム（オプション）

#### ダウンロードした証明書の検証

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

### 2. 重要: 正しい証明書の確認

**⚠️ クライアントマシンにサーバ証明書をインストールしないでください！**

これが最も一般的な誤りです：

| 証明書 | ファイル | サブジェクト (CN) | 用途 | クライアントにインストール? |
|------------|------|--------------|---------|-------------------|
| ❌ サーバ証明書 | `server.crt` | CN=your-server-name | HTTPSサーバで使用 | **NO - インストールしない!** |
| ✅ CA証明書 | `ca.crt` | CN=OnPremise-CA-Root | サーバ証明書に署名 | **YES - これをインストール!** |

**正しいファイルを持っているか確認する方法:**

```bash
# 証明書のサブジェクトを確認
openssl x509 -in your-file.crt -noout -subject

# 正しい（CA証明書）:
subject=C=JP, ST=Tokyo, L=Tokyo, O=OnPremise-CA, OU=IT, CN=OnPremise-CA-Root

# 誤り（サーバ証明書）:
subject=C=JP, ST=Tokyo, L=Tokyo, O=OnPremise-CA, OU=IT, CN=your-server-name
```

**誤ってサーバ証明書をインストールした場合:**
1. 証明書ストアから削除
2. 正しい`ca.crt`ファイルをダウンロード
3. `ca.crt`（CN=OnPremise-CA-Rootのファイル）をインストール

**避けるべき一般的な誤り:**
- ❌ サーバ証明書（CN=your-server-name）をエクスポートしない - CA証明書（CN=OnPremise-CA-Root）をエクスポート
- ❌ `.pfx`または`.p12`形式で保存しない（これらはパスワードが必要で、異なる目的のためのものです）
- ❌ 証明書チェーン全体をエクスポートしない - ルートCA証明書のみ
- ✅ 証明書のサブジェクト/発行者に"OnPremise-CA-Root"があることを確認

### 3. CA証明書のインストール

#### Linux（Ubuntu/Debian）

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
Firefoxは独自の証明書ストアを使用します（後述のFirefoxセクションを参照）。

#### Linux（CentOS/RHEL/Fedora）

```bash
# トラストストアにCA証明書をコピー
sudo cp ca.crt /etc/pki/ca-trust/source/anchors/onpremise-ca.crt

# トラストストアを更新
sudo update-ca-trust extract

# インストールを確認
trust list | grep "OnPremise-CA"

# ブラウザを再起動
```

#### Windows

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
- Firefoxは独自の証明書ストアを使用（後述のFirefoxセクションを参照）

#### macOS

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
- 独自の証明書ストアを使用（後述のFirefoxセクションを参照）

#### Firefox（全プラットフォーム）

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
12. **ページを更新**（F5）または`https://<SERVER_IP>:5006/`を再訪問

警告が消え、ロックアイコン🔒が表示されるはずです。

### 4. インストールの確認

CA証明書をインストールした後、動作することを確認します：

**ブラウザで:**
1. `https://<SERVER_IP>:5006/`にアクセス
2. アドレスバーに**ロックアイコン**🔒が表示されるはずです（警告三角形ではありません）
3. ロックアイコンをクリック
4. **"接続は保護されています"**または**"証明書"**をクリック
5. 確認:
   - 発行先: `your-server-name`
   - 発行者: `OnPremise-CA-Root`
   - 有効期間の開始: （証明書開始日）
   - 有効期間の終了: （証明書有効期限）

**コマンドラインテスト:**
```bash
# Linux/Mac
curl https://<SERVER_IP>:5006/

# CA証明書がシステム全体にインストールされている場合、-kフラグなしで動作するはずです
# 証明書エラーで失敗する場合、CA証明書が正しくインストールされていません

# Windows PowerShell
Invoke-WebRequest -Uri https://<SERVER_IP>:5006/

# 証明書エラーなしで動作するはずです
```

### 5. トラブルシューティング

#### 問題: インストール後もまだ"保護されていない通信"が表示される

解決策:
1. **ブラウザを完全に再起動**（タブだけでなく、すべてのウィンドウを閉じる）
2. **ブラウザキャッシュをクリア**: 設定 → プライバシー → 閲覧データを削除
3. **証明書が正しいストアにあるか確認**:
   - Windows: "信頼されたルート証明機関"にある必要があります、"個人"ではありません
   - Linux: sudoで`update-ca-certificates`を実行
   - Mac: 証明書を"常に信頼"に設定する必要があります
4. **Firefox向け**: OS経由ではなく、Firefox独自の証明書マネージャーでインストール
5. **ページをハードリフレッシュ**: Ctrl+Shift+R（Windows/Linux）またはCmd+Shift+R（Mac）

#### 問題: "このCAルート証明書は信頼されていません"

解決策:
1. `ca.crt`（`server.crt`ではない）をインストールしたことを確認
2. "信頼されたルート"ストアにインストール（中間または個人ではない）
3. Windowsでは、管理者としてcertutilを実行
4. Linuxでは、ca-certificatesディレクトリでファイル名が`.crt`で終わることを確認

#### 問題: Chromeが"NET::ERR_CERT_AUTHORITY_INVALID"と表示

解決策:
1. CA証明書がシステムトラストストアにありません
2. Linuxで: `sudo update-ca-certificates`を実行してChromeを再起動
3. Windowsで: certutilまたはGUI経由でインストール、Chromeを再起動
4. シークレット/プライベートモードで開いてテスト

#### 問題: Firefoxはまだ警告を表示するが、Chromeは動作する

解決策:
- Firefoxは別の証明書ストアを使用
- Firefox設定 → 証明書を通じてCA証明書をインポートする必要があります
- システムインストールはFirefoxに影響しません

---

## 必要なファイル

### クライアント側で必要なファイル

| ファイル | 場所 | 説明 | 必須 |
|---------|------|------|------|
| `ca.crt` | `certs/ca/ca.crt` | CA証明書 - クライアントにインストール | ✅ 必須 |

### サーバ側のファイル（参考）

| ファイル | 場所 | 説明 | クライアントに必要？ |
|---------|------|------|-------------------|
| `ca.key` | `certs/ca/ca.key` | CA秘密鍵 | ❌ 不要（サーバ側のみ） |
| `server.crt` | `certs/server/server.crt` | サーバ証明書 | ❌ 不要（サーバ側のみ） |
| `server.key` | `certs/server/server.key` | サーバ秘密鍵 | ❌ 不要（サーバ側のみ） |
| `server-chain.crt` | `certs/server/server-chain.crt` | 証明書チェーン | ❌ 不要（サーバ側のみ） |

### 自動インストールスクリプト

| ファイル | 場所 | 説明 |
|---------|------|------|
| `install-ca-windows.ps1` | `certs/ca/install-ca-windows.ps1` | Windows用自動インストールスクリプト |
| `install-ca-linux.sh` | `certs/ca/install-ca-linux.sh` | Linux用自動インストールスクリプト |
| `install-ca-macos.sh` | `certs/ca/install-ca-macos.sh` | macOS用自動インストールスクリプト |

これらのスクリプトは`./scripts/serve-cert.sh`を実行することで、HTTPサーバ経由でクライアントに配布されます。

---

## 関連ドキュメント

- [README.md](README.md) - メインドキュメント
- [AZURE_DEVOPS_SETUP.md](AZURE_DEVOPS_SETUP.md) - Azure DevOps Server設定ガイド
- [QUICKSTART.md](QUICKSTART.md) - クイックスタートガイド
