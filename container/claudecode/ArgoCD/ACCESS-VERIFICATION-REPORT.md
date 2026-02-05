# フロントエンドサービス アクセス検証レポート

**検証日時**: 2026-02-05 08:13 UTC
**サービス**: Organization Management System Frontend

---

## ✅ アクセス検証結果

### 1. ホスト名でのアクセス（推奨）

| URL | ステータス | 説明 |
|-----|----------|------|
| **http://ec2-13-219-96-72.compute-1.amazonaws.com:5006** | ✅ HTTP 200 | メインアクセスURL |
| **http://ec2-13-219-96-72.compute-1.amazonaws.com:30006** | ✅ HTTP 200 | NodePort直接アクセス |

### 2. パブリックIPでのアクセス

| URL | ステータス | 説明 |
|-----|----------|------|
| **http://13.219.96.72:5006** | ✅ HTTP 200 | IPアドレス経由 |
| **http://13.219.96.72:30006** | ✅ HTTP 200 | NodePort直接アクセス |

### 3. 内部アクセス（サーバー内部から）

| URL | ステータス | 説明 |
|-----|----------|------|
| http://127.0.0.1:5006 | ✅ HTTP 200 | ローカルホスト |
| http://10.0.1.191:5006 | ✅ HTTP 200 | プライベートIP |
| http://10.0.1.191:30006 | ✅ HTTP 200 | NodePort |

---

## 🌐 推奨アクセスURL

### ブラウザで以下のURLを開いてください：

```
http://ec2-13-219-96-72.compute-1.amazonaws.com:5006
```

**または**

```
http://13.219.96.72:5006
```

---

## 📊 サービス構成

### ネットワーク設定

```
インターネット
    ↓
AWS EC2 Public DNS: ec2-13-219-96-72.compute-1.amazonaws.com
AWS EC2 Public IP: 13.219.96.72
    ↓
AWS Security Group (sg-00421a9c400795ec7)
    - Port 5006: 0.0.0.0/0 から許可 ✅
    - Port 30006: 0.0.0.0/0 から許可 ✅
    ↓
EC2 Instance (10.0.1.191)
    ↓
socat Port Forward Service (systemd)
    - 0.0.0.0:5006 → 10.0.1.191:30006
    ↓
K3s NodePort Service (30006)
    - Session Affinity: None (ラウンドロビン)
    ↓
3つのPod (Nginx + React)
    - Pod 1: 10.42.0.21:80
    - Pod 2: 10.42.0.22:80
    - Pod 3: 10.42.0.23:80
```

### サービス詳細

| 項目 | 値 |
|------|-----|
| **サービスタイプ** | NodePort |
| **サービスポート** | 5006 |
| **NodePort** | 30006 |
| **コンテナポート** | 80 (Nginx) |
| **レプリカ数** | 3 |
| **負荷分散** | ラウンドロビン |
| **セッション維持** | なし (sessionAffinity: None) |

---

## 🔍 動作確認

### HTMLレスポンス確認

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Organization Management System</title>
    <script type="module" crossorigin src="/assets/index-CKdqtjCo.js"></script>
    <link rel="modulepreload" crossorigin href="/assets/react-vendor-5ewkRQsZ.js">
    <link rel="stylesheet" crossorigin href="/assets/index-H3Bfz0hy.css">
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
```

✅ **正常なHTMLレスポンスを確認**

### ヘルスチェック

```bash
# コマンド
curl http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/health

# レスポンス
healthy
```

✅ **ヘルスチェック正常**

---

## 🛠️ 実施した設定変更

### 1. socat ポート転送サービス修正

**変更前:**
```
ExecStart=/usr/bin/socat TCP-LISTEN:5006,fork,reuseaddr TCP:127.0.0.1:30006
```

**変更後:**
```
ExecStart=/usr/bin/socat TCP-LISTEN:5006,bind=0.0.0.0,fork,reuseaddr TCP:10.0.1.191:30006
```

**理由**:
- 明示的に `bind=0.0.0.0` を指定して全てのネットワークインターフェースでリッスン
- 転送先を `127.0.0.1:30006` から `10.0.1.191:30006` に変更して、K3sのNodePortに確実に転送

### 2. AWS セキュリティグループ

以下のポートが開放されています：

```
Port 5006: TCP, 0.0.0.0/0 → Frontend Port Forward
Port 30006: TCP, 0.0.0.0/0 → K3s NodePort
```

### 3. K3s サービス設定

```yaml
apiVersion: v1
kind: Service
metadata:
  name: orgmgmt-frontend
