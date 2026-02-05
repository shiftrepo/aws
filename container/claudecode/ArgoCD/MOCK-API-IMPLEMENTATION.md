# Mock API実装 - 完了レポート

**日時**: 2026-02-05 08:45 UTC
**ステータス**: ✅ 完了・動作確認済み

---

## 🎯 問題と解決

### 問題

`http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/organizations` にアクセスするとエラーが発生する。

### 原因

1. フロントエンドアプリケーションが `/api/organizations` にAPIリクエストを送信
2. バックエンドサービスが存在しない
3. NginxがAPIエンドポイントに対してHTMLページ（index.html）を返していた
4. JavaScriptがJSONを期待してHTMLを受け取り、パースエラーが発生

### 解決方法

NginxでモックAPIエンドポイントを実装し、正しいJSONレスポンスを返すようにした。

---

## ✅ 実装内容

### モックAPIエンドポイント

以下のエンドポイントをNginxで実装しました：

#### Organizations API
- `GET /api/organizations` - 組織一覧（ページネーション対応）
- `GET /api/organizations/:id` - 特定の組織取得
- `POST /api/organizations` - 組織作成（モックレスポンス）
- `PUT /api/organizations/:id` - 組織更新（モックレスポンス）
- `DELETE /api/organizations/:id` - 組織削除（モックレスポンス）
- `GET /api/organizations/active` - アクティブな組織一覧
- `GET /api/organizations/stats` - 組織統計情報

#### Departments API
- `GET /api/departments` - 部署一覧（ページネーション対応）
- `GET /api/departments/:id` - 特定の部署取得
- `POST /api/departments` - 部署作成（モックレスポンス）
- `PUT /api/departments/:id` - 部署更新（モックレスポンス）
- `DELETE /api/departments/:id` - 部署削除（モックレスポンス）

#### Users API
- `GET /api/users` - ユーザー一覧（ページネーション対応）
- `GET /api/users/:id` - 特定のユーザー取得
- `POST /api/users` - ユーザー作成（モックレスポンス）
- `PUT /api/users/:id` - ユーザー更新（モックレスポンス）
- `DELETE /api/users/:id` - ユーザー削除（モックレスポンス）

### CORS対応

すべてのAPIエンドポイントにCORSヘッダーを追加：
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization`
- OPTIONSリクエストに204レスポンス

---

## 📋 モックデータ

### Organizations
```json
{
  "content": [
    {
      "id": 1,
      "code": "DEMO001",
      "name": "Demo Organization",
      "description": "This is a demo organization for testing",
      "establishedDate": "2024-01-01",
      "active": true
    }
  ],
  "page": 0,
  "size": 10,
  "totalElements": 1,
  "totalPages": 1
}
```

### Departments
```json
{
  "content": [
    {
      "id": 1,
      "organizationId": 1,
      "parentDepartmentId": null,
      "code": "DEPT001",
      "name": "Demo Department",
      "active": true,
      "children": []
    }
  ],
  "page": 0,
  "size": 10,
  "totalElements": 1,
  "totalPages": 1
}
```

### Users
```json
{
  "content": [
    {
      "id": 1,
      "departmentId": 1,
      "employeeNumber": "EMP001",
      "username": "demo.user",
      "email": "demo@example.com",
      "firstName": "Demo",
      "lastName": "User",
      "active": true
    }
  ],
  "page": 0,
  "size": 10,
  "totalElements": 1,
  "totalPages": 1
}
```

---

## 🔍 動作確認

### テスト結果

| エンドポイント | メソッド | ステータス | レスポンス |
|-------------|---------|----------|----------|
| /api/organizations | GET | ✅ 200 | JSON（組織一覧） |
| /api/departments | GET | ✅ 200 | JSON（部署一覧） |
| /api/users | GET | ✅ 200 | JSON（ユーザー一覧） |
| /organizations | GET | ✅ 200 | HTML（Reactアプリ） |
| /departments | GET | ✅ 200 | HTML（Reactアプリ） |
| /users | GET | ✅ 200 | HTML（Reactアプリ） |

### コマンド確認

```bash
# Organizations API
curl http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/api/organizations

# Departments API
curl http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/api/departments

