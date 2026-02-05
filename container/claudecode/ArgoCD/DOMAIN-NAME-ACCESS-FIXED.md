# ドメイン名アクセス問題の解決

**日時**: 2026-02-05 08:39 UTC
**ステータス**: ✅ 解決済み

---

## 🎯 問題の概要

### 症状
- ✅ IPアドレスでアクセス可能: `http://13.219.96.72:5006`
- ❌ ドメイン名でアクセス不可: `http://ec2-13-219-96-72.compute-1.amazonaws.com:5006`
- ✅ ArgoCDはドメイン名でアクセス可能

### 原因分析

**問題の根本原因:**
ポート5006の転送先が、Traefik Ingressを経由せずに、直接フロントエンドサービス（NodePort 30006）に転送されていたため、Hostヘッダーのルーティングが効かなかった。

**詳細:**

#### 修正前のアーキテクチャ:
```
外部リクエスト (ドメイン名指定)
    ↓
ポート5006
    ↓
socat転送 → NodePort 30006 (直接フロントエンドサービス)
    ↓
Frontend Service
    ↓
Frontend Pods (Nginx)

問題: Traefik Ingressを経由しないため、
      Ingress設定のHostルールが適用されない
      → IPアドレスは動作するが、ドメイン名は404
```

#### 修正後のアーキテクチャ:
```
外部リクエスト (ドメイン名指定)
    ↓
ポート5006
    ↓
socat転送 → NodePort 31824 (Traefik)
    ↓
Traefik Ingress Controller
    ├─ Hostヘッダーチェック
    └─ Ingress Ruleマッチング
        ↓
Frontend Service
    ↓
Frontend Pods (Nginx)

解決: Traefik Ingress経由で、
      Hostルールが正しく適用される
      → IPアドレスもドメイン名も両方動作
```

---

## ✅ 解決方法

### 実施した変更

**1. socatの転送先を変更**

**修正前:**
```ini
ExecStart=/usr/bin/socat TCP-LISTEN:5006,bind=0.0.0.0,fork,reuseaddr TCP:10.0.1.191:30006
```
↓ NodePort 30006（直接フロントエンドサービス）

**修正後:**
```ini
ExecStart=/usr/bin/socat TCP-LISTEN:5006,bind=0.0.0.0,fork,reuseaddr TCP:10.0.1.191:31824
```
↓ NodePort 31824（Traefik Ingress）

### 実施コマンド

```bash
# socatサービス設定を更新
sudo vi /etc/systemd/system/k3s-frontend-forward.service

# 変更内容:
# 転送先を 30006 から 31824 に変更

# systemd設定をリロード
sudo systemctl daemon-reload

# サービスを再起動
sudo systemctl restart k3s-frontend-forward

# 動作確認
systemctl status k3s-frontend-forward
```

---

## 🔍 技術的な詳細

### Traefik Ingressの役割

Traefik Ingressは以下の処理を行います：

1. **Hostヘッダーの確認**
   - リクエストの `Host:` ヘッダーをチェック
   - Ingress設定のHostルールとマッチング

2. **ルーティング決定**
   - マッチしたIngress Ruleに基づいてバックエンドサービスを決定
   - 該当するServiceにトラフィックを転送

3. **ロードバランシング**
   - Serviceの複数のPodに対してラウンドロビン分散

### Ingress設定

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: orgmgmt-frontend
  namespace: default
spec:
  ingressClassName: traefik
  rules:
    - host: ec2-13-219-96-72.compute-1.amazonaws.com  # ← このHostルールが適用される
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: orgmgmt-frontend
                port:
                  number: 5006
```

### Traefikのサービス設定

```
NAME: traefik
TYPE: LoadBalancer
CLUSTER-IP: 10.43.104.254
EXTERNAL-IP: 10.0.1.191
PORTS:
  - 80:31824/TCP   ← HTTP (web entrypoint)
  - 443:32590/TCP  ← HTTPS (websecure entrypoint)
```

**ポート31824がTraefikのHTTPエントリーポイントです。**

---

## ✅ 検証結果

### アクセステスト

| テスト項目 | URL | 結果 |
|----------|-----|------|
| IPアドレス | http://13.219.96.72:5006/health | ✅ HTTP 200 |
| ドメイン名 | http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/health | ✅ HTTP 200 |
| HTMLページ (IP) | http://13.219.96.72:5006/ | ✅ 正常表示 |
| HTMLページ (ドメイン) | http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/ | ✅ 正常表示 |
| ラウンドロビン | 6回連続アクセス | ✅ すべて成功 |

### curlでの確認

```bash
# ドメイン名でアクセス
$ curl -v http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/health

> GET /health HTTP/1.1
> Host: ec2-13-219-96-72.compute-1.amazonaws.com:5006
< HTTP/1.1 200 OK
< Server: nginx/1.25.5

healthy
```

**Hostヘッダー**: `ec2-13-219-96-72.compute-1.amazonaws.com:5006` ✅
**HTTPステータス**: 200 OK ✅
**レスポンス**: `healthy` ✅

---

## 🚀 現在のアクセス方法

### ✅ 推奨アクセスURL

**ドメイン名（推奨）:**
```
http://ec2-13-219-96-72.compute-1.amazonaws.com:5006
```

**IPアドレス（代替）:**
```
http://13.219.96.72:5006
```

**どちらも正常に動作します！**

---

## 📊 リクエストフロー

### 完全なリクエストフロー図

```
1. ブラウザ
   ↓
   http://ec2-13-219-96-72.compute-1.amazonaws.com:5006
   Host: ec2-13-219-96-72.compute-1.amazonaws.com:5006

2. DNS解決
   ↓
   13.219.96.72:5006

