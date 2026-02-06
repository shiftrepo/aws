# ホストOSから実行できるコマンド一覧

**環境**: RHEL 9 / EC2インスタンス
**作成日**: 2026-02-05

---

## 📋 目次

1. [K3s/Kubernetes管理](#k3skubernetes管理)
2. [Podmanコンテナ管理](#podmanコンテナ管理)
3. [Ansible自動化](#ansible自動化)
4. [Git操作](#git操作)
5. [システム管理](#システム管理)
6. [ネットワーク確認](#ネットワーク確認)
7. [ログ確認](#ログ確認)

---

## K3s/Kubernetes管理

### 基本操作

#### Pod確認
```bash
# すべてのPod表示
sudo /usr/local/bin/kubectl get pods -A

# defaultネームスペースのPod
sudo /usr/local/bin/kubectl get pods -n default

# 詳細表示
sudo /usr/local/bin/kubectl get pods -o wide

# 特定のPod詳細
sudo /usr/local/bin/kubectl describe pod <pod-name> -n default
```

#### Deployment管理
```bash
# Deployment一覧
sudo /usr/local/bin/kubectl get deployments -n default

# レプリカ数変更
sudo /usr/local/bin/kubectl scale deployment orgmgmt-frontend --replicas=5 -n default

# Deployment詳細
sudo /usr/local/bin/kubectl describe deployment orgmgmt-frontend -n default

# ローリングアップデート
sudo /usr/local/bin/kubectl rollout restart deployment orgmgmt-frontend -n default

# ロールアウト状態確認
sudo /usr/local/bin/kubectl rollout status deployment orgmgmt-frontend -n default

# ロールアウト履歴
sudo /usr/local/bin/kubectl rollout history deployment orgmgmt-frontend -n default
```

#### Service確認
```bash
# Service一覧
sudo /usr/local/bin/kubectl get svc -A

# 特定Service詳細
sudo /usr/local/bin/kubectl describe svc orgmgmt-frontend -n default

# Endpoints確認
sudo /usr/local/bin/kubectl get endpoints -n default
```

#### ログ確認
```bash
# Pod内のログ
sudo /usr/local/bin/kubectl logs <pod-name> -n default

# リアルタイムログ
sudo /usr/local/bin/kubectl logs -f <pod-name> -n default

# 前回のPodログ（再起動後）
sudo /usr/local/bin/kubectl logs <pod-name> --previous -n default

# 複数Podのログ（ラベル指定）
sudo /usr/local/bin/kubectl logs -l app=orgmgmt-frontend -n default --tail=50
```

#### Pod操作
```bash
# Pod内でコマンド実行
sudo /usr/local/bin/kubectl exec -it <pod-name> -n default -- sh

# Podの削除（自動的に再作成される）
sudo /usr/local/bin/kubectl delete pod <pod-name> -n default

# リソース使用状況
sudo /usr/local/bin/kubectl top pods -n default
sudo /usr/local/bin/kubectl top nodes
```

#### マニフェスト操作
```bash
# マニフェスト適用
sudo /usr/local/bin/kubectl apply -f /path/to/manifest.yaml

# マニフェスト削除
sudo /usr/local/bin/kubectl delete -f /path/to/manifest.yaml

# 動的なリソース取得
sudo /usr/local/bin/kubectl get deployment orgmgmt-frontend -o yaml -n default
```

### ArgoCD操作

```bash
# ArgoCD Application確認
sudo /usr/local/bin/kubectl get applications -n argocd

# Application詳細
sudo /usr/local/bin/kubectl describe application orgmgmt-frontend -n argocd

# Application削除
sudo /usr/local/bin/kubectl delete application orgmgmt-frontend -n argocd

# ArgoCD Pod確認
sudo /usr/local/bin/kubectl get pods -n argocd
```

### K3s サービス管理

```bash
# K3s サービス状態確認
sudo systemctl status k3s

# K3s 再起動
sudo systemctl restart k3s

# K3s ログ
sudo journalctl -u k3s -f

# K3s 停止/開始
sudo systemctl stop k3s
sudo systemctl start k3s
```

---

## Podmanコンテナ管理

### コンテナ操作

```bash
# コンテナ一覧
podman ps -a

# 稼働中のコンテナのみ
podman ps

# コンテナログ
podman logs <container-name>
podman logs -f <container-name>  # リアルタイム

# コンテナ内でコマンド実行
podman exec -it <container-name> bash
podman exec -it <container-name> sh

# コンテナ停止/起動/再起動
podman stop <container-name>
podman start <container-name>
podman restart <container-name>

# コンテナ削除
podman rm -f <container-name>
```

### イメージ管理

```bash
# イメージ一覧
podman images

# イメージ削除
podman rmi <image-id>
podman rmi localhost:5000/orgmgmt-frontend:latest

# イメージビルド
podman build -t <image-name>:<tag> -f Dockerfile .

# イメージプッシュ
podman push localhost:5000/orgmgmt-frontend:latest --tls-verify=false

# 未使用イメージ削除
podman image prune
```

### Podman Compose

```bash
# 起動
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose up -d

# 停止
podman-compose down

# ログ確認
podman-compose logs <service-name>
podman-compose logs -f  # すべてのサービス

# 特定サービス再起動
podman-compose restart <service-name>

# サービス状態確認
podman-compose ps
```

### よく使うコンテナ

```bash
# Nexus
podman logs orgmgmt-nexus
podman exec -it orgmgmt-nexus sh

# PostgreSQL
podman logs orgmgmt-postgres
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt

# ArgoCD
podman logs argocd-server
podman logs argocd-application-controller

# レジストリ
podman logs registry
```

---

## Ansible自動化

### プレイブック実行

```bash
cd /root/aws.git/container/claudecode/ArgoCD

# 完全CDパイプライン
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/complete_cd_pipeline.yml

# Kubernetes Dashboard インストール
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/install_k3s_dashboard.yml

# インフラ構築
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy_infrastructure.yml

# ビルドツールインストール
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/install_build_tools.yml

# アーティファクトビルド&デプロイ
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/build_and_deploy_artifacts.yml
```

### 構文チェック

```bash
# プレイブック構文チェック
ansible-playbook --syntax-check \
  ansible/playbooks/complete_cd_pipeline.yml

# Dry run（実行せず確認）
ansible-playbook --check \
  -i ansible/inventory/hosts.yml \
  ansible/playbooks/complete_cd_pipeline.yml
```

### 特定タスクのみ実行

```bash
# タグ指定実行
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/complete_cd_pipeline.yml \
  --tags "step2,step3"

# タスク一覧表示
ansible-playbook --list-tasks \
  ansible/playbooks/complete_cd_pipeline.yml
```

---

## Git操作

### 基本操作

```bash
cd /root/aws.git/container/claudecode/ArgoCD

# 状態確認
git status

# 差分確認
git diff
git diff <file-name>

# ログ確認
git log --oneline -10
git log --graph --oneline --all -20

# 追加・コミット
git add .
git add <file-name>
git commit -m "commit message"

# プッシュ
git push origin main

# プル
git pull origin main

# ブランチ確認
git branch
git branch -a  # リモートも表示
```

### GitOpsマニフェスト更新

```bash
cd /root/aws.git/container/claudecode/ArgoCD

# マニフェスト編集
vim gitops/orgmgmt-frontend/frontend-deployment.yaml

# コミット&プッシュ
git add gitops/
git commit -m "Update deployment configuration"
git push origin main

# ArgoCDが自動的に検知してデプロイ（3分以内）
```

---

## システム管理

### サービス管理

```bash
# K3s
sudo systemctl status k3s
sudo systemctl restart k3s
sudo systemctl stop k3s
sudo systemctl start k3s

# Dashboardポート転送
sudo systemctl status k3s-dashboard-forward
sudo systemctl restart k3s-dashboard-forward

# Frontendポート転送
sudo systemctl status k3s-frontend-forward
sudo systemctl restart k3s-frontend-forward

# すべてのsystemdサービス確認
systemctl list-units --type=service --state=running
```

### ディスク管理

```bash
# ディスク使用状況
df -h

# ディレクトリサイズ
du -sh /root/aws.git/container/claudecode/ArgoCD/
du -sh /home/ec2-user/.local/share/containers/

# ディスククリーンアップ
podman system prune -a  # 未使用イメージ/コンテナ削除
```

### プロセス確認

```bash
# プロセス一覧
ps aux | grep k3s
ps aux | grep podman

# ポート使用状況
ss -tlnp | grep -E ":(5001|5002|5003|5004|5005|5006|8000)"
netstat -tlnp | grep LISTEN

# リソース使用状況
top
htop  # インストールされている場合
free -h
```

---

## ネットワーク確認

### 接続テスト

```bash
# アプリケーション
curl -s http://localhost:5006/
curl -s http://localhost:5006/api/organizations

# Kubernetes Dashboard
curl -k -s https://localhost:5004/

# Nexus
curl -s http://localhost:8000/

# ArgoCD
curl -s http://localhost:5010/

# 外部アクセステスト
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
curl -s http://${PUBLIC_IP}:5006/
```

### DNS/ネットワーク

```bash
# パブリックIP取得
curl -s http://169.254.169.254/latest/meta-data/public-ipv4

# プライベートIP
hostname -I

# ネットワークインターフェース
ip addr show

# ルーティングテーブル
ip route
```

---

## ログ確認

### Systemdログ

```bash
# K3sログ
sudo journalctl -u k3s -f
sudo journalctl -u k3s --since "10 minutes ago"

# Dashboard転送ログ
sudo journalctl -u k3s-dashboard-forward -f

# すべてのシステムログ
sudo journalctl -f
sudo journalctl --since today
```

### Podmanログ

```bash
# コンテナログ
podman logs orgmgmt-nexus --tail 100
podman logs -f argocd-server

# すべてのコンテナ
for container in $(podman ps -q); do
  echo "=== $(podman ps -f id=$container --format '{{.Names}}') ==="
  podman logs $container --tail 10
done
```

### Kubernetesログ

```bash
# Pod内アプリケーションログ
sudo /usr/local/bin/kubectl logs -f deployment/orgmgmt-frontend -n default

# すべてのPodのログ
sudo /usr/local/bin/kubectl logs -l app=orgmgmt-frontend -n default --tail=50

# イベントログ
sudo /usr/local/bin/kubectl get events -n default --sort-by='.lastTimestamp'
sudo /usr/local/bin/kubectl get events -A --sort-by='.lastTimestamp'
```

### アプリケーションログ

```bash
# フロントエンドビルドログ
cat /root/aws.git/container/claudecode/ArgoCD/app/frontend/npm-debug.log

# Ansibleログ（最後の実行）
cat /tmp/cd-pipeline-execution-final.log
cat /tmp/fresh-cd-pipeline-execution.log
```

---

## 便利なエイリアス設定

`~/.bashrc` に追加すると便利：

```bash
# kubectl エイリアス
alias k='sudo /usr/local/bin/kubectl'
alias kgp='sudo /usr/local/bin/kubectl get pods'
alias kgs='sudo /usr/local/bin/kubectl get svc'
alias kgd='sudo /usr/local/bin/kubectl get deployments'
alias kgpa='sudo /usr/local/bin/kubectl get pods -A'
alias klogs='sudo /usr/local/bin/kubectl logs'

# Podman エイリアス
alias pps='podman ps'
alias plogs='podman logs'
alias pexec='podman exec -it'

# ディレクトリ移動
alias cdargo='cd /root/aws.git/container/claudecode/ArgoCD'
alias cdinfra='cd /root/aws.git/container/claudecode/ArgoCD/infrastructure'
alias cdansible='cd /root/aws.git/container/claudecode/ArgoCD/ansible'

# よく使うコマンド
alias k3s-status='sudo systemctl status k3s'
alias k3s-logs='sudo journalctl -u k3s -f'
```

設定を反映：
```bash
source ~/.bashrc
```

---

## トラブルシューティング

### Pod が起動しない

```bash
# Pod状態確認
sudo /usr/local/bin/kubectl get pods -n default

# 詳細情報
sudo /usr/local/bin/kubectl describe pod <pod-name> -n default

# ログ確認
sudo /usr/local/bin/kubectl logs <pod-name> -n default

# イベント確認
sudo /usr/local/bin/kubectl get events -n default --sort-by='.lastTimestamp' | tail -20

# Podを再作成
sudo /usr/local/bin/kubectl delete pod <pod-name> -n default
```

### コンテナが起動しない

```bash
# コンテナ状態
podman ps -a

# ログ確認
podman logs <container-name>

# コンテナ再起動
podman restart <container-name>

# 完全再作成
podman stop <container-name>
podman rm <container-name>
cd infrastructure && podman-compose up -d <service-name>
```

### ポートにアクセスできない

```bash
# ポート確認
ss -tlnp | grep 5006

# ファイアウォール確認
sudo firewall-cmd --list-all

# ポート転送サービス確認
sudo systemctl status k3s-frontend-forward

# 再起動
sudo systemctl restart k3s-frontend-forward
```

---

## クイックリファレンス

### 現在の状態確認（ワンライナー）

```bash
# すべての状態を一度に確認
echo "=== Podman Containers ===" && \
podman ps && \
echo "" && \
echo "=== K3s Pods ===" && \
sudo /usr/local/bin/kubectl get pods -A && \
echo "" && \
echo "=== Services ===" && \
sudo /usr/local/bin/kubectl get svc -A && \
echo "" && \
echo "=== ArgoCD Applications ===" && \
sudo /usr/local/bin/kubectl get applications -n argocd
```

### 完全再起動

```bash
# すべてのサービスを再起動
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose down
podman-compose up -d
sudo systemctl restart k3s
```

### アプリケーションテスト

```bash
# すべてのエンドポイントをテスト
echo "Frontend: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:5006/)"
echo "API: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:5006/api/organizations)"
echo "Dashboard: $(curl -k -s -o /dev/null -w '%{http_code}' https://localhost:5004/)"
echo "Nexus: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/)"
```

---

## 📚 関連ドキュメント

- `K3S-MANAGEMENT-SERVICES.md` - 管理サービス詳細
- `K3S-DASHBOARD-INSTALLATION.md` - Dashboard設定
- `ARGOCD-GITOPS-DEPLOYMENT.md` - ArgoCD GitOps設定
- `COMPLETE-CD-PIPELINE-REPORT.md` - CDパイプライン詳細
- `FRESH-DEPLOYMENT-REPORT.md` - デプロイメント手順

---

**すべてのコマンドはホストOS（EC2インスタンス）から実行可能です！**
