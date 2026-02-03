# マルチモジュールJaCoCoカバレッジ設定ガイド

## 問題: カバレッジが集計されない原因

1. **JaCoCoプラグイン設定不足**: 親pom.xmlにJaCoCoプラグインが設定されていない
2. **XMLレポート生成設定不足**: HTMLレポートのみ生成され、XMLレポートが生成されない
3. **マルチモジュール集約設定不足**: 各モジュールのカバレッジが統合されない

## 解決策: 親pom.xmlへのJaCoCo設定追加

### 1. プロパティの追加
```xml
<properties>
    <!-- 既存のプロパティに追加 -->
    <jacoco.version>0.8.11</jacoco.version>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>
```

### 2. JaCoCoプラグインをbuild/pluginsセクションに追加

現在のexec-maven-pluginの後に以下を追加：

```xml
<build>
    <plugins>
        <!-- 既存のexec-maven-plugin -->
        <plugin>
            <groupId>org.codehaus.mojo</groupId>
            <artifactId>exec-maven-plugin</artifactId>
            <!-- ...既存の設定... -->
        </plugin>

        <!-- JaCoCoプラグイン追加 -->
        <plugin>
            <groupId>org.jacoco</groupId>
            <artifactId>jacoco-maven-plugin</artifactId>
            <version>${jacoco.version}</version>
            <executions>
                <!-- テスト前にJaCoCoエージェントを準備 -->
                <execution>
                    <id>prepare-agent</id>
                    <goals>
                        <goal>prepare-agent</goal>
                    </goals>
                </execution>

                <!-- テスト後にレポート生成 -->
                <execution>
                    <id>report</id>
                    <phase>test</phase>
                    <goals>
                        <goal>report</goal>
                    </goals>
                </execution>

                <!-- マルチモジュール集約レポート -->
                <execution>
                    <id>report-aggregate</id>
                    <phase>verify</phase>
                    <goals>
                        <goal>report-aggregate</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>

        <!-- Surefireプラグインでテスト実行設定 -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <version>3.0.0-M9</version>
            <configuration>
                <!-- JaCoCoエージェントプロパティを継承 -->
                <argLine>${argLine}</argLine>
            </configuration>
        </plugin>
    </plugins>
</build>
```

### 3. JUnit依存関係の追加（テスト実行用）

dependencyManagementセクションに追加：

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.10.1</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

## 子モジュールpom.xmlでの設定

各子モジュール（module-a, module-b等）のpom.xmlには以下を追加：

```xml
<dependencies>
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>

<build>
    <plugins>
        <plugin>
            <groupId>org.jacoco</groupId>
            <artifactId>jacoco-maven-plugin</artifactId>
        </plugin>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

## 実行コマンド

### カバレッジレポート生成
```bash
# 全モジュールでテスト実行＋カバレッジ生成
mvn clean compile test jacoco:report

# または集約レポートも含める場合
mvn clean compile test verify
```

### Java Test Specification Generator実行
```bash
# 生成されたカバレッジレポートを使用してテスト仕様書生成
java -jar target/java-test-specification-generator-1.0.0.jar \
  --project-root . \
  --output-dir ./reports \
  --log-level DEBUG
```

## 期待される出力構造

```
各モジュールディレクトリ/
├── target/site/jacoco/
│   ├── jacoco.xml          # ←これが重要！XMLレポート
│   ├── jacoco.csv
│   └── index.html

親ディレクトリ/
└── target/site/jacoco-aggregate/
    ├── jacoco.xml          # 集約XMLレポート
    └── index.html          # 集約HTMLレポート
```

## トラブルシューティング

### XMLレポートが生成されない場合
```bash
# JaCoCoバージョン確認
mvn help:effective-pom | grep jacoco

# レポートファイル確認
find . -name "jacoco.xml" -type f
```

### Java Test Specification Generatorでデバッグ
```bash
# デバッグモードで詳細ログ確認
java -jar target/java-test-specification-generator-1.0.0.jar \
  --project-root . \
  --output-dir ./debug-output \
  --log-level DEBUG

# ログでカバレッジファイル検出状況を確認
```

## よくある問題と解決策

1. **HTMLレポートのみ生成される**
   - `jacoco:report`ゴールが実行されていない
   - 解決: `mvn test jacoco:report`で明示的実行

2. **マルチモジュールで集約されない**
   - `report-aggregate`実行設定不足
   - 解決: `mvn verify`で集約レポート生成

3. **パッケージフィルタリングで除外**
   - デバッグログでパッケージ名確認
   - 解決: 適切なパッケージ名でテストファイルを配置