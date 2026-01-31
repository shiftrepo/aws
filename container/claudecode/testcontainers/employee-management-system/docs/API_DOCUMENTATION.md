# API ドキュメント - 職員管理システム

包括的な例とテストシナリオを含む職員管理システムの完全なREST APIドキュメントです。

## 🔗 ベース URL

```
http://localhost:8080/api/v1
```

## 📋 API 概要

職員管理システムは、包括的なCRUD操作、検索機能、ビジネスロジックエンドポイントを備えた職員と部署管理のためのRESTful APIを提供します。

### 認証
現在、APIは教育目的のため認証なしで動作します。本番環境では適切な認証メカニズムを実装してください。

### レスポンス形式
すべてのAPIレスポンスは一貫したJSON構造に従います：

```json
{
  "id": 1,
  "name": "リソース名",
  "createdAt": "2024-01-15T10:30:00Z",
  "modifiedAt": "2024-01-15T10:30:00Z"
}
```

### エラーハンドリング
エラーレスポンスには詳細情報が含まれます：

```json
{
  "error": "Bad Request",
  "message": "職員のメールアドレスが既に存在します",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/v1/employees"
}
```

## 👥 職員 API

### 基本操作

#### GET /api/v1/employees
オプションのフィルタリング付きですべての職員を取得。

**パラメータ:**
- `activeOnly` (boolean, オプション): アクティブな職員のみをフィルタ

```bash
# すべての職員を取得
curl http://localhost:8080/api/v1/employees

# アクティブな職員のみを取得
curl http://localhost:8080/api/v1/employees?activeOnly=true
```

**レスポンス:**
```json
[
  {
    "id": 1,
    "firstName": "太郎",
    "lastName": "田中",
    "email": "tanaka.taro@company.com",
    "hireDate": "2023-01-15",
    "phoneNumber": "+81-90-1234-5678",
    "address": "東京都新宿区西新宿1-1-1",
    "active": true,
    "departmentId": 1,
    "departmentName": "人事部",
    "departmentCode": "HR",
    "fullName": "田中 太郎",
    "yearsOfService": 1,
    "isNewEmployee": false,
    "isVeteranEmployee": false,
    "createdAt": "2024-01-15T10:30:00Z",
    "modifiedAt": "2024-01-15T10:30:00Z"
  }
]
```

#### GET /api/v1/employees/{id}
IDで特定の職員を取得。

```bash
curl http://localhost:8080/api/v1/employees/1
```

**レスポンス:** 単一の職員オブジェクト（上記と同じ構造）

#### GET /api/v1/employees/email/{email}
メールアドレスで職員を取得。

```bash
curl http://localhost:8080/api/v1/employees/email/tanaka.taro@company.com
```

#### POST /api/v1/employees
新しい職員を作成。

```bash
curl -X POST http://localhost:8080/api/v1/employees \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "花子",
    "lastName": "佐藤",
    "email": "sato.hanako@company.com",
    "hireDate": "2024-01-15",
    "phoneNumber": "+81-90-2345-6789",
    "address": "大阪府大阪市中央区本町1-1-1",
    "departmentId": 2
  }'
```

**検証ルール:**
- `firstName`: 必須、1-50文字
- `lastName`: 必須、1-50文字
- `email`: 必須、有効なメール形式、一意
- `hireDate`: 必須、未来日不可
- `phoneNumber`: オプション、有効な電話番号形式
- `address`: オプション、最大200文字

#### PUT /api/v1/employees/{id}
既存の職員を更新。

```bash
curl -X PUT http://localhost:8080/api/v1/employees/1 \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "太郎",
    "lastName": "更新",
    "email": "tanaka.updated@company.com",
    "hireDate": "2023-01-15",
    "phoneNumber": "+81-90-9999-9999",
    "address": "東京都渋谷区道玄坂1-1-1",
    "departmentId": 2,
    "active": true
  }'
```

#### DELETE /api/v1/employees/{id}
職員を削除（active=falseに設定するソフト削除）。

```bash
curl -X DELETE http://localhost:8080/api/v1/employees/1
```

### 部署操作

#### PATCH /api/v1/employees/{id}/department/{departmentId}
職員を部署に割り当て。

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/1/department/2
```

#### PATCH /api/v1/employees/{id}/remove-department
職員を現在の部署から除外。

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/1/remove-department
```

#### POST /api/v1/employees/{id}/transfer/{newDepartmentId}
ビジネスルール検証付きで職員を新しい部署に異動。

```bash
curl -X POST http://localhost:8080/api/v1/employees/1/transfer/3
```

### ステータス操作

#### PATCH /api/v1/employees/{id}/activate
職員をアクティブ化。

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/1/activate
```

#### PATCH /api/v1/employees/{id}/deactivate
職員を非アクティブ化。

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/1/deactivate
```

