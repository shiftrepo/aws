package com.testspecgenerator.core;

import com.testspecgenerator.model.CoverageInfo;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Coverage Data Flow Test - SIMPLIFIED API
 *
 * Tests the simplified coverage data flow:
 * XML → List<CoverageInfo> → Excel/CSV (NO Map conversion)
 *
 * @ソフトウェア・サービス Coverage Data Flow Service
 * @項目名 カバレッジデータフロー統合テスト
 * @試験内容 XML解析からExcel出力までのカバレッジデータフローをテストする（Map変換なし）
 * @確認項目 数値が正確に保持されてExcel出力まで伝わること
 * @テスト対象モジュール名 CoverageReportParser
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 TestTeam
 * @テストケース作成日 2026-02-04
 * @テストケース修正者 TestTeam
 * @テストケース修正日 2026-02-04
 */
class CoverageDataFlowTest {

    private CoverageReportParser parser;

    @TempDir
    Path tempDir;

    @BeforeEach
    void setUp() {
        parser = new CoverageReportParser();
    }

    /**
     * Test 1: XML解析 → List<CoverageInfo> 直接変換
     *
     * @ソフトウェア・サービス Coverage Data Flow Service
     * @項目名 processCoverageReports()メソッド基本動作テスト
     * @試験内容 processCoverageReports()がList<CoverageInfo>を直接返すことを確認
     * @確認項目 Map変換を経由せずList<CoverageInfo>が返されること
     * @テスト対象モジュール名 CoverageReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-04
     */
    @Test
    void testProcessCoverageReportsReturnsListDirectly() throws IOException {
        // Arrange: Create real JaCoCo XML file
        Path jacocoXml = createRealJaCoCoXml();
        List<Path> coverageFiles = List.of(jacocoXml);

        // Act: Call processCoverageReports() - should return List<CoverageInfo> directly
        List<CoverageInfo> result = parser.processCoverageReports(coverageFiles);

        // Assert: Verify List<CoverageInfo> is returned
        assertNotNull(result, "Result should not be null");
        assertTrue(result instanceof List, "Result should be List");

        System.out.println("[Test] processCoverageReports() returned List with " + result.size() + " entries");
    }

    /**
     * Test 2: カバレッジ数値の正確性テスト
     *
     * @ソフトウェア・サービス Coverage Data Flow Service
     * @項目名 カバレッジ数値保持テスト
     * @試験内容 XML解析で取得した数値が正確にCoverageInfoに設定されることを確認
     * @確認項目 ブランチ、ライン、命令カバレッジの数値が正確であること
     * @テスト対象モジュール名 CoverageReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-04
     */
    @Test
    void testCoverageValuesAreAccurate() throws IOException {
        // Arrange: Create JaCoCo XML with known values
        Path jacocoXml = createJaCoCoXmlWithKnownValues();
        List<Path> coverageFiles = List.of(jacocoXml);

        // Act
        List<CoverageInfo> result = parser.processCoverageReports(coverageFiles);

        // Assert: Find HelloService.hello entry (should have 100% branch coverage)
        CoverageInfo helloMethod = result.stream()
            .filter(c -> "HelloService".equals(c.getClassName()) && "hello".equals(c.getMethodName()))
            .findFirst()
            .orElse(null);

        assertNotNull(helloMethod, "HelloService.hello should be found");

        // Verify branch coverage
        assertEquals(2, helloMethod.getBranchesCovered(), "Branches covered should be 2");
        assertEquals(2, helloMethod.getBranchesTotal(), "Branches total should be 2");
        assertEquals(100.0, helloMethod.getBranchCoverage(), 0.01, "Branch coverage should be 100%");

        // Verify line coverage
        assertEquals(3, helloMethod.getLinesCovered(), "Lines covered should be 3");
        assertEquals(3, helloMethod.getLinesTotal(), "Lines total should be 3");
        assertEquals(100.0, helloMethod.getLineCoverage(), 0.01, "Line coverage should be 100%");

        System.out.println("[Test] Coverage values verified: Branch=" + helloMethod.getBranchCoverage() +
                         "%, Line=" + helloMethod.getLineCoverage() + "%");
    }

