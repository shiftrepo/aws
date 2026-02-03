package com.testspecgenerator.model;

import org.junit.jupiter.api.Test;

import java.nio.file.Paths;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @ソフトウェア・サービス Module Result Service
 * @項目名 ModuleResult単体テスト
 * @試験内容 ModuleResultデータクラスの機能をテストする
 * @確認項目 正しくデータが格納・取得されること
 * @テスト対象モジュール名 ModuleResult
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 TestTeam
 * @テストケース作成日 2026-02-03
 * @テストケース修正者 TestTeam
 * @テストケース修正日 2026-02-03
 */
class ModuleResultTest {

    /**
     * @ソフトウェア・サービス Module Result Service
     * @項目名 成功したModuleResultの作成テスト
     * @試験内容 正常なModuleResultオブジェクトの作成をテストする
     * @確認項目 全てのプロパティが正しく設定されること
     * @テスト対象モジュール名 ModuleResult
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testSuccessfulModuleResultCreation() {
        // Setup
        ModuleInfo moduleInfo = ModuleInfo.builder()
            .moduleName("test-module")
            .moduleRoot(Paths.get("/test"))
            .build();

        List<TestCaseInfo> testCases = Arrays.asList(
            new TestCaseInfo("path1", "Class1", "method1"),
            new TestCaseInfo("path2", "Class2", "method2")
        );

        Map<String, Object> coverageData = new HashMap<>();
        coverageData.put("coverage1", "data1");
        coverageData.put("coverage2", "data2");

        long processingTime = 1000L;

        // Execute
        ModuleResult result = ModuleResult.builder()
            .moduleInfo(moduleInfo)
            .testCases(testCases)
            .coverageData(coverageData)
            .processingTimeMs(processingTime)
            .build();

        // Verify
        assertEquals(moduleInfo, result.getModuleInfo());
        assertEquals(testCases, result.getTestCases());
        assertEquals(coverageData, result.getCoverageData());
        assertEquals(ModuleResult.ProcessingStatus.SUCCESS, result.getProcessingStatus());
        assertEquals(processingTime, result.getProcessingTimeMs());
        assertTrue(result.isSuccessful());
        assertTrue(result.hasTestCases());
        assertTrue(result.hasCoverageData());
        assertNull(result.getErrorMessage());
    }

    /**
     * @ソフトウェア・サービス Module Result Service
     * @項目名 失敗したModuleResultの作成テスト
     * @試験内容 エラー情報を持つModuleResultオブジェクトの作成をテストする
     * @確認項目 失敗状態とエラーメッセージが正しく設定されること
     * @テスト対象モジュール名 ModuleResult
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testFailedModuleResultCreation() {
        // Setup
        ModuleInfo moduleInfo = ModuleInfo.builder()
            .moduleName("failed-module")
            .moduleRoot(Paths.get("/failed"))
            .build();
        String errorMessage = "Processing failed due to test error";

        // Execute
        ModuleResult result = ModuleResult.builder()
            .moduleInfo(moduleInfo)
            .failed(errorMessage)
            .build();

        // Verify
        assertEquals(moduleInfo, result.getModuleInfo());
        assertEquals(ModuleResult.ProcessingStatus.FAILED, result.getProcessingStatus());
        assertEquals(errorMessage, result.getErrorMessage());
        assertFalse(result.isSuccessful());
        assertFalse(result.hasTestCases());
        assertFalse(result.hasCoverageData());
    }

    /**
     * @ソフトウェア・サービス Module Result Service
     * @項目名 部分的成功のModuleResultの作成テスト
     * @試験内容 警告メッセージを持つModuleResultオブジェクトの作成をテストする
     * @確認項目 部分成功状態が正しく設定されること
     * @テスト対象モジュール名 ModuleResult
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testPartialSuccessModuleResult() {
        // Setup
        ModuleInfo moduleInfo = ModuleInfo.builder()
            .moduleName("partial-module")
            .moduleRoot(Paths.get("/partial"))
            .build();
        List<TestCaseInfo> testCases = Arrays.asList(new TestCaseInfo("path", "Class", "method"));
        String warningMessage = "Some coverage data could not be processed";

        // Execute
        ModuleResult result = ModuleResult.builder()
            .moduleInfo(moduleInfo)
            .testCases(testCases)
            .errorMessage(warningMessage)  // This should change status to PARTIAL_SUCCESS
            .build();

        // Verify
        assertEquals(ModuleResult.ProcessingStatus.PARTIAL_SUCCESS, result.getProcessingStatus());
        assertEquals(warningMessage, result.getErrorMessage());
        assertTrue(result.hasTestCases());
        assertFalse(result.hasCoverageData());  // No coverage data provided
    }

    /**
     * @ソフトウェア・サービス Module Result Service
     * @項目名 空のデータを持つModuleResultのテスト
     * @試験内容 テストケースやカバレッジデータが空の場合の動作をテストする
     * @確認項目 空のデータが正しく処理されること
     * @テスト対象モジュール名 ModuleResult
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testEmptyDataModuleResult() {
        // Setup
        ModuleInfo moduleInfo = ModuleInfo.builder()
            .moduleName("empty-module")
            .moduleRoot(Paths.get("/empty"))
            .build();

        // Execute - with empty lists/maps
        ModuleResult result = ModuleResult.builder()
            .moduleInfo(moduleInfo)
            .testCases(new ArrayList<>())
            .coverageData(new HashMap<>())
            .build();

        // Verify
        assertTrue(result.isSuccessful());
        assertFalse(result.hasTestCases());  // Empty list
        assertFalse(result.hasCoverageData());  // Empty map

        // Execute - with null data
        ModuleResult nullResult = ModuleResult.builder()
            .moduleInfo(moduleInfo)
            .testCases(null)
            .coverageData(null)
            .build();

        // Verify
        assertFalse(nullResult.hasTestCases());
        assertFalse(nullResult.hasCoverageData());
    }

    /**
     * @ソフトウェア・サービス Module Result Service
     * @項目名 equals/hashCodeテスト
     * @試験内容 equalsとhashCodeメソッドの動作をテストする
     * @確認項目 同じModuleInfoを持つオブジェクトが等価であること
     * @テスト対象モジュール名 ModuleResult
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testEqualsAndHashCode() {
        // Setup
        ModuleInfo moduleInfo1 = ModuleInfo.builder()
            .moduleName("test")
            .moduleRoot(Paths.get("/test"))
            .build();

        ModuleInfo moduleInfo2 = ModuleInfo.builder()
            .moduleName("test")
            .moduleRoot(Paths.get("/test"))
            .build();

        ModuleInfo differentModuleInfo = ModuleInfo.builder()
            .moduleName("different")
            .moduleRoot(Paths.get("/different"))
            .build();

        ModuleResult result1 = ModuleResult.builder().moduleInfo(moduleInfo1).build();
        ModuleResult result2 = ModuleResult.builder().moduleInfo(moduleInfo2).build();
        ModuleResult differentResult = ModuleResult.builder().moduleInfo(differentModuleInfo).build();

        // Verify
        assertEquals(result1, result2);
        assertEquals(result1.hashCode(), result2.hashCode());
        assertNotEquals(result1, differentResult);
        assertNotEquals(result1, null);
        assertEquals(result1, result1);
    }

    /**
     * @ソフトウェア・サービス Module Result Service
     * @項目名 toStringテスト
     * @試験内容 toStringメソッドの動作をテストする
     * @確認項目 適切な文字列表現が返されること
     * @テスト対象モジュール名 ModuleResult
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testToString() {
        // Setup
        ModuleInfo moduleInfo = ModuleInfo.builder()
            .moduleName("test-module")
            .moduleRoot(Paths.get("/test"))
            .build();

        ModuleResult result = ModuleResult.builder()
            .moduleInfo(moduleInfo)
            .testCases(Arrays.asList(new TestCaseInfo("path", "Class", "method")))
            .build();

        // Execute
        String toString = result.toString();

        // Verify
        assertTrue(toString.contains("test-module"));
        assertTrue(toString.contains("SUCCESS"));
        assertTrue(toString.contains("testCases=1"));
    }

    /**
     * @ソフトウェア・サービス Module Result Service
     * @項目名 ProcessingStatus列挙型テスト
     * @試験内容 ProcessingStatus列挙型の全ての値をテストする
     * @確認項目 全ての列挙値が正しく定義されていること
     * @テスト対象モジュール名 ModuleResult
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testProcessingStatusEnum() {
        // Verify all enum values exist
        ModuleResult.ProcessingStatus[] statuses = ModuleResult.ProcessingStatus.values();
        assertEquals(4, statuses.length);

        // Verify specific values
        assertTrue(Arrays.asList(statuses).contains(ModuleResult.ProcessingStatus.SUCCESS));
        assertTrue(Arrays.asList(statuses).contains(ModuleResult.ProcessingStatus.PARTIAL_SUCCESS));
        assertTrue(Arrays.asList(statuses).contains(ModuleResult.ProcessingStatus.FAILED));
        assertTrue(Arrays.asList(statuses).contains(ModuleResult.ProcessingStatus.SKIPPED));
    }
}