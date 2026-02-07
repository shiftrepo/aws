# セッション管理の仕組みとRedisのメリット

## 1. セッション管理の基本的な仕組み

### 従来のセッション管理（インメモリ）

```
┌─────────────┐
│   Client    │
│             │
│  Cookie:    │
│  SESSION=ABC│
└──────┬──────┘
       │ HTTP Request
       ↓
┌─────────────────────────┐
│  Application Server     │
│                         │
│  ┌───────────────────┐  │
│  │ Session Storage   │  │
│  │ (Memory/Heap)     │  │
│  │                   │  │
│  │ ABC → {userId:123}│  │
│  │       {cart:[]}   │  │
│  └───────────────────┘  │
└─────────────────────────┘
```

**問題点**:
- サーバーを再起動するとセッションが消える
- 複数サーバーでセッションが共有できない
- スケールアウトできない

### Redisを使ったセッション管理

```
┌─────────────┐         ┌─────────────┐
│  Client 1   │         │  Client 2   │
│ SESSION=ABC │         │ SESSION=XYZ │
└──────┬──────┘         └──────┬──────┘
       │                       │
       ↓                       ↓
┌──────────────────────────────────────┐
│        Load Balancer                 │
└──────────┬───────────────────┬───────┘
           │                   │
           ↓                   ↓
    ┌──────────┐        ┌──────────┐
    │ Pod 1    │        │ Pod 2    │
    │ Backend  │        │ Backend  │
    └────┬─────┘        └────┬─────┘
         │                   │
         └─────────┬─────────┘
                   ↓
            ┌─────────────┐
            │   Redis     │
            │             │
            │ ABC → {...} │
            │ XYZ → {...} │
            └─────────────┘
```

## 2. Redisセッション管理のメリット

### 2.1 永続性（Persistence）

**インメモリの場合**:
```
Server Restart → Sessions Lost ❌
```

**Redisの場合**:
```
Server Restart → Sessions Preserved ✅
```

### 2.2 分散システム対応（Distributed Sessions）

**インメモリの場合**:
```
Client → Server 1 (Session ABC)
Client → Server 2 (Session ABC not found!) ❌
```

**Redisの場合**:
```
Client → Server 1 → Redis (Session ABC) ✅
Client → Server 2 → Redis (Session ABC) ✅
```

### 2.3 高速アクセス

Redis特性:
- In-Memory Database: メモリ上で動作
- Key-Value Store: O(1)の高速アクセス
- 平均レスポンス: < 1ms

### 2.4 自動有効期限管理

```redis
spring:session:sessions:ABC
  TTL: 1800 seconds (30 minutes)
  ↓
  Automatic cleanup when expired
```

## 3. Kubernetes環境での特有のメリット

### 3.1 Pod の再起動・スケーリングに対応

```
Scenario 1: Pod Crash
┌─────────┐
│ Pod 1   │ ← Crash! 💥
└─────────┘
     ↓ Kubernetes restarts
┌─────────┐
│ Pod 1'  │ ← Sessions still available from Redis ✅
└─────────┘

Scenario 2: Scale Up
┌─────────┐
│ Pod 1   │
└─────────┘
     ↓ kubectl scale --replicas=3
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Pod 1   │  │ Pod 2   │  │ Pod 3   │
└─────────┘  └─────────┘  └─────────┘
      ↓           ↓           ↓
          All share Redis sessions ✅
```

### 3.2 Rolling Update（無停止デプロイ）

```
Version 1.0.0                    Version 1.1.0
┌─────────┐  ┌─────────┐        ┌─────────┐  ┌─────────┐
│ Pod 1   │  │ Pod 2   │   →    │ Pod 1'  │  │ Pod 2'  │
│ v1.0.0  │  │ v1.0.0  │        │ v1.1.0  │  │ v1.1.0  │
└────┬────┘  └────┬────┘        └────┬────┘  └────┬────┘
     │            │                   │            │
     └────────────┴───────────────────┴────────────┘
                         │
                    ┌─────────┐
                    │  Redis  │ ← Sessions maintained during update ✅
                    └─────────┘

User Experience:
- No session loss during deployment
- No forced re-login
- Seamless version transition
```

