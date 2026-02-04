package com.testspecgenerator.core;

import com.testspecgenerator.model.TestCaseInfo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Javaファイルからカスタムアノテーションとテストメソッドを抽出するクラス
 */
public class JavaAnnotationParser {

    private static final Logger logger = LoggerFactory.getLogger(JavaAnnotationParser.class);

    // アノテーションパターン
    private static final Pattern ANNOTATION_PATTERN = Pattern.compile(
            "@(\\w+)\\s+(.+?)(?=\\s*@\\w+|\\s*\\*/|$)",
            Pattern.MULTILINE | Pattern.DOTALL
    );

    // テストメソッドパターン (JUnit 5では修飾子はオプション)
    // 完全一致でTestとParameterizedTestのみを対象とする
    private static final Pattern TEST_METHOD_PATTERN = Pattern.compile(
            "@(?:Test(?!\\w)|ParameterizedTest).*?(?:public\\s+)?void\\s+(\\w+)\\s*\\(",
            Pattern.DOTALL | Pattern.MULTILINE
    );

    // JavaDocコメントパターン
    private static final Pattern JAVADOC_PATTERN = Pattern.compile(
            "/\\*\\*(.*?)\\*/",
            Pattern.DOTALL
    );

    // クラス名抽出パターン
    private static final Pattern CLASS_NAME_PATTERN = Pattern.compile(
            "(?:public\\s+)?(?:abstract\\s+)?class\\s+(\\w+)",
            Pattern.MULTILINE
    );

    // パッケージ名抽出パターン
    private static final Pattern PACKAGE_PATTERN = Pattern.compile(
            "^\\s*package\\s+([\\w.]+);",
            Pattern.MULTILINE
    );

    // サポートするアノテーション名
    private static final Set<String> SUPPORTED_ANNOTATIONS = Set.of(
            // 日本語アノテーション（優先）
            "ソフトウェア・サービス", "項目名", "試験内容", "確認項目",
            "テスト対象モジュール名", "テスト実施ベースラインバージョン",
            "テストケース作成者", "テストケース作成日", "テストケース修正者", "テストケース修正日",
            // 旧英語アノテーション（互換性のため残す）
            "TestModule", "TestCase", "BaselineVersion", "TestOverview",
            "TestPurpose", "TestProcess", "TestResults", "Creator",
            "CreatedDate", "Modifier", "ModifiedDate", "TestCategory",
            "Priority", "Requirements", "Dependencies",
            // 実際のテストファイルで使用されているアノテーション
            "TestType", "TestObjective", "PreCondition", "ExpectedResult", "TestData"
    );

    // ファイルエンコーディング候補
    private static final List<Charset> ENCODING_CANDIDATES = List.of(
            StandardCharsets.UTF_8,
            Charset.forName("Shift_JIS"),
            Charset.forName("MS932"),
            StandardCharsets.ISO_8859_1
    );

    /**
     * Javaファイルのリストを処理してテストケース情報を抽出
     */
    public List<TestCaseInfo> processJavaFiles(List<Path> javaFiles) {
        logger.info("Java file processing started: {} files", javaFiles.size());
        logger.info("[Detail Log] Test name extraction started - Target files: {}",
                   javaFiles.stream().map(Path::getFileName).map(Path::toString).toList());

        List<TestCaseInfo> testCases = new ArrayList<>();
        int totalTestMethods = 0;
        int totalAnnotations = 0;

        for (int i = 0; i < javaFiles.size(); i++) {
            Path javaFile = javaFiles.get(i);
            logger.debug("Processing: {} ({}/{})", javaFile.getFileName(), i + 1, javaFiles.size());

            try {
                List<TestCaseInfo> fileCases = processJavaFile(javaFile);
                testCases.addAll(fileCases);

                // Detail log: File-by-file processing results
                int fileTestMethods = fileCases.size();
                int fileAnnotations = fileCases.size() * 10; // Estimated annotations (approx. 10 fields per test case)
                totalTestMethods += fileTestMethods;
                totalAnnotations += fileAnnotations;

                logger.info("[Detail Log] File processing result: {} - Test methods: {}, Annotations: {}",
                           javaFile.getFileName(), fileTestMethods, fileAnnotations);

                // Detail log for each test method
                for (TestCaseInfo testCase : fileCases) {
                    logger.debug("[Detail Log] Test case extracted: {} - FQCN: {}, Fields set",
                               testCase.getMethodName(), testCase.getFullyQualifiedName());
                }

            } catch (Exception e) {
                logger.warn("Error processing file: {} - {}", javaFile, e.getMessage());
            }
        }

        logger.info("Java file processing completed: {} test cases extracted", testCases.size());
        logger.info("[Detail Log] Extraction summary - Total test methods: {}, Total annotations: {}",
                   totalTestMethods, totalAnnotations);

        return testCases;
    }

