package com.testspecgenerator.core;

import com.testspecgenerator.model.TestCaseInfo;
import com.testspecgenerator.model.TestExecutionInfo;
import com.testspecgenerator.model.TestExecutionInfo.TestMethodResult;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Maven Surefireテストレポート（TEST-*.xml）を解析するパーサー
 * テスト実行結果の情報を抽出し、TestCaseInfoに統合します
 */
public class SurefireReportParser {

    private static final Logger logger = LoggerFactory.getLogger(SurefireReportParser.class);

    /**
     * Surefireレポートファイルのリストを解析
     * @param reportFiles レポートファイルのパスリスト
     * @return テスト実行情報のリスト
     */
    public List<TestExecutionInfo> parseSurefireReports(List<Path> reportFiles) {
        List<TestExecutionInfo> executionInfos = new ArrayList<>();

        for (Path reportFile : reportFiles) {
            try {
                TestExecutionInfo info = parseSingleReport(reportFile);
                if (info != null) {
                    executionInfos.add(info);
                    logger.debug("Surefireレポート解析成功: {}", reportFile.getFileName());
                }
            } catch (Exception e) {
                logger.warn("Surefireレポート解析エラー: {} - {}", reportFile, e.getMessage());
            }
        }

        logger.info("Surefire report analysis completed: {} test suites", executionInfos.size());
        return executionInfos;
    }

    /**
     * 単一のSurefireレポートファイルを解析
     * @param reportFile レポートファイルのパス
     * @return テスト実行情報、解析失敗時はnull
     */
    private TestExecutionInfo parseSingleReport(Path reportFile) throws IOException {
        File file = reportFile.toFile();
        if (!file.exists() || !file.canRead()) {
            logger.warn("Cannot read report file: {}", reportFile);
            return null;
        }

        // JSoupでXMLを解析
        Document doc = Jsoup.parse(file, StandardCharsets.UTF_8.name());

        // testsuite要素を取得
        Element testSuite = doc.selectFirst("testsuite");
        if (testSuite == null) {
            logger.warn("testsuite element not found: {}", reportFile);
            return null;
        }

        // テストスイートの属性を取得
        String className = testSuite.attr("name");
        int totalTests = parseIntAttribute(testSuite, "tests", 0);
        int errors = parseIntAttribute(testSuite, "errors", 0);
        int failures = parseIntAttribute(testSuite, "failures", 0);
        int skipped = parseIntAttribute(testSuite, "skipped", 0);
        double time = parseDoubleAttribute(testSuite, "time", 0.0);

        // 成功したテスト数を計算
        int passed = totalTests - errors - failures - skipped;

        // TestExecutionInfoを作成
        TestExecutionInfo info = new TestExecutionInfo(className, className);
        info.setTotalTests(totalTests);
        info.setPassedTests(passed);
        info.setFailedTests(failures);
        info.setErrorTests(errors);
        info.setSkippedTests(skipped);
        info.setExecutionTime(time);

        // 個々のテストケースの結果を解析
        Elements testCases = doc.select("testcase");
        for (Element testCase : testCases) {
            String methodName = testCase.attr("name");
            String testClassName = testCase.attr("classname");
            double testTime = parseDoubleAttribute(testCase, "time", 0.0);

            // テストの状態を判定
            String status;
            String errorMessage = null;
            String errorType = null;

            Element failure = testCase.selectFirst("failure");
            Element error = testCase.selectFirst("error");
            Element skippedElement = testCase.selectFirst("skipped");

            if (failure != null) {
                status = "failed";
                errorMessage = failure.attr("message");
                errorType = failure.attr("type");
            } else if (error != null) {
                status = "error";
                errorMessage = error.attr("message");
                errorType = error.attr("type");
            } else if (skippedElement != null) {
                status = "skipped";
                errorMessage = skippedElement.attr("message");
            } else {
                status = "passed";
            }

            // TestMethodResultを作成して追加
            TestMethodResult methodResult = new TestMethodResult(methodName, status, testTime);
            if (errorMessage != null) {
                methodResult.setErrorMessage(errorMessage);
            }
            if (errorType != null) {
                methodResult.setErrorType(errorType);
            }

            info.addMethodResult(methodName, methodResult);
        }

        logger.debug("テスト実行情報解析: {} - テスト数: {}, 成功: {}, 失敗: {}, エラー: {}, スキップ: {}",
            className, totalTests, passed, failures, errors, skipped);

        return info;
    }

