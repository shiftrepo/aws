# 外部アクセス トラブルシューティングガイド

**更新日時**: 2026-02-05 08:35 UTC
**ステータス**: サーバー側設定完了 ✅

---

## 🎯 アクセス方法（確定版）

### ✅ 使用可能なポート: 5006

外部からアクセス可能なポートの制限により、**ポート5006のみ**使用できます。

### 📍 正しいアクセスURL

**以下のいずれかのURLをブラウザで開いてください:**

```
http://ec2-13-219-96-72.compute-1.amazonaws.com:5006
```

**または**

```
http://13.219.96.72:5006
```

**⚠️ 重要**: 必ず `:5006` を含めてください。ポート番号なしではアクセスできません。

---

## ✅ サーバー側設定状況

| 項目 | ステータス | 詳細 |
|------|----------|------|
| **Podの状態** | ✅ 正常 | 3つのPodが稼働中 |
| **Network Policy** | ✅ 設定済み | すべてのIngressトラフィックを許可 |
| **Port Forward** | ✅ 稼働中 | 0.0.0.0:5006 → NodePort:30006 |
| **AWS Security Group** | ✅ 開放済み | ポート5006: 0.0.0.0/0 |
| **サービステスト** | ✅ 成功 | HTTP 200 OK (応答時間 1-3ms) |

---

## 🔍 アクセスできない場合のトラブルシューティング

### ステップ1: ブラウザのキャッシュをクリア

**Chrome:**
1. `Ctrl + Shift + Delete` (Windows/Linux) または `Cmd + Shift + Delete` (Mac)
2. 「キャッシュされた画像とファイル」を選択
3. 「データを削除」をクリック
4. ブラウザを再起動

**Firefox:**
1. `Ctrl + Shift + Delete` (Windows/Linux) または `Cmd + Shift + Delete` (Mac)
2. 「キャッシュ」を選択
3. 「今すぐ消去」をクリック
4. ブラウザを再起動

**Safari:**
1. `Safari` → `環境設定` → `詳細`
2. 「メニューバーに"開発"メニューを表示」にチェック
3. `開発` → `キャッシュを空にする`
4. ブラウザを再起動

---

### ステップ2: シークレット/プライベートモードで試す

**Chrome:**
- `Ctrl + Shift + N` (Windows/Linux) または `Cmd + Shift + N` (Mac)

**Firefox:**
- `Ctrl + Shift + P` (Windows/Linux) または `Cmd + Shift + P` (Mac)

**Safari:**
- `File` → `新規プライベートウィンドウ`

**シークレットモードで以下のURLを開く:**
```
http://ec2-13-219-96-72.compute-1.amazonaws.com:5006
```

---

### ステップ3: DNSキャッシュをクリア

**Windows:**
```cmd
ipconfig /flushdns
```

**macOS:**
```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

**Linux:**
```bash
sudo systemd-resolve --flush-caches
```

---

### ステップ4: 直接IPアドレスで試す

ホスト名のDNS解決に問題がある可能性があります。IPアドレスで直接アクセスしてください：

```
http://13.219.96.72:5006
```

---

### ステップ5: コマンドラインでテスト

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri "http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/health" -UseBasicParsing
```

**macOS/Linux:**
```bash
curl http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/health
```

**期待される結果:**
```
healthy
```

**正常に表示されれば、サーバーには問題ありません。**

---

### ステップ6: プロキシ設定を確認

**Windows:**
1. `設定` → `ネットワークとインターネット` → `プロキシ`
2. 「プロキシサーバーを使う」がOFFになっているか確認

**macOS:**
1. `システム環境設定` → `ネットワーク`
2. `詳細` → `プロキシ`
3. すべてのプロキシ設定がOFFになっているか確認

**ブラウザ (Chrome):**
1. `設定` → `詳細設定` → `システム`
2. `パソコンのプロキシ設定を開く`
3. プロキシ設定を確認

---

### ステップ7: ファイアウォール/セキュリティソフトを一時的に無効化

**注意**: セキュリティリスクがあるため、テスト後は必ず再度有効化してください。

**Windows Defender Firewall:**
1. `コントロールパネル` → `Windows Defender ファイアウォール`
2. `Windows Defender ファイアウォールの有効化または無効化`
3. 一時的に無効化してテスト

**macOS Firewall:**
1. `システム環境設定` → `セキュリティとプライバシー` → `ファイアウォール`
2. 一時的に無効化してテスト

---

### ステップ8: 別のネットワークで試す

**会社や学校のネットワークでアクセスできない場合:**
- モバイルデータ通信（テザリング）で試す
- 自宅のWi-Fiで試す
- 別のインターネット接続で試す