    /**
     * 単一のJavaファイルを処理してテストケース情報を抽出
     */
    public List<TestCaseInfo> processJavaFile(Path javaFile) throws IOException {
        // ファイル内容を読み込み
        String content = readFileWithEncoding(javaFile);
        if (content == null || content.trim().isEmpty()) {
            logger.warn("File content is empty or cannot be read: {}", javaFile);
            return new ArrayList<>();
        }

        // クラス名を抽出
        String className = extractClassName(content);
        if (className == null) {
            logger.warn("クラス名を抽出できません: {}", javaFile);
            return new ArrayList<>();
        }

        // パッケージ名を抽出
        String packageName = extractPackageName(content);

        // テストメソッドを検索
        List<String> testMethods = extractTestMethods(content);
        logger.debug("Test methods found: {} in {}", testMethods.size(), className);

        if (testMethods.isEmpty()) {
            logger.debug("No test methods found: {}", javaFile);
            return new ArrayList<>();
        }

        // 各テストメソッドについてアノテーション情報を抽出
        List<TestCaseInfo> testCases = new ArrayList<>();

        for (String methodName : testMethods) {
            TestCaseInfo testCase = new TestCaseInfo(javaFile.toString(), className, methodName, packageName);

            // メソッドレベルのアノテーション抽出
            Map<String, String> methodAnnotations = extractMethodAnnotations(content, methodName);

            // クラスレベルのアノテーション抽出（フォールバック）
            Map<String, String> classAnnotations = extractClassAnnotations(content);

            // アノテーション情報をマージ（メソッドレベルが優先）
            Map<String, String> mergedAnnotations = new HashMap<>(classAnnotations);
            mergedAnnotations.putAll(methodAnnotations);

            // TestCaseInfoにアノテーション情報を設定
            applyAnnotationsToTestCase(testCase, mergedAnnotations);

            testCases.add(testCase);

            logger.debug("Test case extracted: {}.{} - Module: {}, Case: {}",
                    className, methodName,
                    testCase.getTestModule(), testCase.getTestCase());
        }

        return testCases;
    }

    /**
     * エンコーディングを自動検出してファイルを読み込み
     */
    private String readFileWithEncoding(Path filePath) throws IOException {
        for (Charset charset : ENCODING_CANDIDATES) {
            try {
                String content = Files.readString(filePath, charset);
                logger.debug("File read successfully: {} ({})", filePath, charset.name());
                return content;
            } catch (IOException e) {
                logger.debug("エンコーディング {} で読み込み失敗: {}", charset.name(), filePath);
            }
        }

        logger.error("すべてのエンコーディングで読み込み失敗: {}", filePath);
        throw new IOException("Cannot read file: " + filePath);
    }

    /**
     * Javaファイルからクラス名を抽出
     */
    private String extractClassName(String content) {
        Matcher matcher = CLASS_NAME_PATTERN.matcher(content);
        if (matcher.find()) {
            return matcher.group(1);
        }
        return null;
    }

    /**
     * Javaファイルからパッケージ名を抽出
     */
    private String extractPackageName(String content) {
        Matcher matcher = PACKAGE_PATTERN.matcher(content);
        if (matcher.find()) {
            String packageName = matcher.group(1);
            logger.debug("パッケージ名抽出成功: {}", packageName);
            return packageName;
        }
        logger.debug("パッケージ宣言が見つかりません、デフォルト値を使用: 未指定");
        return "未指定";
    }

