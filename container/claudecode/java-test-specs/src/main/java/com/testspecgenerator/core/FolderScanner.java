package com.testspecgenerator.core;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;
import java.util.stream.Collectors;

/**
 * ディレクトリ内のJavaファイルとカバレッジレポートファイルをスキャンするクラス
 */
public class FolderScanner {

    private static final Logger logger = LoggerFactory.getLogger(FolderScanner.class);

    // Javaファイルのパターン
    private static final Set<String> JAVA_FILE_PATTERNS = Set.of(
            "*.java"
    );

    // カバレッジレポートファイルのパターン
    private static final Set<String> COVERAGE_FILE_PATTERNS = Set.of(
            "jacoco*.xml",
            "*coverage*.xml",
            "index.html",
            "*coverage*.html"
    );

    // 除外するディレクトリパターン
    private static final Set<String> EXCLUDED_DIRECTORIES = Set.of(
            ".git",
            ".svn",
            "node_modules",
            "target",
            "build",
            "out",
            ".idea",
            ".vscode"
    );

    // 最大ファイルsize (10MB)
    private static final long MAX_FILE_SIZE = 100 * 1024 * 1024;

    /**
     * 指定ディレクトリからJavaファイルを再帰的にスキャン
     *
     * @param sourceDirectory スキャンするディレクトリ
     * @return 発見されたJavaファイルのリスト
     */
    public List<Path> scanForJavaFiles(Path sourceDirectory) {
        logger.info("Java file scanning started: {}", sourceDirectory);

        if (!Files.exists(sourceDirectory)) {
            logger.warn("Specified directory does not exist: {}", sourceDirectory);
            return new ArrayList<>();
        }

        if (!Files.isDirectory(sourceDirectory)) {
            logger.warn("Specified path is not a directory: {}", sourceDirectory);
            return new ArrayList<>();
        }

        List<Path> javaFiles = new ArrayList<>();

        try {
            Files.walkFileTree(sourceDirectory, new SimpleFileVisitor<Path>() {
                @Override
                public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) {
                    String dirName = dir.getFileName().toString();
                    if (EXCLUDED_DIRECTORIES.contains(dirName)) {
                        logger.debug("Skipping directory: {}", dir);
                        return FileVisitResult.SKIP_SUBTREE;
                    }
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                    try {
                        if (isJavaFile(file) && isFileSizeValid(file)) {
                            javaFiles.add(file);
                            logger.debug("Java file found: {}", file);
                        }
                    } catch (Exception e) {
                        logger.warn("Error checking file: {} - {}", file, e.getMessage());
                    }
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult visitFileFailed(Path file, IOException exc) {
                    logger.warn("File access failed: {} - {}", file, exc.getMessage());
                    return FileVisitResult.CONTINUE;
                }
            });

        } catch (IOException e) {
            logger.error("Error during directory scan", e);
            return new ArrayList<>();
        }

        // ファイル名でソート
        javaFiles.sort(Comparator.comparing(Path::toString));

        logger.info("Java file scan completed: {} files found", javaFiles.size());
        return javaFiles;
    }

