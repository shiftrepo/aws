# 外部アクセス可能ポート設定

## 利用可能な外部ポート一覧

以下のポートが外部からのアクセスに利用可能です：

```
3000
8501
8000   ← ArgoCD HTTP (使用中)
8082   ← ArgoCD HTTPS (使用中)
8083   ← Backend API (使用中)
5001
5002
5003
5004
5005
5006   ← Frontend (使用中)
```

## 現在の割り当て

| サービス | ポート | 用途 | アクセスURL |
|---------|-------|------|-----------|
| Backend API | 8083 | REST API / Health Check | http://10.0.1.200:8083 |
| Frontend | 5006 | Web UI | http://10.0.1.200:5006 |
| ArgoCD HTTPS | 8082 | GitOps管理UI (HTTPS) | https://10.0.1.200:8082 |
| ArgoCD HTTP | 8000 | GitOps管理UI (HTTP) | http://10.0.1.200:8000 |

## Kubernetesサービス設定

### Backend Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: orgmgmt-backend
spec:
  type: LoadBalancer
  externalIPs:
  - 10.0.1.200
  ports:
  - name: http
    port: 8083        # 外部アクセスポート
    targetPort: 8080  # Pod内部ポート
```

### Frontend Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: orgmgmt-frontend
spec:
  type: LoadBalancer
  externalIPs:
  - 10.0.1.200
  ports:
  - name: http
    port: 5006        # 外部アクセスポート
    targetPort: 80    # Pod内部ポート (nginx)
```

## 新しいサービスの追加方法

利用可能なポートから未使用のものを選択して、Serviceマニフェストの `spec.ports[].port` に設定します。

例：新しいサービスをポート5001で公開する場合
```yaml
apiVersion: v1
kind: Service
metadata:
  name: new-service
spec:
  type: LoadBalancer
  externalIPs:
  - 10.0.1.200
  ports:
  - name: http
    port: 5001        # 利用可能なポートから選択
    targetPort: 8080  # Pod内のアプリケーションポート
  selector:
    app: new-service
```

## 確認方法

### サービスのポート確認
```bash
kubectl get svc
# または
kubectl get svc <service-name> -o yaml | grep -A 5 "ports:"
```

### アクセステスト
```bash
# Backend
curl http://10.0.1.200:8083/actuator/health

# Frontend
curl http://10.0.1.200:5006/
```

## 注意事項

- LoadBalancerタイプのサービスで `externalIPs` を使用する場合、`spec.ports[].port` で指定したポートが外部アクセスポートになります
- NodePortは自動割り当てされますが、外部アクセスには使用しません
- 新しいサービスを追加する際は、必ず利用可能なポート一覧から選択してください
- ポート80は利用可能ポートに含まれていないため、5006に変更しました

---
Updated: 2026-02-06