    /**
     * Javaファイルからテストメソッド名を抽出
     */
    private List<String> extractTestMethods(String content) {
        List<String> methods = new ArrayList<>();
        Matcher matcher = TEST_METHOD_PATTERN.matcher(content);

        while (matcher.find()) {
            String methodName = matcher.group(1);
            methods.add(methodName);
            logger.debug("Test method found: {} at position {}", methodName, matcher.start());
        }

        return methods;
    }

    /**
     * 指定メソッドのアノテーション情報を抽出
     */
    private Map<String, String> extractMethodAnnotations(String content, String methodName) {
        // メソッド定義の位置を検索 (JUnit 5では修飾子はオプション、@DisplayNameなど他のアノテーションも考慮)
        Pattern methodPattern = Pattern.compile(
                "/\\*\\*(.*?)\\*/\\s*(?:@\\w+(?:\\([^)]*\\))?\\s*)*@(?:Test|ParameterizedTest)(?:\\([^)]*\\))?\\s*" +
                "(?:@\\w+(?:\\([^)]*\\))?\\s*)*(?:public\\s+)?void\\s+" +
                        Pattern.quote(methodName) + "\\s*\\(",
                Pattern.DOTALL | Pattern.MULTILINE
        );

        Matcher matcher = methodPattern.matcher(content);
        if (matcher.find()) {
            String javadocContent = matcher.group(1);
            logger.debug("Method {} JavaDoc extraction successful: {}", methodName, javadocContent.trim());
            return parseAnnotations(javadocContent);
        } else {
            logger.debug("Method {} JavaDoc extraction failed", methodName);
        }

        return new HashMap<>();
    }

    /**
     * クラスレベルのアノテーション情報を抽出
     */
    private Map<String, String> extractClassAnnotations(String content) {
        // クラス定義より前のJavaDocコメントを検索
        Pattern classJavadocPattern = Pattern.compile(
                "/\\*\\*(.*?)\\*/\\s*(?:public\\s+)?(?:abstract\\s+)?class",
                Pattern.DOTALL | Pattern.MULTILINE
        );

        Matcher matcher = classJavadocPattern.matcher(content);
        if (matcher.find()) {
            String javadocContent = matcher.group(1);
            return parseAnnotations(javadocContent);
        }

        return new HashMap<>();
    }

    /**
     * JavaDocコメント内容からアノテーション情報を解析
     */
    private Map<String, String> parseAnnotations(String javadocContent) {
        Map<String, String> annotations = new HashMap<>();

        if (javadocContent == null || javadocContent.trim().isEmpty()) {
            return annotations;
        }

        // 行単位で処理
        String[] lines = javadocContent.split("\\n");
        for (String line : lines) {
            line = line.trim();

            // コメント記号を除去
            if (line.startsWith("*")) {
                line = line.substring(1).trim();
            }

            // @アノテーション形式をチェック
            if (line.startsWith("@")) {
                parseAnnotationLine(line, annotations);
            }
        }

        return annotations;
    }

    /**
     * 単一のアノテーション行を解析
     */
    private void parseAnnotationLine(String line, Map<String, String> annotations) {
        // @AnnotationName value の形式を解析
        int spaceIndex = line.indexOf(' ', 1);
        if (spaceIndex == -1) {
            spaceIndex = line.indexOf('\t', 1);
        }

        if (spaceIndex > 1) {
            String annotationName = line.substring(1, spaceIndex).trim();
            String value = line.substring(spaceIndex + 1).trim();

            if (SUPPORTED_ANNOTATIONS.contains(annotationName)) {
                annotations.put(annotationName, value);
                logger.debug("Annotation parsed: {} = {}", annotationName, value);
            }
        }
    }