### 検索とフィルタリング

#### GET /api/v1/employees/search
複数の条件による高度な職員検索。

**パラメータ:**
- `term` (string): 名前とメールアドレスで検索
- `hiredAfter` (date): 入社日の後でフィルタ
- `hiredBefore` (date): 入社日の前でフィルタ
- `hiredInYear` (integer): 特定の入社年でフィルタ
- `minYearsOfService` (integer): 最小勤続年数
- `minDepartmentBudget` (decimal): 最小部署予算
- `fullText` (boolean): PostgreSQL全文検索を有効化

```bash
# 名前で検索
curl "http://localhost:8080/api/v1/employees/search?term=太郎"

# 入社日範囲で検索
curl "http://localhost:8080/api/v1/employees/search?hiredAfter=2023-01-01&hiredBefore=2023-12-31"

# 勤続年数で検索
curl "http://localhost:8080/api/v1/employees/search?minYearsOfService=5"

# 全文検索（PostgreSQL特有）
curl "http://localhost:8080/api/v1/employees/search?term=マネージャー&fullText=true"
```

#### 部署ベースのクエリ

```bash
# 部署IDで職員を取得
curl http://localhost:8080/api/v1/employees/department/1

# 部署コードで職員を取得
curl http://localhost:8080/api/v1/employees/department/code/HR

# 部署未所属の職員を取得
curl http://localhost:8080/api/v1/employees/without-department

# アクティブ部署のみの職員を取得
curl http://localhost:8080/api/v1/employees/in-active-departments
```

#### 特別カテゴリ

```bash
# 新入社員を取得（過去1年以内に入社）
curl http://localhost:8080/api/v1/employees/new-employees

# ベテラン職員を取得（勤続5年以上）
curl http://localhost:8080/api/v1/employees/veteran-employees
```

### 統計と分析

#### GET /api/v1/employees/statistics
職員統計と分析を取得。

```bash
curl http://localhost:8080/api/v1/employees/statistics
```

**レスポンス:**
```json
{
  "totalActiveEmployees": 25,
  "hiringStatisticsByYear": [
    [2023, 15],
    [2024, 10]
  ],
  "departmentEmployeeCounts": [
    ["IT", 8],
    ["人事", 5],
    ["経理", 4]
  ]
}
```

#### GET /api/v1/employees/statistics/department/{departmentId}
特定部署の統計を取得。

```bash
curl http://localhost:8080/api/v1/employees/statistics/department/1
```

### 検証エンドポイント

#### GET /api/v1/employees/email/{email}/unique
メールアドレスが一意かどうかをチェック。

**パラメータ:**
- `excludeId` (integer, オプション): チェックから特定の職員を除外

```bash
curl "http://localhost:8080/api/v1/employees/email/new@company.com/unique"
curl "http://localhost:8080/api/v1/employees/email/existing@company.com/unique?excludeId=1"
```

**レスポンス:**
```json
{
  "unique": true
}
```

#### GET /api/v1/employees/{id}/active
職員がアクティブかどうかをチェック。

```bash
curl http://localhost:8080/api/v1/employees/1/active
```

#### GET /api/v1/employees/{id}/can-delete
職員を削除できるかどうかをチェック。

```bash
curl http://localhost:8080/api/v1/employees/1/can-delete
```

#### GET /api/v1/employees/{employeeId}/can-assign/{departmentId}
職員を部署に割り当て可能かどうかをチェック。

```bash
curl http://localhost:8080/api/v1/employees/1/can-assign/2
```

### バッチ操作

#### PATCH /api/v1/employees/batch/activate
複数の職員をアクティブ化。

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/batch/activate \
  -H "Content-Type: application/json" \
  -d '[1, 2, 3, 4, 5]'
```

**レスポンス:**
```json
{
  "activated": 5
}
```

#### PATCH /api/v1/employees/batch/deactivate
複数の職員を非アクティブ化。

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/batch/deactivate \
  -H "Content-Type: application/json" \
  -d '[1, 2, 3]'
```

#### PATCH /api/v1/employees/batch/transfer/{newDepartmentId}
複数の職員を新しい部署に異動。

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/batch/transfer/2 \
  -H "Content-Type: application/json" \
  -d '[1, 3, 5]'
```

#### PATCH /api/v1/employees/department/{departmentId}/remove-all
部署からすべての職員を除外。

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/department/1/remove-all
```

## 🏢 部署 API

### 基本操作

#### GET /api/v1/departments
オプションのフィルタリング付きですべての部署を取得。

**パラメータ:**
- `activeOnly` (boolean, オプション): アクティブな部署のみをフィルタ

```bash
# すべての部署を取得
curl http://localhost:8080/api/v1/departments

# アクティブな部署のみを取得
curl http://localhost:8080/api/v1/departments?activeOnly=true
```