**組織のファイアウォールでブロックされている可能性があります。**

---

## 🔍 詳細診断

### ポート接続テスト

**Windows (PowerShell):**
```powershell
Test-NetConnection -ComputerName ec2-13-219-96-72.compute-1.amazonaws.com -Port 5006
```

**期待される結果:**
```
TcpTestSucceeded : True
```

**macOS/Linux:**
```bash
nc -zv ec2-13-219-96-72.compute-1.amazonaws.com 5006
```

**期待される結果:**
```
Connection to ec2-13-219-96-72.compute-1.amazonaws.com 5006 port [tcp/*] succeeded!
```

---

### tracerouteでネットワーク経路を確認

**Windows:**
```cmd
tracert ec2-13-219-96-72.compute-1.amazonaws.com
```

**macOS/Linux:**
```bash
traceroute ec2-13-219-96-72.compute-1.amazonaws.com
```

最終的に `13.219.96.72` に到達するか確認してください。

---

### DNS解決の確認

**すべてのOS:**
```bash
nslookup ec2-13-219-96-72.compute-1.amazonaws.com
```

**期待される結果:**
```
Name: ec2-13-219-96-72.compute-1.amazonaws.com
Address: 13.219.96.72
```

---

## 📞 問題が解決しない場合

### 情報収集

以下のコマンドを実行して、結果をコピーしてください：

**Windows (PowerShell):**
```powershell
# ポート接続テスト
Test-NetConnection -ComputerName 13.219.96.72 -Port 5006

# Web リクエスト
Invoke-WebRequest -Uri "http://13.219.96.72:5006/health" -UseBasicParsing

# DNS解決
nslookup ec2-13-219-96-72.compute-1.amazonaws.com
```

**macOS/Linux:**
```bash
# ポート接続テスト
nc -zv 13.219.96.72 5006

# Web リクエスト
curl -v http://13.219.96.72:5006/health

# DNS解決
nslookup ec2-13-219-96-72.compute-1.amazonaws.com

# traceroute
traceroute 13.219.96.72
```

---

## ✅ 動作確認チェックリスト

以下を順番に確認してください：

- [ ] URLに `:5006` が含まれているか
- [ ] ブラウザのキャッシュをクリアしたか
- [ ] シークレット/プライベートモードで試したか
- [ ] DNSキャッシュをクリアしたか
- [ ] 直接IPアドレス (13.219.96.72:5006) で試したか
- [ ] コマンドラインでアクセスできるか確認したか
- [ ] プロキシ設定をOFFにしたか
- [ ] ファイアウォールを一時的に無効化して試したか
- [ ] 別のネットワーク（モバイルデータなど）で試したか
- [ ] 別のデバイス（スマホなど）で試したか
- [ ] 別のブラウザで試したか

---

## 📊 サーバー側の確認済み項目

以下はすべてサーバー側で確認済みです：

✅ **Kubernetes Pods**: 3つすべて Running
✅ **Kubernetes Service**: NodePort 正常動作
✅ **Network Policy**: Ingress許可設定完了
✅ **Port Forwarding**: socat 稼働中
✅ **AWS Security Group**: ポート5006 開放済み
✅ **ローカルアクセステスト**: HTTP 200 OK
✅ **パブリックIPアクセステスト**: HTTP 200 OK
✅ **ホスト名アクセステスト**: HTTP 200 OK

**サーバー側には問題ありません。**

---

## 🌐 アクセス方法まとめ

### 推奨アクセスURL（必ずポート番号を含める）

```
http://ec2-13-219-96-72.compute-1.amazonaws.com:5006
```

### 代替URL（IPアドレス）

```
http://13.219.96.72:5006
```

### ヘルスチェックURL

```
http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/health
```

**このURLで "healthy" と表示されれば正常です。**

---

## 🔒 セキュリティ情報

### 現在の設定

- ✅ ポート5006: 世界中からアクセス可能 (0.0.0.0/0)
- ✅ HTTP (非暗号化通信)
- ✅ 認証なし

### アクセス制限の理由

外部ファイアウォールポリシーにより、以下のポートのみ外部からアクセス可能です：

```
3000, 8501, 8000, 8082, 8083, 5001, 5002, 5003, 5004, 5005, 5006
```

**ポート80や443（HTTPS）は使用できません。**

---

## 結論

サーバー側の設定は完全に完了しており、以下のURLで外部からアクセス可能です：

```
http://ec2-13-219-96-72.compute-1.amazonaws.com:5006
```

**または**

```
http://13.219.96.72:5006
```

アクセスできない場合は、クライアント側（ブラウザ、ネットワーク、ファイアウォール）の問題である可能性が高いです。上記のトラブルシューティング手順を順番に試してください。
