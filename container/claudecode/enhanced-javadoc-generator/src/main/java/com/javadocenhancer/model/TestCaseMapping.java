package com.javadocenhancer.model;

import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

/**
 * テストケースマッピング情報クラス
 *
 * ソースメソッドとテストメソッドの関連付けを管理し、
 * テストケースリンク機能で使用されます。
 */
public class TestCaseMapping {

    // テストケース基本情報
    private String testClassName;       // テストクラス名
    private String testMethodName;      // テストメソッド名
    private String testPackageName;     // テストパッケージ名
    private Path testFilePath;          // テストファイルパス
    private int testLineNumber;         // テストメソッドの行番号

    // 関連ソースメソッド情報
    private String sourceClassName;     // ソースクラス名
    private String sourceMethodName;    // ソースメソッド名
    private String sourcePackageName;   // ソースパッケージ名

    // マッピング詳細情報
    private MappingType mappingType;    // マッピングタイプ
    private double mappingConfidence;   // マッピング信頼度（0.0-1.0）
    private String mappingReason;       // マッピング理由

    // テストアノテーション情報
    private Map<String, String> testAnnotations; // テストアノテーション（@Test, @TestCase等）

    // メタ情報
    private long createdTime = System.currentTimeMillis(); // 作成時刻
    private String mappingSource = "AUTO_DETECTION";        // マッピング元

    /**
     * マッピングタイプ列挙型
     */
    public enum MappingType {
        EXACT_MATCH("完全一致", 1.0),           // testAdd -> add
        PATTERN_MATCH("パターン一致", 0.8),     // testAddNumbers -> add
        NAME_SIMILARITY("名前類似", 0.6),       // testCalculate -> calc
        ANNOTATION_BASED("アノテーション", 0.9), // @TestCase(target="add")
        MANUAL("手動設定", 1.0),               // 手動で設定
        UNKNOWN("不明", 0.1);                  // 関連性不明

        private final String description;
        private final double defaultConfidence;

        MappingType(String description, double defaultConfidence) {
            this.description = description;
            this.defaultConfidence = defaultConfidence;
        }

        public String getDescription() {
            return description;
        }

        public double getDefaultConfidence() {
            return defaultConfidence;
        }
    }

    /**
     * デフォルトコンストラクタ
     */
    public TestCaseMapping() {
        this.testAnnotations = new HashMap<>();
        this.mappingType = MappingType.UNKNOWN;
        this.mappingConfidence = 0.0;
    }

    /**
     * 基本情報付きコンストラクタ
     *
     * @param testClassName テストクラス名
     * @param testMethodName テストメソッド名
     * @param sourceClassName ソースクラス名
     * @param sourceMethodName ソースメソッド名
     */
    public TestCaseMapping(String testClassName, String testMethodName,
                          String sourceClassName, String sourceMethodName) {
        this();
        this.testClassName = testClassName;
        this.testMethodName = testMethodName;
        this.sourceClassName = sourceClassName;
        this.sourceMethodName = sourceMethodName;
    }

    /**
     * 完全な情報付きコンストラクタ
     *
     * @param testClassName テストクラス名
     * @param testMethodName テストメソッド名
     * @param sourceClassName ソースクラス名
     * @param sourceMethodName ソースメソッド名
     * @param mappingType マッピングタイプ
     */
    public TestCaseMapping(String testClassName, String testMethodName,
                          String sourceClassName, String sourceMethodName,
                          MappingType mappingType) {
        this(testClassName, testMethodName, sourceClassName, sourceMethodName);
        this.mappingType = mappingType;
        this.mappingConfidence = mappingType.getDefaultConfidence();
    }

    /**
     * テストケースの完全修飾名を取得
     *
     * @return パッケージ.クラス.メソッド形式
     */
    public String getFullyQualifiedTestName() {
        StringBuilder sb = new StringBuilder();
        if (testPackageName != null && !testPackageName.isEmpty()) {
            sb.append(testPackageName).append(".");
        }
        if (testClassName != null && !testClassName.isEmpty()) {
            sb.append(testClassName).append(".");
        }
        if (testMethodName != null && !testMethodName.isEmpty()) {
            sb.append(testMethodName);
        }
        return sb.toString();
    }

    /**
     * ソースメソッドの完全修飾名を取得
     *
     * @return パッケージ.クラス.メソッド形式
     */
    public String getFullyQualifiedSourceName() {
        StringBuilder sb = new StringBuilder();
        if (sourcePackageName != null && !sourcePackageName.isEmpty()) {
            sb.append(sourcePackageName).append(".");
        }
        if (sourceClassName != null && !sourceClassName.isEmpty()) {
            sb.append(sourceClassName).append(".");
        }
        if (sourceMethodName != null && !sourceMethodName.isEmpty()) {
            sb.append(sourceMethodName);
        }
        return sb.toString();
    }

    /**
     * マッピングの一意識別子を取得
     *
     * @return テストメソッド->ソースメソッド形式
     */
    public String getMappingIdentifier() {
        return getFullyQualifiedTestName() + " -> " + getFullyQualifiedSourceName();
    }

