# ロードバランシング下でのRedisセッション管理の影響

## 1. ロードバランシングの基本パターン

### パターンA: Redisなし + Session Affinityなし（最悪）
```
Request 1 → LB → Pod1 [Session ABC created in Pod1 memory]
Request 2 → LB → Pod2 [Session ABC not found!] ❌
User: "ログインできない！"
```

### パターンB: Redisなし + Session Affinityあり（準最適）
```
Request 1 → LB → Pod1 [Session ABC in Pod1 memory]
Request 2 → LB → Pod1 [Same pod, Session ABC found] ✅
Problem: Pod1が落ちたら？ → Session消失 ❌
```

### パターンC: Redisあり + Session Affinityなし（良い）
```
Request 1 → LB → Pod1 → Redis [Session ABC]
Request 2 → LB → Pod2 → Redis [Session ABC found] ✅
Any pod can serve any request!
```

### パターンD: Redisあり + Session Affinityあり（最適）
```
Request 1 → LB → Pod1 → Redis [Session ABC]
Request 2 → LB → Pod1 (sticky) → Redis [Session ABC]
Benefits: 
  - Lower Redis queries (local cache可能)
  - Better performance
  - Failover時もRedisで保護
```

## 2. ロードバランシングアルゴリズムの種類

### Round Robin（順番）
```
Client A: Pod1 → Pod2 → Pod3 → Pod1 → ...
Client B: Pod2 → Pod3 → Pod1 → Pod2 → ...
```
- メリット: 均等に負荷分散
- デメリット: Sessionの分散（Redisなしでは問題）

### Least Connections（最小接続数）
```
Pod1: 5 connections  ← Next request goes here
Pod2: 10 connections
Pod3: 8 connections
```
- メリット: 負荷の偏りを自動調整
- デメリット: Session追跡が複雑

### IP Hash / ClientIP Affinity（IPベース）
```
Client IP: 192.168.1.100 → Hash → Always Pod2
Client IP: 192.168.1.101 → Hash → Always Pod1
```
- メリット: 同一クライアントは同一Pod（Session維持容易）
- デメリット: IPが変わると別Pod（NAT環境で問題）

### Cookie-based Affinity（クッキーベース）
```
First Request → Pod2 → Set-Cookie: SERVERID=Pod2
Next Request (with Cookie) → Always Pod2
```
- メリット: クライアント単位で確実にSticky
- デメリット: 負荷の偏りが発生しやすい

## 3. Session Affinity（Sticky Session）の詳細

### 動作メカニズム

**Without Session Affinity:**
```
Time  Client    LoadBalancer    Backend
T1    Request → Round Robin  →  Pod1 (Session created)
T2    Request → Round Robin  →  Pod2 (Session not found!)
T3    Request → Round Robin  →  Pod3 (Session not found!)
```

**With Session Affinity (ClientIP):**
```
Time  Client IP      LoadBalancer         Backend
T1    10.0.1.50  →   Hash(10.0.1.50)  →  Pod2 (Session created)
T2    10.0.1.50  →   Hash(10.0.1.50)  →  Pod2 (Session found!)
T3    10.0.1.50  →   Hash(10.0.1.50)  →  Pod2 (Session found!)
```

### Kubernetes Service設定

```yaml
# Session Affinityなし（デフォルト）
apiVersion: v1
kind: Service
spec:
  sessionAffinity: None
  # Result: Round-robin distribution
  # Requires: Redis for session sharing

# Session Affinityあり
apiVersion: v1
kind: Service
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 1800  # 30 minutes
  # Result: Same client → same pod for 30min
  # Benefit: Reduced Redis queries
```

## 4. パフォーマンスへの影響

### Redisなしの場合

```
Scenario: 3 Pods, 100 requests/sec

Without Session Affinity:
  Request → Random Pod → Session not found (66% miss rate)
  Result: 66 login failures per second ❌
  
With Session Affinity:
  Request → Sticky Pod → Session in memory (0% miss rate)
  Result: 0 login failures ✅
  BUT: Pod crashes → All sessions lost ❌
```

### Redisありの場合

```
Scenario: 3 Pods, 100 requests/sec

Without Session Affinity:
  Request 1 → Pod1 → Redis lookup (1ms)
  Request 2 → Pod2 → Redis lookup (1ms)
  Request 3 → Pod3 → Redis lookup (1ms)
  Average: 1ms overhead per request
  Total: 100ms/sec Redis overhead

With Session Affinity:
  Request 1 → Pod1 → Redis lookup (1ms, cache locally)
  Request 2 → Pod1 → Local cache (0ms) ✅
  Request 3 → Pod1 → Local cache (0ms) ✅
  Average: 0.1ms overhead per request
  Total: 10ms/sec Redis overhead
  
Performance improvement: 10x faster! 🚀
```

### レスポンスタイム比較