**レスポンス:**
```json
[
  {
    "id": 1,
    "name": "人事部",
    "code": "HR",
    "budget": 1200000.00,
    "description": "人事部門",
    "active": true,
    "employeeCount": 5,
    "createdAt": "2024-01-15T10:30:00Z",
    "modifiedAt": "2024-01-15T10:30:00Z"
  }
]
```

#### GET /api/v1/departments/{id}
IDで特定の部署を取得。

```bash
curl http://localhost:8080/api/v1/departments/1
```

#### GET /api/v1/departments/code/{code}
コードで部署を取得。

```bash
curl http://localhost:8080/api/v1/departments/code/HR
```

#### GET /api/v1/departments/with-employee-count
職員数付きですべての部署を取得。

```bash
curl http://localhost:8080/api/v1/departments/with-employee-count
```

#### POST /api/v1/departments
新しい部署を作成。

```bash
curl -X POST http://localhost:8080/api/v1/departments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "新部署",
    "code": "NEW",
    "budget": 1500000.00,
    "description": "テスト用の新しい部署"
  }'
```

**検証ルール:**
- `name`: 必須、2-100文字
- `code`: 必須、2-10文字、一意
- `budget`: 必須、正の数値
- `description`: オプション、最大500文字

#### PUT /api/v1/departments/{id}
既存の部署を更新。

```bash
curl -X PUT http://localhost:8080/api/v1/departments/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "更新された人事部",
    "code": "HR",
    "budget": 1300000.00,
    "description": "更新された人事部門",
    "active": true
  }'
```

#### DELETE /api/v1/departments/{id}
部署を削除（アクティブな職員がいない場合のみ）。

```bash
curl -X DELETE http://localhost:8080/api/v1/departments/1
```

### ステータス操作

#### PATCH /api/v1/departments/{id}/activate
部署をアクティブ化。

```bash
curl -X PATCH http://localhost:8080/api/v1/departments/1/activate
```

#### PATCH /api/v1/departments/{id}/deactivate
部署を非アクティブ化。

```bash
curl -X PATCH http://localhost:8080/api/v1/departments/1/deactivate
```

### 検索操作

#### GET /api/v1/departments/search
高度な部署検索。

**パラメータ:**
- `name` (string): 名前パターンで検索
- `minBudget` (decimal): 最小予算フィルタ
- `maxBudget` (decimal): 最大予算フィルタ
- `minEmployees` (integer): 最小職員数

```bash
# 名前で検索
curl "http://localhost:8080/api/v1/departments/search?name=技術"

# 予算範囲で検索
curl "http://localhost:8080/api/v1/departments/search?minBudget=1000000&maxBudget=2000000"

# 最小職員数で検索
curl "http://localhost:8080/api/v1/departments/search?minEmployees=5"
```

#### GET /api/v1/departments/above-average-budget
平均予算を上回る部署を取得。

```bash
curl http://localhost:8080/api/v1/departments/above-average-budget
```

### 統計操作

#### GET /api/v1/departments/statistics
部署統計を取得。

```bash
curl http://localhost:8080/api/v1/departments/statistics
```

**レスポンス:**
```json
{
  "totalActiveDepartments": 5,
  "totalActiveBudget": 9500000.00,
  "averageActiveBudget": 1900000.00
}
```

### ビジネス操作

#### POST /api/v1/departments/{fromId}/transfer-employees/{toId}
ある部署から別の部署にすべての職員を異動。

```bash
curl -X POST http://localhost:8080/api/v1/departments/1/transfer-employees/2
```

**レスポンス:**
```json
{
  "success": true
}
```

### 検証エンドポイント

#### GET /api/v1/departments/code/{code}/unique
部署コードが一意かどうかをチェック。

**パラメータ:**
- `excludeId` (integer, オプション): チェックから特定の部署を除外

```bash
curl "http://localhost:8080/api/v1/departments/code/NEW/unique"
curl "http://localhost:8080/api/v1/departments/code/HR/unique?excludeId=1"
```

#### GET /api/v1/departments/{id}/can-delete
部署を削除できるかどうかをチェック。

```bash
curl http://localhost:8080/api/v1/departments/1/can-delete
```

**レスポンス:**
```json
{
  "canDelete": false
}
```

### バッチ操作

#### PATCH /api/v1/departments/batch/activate
複数の部署をアクティブ化。

```bash
curl -X PATCH http://localhost:8080/api/v1/departments/batch/activate \
  -H "Content-Type: application/json" \
  -d '[1, 2, 3]'
```

#### PATCH /api/v1/departments/batch/deactivate
複数の部署を非アクティブ化。

```bash
curl -X PATCH http://localhost:8080/api/v1/departments/batch/deactivate \
  -H "Content-Type: application/json" \
  -d '[4, 5]'
```

