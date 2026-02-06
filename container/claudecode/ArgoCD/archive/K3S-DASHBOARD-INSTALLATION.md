# Kubernetes Dashboard インストール完了レポート

**日時**: 2026-02-05T09:51:38Z
**ステータス**: ✅ 完了

---

## 📊 インストール詳細

### Dashboard情報
- **Version**: v2.7.0
- **Namespace**: kubernetes-dashboard
- **NodePort**: 30443
- **External Port**: 5001

### アクセス情報

#### 外部アクセス（HTTPS）
```
URL: https://13.219.96.72:5001
URL: https://ec2-13-219-96-72.compute-1.amazonaws.com:5001
```

#### ログイントークン
```
eyJhbGciOiJSUzI1NiIsImtpZCI6IlRGeDdyVlRWRUgyR08tdVJnaDlKWEZDM1V3Q2pJZzVrNGlFYmV5ejVWOUUifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi11c2VyLXRva2VuIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImFkbWluLXVzZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiIyYWE1ZDE4Yi0xYjA0LTQ0NTAtOGM5ZC04OTE2YzE5MTJhYjMiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZXJuZXRlcy1kYXNoYm9hcmQ6YWRtaW4tdXNlciJ9.D9gpvWNZdbGtOKUflSJmUyzYkpoO84G2qkti0ZRnme4UFgwjIml-DgdR50f0uwvl6egcVojoCuZYA-O_nPpAor94Fi1Jk8l66rXuEmZMPdGcpZjkMTxmx6zEAUGNfTXl1-5uhBZ0pC9BgtcICLGGm-0QFVY9qOYlmHAbNlo1CwYqyQdOwIOc-FMX70Sp3csl7u1-FLvmthru-m-P4cKcFtEAvRr2kSoSe0xeZWSaq9wvOhemkywSCa8JIBMhnnsXXAB7DTQom0IVt9djO11LIRPRFpyIItm6SBeY8FxULOu7JGEa0nzPWmesKAgsuLHg25B2N6KaMdL4eJRad1aHBg
```

トークンファイル: `/tmp/kubernetes-dashboard-token.txt`

---

## 🔐 ログイン手順

1. **ブラウザでアクセス**
```
https://13.219.96.72:5001
```

2. **証明書警告をスキップ**
- 自己署名証明書のため警告が表示されます
- 「詳細設定」→「安全でないサイトに進む」をクリック

3. **トークンでログイン**
- 「Token」を選択
- 上記のトークンをコピー&ペースト
- 「Sign in」をクリック

---

## 📊 デプロイ状態

### Pods
```
NAME                                         READY   STATUS    RESTARTS   AGE
dashboard-metrics-scraper-5ffb7d645f-9cz4w   1/1     Running   0          103s
kubernetes-dashboard-6c7b75ffc-p7b69         1/1     Running   0          103s
```

### Services
```
NAME                            TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)         AGE
dashboard-metrics-scraper       ClusterIP   10.43.60.73     <none>        8000/TCP        104s
kubernetes-dashboard            ClusterIP   10.43.14.139    <none>        443/TCP         104s
kubernetes-dashboard-nodeport   NodePort    10.43.165.207   <none>        443:30443/TCP   77s
```

---

## 🔄 再インストール方法

```bash
cd /root/aws.git/container/claudecode/ArgoCD
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/install_k3s_dashboard.yml
```

---

## 🗑️ アンインストール方法

```bash
# Dashboardリソース削除
kubectl delete namespace kubernetes-dashboard

# ポート転送サービス停止
systemctl stop k3s-dashboard-forward
systemctl disable k3s-dashboard-forward
rm -f /etc/systemd/system/k3s-dashboard-forward.service
systemctl daemon-reload
```

---

## 📝 トラブルシューティング

### Podが起動しない
```bash
kubectl get pods -n kubernetes-dashboard
kubectl describe pod <pod-name> -n kubernetes-dashboard
kubectl logs <pod-name> -n kubernetes-dashboard
```

### トークンが無効
```bash
# 新しいトークン取得
kubectl get secret admin-user-token \
  -n kubernetes-dashboard \
  -o jsonpath='{.data.token}' | base64 -d
```

### ポート転送が動作しない
```bash
# サービス状態確認
systemctl status k3s-dashboard-forward

# 再起動
systemctl restart k3s-dashboard-forward

# ログ確認
journalctl -u k3s-dashboard-forward -f
```

---

**Kubernetes Dashboard のインストールが完了しました！**