    /**
     * テスト実行結果をTestCaseInfoリストに統合
     * @param testCases テストケース情報のリスト
     * @param executionResults テスト実行結果のリスト
     */
    public void mergeExecutionResults(List<TestCaseInfo> testCases, List<TestExecutionInfo> executionResults) {
        if (testCases == null || executionResults == null) {
            return;
        }

        // クラス名でテスト実行結果をマップ化（フルクラス名と短縮名の両方でマップ）
        Map<String, TestExecutionInfo> executionMap = new HashMap<>();
        for (TestExecutionInfo info : executionResults) {
            executionMap.put(info.getClassName(), info);
            // 短縮名でもマップに追加（com.example.TestClass -> TestClass）
            String shortName = info.getClassName();
            if (shortName.contains(".")) {
                shortName = shortName.substring(shortName.lastIndexOf(".") + 1);
                executionMap.put(shortName, info);
            }
        }

        // TestCaseInfoをクラス名でグループ化
        Map<String, List<TestCaseInfo>> testCasesByClass = new HashMap<>();
        for (TestCaseInfo testCase : testCases) {
            String className = testCase.getClassName();
            testCasesByClass.computeIfAbsent(className, k -> new ArrayList<>()).add(testCase);
        }

        // 各テストクラスの実行結果を設定
        for (Map.Entry<String, List<TestCaseInfo>> entry : testCasesByClass.entrySet()) {
            String className = entry.getKey();
            List<TestCaseInfo> classTestCases = entry.getValue();

            // 対応するテスト実行結果を検索
            TestExecutionInfo executionInfo = executionMap.get(className);

            if (executionInfo != null) {
                // 各テストケースに実行結果を設定
                for (TestCaseInfo testCase : classTestCases) {
                    testCase.setTestsTotal(executionInfo.getTotalTests());
                    testCase.setTestsPassed(executionInfo.getPassedTests());
                    testCase.setTestExecutionStatus(executionInfo.getExecutionStatus());
                    testCase.setTestSuccessRate(executionInfo.getSuccessRate());

                    logger.debug("テスト実行結果を統合: {} - {}",
                        testCase.getClassName(), executionInfo.getTestExecutionDisplay());
                }
            } else {
                // Surefireレポートが見つからない場合
                logger.debug("Surefireレポートが見つかりません: {}", className);
                for (TestCaseInfo testCase : classTestCases) {
                    testCase.setTestsTotal(0);
                    testCase.setTestsPassed(0);
                    testCase.setTestExecutionStatus("Unknown");
                    testCase.setTestSuccessRate(0.0);
                }
            }
        }

        logger.info("Test execution result integration completed: {} test classes", testCasesByClass.size());
    }

    /**
     * 整数属性を安全に解析
     */
    private int parseIntAttribute(Element element, String attrName, int defaultValue) {
        try {
            String value = element.attr(attrName);
            if (value != null && !value.isEmpty()) {
                return Integer.parseInt(value);
            }
        } catch (NumberFormatException e) {
            logger.debug("整数属性の解析エラー: {} = {}", attrName, element.attr(attrName));
        }
        return defaultValue;
    }

    /**
     * 浮動小数点数属性を安全に解析
     */
    private double parseDoubleAttribute(Element element, String attrName, double defaultValue) {
        try {
            String value = element.attr(attrName);
            if (value != null && !value.isEmpty()) {
                return Double.parseDouble(value);
            }
        } catch (NumberFormatException e) {
            logger.debug("浮動小数点数属性の解析エラー: {} = {}", attrName, element.attr(attrName));
        }
        return defaultValue;
    }
}