#### DELETE /api/v1/departments/cleanup/inactive-without-employees
職員のいない非アクティブな部署をすべて削除。

```bash
curl -X DELETE http://localhost:8080/api/v1/departments/cleanup/inactive-without-employees
```

**レスポンス:**
```json
{
  "deleted": 2
}
```

## 🔐 エラーレスポンス

### 標準エラーコード

| コード | 説明 | 例 |
|------|-------------|---------|
| 200  | 成功 | リクエストが正常に完了 |
| 201  | 作成 | リソースが正常に作成 |
| 204  | コンテンツなし | リソースが正常に削除 |
| 400  | 不正なリクエスト | 無効な入力データ |
| 404  | 見つかりません | リソースが見つからない |
| 409  | 競合 | リソース制約違反 |
| 500  | 内部サーバーエラー | 予期しないサーバーエラー |

### エラーレスポンス例

#### 検証エラー (400)
```json
{
  "error": "Bad Request",
  "message": "職員のメールアドレスが既に存在します: tanaka.taro@company.com",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/v1/employees"
}
```

#### 見つからないエラー (404)
```json
{
  "error": "Not Found",
  "message": "ID: 999の職員が見つかりません",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/v1/employees/999"
}
```

#### 競合エラー (409)
```json
{
  "error": "Conflict",
  "message": "アクティブな職員がいる部署は削除できません",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/v1/departments/1"
}
```

## 🧪 API テスト例

### 完全ワークフロー例

```bash
#!/bin/bash
# 完全な職員管理ワークフロー

echo "1. 部署を作成"
DEPT_ID=$(curl -s -X POST http://localhost:8080/api/v1/departments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "エンジニアリング部",
    "code": "ENG",
    "budget": 2500000.00,
    "description": "ソフトウェアエンジニアリング部門"
  }' | jq -r '.id')

echo "部署が作成されました ID: $DEPT_ID"

echo "2. 職員を作成"
EMP_ID=$(curl -s -X POST http://localhost:8080/api/v1/employees \
  -H "Content-Type: application/json" \
  -d "{
    \"firstName\": \"愛美\",
    \"lastName\": \"エンジニア\",
    \"email\": \"engineer.aimi@company.com\",
    \"hireDate\": \"2024-01-15\",
    \"departmentId\": $DEPT_ID
  }" | jq -r '.id')

echo "職員が作成されました ID: $EMP_ID"

echo "3. 職員詳細を取得"
curl -s http://localhost:8080/api/v1/employees/$EMP_ID | jq '.'

echo "4. 職員を別の部署に異動"
curl -s -X POST http://localhost:8080/api/v1/employees/$EMP_ID/transfer/1 | jq '.'

echo "5. 部署統計を取得"
curl -s http://localhost:8080/api/v1/departments/statistics | jq '.'

echo "6. 職員を検索"
curl -s "http://localhost:8080/api/v1/employees/search?term=愛美" | jq '.'

echo "ワークフローが正常に完了しました！"
```

### パフォーマンステスト

```bash
#!/bin/bash
# パフォーマンステストスクリプト

echo "パフォーマンステスト用に複数の職員を作成中..."

for i in {1..100}; do
  curl -s -X POST http://localhost:8080/api/v1/employees \
    -H "Content-Type: application/json" \
    -d "{
      \"firstName\": \"職員$i\",
      \"lastName\": \"テスト\",
      \"email\": \"employee$i@perf.com\",
      \"hireDate\": \"2024-01-$((i % 28 + 1))\",
      \"departmentId\": $((i % 3 + 1))
    }" > /dev/null

  if [ $((i % 10)) -eq 0 ]; then
    echo "$i人の職員を作成しました..."
  fi
done

echo "パフォーマンステストデータが作成されました。検索パフォーマンスをテスト中..."

time curl -s "http://localhost:8080/api/v1/employees/search?term=職員" > /dev/null
time curl -s "http://localhost:8080/api/v1/employees?activeOnly=true" > /dev/null
time curl -s "http://localhost:8080/api/v1/departments/with-employee-count" > /dev/null

echo "パフォーマンステストが完了しました！"
```

## 📊 監視とヘルスチェック

### ヘルスエンドポイント
```bash
# アプリケーションヘルスをチェック
curl http://localhost:8080/actuator/health
```

**レスポンス:**
```json
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP",
      "details": {
        "database": "PostgreSQL",
        "validationQuery": "isValid()"
      }
    }
  }
}
```

### メトリクスエンドポイント
```bash
# アプリケーションメトリクスを取得
curl http://localhost:8080/actuator/metrics
```

---

**次のステップ**: このAPIドキュメントを[テストガイド](TESTING_GUIDE.md)と一緒に使用して、学習の旅のための包括的なテストシナリオを作成してください。