# Azure DevOps Server HTTPS設定ガイド

このドキュメントでは、CA証明書基盤で生成した証明書を使用して、Azure DevOps Server（オンプレミス）にHTTPSを設定する方法を説明します。

## 目次

1. [概要](#概要)
2. [前提条件](#前提条件)
3. [必要なファイル](#必要なファイル)
4. [方法1: 自動インストール](#方法1-自動インストール)
5. [方法2: 手動インストール](#方法2-手動インストール)
6. [トラブルシューティング](#トラブルシューティング)
7. [セキュリティベストプラクティス](#セキュリティベストプラクティス)

## 概要

Azure DevOps Serverには、以下の証明書が必要です：
- **CA証明書**（ca.crt）- クライアント信頼用
- **サーバ証明書**（server.crt）- HTTPS動作用
- **サーバ秘密鍵**（server.key）- HTTPS動作用

このガイドでは、これらの証明書をAzure DevOps ServerとIISに正しくインストールし、HTTPSを有効化する手順を説明します。

## 前提条件

- Windows ServerにAzure DevOps Serverがインストール済み
- IISがインストールされ実行中
- OpenSSLが利用可能（Git for WindowsにはOpenSSLが含まれます）
- 管理者権限
- CA証明書基盤から証明書がエクスポート済み

## 必要なファイル

### Azure DevOps Serverで使用するファイル

| ファイル | 場所（エクスポート後） | 説明 | 用途 |
|---------|---------------------|------|------|
| `ca.crt` | `ca-bundle-*/ca.crt` | CA証明書 | LocalMachine\Rootにインストール |
| `server.crt` | `ca-bundle-*/server.crt` | サーバ証明書 | PFXに変換してインストール |
| `server.key` | `ca-bundle-*/server.key` | サーバ秘密鍵 | PFXに変換してインストール |
| `server-chain.crt` | `ca-bundle-*/server-chain.crt` | 証明書チェーン | （オプション）IISで使用可能 |

### 自動インストールスクリプト

| ファイル | 場所 | 説明 |
|---------|------|------|
| `install-cert-devops-server.ps1` | `scripts/install-cert-devops-server.ps1` | Azure DevOps Server用自動インストールスクリプト |

## 方法1: 自動インストール

自動インストールスクリプトを使用すると、すべての手順が自動化されます。

### ステップ1: CAサーバから証明書をエクスポート

CAサーバ上で実行：

```bash
# CAサーバ上で実行
cd /root/aws.git/container/claudecode/CA
./scripts/export-certificates.sh

# エクスポートされたファイルを確認
ls -lh certs/export/ca-bundle-*.tar.gz

# Azure DevOps Serverに転送
# バンドルには以下が含まれます: ca.crt, server.crt, server.key, server-chain.crt
```

### ステップ2: 証明書バンドルをAzure DevOps Serverに転送

```bash
# CAサーバからDevOpsサーバへ
scp certs/export/ca-bundle-*.tar.gz administrator@devops-server:C:\Temp\
```

### ステップ3: 展開してインストールスクリプトを実行

Azure DevOps Server上で（PowerShellを管理者として実行）:

```powershell
# 証明書バンドルを展開
cd C:\Temp
tar -xzf ca-bundle-*.tar.gz

# CAサーバからインストールスクリプトをダウンロード
# オプション1: HTTPサーバから取得（CAサーバで ./scripts/serve-cert.sh を実行している場合）
Invoke-WebRequest -Uri "http://<SERVER_IP>:8080/install-cert-devops-server.ps1" -OutFile "install-cert-devops-server.ps1"

# オプション2: ファイルを直接コピー
# CAサーバから scripts\install-cert-devops-server.ps1 を転送

# インストールスクリプトを実行
powershell -ExecutionPolicy Bypass -File install-cert-devops-server.ps1 -CertificateBundle "C:\Temp\ca-bundle-YYYYMMDD-HHMMSS"
```

**注意:** `ca-bundle-YYYYMMDD-HHMMSS` は実際のディレクトリ名に置き換えてください（例: ca-bundle-20260120-013115）。

### スクリプトが実行する処理

自動インストールスクリプトは以下を実行します：

1. ✅ **CA証明書のインストール** - 信頼されたルート証明機関にCA証明書をインストール
2. ✅ **PFXファイルの作成** - 証明書と秘密鍵からPFXファイルを作成
3. ✅ **サーバ証明書のインポート** - 個人証明書ストアにサーバ証明書をインポート
4. ✅ **IIS HTTPSバインディングの設定** - IISのHTTPSバインディングを設定（ポート443）
5. ✅ **設定手順の表示** - Azure DevOps Server設定手順を表示

### ステップ4: Azure DevOps Serverの設定

スクリプト完了後、Azure DevOps Serverの設定を更新します：

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

---

## 方法2: 手動インストール

自動スクリプトが利用できない場合や、手動で設定したい場合は、以下の手順に従ってください。

### ステップ1: CA証明書のインストール

Azure DevOps Server上で（PowerShellを管理者として実行）:

```powershell
# 信頼されたルートにCA証明書をインポート
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2("C:\Temp\ca-bundle-xxx\ca.crt")

$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root","LocalMachine")
$store.Open("ReadWrite")
$store.Add($cert)
$store.Close()

Write-Host "CA証明書がインストールされました"
```

### ステップ2: 証明書と鍵からPFXを作成

IISではPFX（PKCS#12）形式が必要なため、証明書と秘密鍵を結合します：

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

# パスワードは安全なものを使用してください
```

**注意:** `YourPassword` は強力なパスワードに置き換えてください。このパスワードは次のステップで必要になります。

### ステップ3: サーバ証明書のインポート

PFXファイルを個人証明書ストア（LocalMachine\My）にインポートします：

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

**重要:** `MachineKeySet` フラグを指定することで、IISがこの証明書にアクセスできるようになります。

### ステップ4: IISのHTTPSバインディングを設定

#### 方法A: IISマネージャー（GUI）を使用

1. **IISマネージャー**（`inetmgr`）を開く
2. **Azure DevOps Serverサイト**（または"既定のWebサイト"）を選択
3. アクションペインの**"バインド..."**をクリック
4. HTTPSの**"追加..."**または**"編集..."**をクリック
5. **種類:** https
6. **ポート:** 443
7. **SSL証明書:** サーバ証明書を選択（サブジェクト/CNが表示されます）
8. **OK**をクリック

#### 方法B: PowerShellを使用

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

### ステップ5: IIS設定のテスト

```powershell
# HTTPSバインディングをテスト
netstat -an | findstr ":443"

# 以下が表示されるはずです:
# TCP    0.0.0.0:443            0.0.0.0:0              LISTENING

# ブラウザまたはcurlでテスト
curl https://localhost/ -k
```

### ステップ6: Azure DevOps Server設定の更新

方法1のステップ4（Azure DevOps Server管理コンソール設定）に従ってください。

---

## トラブルシューティング

### 問題: IISに証明書が表示されない

**症状:** IISマネージャーのSSL証明書一覧に、インポートした証明書が表示されません。

**解決策:**

```powershell
# 個人ストアに証明書があることを確認
Get-ChildItem -Path Cert:\LocalMachine\My | Format-List Subject, Issuer, Thumbprint

# 証明書に秘密鍵があることを確認
Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.HasPrivateKey } | Format-List Subject
```

秘密鍵がない場合、PFXインポート時に `MachineKeySet` フラグを指定していないことが原因です。ステップ3を再実行してください。

### 問題: IISが"指定されたネットワークパスワードが正しくありません"と表示

**症状:** IISバインディング設定時に、証明書を選択すると上記のエラーが表示されます。

**原因:** 証明書がマシンストアではなくユーザーストアにインポートされました。

**解決策:**

```powershell
# MachineKeySetフラグで再インポート
$pfxPassword = ConvertTo-SecureString -String "YourPassword" -AsPlainText -Force

$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2(
    "server.pfx",
    $pfxPassword,
    [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::MachineKeySet
)

$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("My","LocalMachine")
$store.Open("ReadWrite")
$store.Add($cert)
$store.Close()
```

### 問題: Azure DevOps ServerがまだHTTPを使用している

**症状:** IISは正しく設定されているが、Azure DevOps Serverは依然としてHTTPでアクセスを返します。

**解決策:**

1. **管理コンソールでアプリケーション層URLを確認**
   - Azure DevOps Server管理コンソールを開く
   - アプリケーション層 → 設定を確認
   - パブリックURLが `https://` で始まることを確認

2. **IISバインディングがアクティブであることを確認**
   ```powershell
   Get-WebBinding -Name "Default Web Site"
   ```

3. **Azure DevOpsサービスを再起動**
   ```powershell
   Restart-Service "Azure DevOps Server"
   Restart-Service "VSS*"
   ```

4. **ブラウザキャッシュをクリア**
   - ブラウザのキャッシュと Cookie をクリア
   - ブラウザを再起動

### 問題: クライアントがまだ証明書警告を表示する

**症状:** Azure DevOps ServerはHTTPSで動作しているが、クライアントのブラウザで証明書警告が表示されます。

**原因:** クライアントマシンにCA証明書がインストールされていません。

**解決策:**

クライアント側にCA証明書（ca.crt）をインストールする必要があります。詳細は [CLIENT_INSTALLATION.md](CLIENT_INSTALLATION.md) を参照してください。

### 問題: ポート443が既に使用されている

**症状:** HTTPSバインディングを追加しようとすると、"ポート443は既に使用されています"というエラーが表示されます。

**解決策:**

```powershell
# ポート443を使用しているプロセスを確認
netstat -ano | findstr ":443"

# 既存のバインディングを確認
Get-WebBinding | Where-Object { $_.bindingInformation -like "*:443:*" }

# 既存のHTTPSバインディングを削除
Remove-WebBinding -Name "既存のサイト名" -Protocol "https" -Port 443
```

---

## セキュリティベストプラクティス

Azure DevOps ServerでHTTPSを運用する際の推奨事項：

### 1. 強力なPFXパスワードを使用

- PFXファイル作成時には強力なパスワードを使用
- パスワードは安全な場所に保管
- ソース管理やドキュメントにパスワードをコミットしない

### 2. 証明書秘密鍵のアクセスを制限

- サーバ証明書の秘密鍵へのアクセスは、サービスアカウントのみに制限
- 不要なユーザーに権限を付与しない
- 定期的にアクセス権限を監査

### 3. HTTPS専用を有効化

IISでHTTPからHTTPSへのリダイレクトを設定：

```powershell
# URL Rewriteモジュールを使用してHTTP→HTTPSリダイレクト
# または、HTTPバインディングを削除してHTTPS専用にする
Remove-WebBinding -Name "Default Web Site" -Protocol "http" -Port 80
```

### 4. ファイアウォールルールを更新

Windows Firewallでポート443を許可し、必要に応じてポート80をブロック：

```powershell
# HTTPS（ポート443）を許可
New-NetFirewallRule -DisplayName "Azure DevOps HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# オプション: HTTPSが動作した後にHTTP（ポート80）をブロック
New-NetFirewallRule -DisplayName "Block Azure DevOps HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Block
```

### 5. 証明書の有効期限を監視

- 証明書の有効期限を追跡（デフォルト: 730日）
- 有効期限の30日前にアラートを設定
- 証明書更新プロセスを文書化

```powershell
# 証明書の有効期限を確認
$cert = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.Subject -like "*your-server-name*" }
Write-Host "有効期限: $($cert.NotAfter)"
```

### 6. 証明書をバックアップ

- PFXファイルとパスワードを安全な場所にバックアップ
- 暗号化されたストレージに保管
- バックアップの定期的なテストと検証

```powershell
# 証明書をPFXとしてエクスポート（バックアップ用）
$cert = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.Subject -like "*your-server-name*" }
$password = ConvertTo-SecureString -String "BackupPassword" -AsPlainText -Force
Export-PfxCertificate -Cert $cert -FilePath "C:\Backup\server-backup.pfx" -Password $password
```

---

## 関連ドキュメント

- [README.md](README.md) - メインドキュメント
- [CLIENT_INSTALLATION.md](CLIENT_INSTALLATION.md) - クライアント側CA証明書インストールガイド
- [QUICKSTART.md](QUICKSTART.md) - クイックスタートガイド
- [scripts/install-cert-devops-server.ps1](scripts/install-cert-devops-server.ps1) - 自動インストールスクリプト

---

## 参考情報

### Azure DevOps Server管理コンソール

- 場所: スタートメニュー → Azure DevOps Server → Azure DevOps Server Administration Console
- または: `%ProgramFiles%\Azure DevOps Server 2022\Tools\AdminConsole.exe`

### IISマネージャー

- 場所: スタートメニュー → Windows Administrative Tools → Internet Information Services (IIS) Manager
- または: コマンド `inetmgr`

### 証明書ストアの確認

```powershell
# ローカルマシンの全証明書ストアを表示
Get-ChildItem -Path Cert:\LocalMachine\ -Recurse

# 信頼されたルート証明機関
Get-ChildItem -Path Cert:\LocalMachine\Root

# 個人証明書ストア
Get-ChildItem -Path Cert:\LocalMachine\My
```