    /**
     * 指定ディレクトリからカバレッジレポートファイルを再帰的にスキャン
     *
     * @param sourceDirectory スキャンするディレクトリ
     * @return 発見されたカバレッジレポートファイルのリスト
     */
    public List<Path> scanForCoverageReports(Path sourceDirectory) {
        logger.info("[Scanner Debug] Coverage report scanning started: {}", sourceDirectory);
        logger.debug("[Scanner Debug] Search directory absolute path: {}", sourceDirectory.toAbsolutePath());

        if (!Files.exists(sourceDirectory)) {
            logger.warn("[Scanner Debug] Specified directory does not exist: {}", sourceDirectory);
            return new ArrayList<>();
        }

        if (!Files.isDirectory(sourceDirectory)) {
            logger.warn("[Scanner Debug] Specified path is not a directory: {}", sourceDirectory);
            return new ArrayList<>();
        }

        List<Path> coverageFiles = new ArrayList<>();
        final int[] totalFilesScanned = {0};
        final int[] totalDirectoriesScanned = {0};
        final int[] skippedDirectories = {0};

        logger.debug("[Scanner Debug] Coverage file patterns: {}", COVERAGE_FILE_PATTERNS);

        try {
            Files.walkFileTree(sourceDirectory, new SimpleFileVisitor<Path>() {
                @Override
                public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) {
                    totalDirectoriesScanned[0]++;
                    String dirName = dir.getFileName().toString();

                    logger.trace("[Scanner Debug] ディレクトリ検査 {}: {}", totalDirectoriesScanned[0], dir);

                    // カバレッジレポートスキャン時はtargetディレクトリを除外しない
                    // (JaCoCoレポートはtarget/site/jacocoにあるため)
                    if (EXCLUDED_DIRECTORIES.contains(dirName) && !"target".equals(dirName)) {
                        skippedDirectories[0]++;
                        logger.debug("[Scanner Debug] Skipping directory ({}): {}", skippedDirectories[0], dir);
                        return FileVisitResult.SKIP_SUBTREE;
                    }

                    // 重要なカバレッジディレクトリを特定
                    if (dirName.equals("jacoco") || dirName.equals("site") || dir.toString().contains("jacoco")) {
                        logger.debug("[Scanner Debug] 重要なカバレッジディレクトリ発見: {}", dir);
                    }

                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                    totalFilesScanned[0]++;

                    try {
                        String fileName = file.getFileName().toString();
                        logger.trace("[Scanner Debug] ファイル検査 {}: {} (size: {} bytes)",
                                   totalFilesScanned[0], fileName, attrs.size());

                        boolean isCoverageMatch = isCoverageFile(file);
                        boolean isSizeValid = isFileSizeValid(file);

                        logger.trace("[Scanner Debug] ファイル判定: {} - カバレッジファイル: {}, size有効: {}",
                                   fileName, isCoverageMatch, isSizeValid);

                        if (isCoverageMatch && isSizeValid) {
                            coverageFiles.add(file);
                            logger.info("[Scanner Debug] Coverage file found ({}): {} (size: {} bytes)",
                                       coverageFiles.size(), file, attrs.size());

                            // ファイルの詳細情報をログ出力
                            try {
                                String fileContent = Files.readString(file, StandardCharsets.UTF_8);
                                int contentLength = fileContent.length();
                                logger.debug("[Scanner Debug] ファイル内容確認: {} 文字, 先頭: '{}'",
                                           contentLength, contentLength > 0 ?
                                           fileContent.substring(0, Math.min(50, contentLength)).replace('\n', ' ') : "空");
                            } catch (Exception e) {
                                logger.debug("[Scanner Debug] ファイル内容読み取り失敗: {} - {}", file, e.getMessage());
                            }
                        } else if (isCoverageMatch && !isSizeValid) {
                            logger.warn("[Scanner Debug] カバレッジファイルだがsize無効: {} (size: {})", file, attrs.size());
                        } else if (!isCoverageMatch && fileName.contains("jacoco")) {
                            logger.debug("[Scanner Debug] JaCoCoファイルだがパターン不一致: {}", file);
                        }
                    } catch (Exception e) {
                        logger.warn("[Scanner Debug] Error checking file: {} - {}", file, e.getMessage());
                    }
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult visitFileFailed(Path file, IOException exc) {
                    logger.warn("[Scanner Debug] File access failed: {} - {}", file, exc.getMessage());
                    return FileVisitResult.CONTINUE;
                }
            });

        } catch (IOException e) {
            logger.error("[Scanner Debug] Error during directory scan", e);
            return new ArrayList<>();
        }

        // ファイル名でソート
        coverageFiles.sort(Comparator.comparing(Path::toString));

        // 詳細なScan statistics
        logger.info("[Scanner Debug] Scan statistics:");
        logger.info("[Scanner Debug] - Directories scanned: {}", totalDirectoriesScanned[0]);
        logger.info("[Scanner Debug] - Directories skipped: {}", skippedDirectories[0]);
        logger.info("[Scanner Debug] - Files scanned: {}", totalFilesScanned[0]);
        logger.info("[Scanner Debug] - Coverage files found: {}", coverageFiles.size());

        if (coverageFiles.isEmpty()) {
            logger.warn("[Scanner Debug] No coverage files found");
            logger.warn("[Scanner Debug] Possible causes:");
            logger.warn("[Scanner Debug] 1. JaCoCoレポートが生成されていない - 'mvn test jacoco:report' を実行してください");
            logger.warn("[Scanner Debug] 2. 検索ディレクトリが間違っている - プロジェクトルートを指定してください");
            logger.warn("[Scanner Debug] 3. target/site/jacoco/ ディレクトリが存在しない");
            logger.warn("[Scanner Debug] 4. XMLファイル以外のみ存在（HTMLファイルは処理されません）");

            // 推奨の場所を確認
            Path targetJacoco = sourceDirectory.resolve("target/site/jacoco");
            if (Files.exists(targetJacoco)) {
                logger.info("[Scanner Debug] target/site/jacoco ディレクトリは存在します: {}", targetJacoco);
                try {
                    logger.info("[Scanner Debug] ディレクトリ内容:");
                    Files.list(targetJacoco).forEach(path ->
                        logger.info("[Scanner Debug] - {}", path.getFileName()));
                } catch (IOException e) {
                    logger.debug("[Scanner Debug] ディレクトリ内容の取得に失敗: {}", e.getMessage());
                }
            } else {
                logger.warn("[Scanner Debug] target/site/jacoco ディレクトリが存在しません: {}", targetJacoco);
            }
        } else {
            logger.info("[Scanner Debug] 発見されたカバレッジファイル:");
            for (int i = 0; i < coverageFiles.size(); i++) {
                Path file = coverageFiles.get(i);
                try {
                    long fileSize = Files.size(file);
                    logger.info("[Scanner Debug] {}. {} ({}bytes)", i + 1, file, fileSize);
                } catch (IOException e) {
                    logger.info("[Scanner Debug] {}. {} (size取得失敗)", i + 1, file);
                }
            }
        }

        logger.info("[Scanner Debug] Coverage report scan completed: {} files found", coverageFiles.size());
        return coverageFiles;
    }

