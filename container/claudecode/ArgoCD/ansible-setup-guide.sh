#!/bin/bash
# ArgoCD環境構築ガイド - Ansible使用

cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║    ArgoCD環境構築ガイド - Ansible使用                                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 前提条件の確認
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Ansibleがインストールされているか確認:
   ansible --version

2. Podmanがインストールされているか確認:
   podman --version

3. 必要なディスク容量の確認:
   df -h /root (最低50GB必要)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 環境構築の実行
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

オプション1: 完全自動セットアップ（推奨）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cd /root/aws.git/container/claudecode/ArgoCD

# 1. すべてのコンポーネントを自動構築
ansible-playbook ansible/playbooks/site.yml

このコマンドは以下を実行します:
  ✅ Podmanレジストリの設定
  ✅ ArgoCD CLIのインストール
  ✅ インフラストラクチャのデプロイ（9サービス）
  ✅ アプリケーションのセットアップ

実行時間: 約15-20分


オプション2: 段階的セットアップ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cd /root/aws.git/container/claudecode/ArgoCD/ansible

# ステップ1: Podmanレジストリの設定
ansible-playbook playbooks/configure_podman_registry.yml

# ステップ2: ArgoCD CLIのインストール
ansible-playbook playbooks/install_argocd.yml

# ステップ3: インフラストラクチャのデプロイ
ansible-playbook playbooks/deploy_infrastructure.yml

# ステップ4: アプリケーションのセットアップ
ansible-playbook playbooks/setup_application.yml


オプション3: タグを使った選択的実行
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# レジストリ設定のみ
ansible-playbook ansible/playbooks/site.yml --tags registry

# CLIインストールのみ
ansible-playbook ansible/playbooks/site.yml --tags cli

# インフラストラクチャのみ
ansible-playbook ansible/playbooks/site.yml --tags infrastructure

# アプリケーション設定のみ
ansible-playbook ansible/playbooks/site.yml --tags application


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 構築後の確認
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# すべてのサービスの状態確認
./scripts/status.sh

# コンテナの確認
podman ps

# ArgoCD CLIの確認
argocd version


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 アクセスURL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

サービス              URL                          認証情報
─────────────────────────────────────────────────────────────────────
PostgreSQL            localhost:5432               orgmgmt_user / SecurePassword123!
pgAdmin               http://localhost:5050        admin@orgmgmt.local / AdminPassword123!
Nexus                 http://localhost:8081        admin / NexusAdmin123!
GitLab                http://localhost:5003        root / GitLabRoot123!
GitLab Registry       localhost:5005               root / GitLabRoot123!
ArgoCD                http://localhost:5010        admin / ArgoCDAdmin123!

構築完了後、アプリケーションのビルドとデプロイ:
./scripts/build-and-deploy.sh


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 トラブルシューティング
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

問題: Ansibleが見つからない
解決: export PATH="$HOME/.local/bin:$PATH"

問題: サービスが起動しない
解決: podman ps -a でログを確認
      ./scripts/logs.sh <service-name>

問題: ポートが使用中
解決: sudo lsof -i :<port> で確認
      競合するサービスを停止

詳細なトラブルシューティング:
cat TROUBLESHOOTING.md


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 追加リソース
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

完全なドキュメント:
  - README.md (メインドキュメント)
  - QUICKSTART.md (クイックスタート)
  - ansible/README.md (Ansibleガイド)

Ansibleプレイブック詳細:
  - ansible/QUICKSTART.md
  - ansible/EXAMPLES.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