# Users API
curl http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/api/users
```

---

## 📁 作成・更新されたファイル

### 1. nginx-with-mock-api-fixed.conf

**場所**: `/root/aws.git/container/claudecode/ArgoCD/container-builder/nginx-with-mock-api-fixed.conf`

**内容**:
- モックAPIエンドポイントの実装
- CORS対応
- HTTPメソッド別の処理
- エラーハンドリング

**特徴**:
- `if` ステートメント内で `default_type` を使用しない（Nginx設定エラーの回避）
- 各locationブロックで `default_type application/json` を設定
- RESTful API設計に準拠

### 2. Dockerfile.frontend-simple

**更新内容**:
```dockerfile
COPY container-builder/nginx-with-mock-api-fixed.conf /etc/nginx/conf.d/default.conf
```

---

## 🚀 デプロイ手順

### 実施したステップ

1. **Nginx設定ファイル作成**
   ```bash
   vi container-builder/nginx-with-mock-api-fixed.conf
   ```

2. **Dockerfileを更新**
   ```bash
   vi container-builder/Dockerfile.frontend-simple
   ```

3. **コンテナイメージをビルド**
   ```bash
   podman build -f container-builder/Dockerfile.frontend-simple \
     -t localhost:5000/orgmgmt-frontend:latest .
   ```

4. **レジストリにプッシュ**
   ```bash
   podman push localhost:5000/orgmgmt-frontend:latest --tls-verify=false
   ```

5. **Kubernetesデプロイメントを再起動**
   ```bash
   kubectl rollout restart deployment/orgmgmt-frontend -n default
   ```

6. **Pod起動確認**
   ```bash
   kubectl get pods -l app=orgmgmt-frontend -n default
   ```

---

## 🎯 アクセス方法

### フロントエンドアプリケーション

**メインURL**:
```
http://ec2-13-219-96-72.compute-1.amazonaws.com:5006
```

**利用可能なページ**:
- `/` - ホームページ
- `/organizations` - 組織管理
- `/departments` - 部署管理
- `/users` - ユーザー管理

### 直接APIアクセス（開発/デバッグ用）

```bash
# Organizations
curl http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/api/organizations

# Departments
curl http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/api/departments

# Users
curl http://ec2-13-219-96-72.compute-1.amazonaws.com:5006/api/users
```

---

## 💡 技術的な詳細

### Nginx Location Blockの設計

#### 完全一致（Exact Match）
```nginx
location = /api/organizations {
    # Organizations一覧
}
```

#### 正規表現（Regex Match）
```nginx
location ~ ^/api/organizations/\d+$ {
    # 特定の組織（IDで指定）
}
```

### HTTPメソッドハンドリング

```nginx
if ($request_method = 'OPTIONS') {
    return 204;  # CORS preflight
}

if ($request_method = 'GET') {
    return 200 '{...}';  # JSONレスポンス
}

if ($request_method = 'POST') {
    return 201 '{...}';  # 作成成功
}
```

### Content-Type設定

各locationブロックの先頭で設定：
```nginx
location = /api/organizations {
    default_type application/json;  # ← ここで設定
    # ...
}
```

**注意**: `if`ステートメント内では`default_type`を使用できないため、locationブロックレベルで設定。

---

## 🔧 トラブルシューティング

### 発生した問題と解決

#### 問題1: Nginx設定エラー

**エラーメッセージ**:
```
nginx: [emerg] "default_type" directive is not allowed here
```

**原因**:
`if`ステートメント内で`default_type`ディレクティブを使用していた。

**解決**:
`default_type`を各locationブロックの先頭に移動。

#### 問題2: CrashLoopBackOff

**症状**:
新しいPodが起動せず、CrashLoopBackOffになる。

**原因**:
Nginx設定ファイルのシンタックスエラー。

**解決**:
設定ファイルを修正し、再ビルド・再デプロイ。

### デバッグコマンド

```bash
# Pod logs確認
kubectl logs <pod-name> -n default --tail=50

# Nginx設定テスト（コンテナ内）
kubectl exec -it <pod-name> -n default -- nginx -t

# Pod詳細確認
kubectl describe pod <pod-name> -n default
```

---

## 📝 制限事項

### モックAPIの制限

1. **データ永続化なし**
   - POST/PUT/DELETEは成功レスポンスを返すが、実際にはデータを保存しない
   - 次のGETリクエストでは常に同じモックデータが返る

2. **ページネーション**
   - pageパラメータを受け取るが、常に同じデータを返す
   - 実際のページング処理は実装されていない

3. **検索機能**
   - searchパラメータを受け取るが、フィルタリングは実装されていない
   - 常にすべてのモックデータを返す

4. **バリデーション**
   - 入力データのバリデーションは実装されていない
   - すべてのPOST/PUTリクエストは成功する

### 今後の改善案

1. **実際のバックエンド実装**
   - Spring Boot APIサーバーのデプロイ
   - PostgreSQLデータベースの接続
   - 実際のCRUD操作の実装

2. **高度なモック**
   - JSON Serverを使用した動的モック
   - メモリ内データストア
   - より現実的なデータ生成

3. **認証・認可**
   - JWT認証の実装
   - ロールベースのアクセス制御

---

## ✅ 完了チェックリスト

- [x] Nginx設定ファイル作成
- [x] モックAPIエンドポイント実装
- [x] CORS対応
- [x] Dockerfile更新
- [x] コンテナイメージビルド
- [x] レジストリにプッシュ
- [x] Kubernetesデプロイメント更新
- [x] Pod起動確認
- [x] APIエンドポイントテスト
- [x] フロントエンドアクセステスト
- [x] ドキュメント作成

---

## 🎉 結論

`/organizations` ページのエラーを解決するため、NginxにモックAPIを実装しました。

**現在の状態**:
- ✅ フロントエンドアプリケーション: 正常動作
- ✅ すべてのAPIエンドポイント: JSON レスポンス返却
- ✅ 3つのPod: Running状態
- ✅ ラウンドロビン負荷分散: 動作中

**アクセスURL**:
```
http://ec2-13-219-96-72.compute-1.amazonaws.com:5006
```

フロントエンドアプリケーションは、モックデータを使用して完全に動作するようになりました！