### 3.3 Multi-AZ / Multi-Region 対応

```
┌──────────────────────────────────────────┐
│          Kubernetes Cluster              │
│                                          │
│  ┌─────────┐    ┌─────────┐            │
│  │ Zone A  │    │ Zone B  │            │
│  │         │    │         │            │
│  │ Pod 1   │    │ Pod 2   │            │
│  └────┬────┘    └────┬────┘            │
│       │              │                  │
│       └──────┬───────┘                  │
│              ↓                          │
│       ┌─────────────┐                   │
│       │Redis Cluster│                   │
│       │(Replication)│                   │
│       └─────────────┘                   │
└──────────────────────────────────────────┘

Zone failure → Sessions still available ✅
```

### 3.4 StatelessなPod設計

**Without Redis (Stateful Pods)**:
```
┌─────────────────┐
│ Pod 1           │
│ ┌─────────────┐ │  ← Must maintain state
│ │   Sessions  │ │  ← Cannot freely terminate
│ │   User data │ │  ← Backup required
│ └─────────────┘ │
└─────────────────┘

❌ Complex lifecycle management
❌ Difficult to scale
❌ Risk of data loss
```

**With Redis (Stateless Pods)**:
```
┌─────────────┐
│ Pod 1       │  ← No local state
│ (Stateless) │  ← Can terminate anytime
└──────┬──────┘  ← Easy to scale
       │
       ↓
┌─────────────┐
│   Redis     │  ← Centralized state
└─────────────┘

✅ Simple lifecycle management
✅ Easy to scale horizontally
✅ No data loss risk
```

## 4. 実際の動作例（現在のシステム）

### 現在の構成

```yaml
Backend Pods: 2 replicas
Redis: 1 pod (production: cluster recommended)
Session Timeout: 1800 seconds (30 minutes)
Session Affinity: ClientIP (Load Balancer level)
```

### セッションデータ構造

```
Key: spring:session:sessions:{uuid}
Type: Hash

Fields:
- creationTime: 1770435350157
- lastAccessedTime: 1770435350157
- maxInactiveInterval: 1800
- sessionAttr:... (application data)
```

### パフォーマンス特性

```
Session Read:  < 1ms (Redis in-memory)
Session Write: < 2ms (Redis persistence)
Network RTT:   < 1ms (same cluster)
Total:         ~ 3-5ms per request
```

## 5. 設定のベストプラクティス

### 5.1 Production環境推奨構成

```yaml
Redis:
  Mode: Cluster or Sentinel
  Replicas: 3+ (High Availability)
  Persistence: AOF + RDB
  Memory: Based on active users
    - 1MB per 1000 sessions (average)
    - 10,000 users → ~10MB

Backend:
  Replicas: 3+ (Load distribution)
  Session Timeout: 30-60 minutes
  Connection Pool: 
    - Min: 2
    - Max: 8 per pod
```

### 5.2 セキュリティ設定

```yaml
Session Cookie:
  HttpOnly: true       ← XSS prevention
  Secure: true         ← HTTPS only (production)
  SameSite: Lax       ← CSRF prevention
  
Redis:
  Authentication: Required
  TLS: Enabled (production)
  Network Policy: Pod-to-Pod only
```

## 6. トレードオフと考慮点

### メリット
✅ High Availability
✅ Horizontal Scaling
✅ Session Persistence
✅ Fast Access
✅ Stateless Architecture

### デメリット/考慮点
⚠️ Redis dependency (single point of failure without HA)
⚠️ Network latency (vs local memory)
⚠️ Serialization overhead
⚠️ Additional infrastructure cost

### 対策
- Redis Cluster/Sentinel for HA
- Redis connection pooling
- Efficient serialization (JSON/Kryo)
- Monitor Redis performance

## 7. 監視項目

```
Redis Metrics:
- Connected clients
- Memory usage
- Key count (active sessions)
- Command latency
- Network throughput

Application Metrics:
- Session creation rate
- Session duration
- Active sessions
- Session timeout rate
```