    /**
     * テストアノテーションの追加
     *
     * @param annotationType アノテーション型（@を除く）
     * @param annotationValue アノテーション値
     */
    public void addTestAnnotation(String annotationType, String annotationValue) {
        if (testAnnotations == null) {
            testAnnotations = new HashMap<>();
        }
        testAnnotations.put(annotationType, annotationValue);
    }

    /**
     * マッピング信頼度の更新
     *
     * @param confidence 信頼度（0.0-1.0）
     * @param reason 更新理由
     */
    public void updateConfidence(double confidence, String reason) {
        this.mappingConfidence = Math.max(0.0, Math.min(1.0, confidence));
        if (reason != null && !reason.isEmpty()) {
            this.mappingReason = reason;
        }
    }

    /**
     * マッピングが有効かどうかの判定
     *
     * @return 信頼度が0.5以上の場合true
     */
    public boolean isValidMapping() {
        return mappingConfidence >= 0.5;
    }

    /**
     * 高信頼度マッピングかどうかの判定
     *
     * @return 信頼度が0.8以上の場合true
     */
    public boolean isHighConfidence() {
        return mappingConfidence >= 0.8;
    }

    /**
     * JUnitテストかどうかの判定
     *
     * @return @Testアノテーションがある場合true
     */
    public boolean isJUnitTest() {
        return testAnnotations != null &&
               (testAnnotations.containsKey("Test") ||
                testAnnotations.containsKey("org.junit.Test") ||
                testAnnotations.containsKey("org.junit.jupiter.api.Test"));
    }

    /**
     * テストケース表示用文字列を生成
     *
     * @return テストクラス#テストメソッド形式
     */
    public String getTestCaseDisplay() {
        String className = testClassName != null ? testClassName : "Unknown";
        String methodName = testMethodName != null ? testMethodName : "unknown";
        return className + "#" + methodName;
    }

    /**
     * マッピング情報の表示用文字列を生成
     *
     * @return 信頼度とタイプを含む表示文字列
     */
    public String getMappingDisplay() {
        return String.format("%s (%.0f%% %s)",
            getMappingIdentifier(),
            mappingConfidence * 100,
            mappingType.getDescription());
    }

    // Getter methods
    public String getTestClassName() {
        return testClassName;
    }

    public String getTestMethodName() {
        return testMethodName;
    }

    public String getTestPackageName() {
        return testPackageName;
    }

    public Path getTestFilePath() {
        return testFilePath;
    }

    public int getTestLineNumber() {
        return testLineNumber;
    }

    public String getSourceClassName() {
        return sourceClassName;
    }

    public String getSourceMethodName() {
        return sourceMethodName;
    }

    public String getSourcePackageName() {
        return sourcePackageName;
    }

    public MappingType getMappingType() {
        return mappingType;
    }

    public double getMappingConfidence() {
        return mappingConfidence;
    }

    public String getMappingReason() {
        return mappingReason;
    }

    public Map<String, String> getTestAnnotations() {
        return testAnnotations;
    }

    public long getCreatedTime() {
        return createdTime;
    }

    public String getMappingSource() {
        return mappingSource;
    }

    // Setter methods
    public void setTestClassName(String testClassName) {
        this.testClassName = testClassName;
    }

    public void setTestMethodName(String testMethodName) {
        this.testMethodName = testMethodName;
    }

    public void setTestPackageName(String testPackageName) {
        this.testPackageName = testPackageName;
    }

    public void setTestFilePath(Path testFilePath) {
        this.testFilePath = testFilePath;
    }

    public void setTestLineNumber(int testLineNumber) {
        this.testLineNumber = testLineNumber;
    }

    public void setSourceClassName(String sourceClassName) {
        this.sourceClassName = sourceClassName;
    }

    public void setSourceMethodName(String sourceMethodName) {
        this.sourceMethodName = sourceMethodName;
    }

    public void setSourcePackageName(String sourcePackageName) {
        this.sourcePackageName = sourcePackageName;
    }

    public void setMappingType(MappingType mappingType) {
        this.mappingType = mappingType;
        if (mappingType != null && mappingConfidence == 0.0) {
            this.mappingConfidence = mappingType.getDefaultConfidence();
        }
    }

    public void setMappingConfidence(double mappingConfidence) {
        this.mappingConfidence = Math.max(0.0, Math.min(1.0, mappingConfidence));
    }

    public void setMappingReason(String mappingReason) {
        this.mappingReason = mappingReason;
    }

    public void setTestAnnotations(Map<String, String> testAnnotations) {
        this.testAnnotations = testAnnotations;
    }

    public void setCreatedTime(long createdTime) {
        this.createdTime = createdTime;
    }

    public void setMappingSource(String mappingSource) {
        this.mappingSource = mappingSource;
    }

    @Override
    public String toString() {
        return "TestCaseMapping{" +
                "test=" + getTestCaseDisplay() +
                ", source=" + sourceClassName + "#" + sourceMethodName +
                ", type=" + mappingType.getDescription() +
                ", confidence=" + String.format("%.0f%%", mappingConfidence * 100) +
                '}';
    }
}