    /**
     * Test 3: 0%カバレッジのハンドリング
     *
     * @ソフトウェア・サービス Coverage Data Flow Service
     * @項目名 0%カバレッジ処理テスト
     * @試験内容 カバレッジが0%のメソッドを正しく処理できることを確認
     * @確認項目 0%カバレッジが正確に保持されること
     * @テスト対象モジュール名 CoverageReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-04
     */
    @Test
    void testZeroCoverageHandling() throws IOException {
        // Arrange: Create JaCoCo XML with 0% coverage methods
        Path jacocoXml = createJaCoCoXmlWithZeroCoverage();
        List<Path> coverageFiles = List.of(jacocoXml);

        // Act
        List<CoverageInfo> result = parser.processCoverageReports(coverageFiles);

        // Assert: Find method with 0% coverage
        CoverageInfo zeroMethod = result.stream()
            .filter(c -> "TestClass".equals(c.getClassName()) && "uncoveredMethod".equals(c.getMethodName()))
            .findFirst()
            .orElse(null);

        assertNotNull(zeroMethod, "Uncovered method should be found");
        assertEquals(0, zeroMethod.getBranchesCovered(), "Branches covered should be 0");
        assertEquals(4, zeroMethod.getBranchesTotal(), "Branches total should be 4");
        assertEquals(0.0, zeroMethod.getBranchCoverage(), 0.01, "Branch coverage should be 0%");

        System.out.println("[Test] Zero coverage correctly handled: 0/" +
                         zeroMethod.getBranchesTotal() + " branches covered");
    }

    /**
     * Test 4: 複数クラス・メソッドの一括処理
     *
     * @ソフトウェア・サービス Coverage Data Flow Service
     * @項目名 複数エントリ処理テスト
     * @試験内容 複数のクラス・メソッドを含むXMLを正しく解析できることを確認
     * @確認項目 全てのエントリが正しく抽出されること
     * @テスト対象モジュール名 CoverageReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-04
     */
    @Test
    void testMultipleClassesAndMethods() throws IOException {
        // Arrange: Create JaCoCo XML with multiple classes/methods
        Path jacocoXml = createJaCoCoXmlWithMultipleEntries();
        List<Path> coverageFiles = List.of(jacocoXml);

        // Act
        List<CoverageInfo> result = parser.processCoverageReports(coverageFiles);

        // Assert: Verify all entries are extracted
        assertTrue(result.size() >= 5, "Should have at least 5 coverage entries");

        // Verify different classes exist
        long classCount = result.stream()
            .map(CoverageInfo::getClassName)
            .distinct()
            .count();
        assertTrue(classCount >= 3, "Should have at least 3 different classes");

        // Verify all entries have valid coverage values
        for (CoverageInfo info : result) {
            assertTrue(info.getBranchesTotal() >= 0, "Branches total should be non-negative");
            assertTrue(info.getLinesTotal() >= 0, "Lines total should be non-negative");
            assertTrue(info.getInstructionsTotal() >= 0, "Instructions total should be non-negative");
            assertTrue(info.getBranchCoverage() >= 0.0 && info.getBranchCoverage() <= 100.0,
                      "Branch coverage should be between 0-100%");
        }

        System.out.println("[Test] Multiple entries processed: " + result.size() +
                         " methods from " + classCount + " classes");
    }

    /**
     * Test 5: CoverageInfo → Excel データフロー
     *
     * @ソフトウェア・サービス Coverage Data Flow Service
     * @項目名 Excel出力データフローテスト
     * @試験内容 CoverageInfoからExcel出力への数値伝達を確認
     * @確認項目 CoverageInfoの数値がExcelSheetBuilderに正しく渡されること
     * @テスト対象モジュール名 CoverageReportParser, ExcelSheetBuilder
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-04
     */
    @Test
    void testCoverageInfoToExcelFlow() throws IOException {
        // Arrange: Create coverage data
        Path jacocoXml = createRealJaCoCoXml();
        List<Path> coverageFiles = List.of(jacocoXml);
        List<CoverageInfo> coverageData = parser.processCoverageReports(coverageFiles);

        // Act: Pass to ExcelSheetBuilder (test that it accepts List<CoverageInfo>)
        ExcelSheetBuilder excelBuilder = new ExcelSheetBuilder();
        Path outputPath = tempDir.resolve("test_output.xlsx");

        boolean success = excelBuilder.generateTestSpecificationReport(
            outputPath.toString(),
            List.of(), // Empty test cases for this test
            coverageData // Direct List<CoverageInfo> - NO Map conversion!
        );

        // Assert: Excel generation should succeed
        assertTrue(success, "Excel generation should succeed");
        assertTrue(Files.exists(outputPath), "Excel file should be created");
        assertTrue(Files.size(outputPath) > 0, "Excel file should not be empty");

        System.out.println("[Test] Excel file generated: " + outputPath +
                         " (size: " + Files.size(outputPath) + " bytes)");
    }

    // ========== Helper Methods to Create Test Data ==========

