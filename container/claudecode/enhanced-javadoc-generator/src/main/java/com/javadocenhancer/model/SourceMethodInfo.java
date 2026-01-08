package com.javadocenhancer.model;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * ソースメソッド情報クラス
 *
 * ソースファイルから抽出されたメソッド情報を保持し、
 * JavaDoc生成とテストケースリンク機能で使用されます。
 */
public class SourceMethodInfo {

    // 基本識別情報
    private String className;           // クラス名
    private String methodName;          // メソッド名
    private String packageName;         // パッケージ名
    private Path sourceFilePath;        // ソースファイルパス
    private int lineNumber;             // メソッドの行番号

    // JavaDoc情報
    private String javadocComment;      // JavaDocコメント（生）
    private Map<String, String> javadocTags; // JavaDocタグ（@param, @return等）
    private String shortDescription;    // 短い説明
    private String longDescription;     // 詳細説明

    // メソッド詳細情報
    private String methodSignature;     // メソッドシグネチャ
    private List<String> parameters;    // パラメータリスト
    private String returnType;          // 戻り値型
    private List<String> exceptions;    // 例外型リスト
    private List<String> modifiers;     // 修飾子（public, static等）

    // カバレッジ関連情報
    private CoverageMetrics coverageMetrics; // カバレッジメトリクス
    private boolean hasCoverage = false;     // カバレッジ情報の有無

    // テストケース関連情報
    private List<TestCaseMapping> testCases; // 関連テストケース
    private boolean hasTests = false;        // テストケースの有無

    // メタ情報
    private long extractedTime = System.currentTimeMillis(); // 抽出時刻
    private String extractionSource = "SOURCE_SCAN";         // 抽出元

    /**
     * デフォルトコンストラクタ
     */
    public SourceMethodInfo() {
        this.javadocTags = new HashMap<>();
        this.parameters = new ArrayList<>();
        this.exceptions = new ArrayList<>();
        this.modifiers = new ArrayList<>();
        this.testCases = new ArrayList<>();
    }

    /**
     * 基本情報付きコンストラクタ
     *
     * @param className クラス名
     * @param methodName メソッド名
     */
    public SourceMethodInfo(String className, String methodName) {
        this();
        this.className = className;
        this.methodName = methodName;
    }

    /**
     * 完全な識別情報付きコンストラクタ
     *
     * @param className クラス名
     * @param methodName メソッド名
     * @param packageName パッケージ名
     * @param sourceFilePath ソースファイルパス
     */
    public SourceMethodInfo(String className, String methodName, String packageName, Path sourceFilePath) {
        this(className, methodName);
        this.packageName = packageName;
        this.sourceFilePath = sourceFilePath;
    }

    /**
     * 完全修飾メソッド名を取得
     *
     * @return パッケージ.クラス.メソッド形式
     */
    public String getFullyQualifiedMethodName() {
        StringBuilder sb = new StringBuilder();
        if (packageName != null && !packageName.isEmpty()) {
            sb.append(packageName).append(".");
        }
        if (className != null && !className.isEmpty()) {
            sb.append(className).append(".");
        }
        if (methodName != null && !methodName.isEmpty()) {
            sb.append(methodName);
        }
        return sb.toString();
    }

    /**
     * メソッドの一意識別子を取得
     *
     * @return クラス名.メソッド名(パラメータ)形式
     */
    public String getMethodIdentifier() {
        StringBuilder sb = new StringBuilder();
        if (className != null) {
            sb.append(className);
        }
        sb.append(".");
        if (methodName != null) {
            sb.append(methodName);
        }
        if (parameters != null && !parameters.isEmpty()) {
            sb.append("(").append(String.join(", ", parameters)).append(")");
        } else {
            sb.append("()");
        }
        return sb.toString();
    }

    /**
     * JavaDocタグの追加
     *
     * @param tagName タグ名（@を除く）
     * @param tagValue タグ値
     */
    public void addJavadocTag(String tagName, String tagValue) {
        if (javadocTags == null) {
            javadocTags = new HashMap<>();
        }
        javadocTags.put(tagName, tagValue);
    }

    /**
     * パラメータの追加
     *
     * @param parameter パラメータ（型 名前形式）
     */
    public void addParameter(String parameter) {
        if (parameters == null) {
            parameters = new ArrayList<>();
        }
        parameters.add(parameter);
    }

    /**
     * 例外の追加
     *
     * @param exception 例外型
     */
    public void addException(String exception) {
        if (exceptions == null) {
            exceptions = new ArrayList<>();
        }
        exceptions.add(exception);
    }

    /**
     * 修飾子の追加
     *
     * @param modifier 修飾子
     */
    public void addModifier(String modifier) {
        if (modifiers == null) {
            modifiers = new ArrayList<>();
        }
        modifiers.add(modifier);
    }

    /**
     * テストケースの追加
     *
     * @param testCase テストケースマッピング
     */
    public void addTestCase(TestCaseMapping testCase) {
        if (testCases == null) {
            testCases = new ArrayList<>();
        }
        testCases.add(testCase);
        hasTests = !testCases.isEmpty();
    }

    /**
     * カバレッジメトリクスの設定
     *
     * @param coverageMetrics カバレッジメトリクス
     */
    public void setCoverageMetrics(CoverageMetrics coverageMetrics) {
        this.coverageMetrics = coverageMetrics;
        this.hasCoverage = (coverageMetrics != null);
    }