    /**
     * 指定ディレクトリからSurefireテストレポートを再帰的にスキャン
     *
     * @param sourceDirectory スキャンするディレクトリ
     * @return 発見されたSurefireレポートファイル（TEST-*.xml）のリスト
     */
    public List<Path> scanForSurefireReports(Path sourceDirectory) {
        logger.info("Surefire test report scan started: {}", sourceDirectory);

        if (!Files.exists(sourceDirectory)) {
            logger.warn("Specified directory does not exist: {}", sourceDirectory);
            return new ArrayList<>();
        }

        if (!Files.isDirectory(sourceDirectory)) {
            logger.warn("Specified path is not a directory: {}", sourceDirectory);
            return new ArrayList<>();
        }

        List<Path> surefireFiles = new ArrayList<>();

        try {
            Files.walkFileTree(sourceDirectory, new SimpleFileVisitor<Path>() {
                @Override
                public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) {
                    String dirName = dir.getFileName().toString();
                    // Surefireレポートはtarget/surefire-reportsにあるため、targetは除外しない
                    if (EXCLUDED_DIRECTORIES.contains(dirName) && !"target".equals(dirName)) {
                        logger.debug("Skipping directory: {}", dir);
                        return FileVisitResult.SKIP_SUBTREE;
                    }
                    // surefire-reportsディレクトリを優先的に検索
                    if ("surefire-reports".equals(dirName)) {
                        logger.debug("Surefire report directory found: {}", dir);
                    }
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                    try {
                        if (isSurefireReportFile(file) && isFileSizeValid(file)) {
                            surefireFiles.add(file);
                            logger.debug("Surefire report found: {}", file);
                        }
                    } catch (Exception e) {
                        logger.warn("Error checking file: {} - {}", file, e.getMessage());
                    }
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult visitFileFailed(Path file, IOException exc) {
                    logger.warn("File access failed: {} - {}", file, exc.getMessage());
                    return FileVisitResult.CONTINUE;
                }
            });

        } catch (IOException e) {
            logger.error("Error during directory scan", e);
            return new ArrayList<>();
        }

        // ファイル名でソート
        surefireFiles.sort(Comparator.comparing(Path::toString));

        logger.info("Surefire report scan completed: {} files found", surefireFiles.size());
        return surefireFiles;
    }

    /**
     * ファイルがSurefireテストレポートファイルかどうかをチェック
     */
    private boolean isSurefireReportFile(Path file) {
        String fileName = file.getFileName().toString();

        // TEST-*.xmlパターンに合致するかチェック
        if (fileName.startsWith("TEST-") && fileName.endsWith(".xml")) {
            // surefire-reportsディレクトリ内にあることを確認（推奨）
            String pathStr = file.toString().replace('\\', '/');
            if (pathStr.contains("/surefire-reports/") || pathStr.contains("/target/surefire-reports/")) {
                return true;
            }
            // surefire-reportsディレクトリ外にあってもTEST-*.xmlパターンなら許可
            logger.debug("Surefireレポートがsurefire-reportsディレクトリ外で発見: {}", file);
            return true;
        }
        return false;
    }

    /**
     * ファイルがJavaファイルかどうかをチェック
     */
    private boolean isJavaFile(Path file) {
        String fileName = file.getFileName().toString().toLowerCase();

        // 拡張子チェック
        if (!fileName.endsWith(".java")) {
            return false;
        }

        // テストファイルかどうかをチェック（テストファイルを優先）
        if (fileName.contains("test")) {
            return true;
        }

        // 通常のJavaファイルも対象とする
        return true;
    }