3. AWS Security Group
   ↓
   ポート5006許可 ✅

4. EC2 Instance (10.0.1.191)
   ↓
   socat (0.0.0.0:5006)

5. ポート転送
   ↓
   10.0.1.191:31824 (Traefik NodePort)

6. Traefik Ingress Controller
   ↓
   Hostヘッダーチェック: ec2-13-219-96-72.compute-1.amazonaws.com ✅
   ↓
   Ingress Ruleマッチング ✅

7. Frontend Service (ClusterIP)
   ↓
   ラウンドロビン負荷分散

8. Frontend Pods (3つ)
   ├─ Pod 1 (10.42.0.21:80)
   ├─ Pod 2 (10.42.0.22:80)
   └─ Pod 3 (10.42.0.23:80)

9. Nginx
   ↓
   静的ファイル提供

10. レスポンス
    ↓
    ブラウザに表示 ✅
```

---

## 🔧 トラブルシューティング

### 同様の問題が発生した場合

**チェックポイント:**

1. **socatの転送先を確認**
   ```bash
   systemctl status k3s-frontend-forward
   # ExecStartの転送先ポートを確認
   ```

2. **Traefikのポートを確認**
   ```bash
   kubectl get svc -n kube-system traefik
   # 80:XXXXX/TCP のXXXXXがNodePort
   ```

3. **Ingress設定を確認**
   ```bash
   kubectl get ingress -n default orgmgmt-frontend -o yaml
   # spec.rules[].host を確認
   ```

4. **Hostヘッダーをテスト**
   ```bash
   curl -v -H "Host: your-domain.com" http://IP:PORT/
   # Hostヘッダーが正しく処理されるか確認
   ```

### 正しい転送先の見つけ方

```bash
# 1. Traefikサービスを確認
kubectl get svc -n kube-system traefik

# 出力例:
# NAME      TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)
# traefik   LoadBalancer   10.43.104.254   10.0.1.191    80:31824/TCP,443:32590/TCP

# 2. HTTPエントリーポイント（ポート80）のNodePortを確認
# 上記の例では 31824 がHTTPのNodePort

# 3. socatの転送先をこのNodePortに設定
# TCP:10.0.1.191:31824
```

---

## 📝 関連ファイル

### 更新されたファイル

**1. /etc/systemd/system/k3s-frontend-forward.service**
```ini
[Unit]
Description=K3s Frontend Port Forward (5006 -> Traefik)
After=k3s.service
Requires=k3s.service

[Service]
Type=simple
ExecStart=/usr/bin/socat TCP-LISTEN:5006,bind=0.0.0.0,fork,reuseaddr TCP:10.0.1.191:31824
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**変更点:**
- 転送先を `30006` から `31824` に変更
- Descriptionを更新

### 既存の設定ファイル

**2. k8s-manifests/frontend-ingress.yaml**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: orgmgmt-frontend
  namespace: default
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  ingressClassName: traefik
  rules:
    - host: ec2-13-219-96-72.compute-1.amazonaws.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: orgmgmt-frontend
                port:
                  number: 5006
```

**3. k8s-manifests/frontend-networkpolicy.yaml**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: orgmgmt-frontend-allow-all
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: orgmgmt-frontend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - {}
  egress:
    - {}
```

---

## 💡 学んだこと

### Kubernetes Ingressの仕組み

1. **Ingress Controllerが必要**
   - K3sではデフォルトでTraefikが使用される
   - Ingress Controllerが実際にトラフィックをルーティング

2. **Hostヘッダーの重要性**
   - Ingressは `Host:` ヘッダーでルーティングを決定
   - ヘッダーがマッチしないと404エラー

3. **NodePortの使い分け**
   - サービスの直接NodePort: Ingressをバイパス
   - Ingress ControllerのNodePort: Ingressルール適用

### ArgoCDとの比較

**ArgoCDがドメイン名でアクセスできた理由:**
- ArgoCDもIngressまたはNodePortサービスで公開されている
- 適切なHostルールが設定されている
- または、NodePortに直接アクセスしている（Hostチェックなし）

---

## 🎉 結論

### 問題の本質

**単純な設定ミスでした:**
- socatの転送先が間違っていた
- Ingress Controllerを経由する必要があった

### 解決のポイント

1. ✅ Traefik IngressのNodePortを特定（31824）
2. ✅ socatの転送先を変更
3. ✅ Ingress設定が正しく適用される
4. ✅ ドメイン名でもIPアドレスでもアクセス可能に

### 最終確認

```bash
# ドメイン名でアクセス
curl http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/health
# 結果: healthy ✅

# IPアドレスでアクセス
curl http://13.219.96.72:5006/health
# 結果: healthy ✅
```

**両方とも正常に動作します！**

---

## 📞 今後の参考

### 同様の問題を防ぐために

1. **ポート転送を設定する際は:**
   - Ingress Controllerを経由するか確認
   - Hostヘッダーのルーティングが必要か確認

2. **アクセスできない場合は:**
   - IPアドレスとドメイン名の両方で試す
   - 差があれば、Hostヘッダーの問題

3. **Ingress設定を確認:**
   - Hostルールが正しく設定されているか
   - Ingress Controllerが稼働しているか

---

## ✅ 最終ステータス

| 項目 | ステータス |
|------|----------|
| IPアドレスアクセス | ✅ 動作 |
| ドメイン名アクセス | ✅ 動作 |
| Traefik経由 | ✅ 正常 |
| Ingress適用 | ✅ 正常 |
| ラウンドロビン | ✅ 動作 |
| Network Policy | ✅ 設定済み |

**すべて正常に動作しています！**

---

**アクセスURL:**
```
http://ec2-13-219-96-72.compute-1.amazonaws.com:5006
```