    /**
     * アノテーション情報をTestCaseInfoオブジェクトに適用
     */
    private void applyAnnotationsToTestCase(TestCaseInfo testCase, Map<String, String> annotations) {
        annotations.forEach((key, value) -> {
            if (value != null && !value.trim().isEmpty()) {
                switch (key) {
                    // 日本語アノテーション（優先）
                    case "ソフトウェア・サービス":
                        testCase.setSoftwareService(value.trim());
                        break;
                    case "項目名":
                        testCase.setTestItemName(value.trim());
                        break;
                    case "試験内容":
                        testCase.setTestContent(value.trim());
                        break;
                    case "確認項目":
                        testCase.setConfirmationItem(value.trim());
                        break;
                    case "テスト対象モジュール名":
                        testCase.setTestModule(value.trim());
                        break;
                    case "テスト実施ベースラインバージョン":
                        testCase.setBaselineVersion(value.trim());
                        break;
                    case "テストケース作成者":
                        testCase.setCreator(value.trim());
                        break;
                    case "テストケース作成日":
                        testCase.setCreatedDate(value.trim());
                        break;
                    case "テストケース修正者":
                        testCase.setModifier(value.trim());
                        break;
                    case "テストケース修正日":
                        testCase.setModifiedDate(value.trim());
                        break;
                    // 旧英語アノテーション（互換性のため残す）
                    case "TestModule":
                        testCase.setTestModule(value.trim());
                        break;
                    case "TestCase":
                        testCase.setTestCase(value.trim());
                        testCase.setTestItemName(value.trim());  // 項目名にもマッピング
                        break;
                    case "BaselineVersion":
                        testCase.setBaselineVersion(value.trim());
                        break;
                    case "TestOverview":
                        testCase.setTestOverview(value.trim());
                        break;
                    case "TestPurpose":
                        testCase.setTestPurpose(value.trim());
                        break;
                    case "TestProcess":
                        testCase.setTestProcess(value.trim());
                        testCase.setTestContent(value.trim());  // 試験内容にもマッピング
                        break;
                    case "TestResults":
                        testCase.setTestResults(value.trim());
                        testCase.setConfirmationItem(value.trim());  // 確認項目にもマッピング
                        break;
                    case "Creator":
                        testCase.setCreator(value.trim());
                        break;
                    case "CreatedDate":
                        testCase.setCreatedDate(value.trim());
                        break;
                    case "Modifier":
                        testCase.setModifier(value.trim());
                        break;
                    case "ModifiedDate":
                        testCase.setModifiedDate(value.trim());
                        break;
                    case "TestCategory":
                        testCase.setTestCategory(value.trim());
                        break;
                    case "Priority":
                        testCase.setPriority(value.trim());
                        break;
                    case "Requirements":
                        testCase.setRequirements(value.trim());
                        break;
                    case "Dependencies":
                        testCase.setDependencies(value.trim());
                        break;
                    // 実際のテストファイルで使用されているアノテーションのマッピング
                    case "TestType":
                        testCase.setTestCategory(value.trim());
                        break;
                    case "TestObjective":
                        testCase.setTestPurpose(value.trim());
                        break;
                    case "PreCondition":
                        testCase.setTestProcess(value.trim());
                        testCase.setTestOverview(value.trim());
                        testCase.setTestContent(value.trim());  // 試験内容にもマッピング
                        break;
                    case "ExpectedResult":
                        testCase.setTestResults(value.trim());
                        testCase.setConfirmationItem(value.trim());  // 確認項目にもマッピング
                        break;
                    case "TestData":
                        testCase.setCreator(value.trim());
                        break;
                }
            }
        });
    }

    /**
     * 抽出されたテストケースの統計情報を取得
     */
    public Map<String, Object> getStatistics(List<TestCaseInfo> testCases) {
        Map<String, Object> stats = new HashMap<>();

        stats.put("totalTestCases", testCases.size());
        stats.put("classCount", testCases.stream()
                .map(TestCaseInfo::getClassName)
                .distinct()
                .count());

        // アノテーション完成度統計
        long annotatedCases = testCases.stream()
                .mapToLong(tc -> !"Not Specified".equals(tc.getTestModule()) ? 1 : 0)
                .sum();
        stats.put("annotatedCases", annotatedCases);
        stats.put("annotationCompleteness", testCases.isEmpty() ? 0.0 :
                (double) annotatedCases / testCases.size() * 100.0);

        return stats;
    }

    /**
     * 処理サマリーをログ出力
     */
    public void logProcessingSummary(List<TestCaseInfo> testCases) {
        Map<String, Object> stats = getStatistics(testCases);

        logger.info("=== Annotation Analysis Summary ===");
        logger.info("Total test cases: {}", stats.get("totalTestCases"));
        logger.info("Target classes: {}", stats.get("classCount"));
        logger.info("Annotated cases: {}", stats.get("annotatedCases"));
        logger.info("Annotation completeness: {}%", stats.get("annotationCompleteness"));
    }
}