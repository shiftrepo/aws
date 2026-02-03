import java.io.*;
import java.nio.file.*;
import java.util.*;
import org.jsoup.*;
import org.jsoup.nodes.*;
import org.jsoup.select.*;

public class TestRealCoverage {
    public static void main(String[] args) throws IOException {
        // あなたの実際のJaCoCo XMLを解析
        String xmlPath = "/root/aws.git/container/claudecode/java-test-specs/debug-real-jacoco.xml";

        System.out.println("=== JaCoCo XML Analysis Test ===");

        String content = Files.readString(Paths.get(xmlPath));
        System.out.println("File size: " + content.length() + " characters");

        // XMLパース
        Document doc = Jsoup.parse(content, "", org.jsoup.parser.Parser.xmlParser());

        // レポート要素
        Element reportElement = doc.selectFirst("report");
        System.out.println("Report name: " + reportElement.attr("name"));

        // パッケージ要素
        Elements packages = doc.select("package");
        System.out.println("Packages found: " + packages.size());

        for (int i = 0; i < packages.size(); i++) {
            Element packageElement = packages.get(i);
            String packageName = packageElement.attr("name");
            System.out.println("\nPackage " + (i+1) + ": '" + packageName + "'");

            // クラス要素
            Elements classes = packageElement.select("class");
            System.out.println("  Classes: " + classes.size());

            for (int j = 0; j < classes.size(); j++) {
                Element classElement = classes.get(j);
                String classPath = classElement.attr("name");
                String sourceFileName = classElement.attr("sourcefilename");

                System.out.println("    Class " + (j+1) + ":");
                System.out.println("      classPath: '" + classPath + "'");
                System.out.println("      sourceFile: '" + sourceFileName + "'");

                // クラス名抽出テスト
                String className = extractClassNameFromPath(classPath);
                System.out.println("      extracted className: '" + className + "'");

                // メソッド要素
                Elements methods = classElement.select("method");
                System.out.println("      Methods: " + methods.size());

                for (int k = 0; k < methods.size(); k++) {
                    Element methodElement = methods.get(k);
                    String methodName = methodElement.attr("name");

                    System.out.println("        Method " + (k+1) + ": '" + methodName + "'");

                    // カウンター
                    Elements counters = methodElement.select("counter");
                    for (Element counter : counters) {
                        String type = counter.attr("type");
                        String missed = counter.attr("missed");
                        String covered = counter.attr("covered");

                        if ("BRANCH".equals(type) || "INSTRUCTION".equals(type)) {
                            int totalCount = Integer.parseInt(covered) + Integer.parseInt(missed);
                            double coverage = totalCount > 0 ? (Double.parseDouble(covered) / totalCount * 100) : 0;
                            System.out.println("          " + type + ": " + coverage + "% (" + covered + "/" + totalCount + ")");
                        }
                    }
                }
            }
        }

        System.out.println("\n=== Analysis Complete ===");
    }

    private static String extractClassNameFromPath(String classPath) {
        if (classPath == null || classPath.isEmpty()) {
            return "UnknownClass";
        }

        String[] parts = classPath.split("/");
        String className = parts[parts.length - 1];

        if (className == null || className.isEmpty()) {
            return "UnknownClass";
        }

        return className;
    }
}