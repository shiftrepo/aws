# 環境依存パラメータの分析レポート

## 【現状分析】

### ✅ 正しくパラメータ化されている項目

**1. Ansible Playbooks**
- `private_ip`: コマンドライン引数で指定可能 (-e "private_ip=X.X.X.X")
- `project_root`: コマンドライン引数で指定可能
- `app_version`: バージョンアップ時に指定可能

**2. アプリケーション設定 (application.yml)**
- データベース接続: 環境変数 ${POSTGRES_PASSWORD}
- Redis接続: 環境変数 ${REDIS_HOST}, ${REDIS_PORT}
- サービス名使用: postgres:5432, redis:6379 (Kubernetes内部DNS)

**3. Kubernetes Deployment**
- 環境変数で外部設定:
  - POD_NAME (downward API)
  - POSTGRES_PASSWORD
  - REDIS_HOST, REDIS_PORT
  - SPRING_PROFILES_ACTIVE

### ❌ ハードコードされている項目（要修正）

**1. Kubernetes Service マニフェスト**

`k8s-manifests/backend-service.yaml`:
```yaml
  externalIPs:
  - 10.0.1.200  # ← ハードコード
```

`k8s-manifests/frontend-service.yaml`:
```yaml
  externalIPs:
  - 10.0.1.200  # ← ハードコード
```

**2. Kubernetes Deployment マニフェスト**

`k8s-manifests/backend-deployment.yaml`:
```yaml
image: localhost/orgmgmt-backend:1.1.0  # ← バージョンハードコード
```

`k8s-manifests/frontend-deployment.yaml`:
```yaml
image: localhost/orgmgmt-frontend:1.1.0  # ← バージョンハードコード
```

**3. ArgoCD Application マニフェスト**

- GitリポジトリURL
- ブランチ名/タグ名
- マニフェストパス

## 【推奨される改善策】

### オプション1: Kustomize を使用（推奨）

ディレクトリ構造:
```
k8s-manifests/
├── base/
│   ├── kustomization.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   └── frontend-service.yaml
└── overlays/
    ├── dev/
    │   └── kustomization.yaml
    ├── staging/
    │   └── kustomization.yaml
    └── prod/
        └── kustomization.yaml
```

`overlays/prod/kustomization.yaml`:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
- ../../base

# イメージタグを環境ごとに変更
images:
- name: localhost/orgmgmt-backend
  newTag: 1.1.0
- name: localhost/orgmgmt-frontend
  newTag: 1.1.0

# 環境固有のパッチ
patches:
- target:
    kind: Service
    name: orgmgmt-backend
  patch: |-
    - op: replace
      path: /spec/externalIPs/0
      value: 10.0.1.200
```

### オプション2: Helm Charts を使用

ディレクトリ構造:
```
helm/
└── orgmgmt/
    ├── Chart.yaml
    ├── values.yaml
    ├── values-dev.yaml
    ├── values-staging.yaml
    ├── values-prod.yaml
    └── templates/
        ├── backend-deployment.yaml
        ├── backend-service.yaml
        ├── frontend-deployment.yaml
        └── frontend-service.yaml
```

`values.yaml`:
```yaml
backend:
  image:
    repository: localhost/orgmgmt-backend
    tag: "1.1.0"
  service:
    externalIP: "10.0.1.200"
    port: 8083

frontend:
  image:
    repository: localhost/orgmgmt-frontend
    tag: "1.1.0"
  service:
    externalIP: "10.0.1.200"
    port: 5006
```

### オプション3: Ansible Template を使用（最小変更）

現在のマニフェストをテンプレート化:

`k8s-manifests/backend-service.yaml.j2`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: orgmgmt-backend
spec:
  type: LoadBalancer
  externalIPs:
  - {{ private_ip }}  # ← 変数化
  ports:
  - name: http
    port: {{ backend_port | default(8083) }}
    targetPort: 8080
```

Playbookで生成:
```yaml
- name: Generate backend service manifest
  template:
    src: k8s-manifests/backend-service.yaml.j2
    dest: /tmp/backend-service.yaml
  vars:
    private_ip: "{{ private_ip }}"
```

## 【最も簡単な解決策】

### 現在のPlaybookを拡張（推奨・最小変更）

`ansible/playbooks/deploy_k8s_complete.yml` を修正:

```yaml
vars:
  private_ip: "{{ ansible_default_ipv4.address }}"
  app_version: "1.1.0"
  backend_port: 8083
  frontend_port: 5006

tasks:
  - name: Update backend service external IP
    command: >
      /usr/local/bin/k3s kubectl patch service orgmgmt-backend
      -n default
      -p '{"spec":{"externalIPs":["{{ private_ip }}"]}}'

  - name: Update frontend service external IP
    command: >
      /usr/local/bin/k3s kubectl patch service orgmgmt-frontend
      -n default
      -p '{"spec":{"externalIPs":["{{ private_ip }}"]}}'

  - name: Update backend deployment image
    command: >
      /usr/local/bin/k3s kubectl set image
      deployment/orgmgmt-backend
      backend=localhost/orgmgmt-backend:{{ app_version }}
      -n default

  - name: Update frontend deployment image
    command: >
      /usr/local/bin/k3s kubectl set image
      deployment/orgmgmt-frontend
      frontend=localhost/orgmgmt-frontend:{{ app_version }}
      -n default
```

## 【実装推奨順序】

1. **Phase 1: kubectl patch で動的更新（即座に実装可能）**
   - 現在のマニフェストはそのまま
   - Playbookで動的にパッチ適用
   - ✅ 最小変更で環境依存を解消

2. **Phase 2: Kustomize導入（中期的）**
   - base/ と overlays/ 構造
   - 環境ごとの設定管理
   - ✅ GitOps best practice

3. **Phase 3: Helm Charts（長期的）**
   - より高度なテンプレート機能
   - 依存関係管理
   - ✅ エンタープライズ向け

## 【現在の使用方法】

```bash
# 現在（環境依存あり）
ansible-playbook -i ansible/inventory.ini \
  ansible/playbooks/deploy_k8s_complete.yml \
  -e "project_root=/root/aws.git/container/claudecode/ArgoCD" \
  -e "private_ip=10.0.1.200"

# 改善後（完全にパラメータ化）
ansible-playbook -i ansible/inventory.ini \
  ansible/playbooks/deploy_k8s_complete.yml \
  -e "project_root=/path/to/project" \
  -e "private_ip=192.168.1.100" \
  -e "app_version=1.2.0" \
  -e "backend_port=8083" \
  -e "frontend_port=5006"
```

## 【検証チェックリスト】

別環境でクローンして実行する際の確認項目:

- [ ] Git repository URL (ArgoCD設定内)
- [ ] private_ip (Kubernetes Service externalIPs)
- [ ] project_root (Ansible変数)
- [ ] app_version (イメージタグ)
- [ ] port番号 (必要に応じて変更可能か)
- [ ] データベースパスワード (環境変数で設定可能か)
- [ ] Redis接続情報 (環境変数で設定可能か)

## 【結論】

**現状**: 
- アプリケーション設定は完全にパラメータ化済み ✅
- Kubernetes マニフェストに一部ハードコードあり ❌

**対応が必要な箇所**:
1. Service の externalIPs (2ファイル)
2. Deployment の image tag (2ファイル)
3. ArgoCD Application の repoURL (複数ファイル)

**推奨アクション**: 
Phase 1の kubectl patch 方式を即座に実装し、
別環境でのクローン・実行を完全に可能にする。
