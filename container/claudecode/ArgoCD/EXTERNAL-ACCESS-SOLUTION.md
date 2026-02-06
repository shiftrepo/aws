# 外部アクセス問題 - 解決方法

## 問題の原因

LoadBalancer ServiceでexternalIPsを設定したり、iptables REDIRECTルールを使用しても、**外部IPからアクセスできない**問題が発生していました。

### なぜiptablesでは外部アクセスできないのか

```bash
iptables -t nat -A PREROUTING -p tcp --dport 5006 -j REDIRECT --to-port 31899
```

このルールは以下の理由で外部アクセスに対応できません：

1. **REDIRECTターゲット**はローカルシステム内でのポート変更のみ
2. **外部から来たパケット**は適切にルーティングされない
3. **bind=0.0.0.0でリッスンしていない**ため、外部インターフェースで受信できない

## 解決方法：socat

**socat**を使用して、外部からアクセス可能なポート転送を設定します。

### socatの特徴

- `bind=0.0.0.0` - すべてのネットワークインターフェースでリッスン
- `fork` - 複数の同時接続を処理
- `reuseaddr` - ポートの再利用を許可
- **外部IPから直接アクセス可能**

## 実装方法

### 1. socatのインストール

```bash
sudo dnf install -y socat
```

### 2. systemdサービスの作成

各ポート用にsystemdサービスを作成：

**Frontend (5006 -> 31899):**
```ini
[Unit]
Description=Socat Port Forward - Frontend (5006 -> 31899)
After=network.target k3s.service
Requires=k3s.service

[Service]
Type=simple
User=root
ExecStart=/usr/bin/socat TCP-LISTEN:5006,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:31899
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Backend (8083 -> 31383):**
```ini
[Service]
ExecStart=/usr/bin/socat TCP-LISTEN:8083,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:31383
```

**ArgoCD HTTP (8000 -> 30460):**
```ini
[Service]
ExecStart=/usr/bin/socat TCP-LISTEN:8000,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:30460
```

**ArgoCD HTTPS (8082 -> 30010):**
```ini
[Service]
ExecStart=/usr/bin/socat TCP-LISTEN:8082,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:30010
```

### 3. サービスの有効化と起動

```bash
sudo systemctl daemon-reload
sudo systemctl enable socat-frontend socat-backend socat-argocd-http socat-argocd-https
sudo systemctl start socat-frontend socat-backend socat-argocd-http socat-argocd-https
```

### 4. 確認

```bash
# ポートがリッスンしているか確認
sudo ss -tlnp | grep -E "5006|8083|8082|8000"

# 出力例:
# LISTEN 0   5   0.0.0.0:8000   0.0.0.0:*   users:(("socat",pid=xxx,fd=5))
# LISTEN 0   5   0.0.0.0:8082   0.0.0.0:*   users:(("socat",pid=xxx,fd=5))
# LISTEN 0   5   0.0.0.0:8083   0.0.0.0:*   users:(("socat",pid=xxx,fd=5))
# LISTEN 0   5   0.0.0.0:5006   0.0.0.0:*   users:(("socat",pid=xxx,fd=5))
```

**重要**: `0.0.0.0`でリッスンしていることを確認してください。

## アクセスURL

外部IPから以下のURLでアクセス可能：

- **Frontend**: http://<外部IP>:5006
- **Backend API**: http://<外部IP>:8083
- **ArgoCD HTTPS**: https://<外部IP>:8082
- **ArgoCD HTTP**: http://<外部IP>:8000

## Ansible自動化

`deploy_k8s_complete.yml` Phase 7でsocat設定を自動化：

```yaml
- name: "PHASE 7: Setup Port Forwarding with socat"
  block:
    - name: Install socat
      package:
        name: socat
        state: present
    
    - name: Create socat systemd services
      # ... (4つのサービスを作成)
    
    - name: Enable and start socat services
      systemd:
        name: "{{ item }}"
        enabled: yes
        state: started
      loop:
        - socat-frontend
        - socat-backend
        - socat-argocd-http
        - socat-argocd-https
```

## トラブルシューティング

### ポートが開いていない場合

```bash
# サービスステータス確認
sudo systemctl status socat-frontend

# ログ確認
sudo journalctl -u socat-frontend -f

# ポート確認
sudo ss -tlnp | grep 5006
```

### 外部からアクセスできない場合

1. **AWSセキュリティグループ**でポートが開放されているか確認
2. **ファイアウォール**が無効化されているか確認
3. **socatプロセス**が動作しているか確認

```bash
sudo ps aux | grep socat
```

## まとめ

| 方式 | 外部アクセス | 設定の複雑さ | 推奨 |
|------|-------------|-------------|------|
| iptables REDIRECT | ❌ 不可 | 低 | ❌ |
| LoadBalancer externalIPs | ❌ 不可 | 中 | ❌ |
| **socat 0.0.0.0** | ✅ 可能 | 低 | ✅ |

**結論**: 外部からアクセスするには、**socat**を使用して`bind=0.0.0.0`でリッスンする必要があります。

---
Updated: 2026-02-06