spec:
  type: NodePort
  sessionAffinity: None  # ラウンドロビン負荷分散
  selector:
    app: orgmgmt-frontend
  ports:
    - name: http
      port: 5006
      targetPort: 80
      nodePort: 30006
```

---

## 📋 検証コマンド

### ブラウザアクセス

```
http://ec2-13-219-96-72.compute-1.amazonaws.com:5006
```

### コマンドラインテスト

```bash
# ヘルスチェック
curl http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/health

# HTMLレスポンス取得
curl http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/

# IPアドレスでアクセス
curl http://13.219.96.72:5006/health

# NodePort直接アクセス
curl http://ec2-13-219-96-72.compute-1.amazonaws.com:30006/health
```

### サービス状態確認

```bash
# Pod状態確認
kubectl get pods -l app=orgmgmt-frontend -n default

# サービス確認
kubectl get svc orgmgmt-frontend -n default

# ポート転送サービス確認
systemctl status k3s-frontend-forward

# エンドポイント確認
kubectl get endpoints orgmgmt-frontend -n default
```

---

## 🎯 負荷分散の動作確認

### ラウンドロビンテスト

```bash
# 10回連続でアクセスして負荷分散を確認
for i in {1..10}; do
  echo "Request $i:"
  curl -s http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/health
done
```

**期待される動作:**
- 各リクエストが3つのPodに順次分散される
- セッション維持なし（sessionAffinity: None）
- 各Podが均等にリクエストを処理

---

## ✅ 成功基準

| 項目 | ステータス |
|------|----------|
| ホスト名アクセス (5006) | ✅ 成功 |
| ホスト名アクセス (30006) | ✅ 成功 |
| パブリックIPアクセス (5006) | ✅ 成功 |
| パブリックIPアクセス (30006) | ✅ 成功 |
| HTMLレスポンス | ✅ 正常 |
| ヘルスチェック | ✅ 正常 |
| 3つのPod稼働 | ✅ 確認 |
| ラウンドロビン負荷分散 | ✅ 設定済み |
| AWS SG設定 | ✅ 完了 |
| systemd サービス | ✅ 稼働中 |

---

## 📝 トラブルシューティング

### 接続できない場合

1. **サービス状態確認**
   ```bash
   systemctl status k3s-frontend-forward
   kubectl get svc orgmgmt-frontend -n default
   kubectl get pods -l app=orgmgmt-frontend
   ```

2. **ポート確認**
   ```bash
   ss -tlnp | grep -E ':(5006|30006)'
   ```

3. **ローカルテスト**
   ```bash
   curl http://127.0.0.1:5006/health
   curl http://10.0.1.191:30006/health
   ```

4. **AWS セキュリティグループ確認**
   ```bash
   aws ec2 describe-security-groups --group-ids sg-00421a9c400795ec7
   ```

### よくある問題

| 問題 | 原因 | 解決方法 |
|------|------|---------|
| Connection timeout | AWS SG未設定 | ポート5006, 30006を開放 |
| Connection refused | サービス停止 | systemctl restart k3s-frontend-forward |
| 502 Bad Gateway | Pod未起動 | kubectl get pods で確認 |

---

## 🚀 アクセス方法まとめ

### 🌟 推奨アクセス方法

**ブラウザで以下のURLを開いてください:**

```
http://ec2-13-219-96-72.compute-1.amazonaws.com:5006
```

### 代替アクセス方法

```
# IPアドレス直接
http://13.219.96.72:5006

# NodePort直接アクセス
http://ec2-13-219-96-72.compute-1.amazonaws.com:30006
http://13.219.96.72:30006
```

---

## 📅 検証履歴

| 日時 | 実施内容 | 結果 |
|------|---------|------|
| 2026-02-05 08:08 | 初期デプロイ | ✅ 成功 |
| 2026-02-05 08:09 | AWS SG設定 | ✅ 完了 |
| 2026-02-05 08:11 | socat設定修正 | ✅ 完了 |
| 2026-02-05 08:13 | 外部アクセス確認 | ✅ 成功 |

---

## 📌 重要な注意事項

1. **ポート番号**: 必ず `:5006` または `:30006` を指定してください
2. **プロトコル**: HTTP (https ではありません)
3. **ファイアウォール**: すべての制限を撤去済み
4. **負荷分散**: 自動的にラウンドロビンで分散されます

---

## 結論

✅ **フロントエンドサービスは外部からアクセス可能です**

以下のURLでアクセスしてください:

```
http://ec2-13-219-96-72.compute-1.amazonaws.com:5006
```

または

```
http://13.219.96.72:5006
```

すべてのファイアウォール制限を撤去し、世界中どこからでもアクセス可能です。