    private Path createRealJaCoCoXml() throws IOException {
        String xml = """
            <?xml version="1.0" encoding="UTF-8"?>
            <report name="JaCoCo Coverage">
              <package name="com/example/service">
                <class name="com/example/service/HelloService">
                  <method name="hello" desc="()Ljava/lang/String;">
                    <counter type="BRANCH" missed="0" covered="2"/>
                    <counter type="LINE" missed="0" covered="3"/>
                    <counter type="INSTRUCTION" missed="0" covered="15"/>
                  </method>
                </class>
              </package>
            </report>
            """;

        Path xmlFile = tempDir.resolve("jacoco.xml");
        Files.writeString(xmlFile, xml);
        return xmlFile;
    }

    private Path createJaCoCoXmlWithKnownValues() throws IOException {
        String xml = """
            <?xml version="1.0" encoding="UTF-8"?>
            <report name="JaCoCo Coverage">
              <package name="com/example/service">
                <class name="com/example/service/HelloService">
                  <method name="hello" desc="()Ljava/lang/String;">
                    <counter type="BRANCH" missed="0" covered="2"/>
                    <counter type="LINE" missed="0" covered="3"/>
                    <counter type="INSTRUCTION" missed="0" covered="15"/>
                    <counter type="METHOD" missed="0" covered="1"/>
                  </method>
                  <method name="selectTest" desc="(I)Ljava/lang/String;">
                    <counter type="BRANCH" missed="0" covered="4"/>
                    <counter type="LINE" missed="0" covered="6"/>
                    <counter type="INSTRUCTION" missed="0" covered="28"/>
                    <counter type="METHOD" missed="0" covered="1"/>
                  </method>
                </class>
              </package>
            </report>
            """;

        Path xmlFile = tempDir.resolve("jacoco_known.xml");
        Files.writeString(xmlFile, xml);
        return xmlFile;
    }

    private Path createJaCoCoXmlWithZeroCoverage() throws IOException {
        String xml = """
            <?xml version="1.0" encoding="UTF-8"?>
            <report name="JaCoCo Coverage">
              <package name="com/test">
                <class name="com/test/TestClass">
                  <method name="uncoveredMethod" desc="()V">
                    <counter type="BRANCH" missed="4" covered="0"/>
                    <counter type="LINE" missed="10" covered="0"/>
                    <counter type="INSTRUCTION" missed="50" covered="0"/>
                    <counter type="METHOD" missed="1" covered="0"/>
                  </method>
                </class>
              </package>
            </report>
            """;

        Path xmlFile = tempDir.resolve("jacoco_zero.xml");
        Files.writeString(xmlFile, xml);
        return xmlFile;
    }

    private Path createJaCoCoXmlWithMultipleEntries() throws IOException {
        String xml = """
            <?xml version="1.0" encoding="UTF-8"?>
            <report name="JaCoCo Coverage">
              <package name="com/example/service">
                <class name="com/example/service/HelloService">
                  <method name="hello" desc="()Ljava/lang/String;">
                    <counter type="BRANCH" missed="0" covered="2"/>
                    <counter type="LINE" missed="0" covered="3"/>
                    <counter type="INSTRUCTION" missed="0" covered="15"/>
                  </method>
                  <method name="goodbye" desc="()Ljava/lang/String;">
                    <counter type="BRANCH" missed="1" covered="1"/>
                    <counter type="LINE" missed="2" covered="2"/>
                    <counter type="INSTRUCTION" missed="10" covered="10"/>
                  </method>
                </class>
                <class name="com/example/service/DataService">
                  <method name="loadData" desc="()Ljava/util/List;">
                    <counter type="BRANCH" missed="0" covered="3"/>
                    <counter type="LINE" missed="0" covered="8"/>
                    <counter type="INSTRUCTION" missed="0" covered="42"/>
                  </method>
                  <method name="saveData" desc="(Ljava/util/List;)V">
                    <counter type="BRANCH" missed="2" covered="2"/>
                    <counter type="LINE" missed="3" covered="5"/>
                    <counter type="INSTRUCTION" missed="15" covered="25"/>
                  </method>
                </class>
              </package>
              <package name="com/example/util">
                <class name="com/example/util/StringUtils">
                  <method name="isEmpty" desc="(Ljava/lang/String;)Z">
                    <counter type="BRANCH" missed="0" covered="1"/>
                    <counter type="LINE" missed="0" covered="1"/>
                    <counter type="INSTRUCTION" missed="0" covered="5"/>
                  </method>
                </class>
              </package>
            </report>
            """;

        Path xmlFile = tempDir.resolve("jacoco_multiple.xml");
        Files.writeString(xmlFile, xml);
        return xmlFile;
    }
}
