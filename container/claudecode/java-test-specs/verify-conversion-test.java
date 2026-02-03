import java.io.*;
import java.nio.file.*;
import java.util.*;

// Simplified test to verify the coverage data conversion
public class VerifyConversionTest {
    public static void main(String[] args) {
        System.out.println("=== Coverage Data Conversion Test ===");

        // Simulate the data conversion process

        // Step 1: Simulate CoverageInfo creation (what CoverageReportParser.processCoverageReports returns)
        List<CoverageInfo> mockCoverageInfos = createMockCoverageInfos();
        System.out.println("Step 1: Created " + mockCoverageInfos.size() + " CoverageInfo objects");

        for (CoverageInfo info : mockCoverageInfos) {
            System.out.println("  - " + info.getClassName() + "." + info.getMethodName() +
                " (branch: " + info.getBranchCoverage() + "%)");
        }

        // Step 2: Simulate Map conversion (what CoverageReportParser.convertCoverageInfoToMap does)
        Map<String, Object> coverageDataMap = new HashMap<>();
        for (int i = 0; i < mockCoverageInfos.size(); i++) {
            coverageDataMap.put("coverage_" + i, convertCoverageInfoToMap(mockCoverageInfos.get(i)));
        }
        System.out.println("\nStep 2: Converted to Map with " + coverageDataMap.size() + " entries");

        // Step 3: Simulate List conversion (what MultiModuleProcessor.convertToCoverageInfoList does)
        List<CoverageInfo> convertedBack = convertToCoverageInfoList(coverageDataMap);
        System.out.println("\nStep 3: Converted back to " + convertedBack.size() + " CoverageInfo objects");

        for (CoverageInfo info : convertedBack) {
            System.out.println("  - " + info.getClassName() + "." + info.getMethodName() +
                " (branch: " + info.getBranchCoverage() + "%)");
        }

        // Step 4: Verify data integrity
        System.out.println("\n=== Data Integrity Verification ===");
        boolean allGood = true;

        if (mockCoverageInfos.size() != convertedBack.size()) {
            System.out.println("❌ Size mismatch: " + mockCoverageInfos.size() + " vs " + convertedBack.size());
            allGood = false;
        }

        for (int i = 0; i < Math.min(mockCoverageInfos.size(), convertedBack.size()); i++) {
            CoverageInfo original = mockCoverageInfos.get(i);
            CoverageInfo converted = convertedBack.get(i);

            if (!Objects.equals(original.getClassName(), converted.getClassName())) {
                System.out.println("❌ ClassName mismatch at " + i + ": '" + original.getClassName() +
                    "' vs '" + converted.getClassName() + "'");
                allGood = false;
            }

            if (!Objects.equals(original.getMethodName(), converted.getMethodName())) {
                System.out.println("❌ MethodName mismatch at " + i + ": '" + original.getMethodName() +
                    "' vs '" + converted.getMethodName() + "'");
                allGood = false;
            }
        }

        if (allGood) {
            System.out.println("✅ All data conversion tests passed!");
        } else {
            System.out.println("❌ Data conversion has issues!");
        }
    }

    private static List<CoverageInfo> createMockCoverageInfos() {
        List<CoverageInfo> infos = new ArrayList<>();

        // HelloService methods
        CoverageInfo hello = new CoverageInfo("HelloService", "hello");
        hello.setPackageName("jp/go/courts/addressbook/batch/service");
        hello.setBranchInfo(2, 2); // 100% branch coverage
        infos.add(hello);

        CoverageInfo selectTest = new CoverageInfo("HelloService", "selectTest");
        selectTest.setPackageName("jp/go/courts/addressbook/batch/service");
        selectTest.setBranchInfo(2, 2); // 100% branch coverage
        infos.add(selectTest);

        return infos;
    }

    private static Map<String, Object> convertCoverageInfoToMap(CoverageInfo coverage) {
        Map<String, Object> map = new HashMap<>();
        map.put("className", coverage.getClassName());
        map.put("methodName", coverage.getMethodName());
        map.put("packageName", coverage.getPackageName());
        map.put("branchCoverage", coverage.getBranchCoverage());
        map.put("branchesCovered", coverage.getBranchesCovered());
        map.put("branchesTotal", coverage.getBranchesTotal());
        map.put("linesCovered", coverage.getLinesCovered());
        map.put("linesTotal", coverage.getLinesTotal());
        return map;
    }

    private static List<CoverageInfo> convertToCoverageInfoList(Map<String, Object> coverageData) {
        List<CoverageInfo> coverageInfoList = new ArrayList<>();

        if (coverageData == null) {
            return coverageInfoList;
        }

        for (Map.Entry<String, Object> entry : coverageData.entrySet()) {
            try {
                if (entry.getValue() instanceof Map) {
                    Map<String, Object> coverageMap = (Map<String, Object>) entry.getValue();

                    String className = (String) coverageMap.get("className");
                    String methodName = (String) coverageMap.get("methodName");

                    if (className != null && methodName != null) {
                        CoverageInfo info = new CoverageInfo(className, methodName);

                        if (coverageMap.get("packageName") != null) {
                            info.setPackageName((String) coverageMap.get("packageName"));
                        }

                        if (coverageMap.get("branchesCovered") != null && coverageMap.get("branchesTotal") != null) {
                            Integer branchesCovered = (Integer) coverageMap.get("branchesCovered");
                            Integer branchesTotal = (Integer) coverageMap.get("branchesTotal");
                            info.setBranchInfo(branchesCovered, branchesTotal);
                        }

                        coverageInfoList.add(info);
                    }
                }
            } catch (Exception e) {
                System.out.println("Failed to convert coverage entry: " + entry.getKey() + " - " + e.getMessage());
            }
        }

        return coverageInfoList;
    }
}

// Mock CoverageInfo class
class CoverageInfo {
    private String className;
    private String methodName;
    private String packageName;
    private int branchesCovered = 0;
    private int branchesTotal = 0;
    private int linesCovered = 0;
    private int linesTotal = 0;
    private double branchCoverage = 0.0;

    public CoverageInfo(String className, String methodName) {
        this.className = className;
        this.methodName = methodName;
    }

    public String getClassName() { return className; }
    public String getMethodName() { return methodName; }
    public String getPackageName() { return packageName; }
    public void setPackageName(String packageName) { this.packageName = packageName; }
    public int getBranchesCovered() { return branchesCovered; }
    public int getBranchesTotal() { return branchesTotal; }
    public int getLinesCovered() { return linesCovered; }
    public int getLinesTotal() { return linesTotal; }
    public double getBranchCoverage() { return branchCoverage; }

    public void setBranchInfo(int covered, int total) {
        this.branchesCovered = covered;
        this.branchesTotal = total;
        this.branchCoverage = total > 0 ? (covered * 100.0 / total) : 0.0;
    }
}