    /**
     * コンストラクタかどうかの判定
     *
     * @return コンストラクタの場合true
     */
    public boolean isConstructor() {
        return methodName != null &&
               (methodName.equals("<init>") ||
                (className != null && methodName.equals(className)));
    }

    /**
     * staticメソッドかどうかの判定
     *
     * @return staticメソッドの場合true
     */
    public boolean isStatic() {
        return modifiers != null && modifiers.contains("static");
    }

    /**
     * publicメソッドかどうかの判定
     *
     * @return publicメソッドの場合true
     */
    public boolean isPublic() {
        return modifiers == null || modifiers.isEmpty() || modifiers.contains("public");
    }

    /**
     * JavaDocが存在するかどうかの判定
     *
     * @return JavaDocコメントが存在する場合true
     */
    public boolean hasJavadoc() {
        return javadocComment != null && !javadocComment.trim().isEmpty();
    }

    /**
     * メソッドシグネチャの生成
     *
     * @return 修飾子 戻り値型 メソッド名(パラメータ)形式
     */
    public String generateSignature() {
        StringBuilder sb = new StringBuilder();

        // 修飾子
        if (modifiers != null && !modifiers.isEmpty()) {
            sb.append(String.join(" ", modifiers)).append(" ");
        }

        // 戻り値型
        if (returnType != null && !returnType.isEmpty()) {
            sb.append(returnType).append(" ");
        }

        // メソッド名
        if (methodName != null) {
            sb.append(methodName);
        }

        // パラメータ
        sb.append("(");
        if (parameters != null && !parameters.isEmpty()) {
            sb.append(String.join(", ", parameters));
        }
        sb.append(")");

        // 例外
        if (exceptions != null && !exceptions.isEmpty()) {
            sb.append(" throws ").append(String.join(", ", exceptions));
        }

        return sb.toString().trim();
    }

    // Getter methods
    public String getClassName() {
        return className;
    }

    public String getMethodName() {
        return methodName;
    }

    public String getPackageName() {
        return packageName;
    }

    public Path getSourceFilePath() {
        return sourceFilePath;
    }

    public int getLineNumber() {
        return lineNumber;
    }

    public String getJavadocComment() {
        return javadocComment;
    }

    public Map<String, String> getJavadocTags() {
        return javadocTags;
    }

    public String getShortDescription() {
        return shortDescription;
    }

    public String getLongDescription() {
        return longDescription;
    }

    public String getMethodSignature() {
        return methodSignature;
    }

    public List<String> getParameters() {
        return parameters;
    }

    public String getReturnType() {
        return returnType;
    }

    public List<String> getExceptions() {
        return exceptions;
    }

    public List<String> getModifiers() {
        return modifiers;
    }

    public CoverageMetrics getCoverageMetrics() {
        return coverageMetrics;
    }

    public boolean isHasCoverage() {
        return hasCoverage;
    }

    public List<TestCaseMapping> getTestCases() {
        return testCases;
    }

    public boolean isHasTests() {
        return hasTests;
    }

    public long getExtractedTime() {
        return extractedTime;
    }

    public String getExtractionSource() {
        return extractionSource;
    }

    // Setter methods
    public void setClassName(String className) {
        this.className = className;
    }

    public void setMethodName(String methodName) {
        this.methodName = methodName;
    }

    public void setPackageName(String packageName) {
        this.packageName = packageName;
    }

    public void setSourceFilePath(Path sourceFilePath) {
        this.sourceFilePath = sourceFilePath;
    }

    public void setLineNumber(int lineNumber) {
        this.lineNumber = lineNumber;
    }

    public void setJavadocComment(String javadocComment) {
        this.javadocComment = javadocComment;
    }

    public void setJavadocTags(Map<String, String> javadocTags) {
        this.javadocTags = javadocTags;
    }

    public void setShortDescription(String shortDescription) {
        this.shortDescription = shortDescription;
    }

    public void setLongDescription(String longDescription) {
        this.longDescription = longDescription;
    }

    public void setMethodSignature(String methodSignature) {
        this.methodSignature = methodSignature;
    }

    public void setParameters(List<String> parameters) {
        this.parameters = parameters;
    }

    public void setReturnType(String returnType) {
        this.returnType = returnType;
    }

    public void setExceptions(List<String> exceptions) {
        this.exceptions = exceptions;
    }

    public void setModifiers(List<String> modifiers) {
        this.modifiers = modifiers;
    }

    public void setTestCases(List<TestCaseMapping> testCases) {
        this.testCases = testCases;
        this.hasTests = (testCases != null && !testCases.isEmpty());
    }

    public void setExtractedTime(long extractedTime) {
        this.extractedTime = extractedTime;
    }

    public void setExtractionSource(String extractionSource) {
        this.extractionSource = extractionSource;
    }

    @Override
    public String toString() {
        return "SourceMethodInfo{" +
                "className='" + className + '\'' +
                ", methodName='" + methodName + '\'' +
                ", packageName='" + packageName + '\'' +
                ", signature='" + generateSignature() + '\'' +
                ", hasCoverage=" + hasCoverage +
                ", hasTests=" + hasTests +
                ", lineNumber=" + lineNumber +
                '}';
    }
}