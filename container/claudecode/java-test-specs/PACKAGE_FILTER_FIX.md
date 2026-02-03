# JaCoCoカバレッジパッケージフィルタリング問題の解決

## 問題の詳細分析

### 提供されたJaCoCoレポートの内容
- **全体カバレッジ**: 命令98.1%, ブランチ100%, ライン96.2%
- **パッケージ名**: `com.mycompany.service.batch`
- **クラス数**: 6クラス（3クラスがカバー済み）
- **データ品質**: 完全で正常なJaCoCoレポート

### 問題の原因
Java Test Specification Generatorのデフォルトパッケージフィルタが`com.example`のみを対象とするため、`com.mycompany.service`パッケージが除外されている。

## 解決策

### 1. ツール側での動的パッケージ検出の活用

Java Test Specification Generatorは動的パッケージ検出機能を搭載しているが、テストファイルが必要です。

#### 必要な条件
- テストファイル（*Test.java）が存在する
- テストファイルが適切なパッケージ宣言を含む

#### テストファイル例
```java
package com.mycompany.service.batch;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class HelloServiceTest {

    /**
     * @TestModule HelloService
     * @TestCase サービステスト
     * @TestOverview Hello機能のテスト
     */
    @Test
    void testHello() {
        // テスト実装
        assertTrue(true);
    }
}
```

### 2. パッケージ構造の確認

プロジェクト構造を確認：

```bash
# テストファイルの存在確認
find . -name "*Test.java" -type f

# テストファイルのパッケージ宣言確認
grep -r "package com.mycompany" src/test/java/ || echo "テストファイルにパッケージ宣言がありません"
```

### 3. 実行時デバッグによる確認

```bash
java -jar java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output debug-report.xlsx \
  --log-level DEBUG
```

**期待される動作**:
1. テストファイルから`com.mycompany.service`パッケージを検出
2. 動的パッケージフィルタリングが適用
3. カバレッジデータが正常に処理される

### 4. マルチモジュールプロジェクトの場合

```bash
# マルチモジュールモード（テストファイルがある場合）
java -jar java-test-specification-generator-1.0.0.jar \
  --project-root . \
  --output-dir ./reports \
  --log-level DEBUG
```

### 5. 手動パッケージ指定（将来の機能拡張）

現在のバージョンでは、パッケージ名を手動指定する機能はありませんが、以下のような機能が有用です：

```bash
# 理想的な実行方法（将来の機能拡張案）
java -jar java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output report.xlsx \
  --package-filter "com.mycompany.service"
```

## デバッグ手順

### ステップ1: パッケージ検出の確認

```bash
# デバッグモードで実行
java -jar java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output debug.xlsx \
  --log-level DEBUG 2>&1 | grep -i package
```

**期待される出力**:
```
[Coverage Debug] Dynamic package detection completed: 1 unique packages from X test files
[Coverage Debug] Package distribution: {com/mycompany/service/batch=6}
```

### ステップ2: カバレッジファイル検出の確認

```bash
# カバレッジファイルの存在確認
find . -name "jacoco.xml" -exec echo "Found: {}" \; -exec head -5 {} \;
```

### ステップ3: フィルタリング結果の確認

デバッグログで以下を確認：
```
[Coverage Debug] Filtering completed: Total: X -> Filtered: Y
[Coverage Debug] Filter statistics: Tool packages excluded: A, Package filter excluded: B
```

## 期待される解決結果

### Before（現在）
```
[Coverage Debug] All coverage entries were filtered out!
[Coverage Debug] Applied filter: [com.example]
Coverage data: 0 entries
```

### After（解決後）
```
[Coverage Debug] Dynamic package detection: com.mycompany.service.batch
[Coverage Debug] Filtering completed: Total: 6 -> Filtered: 6
Coverage data: 6 entries with 98.1% instruction coverage
```

## トラブルシューティング

### Q1: テストファイルが存在しない場合
**A**: 最低限のテストファイルを作成してパッケージ宣言を含める

### Q2: 動的検出が機能しない場合
**A**: `--log-level DEBUG`でログを確認し、テストファイルの読み取り状況をチェック

### Q3: 依然としてカバレッジが0の場合
**A**: JaCoCoレポートファイルのパスとアクセス権限を確認

この解決策により、優れたカバレッジデータ（98.1%命令カバレッジ）が正常に集計されるようになります。