    /**
     * ファイルがカバレッジレポートファイルかどうかをチェック
     */
    private boolean isCoverageFile(Path file) {
        String originalFileName = file.getFileName().toString();
        String fileName = originalFileName.toLowerCase();

        logger.trace("[Coverage File Debug] ファイル判定: '{}' -> '{}'", originalFileName, fileName);

        // XMLファイルパターンチェック
        if (fileName.endsWith(".xml")) {
            boolean containsJacoco = fileName.contains("jacoco");
            boolean containsCoverage = fileName.contains("coverage");
            boolean isXmlMatch = containsJacoco || containsCoverage;

            logger.trace("[Coverage File Debug] XMLファイル判定: jacoco={}, coverage={}, 結果={}",
                       containsJacoco, containsCoverage, isXmlMatch);

            if (isXmlMatch) {
                logger.debug("[Coverage File Debug] XMLカバレッジファイルと判定: {}", originalFileName);
                return true;
            } else {
                logger.trace("[Coverage File Debug] XMLファイルだがカバレッジパターン不一致: {}", originalFileName);
            }
        }

        // HTMLファイルパターンチェック
        if (fileName.endsWith(".html")) {
            boolean isIndexHtml = fileName.equals("index.html");
            boolean containsCoverageInHtml = fileName.contains("coverage");
            boolean isHtmlMatch = isIndexHtml || containsCoverageInHtml;

            logger.trace("[Coverage File Debug] HTMLファイル判定: index.html={}, coverage={}, 結果={}",
                       isIndexHtml, containsCoverageInHtml, isHtmlMatch);

            if (isHtmlMatch) {
                logger.debug("[Coverage File Debug] HTMLカバレッジファイルと判定: {} (注意: HTMLは処理されません)", originalFileName);
                return true;
            } else {
                logger.trace("[Coverage File Debug] HTMLファイルだがカバレッジパターン不一致: {}", originalFileName);
            }
        }

        // その他の拡張子
        if (!fileName.endsWith(".xml") && !fileName.endsWith(".html")) {
            logger.trace("[Coverage File Debug] 非対応拡張子: {}", originalFileName);
        }

        logger.trace("[Coverage File Debug] カバレッジファイルではありません: {}", originalFileName);
        return false;
    }

    /**
     * ファイルsizeが有効かどうかをチェック
     */
    private boolean isFileSizeValid(Path file) {
        try {
            long fileSize = Files.size(file);
            if (fileSize > MAX_FILE_SIZE) {
                logger.warn("File size too large（{}MB）: {}", fileSize / (1024 * 1024), file);
                return false;
            }
            return fileSize > 0; // 空ファイルは除外
        } catch (IOException e) {
            logger.warn("Error getting file size: {} - {}", file, e.getMessage());
            return false;
        }
    }

    /**
     * 発見されたファイルの統計情報を取得
     */
    public Map<String, Object> getStatistics(List<Path> javaFiles, List<Path> coverageFiles) {
        Map<String, Object> stats = new HashMap<>();

        // Javaファイル統計
        stats.put("javaFileCount", javaFiles.size());
        stats.put("testFileCount", javaFiles.stream()
                .mapToInt(file -> file.getFileName().toString().toLowerCase().contains("test") ? 1 : 0)
                .sum());

        // カバレッジファイル統計
        stats.put("coverageFileCount", coverageFiles.size());
        stats.put("xmlCoverageCount", coverageFiles.stream()
                .mapToInt(file -> file.toString().toLowerCase().endsWith(".xml") ? 1 : 0)
                .sum());
        stats.put("htmlCoverageCount", coverageFiles.stream()
                .mapToInt(file -> file.toString().toLowerCase().endsWith(".html") ? 1 : 0)
                .sum());

        // ディレクトリ統計
        Set<Path> directories = new HashSet<>();
        javaFiles.forEach(file -> directories.add(file.getParent()));
        coverageFiles.forEach(file -> directories.add(file.getParent()));
        stats.put("directoryCount", directories.size());

        return stats;
    }

    /**
     * ファイル名のパターンマッチング
     */
    private boolean matchesPattern(String fileName, String pattern) {
        // 簡単なワイルドカードマッチング（*のみサポート）
        if (!pattern.contains("*")) {
            return fileName.equals(pattern);
        }

        String regex = pattern.replace("*", ".*");
        return fileName.matches(regex);
    }

    /**
     * スキャンのサマリー情報をログ出力
     */
    public void logScanSummary(List<Path> javaFiles, List<Path> coverageFiles) {
        Map<String, Object> stats = getStatistics(javaFiles, coverageFiles);

        logger.info("=== スキャン結果サマリー ===");
        logger.info("Javaファイル: {}個", stats.get("javaFileCount"));
        logger.info("テストファイル: {}個", stats.get("testFileCount"));
        logger.info("カバレッジファイル: {}個", stats.get("coverageFileCount"));
        logger.info("  - XML: {}個", stats.get("xmlCoverageCount"));
        logger.info("  - HTML: {}個", stats.get("htmlCoverageCount"));
        logger.info("Target directories: {}個", stats.get("directoryCount"));
    }
}