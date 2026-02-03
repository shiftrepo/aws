# JaCoCoカバレッジ集計問題の解決方法

## 問題分析

提供されたpom.xmlは親POMとしての基本構造はありますが、JaCoCoカバレッジ収集に必要な設定が完全に欠けています。

### 欠けている設定
1. **JaCoCoプラグイン**: カバレッジ収集・レポート生成
2. **maven-surefire-plugin**: テスト実行とJaCoCoエージェント連携
3. **テスト依存関係**: JUnit等のテストフレームワーク
4. **プロパティ設定**: JaCoCoバージョンやJavaバージョン管理

## 解決策: 完全なJaCoCo設定追加

### 1. プロパティセクションの追加/更新

現在のpom.xmlの`<repositories>`セクションの前に以下を追加：

```xml
<properties>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>

    <!-- テストフレームワークバージョン -->
    <junit.version>5.10.1</junit.version>

    <!-- JaCoCoバージョン -->
    <jacoco.version>0.8.11</jacoco.version>

    <!-- Mavenプラグインバージョン -->
    <maven-compiler.version>3.11.0</maven-compiler.version>
    <maven-surefire.version>3.0.0-M9</maven-surefire.version>
</properties>
```

### 2. 依存関係管理の追加

`<repositories>`セクションの前に以下を追加：

```xml
<dependencyManagement>
    <dependencies>
        <!-- JUnitテストフレームワーク -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-api</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-engine</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### 3. ビルドプラグインの修正

現在の`<build>`セクションの`<plugins>`内に以下のプラグインを追加：

```xml
<build>
    <plugins>
        <!-- 既存のexec-maven-plugin -->
        <plugin>
            <groupId>org.codehaus.mojo</groupId>
            <artifactId>exec-maven-plugin</artifactId>
            <!-- ...既存の設定... -->
        </plugin>

        <!-- Maven Compiler Plugin -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>${maven-compiler.version}</version>
            <configuration>
                <source>${maven.compiler.source}</source>
                <target>${maven.compiler.target}</target>
                <encoding>${project.build.sourceEncoding}</encoding>
            </configuration>
        </plugin>

        <!-- Maven Surefire Plugin（テスト実行） -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <version>${maven-surefire.version}</version>
            <configuration>
                <!-- JaCoCoエージェントのargLineを継承 -->
                <argLine>${argLine} -Dfile.encoding=UTF-8</argLine>
                <includes>
                    <include>**/*Test.java</include>
                    <include>**/*Tests.java</include>
                </includes>
            </configuration>
        </plugin>

        <!-- ⭐ JaCoCoプラグイン（最重要） -->
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

                <!-- テスト後に各モジュールのレポート生成 -->
                <execution>
                    <id>report</id>
                    <phase>test</phase>
                    <goals>
                        <goal>report</goal>
                    </goals>
                </execution>

                <!-- マルチモジュール集約レポート生成 -->
                <execution>
                    <id>report-aggregate</id>
                    <phase>verify</phase>
                    <goals>
                        <goal>report-aggregate</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

### 4. モジュールセクションの確認

`<modules>`セクションが存在することを確認してください：

```xml
<modules>
    <module>your-module-1</module>
    <module>your-module-2</module>
    <!-- 追加のモジュール -->
</modules>
```

## 子モジュールpom.xml設定

各子モジュールのpom.xmlには以下が必要：

```xml
<project>
    <!-- 親POM継承 -->
    <parent>
        <groupId>com.example</groupId>
        <artifactId>parent</artifactId>
        <version>1.0.0</version>
    </parent>

    <artifactId>child-module</artifactId>

    <!-- テスト依存関係 -->
    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <!-- プラグイン継承（自動） -->
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

## 実行コマンド

### カバレッジレポート生成
```bash
# 全モジュールでテスト実行+カバレッジ生成
mvn clean compile test jacoco:report

# 集約レポートも含める場合
mvn clean compile test verify
```

### 生成されるファイル構造
```
project-root/
├── module-1/
│   └── target/site/jacoco/
│       ├── jacoco.xml      # ⭐重要：XMLレポート
│       ├── jacoco.csv
│       └── index.html
├── module-2/
│   └── target/site/jacoco/
│       ├── jacoco.xml      # ⭐重要：XMLレポート
│       ├── jacoco.csv
│       └── index.html
└── target/site/jacoco-aggregate/
    ├── jacoco.xml          # 集約XMLレポート
    └── index.html          # 集約HTMLレポート
```

## Java Test Specification Generator実行

```bash
# マルチモジュールモードでの実行
java -jar java-test-specification-generator-1.0.0.jar \
  --project-root . \
  --output-dir ./reports \
  --log-level DEBUG
```

## トラブルシューティング

### XMLレポートが生成されない場合

1. **JaCoCoプラグイン確認**
```bash
mvn help:effective-pom | grep -A 10 -B 10 jacoco
```

2. **テスト実行確認**
```bash
mvn clean test -X | grep -i jacoco
```

3. **ファイル生成確認**
```bash
find . -name "jacoco.xml" -type f
```

### よくある問題

1. **argLine設定忘れ**
   - surefire-pluginに`<argLine>${argLine}</argLine>`が必要

2. **プラグインがpluginManagementのみ**
   - 実際の`<plugins>`セクションにプラグインを配置する

3. **依存関係の欠如**
   - JUnitの依存関係が子モジュールに設定されていない

4. **フェーズ設定ミス**
   - `jacoco:report`ゴールが`test`フェーズで実行されるよう設定

## 修正後の動作確認

### 期待される動作
1. `mvn clean test`でJaCoCoエージェントが起動
2. テスト実行時にカバレッジデータが収集
3. `target/site/jacoco/jacoco.xml`が生成される
4. Java Test Specification Generatorがカバレッジを正常に読み込む

### デバッグコマンド
```bash
# JaCoCoプラグイン動作確認
mvn clean test -Djacoco.debug=true

# Java Test Specification Generator詳細ログ
java -jar java-test-specification-generator-1.0.0.jar \
  --project-root . --output-dir ./debug-reports --log-level DEBUG
```

この設定により、JaCoCoカバレッジが正常に集計され、Java Test Specification Generatorで処理できるようになります。