```
┌─────────────────────────────────────────────────┐
│ Configuration          │ Response Time          │
├─────────────────────────────────────────────────┤
│ Local Memory Only      │ 50ms   ████           │
│ Redis (no affinity)    │ 53ms   █████          │
│ Redis (with affinity)  │ 50ms   ████    (cache)│
│ Redis + Local Cache    │ 50ms   ████    (best) │
└─────────────────────────────────────────────────┘

Overhead: ~3ms for Redis lookup (negligible)
```

## 5. 負荷分散とフェイルオーバー

### Without Session Affinity

```
Normal Operation:
  ┌─────┐  ┌─────┐  ┌─────┐
  │Pod1 │  │Pod2 │  │Pod3 │  Each handles 33%
  │ 33% │  │ 33% │  │ 33% │  Perfect distribution
  └──┬──┘  └──┬──┘  └──┬──┘
     └────────┴────────┘
            Redis

Pod1 Crashes:
  ┌─────┐  ┌─────┐
  │Pod2 │  │Pod3 │  Traffic redistributes
  │ 50% │  │ 50% │  Seamlessly to others
  └──┬──┘  └──┬──┘  Sessions preserved! ✅
     └────┬───┘
         Redis
```

### With Session Affinity

```
Normal Operation:
  ┌─────┐  ┌─────┐  ┌─────┐
  │Pod1 │  │Pod2 │  │Pod3 │
  │ 40% │  │ 35% │  │ 25% │  Uneven (by client IP)
  └──┬──┘  └──┬──┘  └──┬──┘
     └────────┴────────┘
            Redis

Pod1 Crashes:
  ┌─────┐  ┌─────┐
  │Pod2 │  │Pod3 │  Clients rehash to
  │ 55% │  │ 45% │  different pods
  └──┬──┘  └──┬──┘  Sessions still work! ✅
     └────┬───┘     (thanks to Redis)
         Redis
         
Without Redis:
  Pod1 clients → Lost sessions ❌
  Must re-login ❌
```

## 6. スケーリング時の影響

### Horizontal Pod Autoscaler (HPA)

```
Load increases: 2 pods → 5 pods

Without Redis:
  Old sessions → Lost (new pods don't have them) ❌
  Users → Must re-login ❌
  
With Redis + No Affinity:
  Old sessions → Available on all pods ✅
  New pods → Immediately serve existing sessions ✅
  Load → Evenly distributed ✅

With Redis + Affinity:
  Old sessions → Preserved ✅
  New pods → Gradually get new sessions
  Load → May be uneven initially (affinity timeout)
  After 30min → Fully rebalanced ✅
```

## 7. ネットワークトラフィックの影響

### Redis通信オーバーヘッド

```
Per Request:
  Client → LB → Pod → Redis
                  ↓     ↑
                  Request (0.1KB)
                  Response (1KB)
                  Network: 1ms RTT
                  
1000 requests/sec:
  Without Redis: 0 KB/sec internal traffic
  With Redis:    1.1 MB/sec internal traffic
  
Cost: Minimal in same cluster/datacenter
Impact: ~1ms added latency (negligible)
```

### Connection Pool効率

```
Configuration:
  Backend Pods: 3
  Redis: 1 instance
  Connection Pool per Pod: Max 8 connections

Total Connections: 3 × 8 = 24 connections to Redis

Benefits:
  - Connection reuse (no TCP handshake per request)
  - Pipelining support
  - Reduced Redis load
  
Without Pool:
  Each request → New connection → Expensive
  Redis → Overloaded with connection overhead
```

## 8. トレードオフ分析

### No Affinity + Redis

**メリット:**
✅ Perfect load distribution
✅ Fast failover (no sticky sessions to lose)
✅ Easy autoscaling (immediate distribution)
✅ No client IP dependency

**デメリット:**
⚠️ Every request hits Redis (more queries)
⚠️ Slightly higher latency (~1ms)
⚠️ More network traffic

**最適用途:**
- High availability critical
- Frequent pod scaling
- Distributed clients (CDN, mobile apps)

### With Affinity + Redis

**メリット:**
✅ Reduced Redis queries (local caching)
✅ Lower latency (cache hits)
✅ Less network traffic
✅ Failover still protected by Redis

**デメリット:**
⚠️ Uneven load distribution
⚠️ Slower autoscaling rebalance
⚠️ IP change issues (NAT, mobile networks)

**最適用途:**
- Performance critical
- Stable client IPs
- Lower Redis load desired

## 9. モニタリング指標

```
Key Metrics:

Load Distribution:
  - Requests per pod (stddev)
  - Connection count per pod
  - CPU/Memory per pod

Session Performance:
  - Session lookup latency (p50, p95, p99)
  - Cache hit rate (with affinity)
  - Session creation rate

Redis Performance:
  - Commands per second
  - Connection count
  - Network throughput
  - Latency (p50, p95, p99)

Failure Scenarios:
  - Session loss rate (should be 0%)
  - Failover time
  - Redistribution time
```
