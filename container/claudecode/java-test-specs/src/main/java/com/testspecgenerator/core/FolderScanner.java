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

    // 最大ファイルサイズ (10MB)
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
            logger.warn("指定されたパスはディレクトリではありません: {}", sourceDirectory);
            return new ArrayList<>();
        }

        List<Path> javaFiles = new ArrayList<>();

        try {
            Files.walkFileTree(sourceDirectory, new SimpleFileVisitor<Path>() {
                @Override
                public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) {
                    String dirName = dir.getFileName().toString();
                    if (EXCLUDED_DIRECTORIES.contains(dirName)) {
                        logger.debug("ディレクトリをスキップ: {}", dir);
                        return FileVisitResult.SKIP_SUBTREE;
                    }
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                    try {
                        if (isJavaFile(file) && isFileSizeValid(file)) {
                            javaFiles.add(file);
                            logger.debug("Javaファイル発見: {}", file);
                        }
                    } catch (Exception e) {
                        logger.warn("ファイルチェック中にエラー: {} - {}", file, e.getMessage());
                    }
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult visitFileFailed(Path file, IOException exc) {
                    logger.warn("ファイルアクセス失敗: {} - {}", file, exc.getMessage());
                    return FileVisitResult.CONTINUE;
                }
            });

        } catch (IOException e) {
            logger.error("ディレクトリスキャン中にエラー", e);
            return new ArrayList<>();
        }

        // ファイル名でソート
        javaFiles.sort(Comparator.comparing(Path::toString));

        logger.info("Javaファイルスキャン完了: {}個のファイルを発見", javaFiles.size());
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
        logger.debug("[Scanner Debug] 検索ディレクトリの絶対パス: {}", sourceDirectory.toAbsolutePath());

        if (!Files.exists(sourceDirectory)) {
            logger.warn("[Scanner Debug] 指定されたディレクトリが存在しません: {}", sourceDirectory);
            return new ArrayList<>();
        }

        if (!Files.isDirectory(sourceDirectory)) {
            logger.warn("[Scanner Debug] 指定されたパスはディレクトリではありません: {}", sourceDirectory);
            return new ArrayList<>();
        }

        List<Path> coverageFiles = new ArrayList<>();
        final int[] totalFilesScanned = {0};
        final int[] totalDirectoriesScanned = {0};
        final int[] skippedDirectories = {0};

        logger.debug("[Scanner Debug] カバレッジファイルパターン: {}", COVERAGE_FILE_PATTERNS);

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
                        logger.debug("[Scanner Debug] ディレクトリをスキップ ({}): {}", skippedDirectories[0], dir);
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
                        logger.trace("[Scanner Debug] ファイル検査 {}: {} (サイズ: {} bytes)",
                                   totalFilesScanned[0], fileName, attrs.size());

                        boolean isCoverageMatch = isCoverageFile(file);
                        boolean isSizeValid = isFileSizeValid(file);

                        logger.trace("[Scanner Debug] ファイル判定: {} - カバレッジファイル: {}, サイズ有効: {}",
                                   fileName, isCoverageMatch, isSizeValid);

                        if (isCoverageMatch && isSizeValid) {
                            coverageFiles.add(file);
                            logger.info("[Scanner Debug] カバレッジファイル発見 ({}): {} (サイズ: {} bytes)",
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
                            logger.warn("[Scanner Debug] カバレッジファイルだがサイズ無効: {} (サイズ: {})", file, attrs.size());
                        } else if (!isCoverageMatch && fileName.contains("jacoco")) {
                            logger.debug("[Scanner Debug] JaCoCoファイルだがパターン不一致: {}", file);
                        }
                    } catch (Exception e) {
                        logger.warn("[Scanner Debug] ファイルチェック中にエラー: {} - {}", file, e.getMessage());
                    }
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult visitFileFailed(Path file, IOException exc) {
                    logger.warn("[Scanner Debug] ファイルアクセス失敗: {} - {}", file, exc.getMessage());
                    return FileVisitResult.CONTINUE;
                }
            });

        } catch (IOException e) {
            logger.error("[Scanner Debug] ディレクトリスキャン中にエラー", e);
            return new ArrayList<>();
        }

        // ファイル名でソート
        coverageFiles.sort(Comparator.comparing(Path::toString));

        // 詳細なスキャン統計
        logger.info("[Scanner Debug] スキャン統計:");
        logger.info("[Scanner Debug] - スキャンしたディレクトリ数: {}", totalDirectoriesScanned[0]);
        logger.info("[Scanner Debug] - スキップしたディレクトリ数: {}", skippedDirectories[0]);
        logger.info("[Scanner Debug] - スキャンしたファイル数: {}", totalFilesScanned[0]);
        logger.info("[Scanner Debug] - 発見したカバレッジファイル数: {}", coverageFiles.size());

        if (coverageFiles.isEmpty()) {
            logger.warn("[Scanner Debug] カバレッジファイルが見つかりませんでした");
            logger.warn("[Scanner Debug] 考えられる原因:");
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
                    logger.info("[Scanner Debug] {}. {} (サイズ取得失敗)", i + 1, file);
                }
            }
        }

        logger.info("[Scanner Debug] カバレッジレポートスキャン完了: {}個のファイルを発見", coverageFiles.size());
        return coverageFiles;
    }

    /**
     * 指定ディレクトリからSurefireテストレポートを再帰的にスキャン
     *
     * @param sourceDirectory スキャンするディレクトリ
     * @return 発見されたSurefireレポートファイル（TEST-*.xml）のリスト
     */
    public List<Path> scanForSurefireReports(Path sourceDirectory) {
        logger.info("Surefireテストレポートスキャン開始: {}", sourceDirectory);

        if (!Files.exists(sourceDirectory)) {
            logger.warn("Specified directory does not exist: {}", sourceDirectory);
            return new ArrayList<>();
        }

        if (!Files.isDirectory(sourceDirectory)) {
            logger.warn("指定されたパスはディレクトリではありません: {}", sourceDirectory);
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
                        logger.debug("ディレクトリをスキップ: {}", dir);
                        return FileVisitResult.SKIP_SUBTREE;
                    }
                    // surefire-reportsディレクトリを優先的に検索
                    if ("surefire-reports".equals(dirName)) {
                        logger.debug("Surefireレポートディレクトリ発見: {}", dir);
                    }
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                    try {
                        if (isSurefireReportFile(file) && isFileSizeValid(file)) {
                            surefireFiles.add(file);
                            logger.debug("Surefireレポート発見: {}", file);
                        }
                    } catch (Exception e) {
                        logger.warn("ファイルチェック中にエラー: {} - {}", file, e.getMessage());
                    }
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult visitFileFailed(Path file, IOException exc) {
                    logger.warn("ファイルアクセス失敗: {} - {}", file, exc.getMessage());
                    return FileVisitResult.CONTINUE;
                }
            });

        } catch (IOException e) {
            logger.error("ディレクトリスキャン中にエラー", e);
            return new ArrayList<>();
        }

        // ファイル名でソート
        surefireFiles.sort(Comparator.comparing(Path::toString));

        logger.info("Surefireレポートスキャン完了: {}個のファイルを発見", surefireFiles.size());
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
     * ファイルサイズが有効かどうかをチェック
     */
    private boolean isFileSizeValid(Path file) {
        try {
            long fileSize = Files.size(file);
            if (fileSize > MAX_FILE_SIZE) {
                logger.warn("ファイルサイズが大きすぎます（{}MB）: {}", fileSize / (1024 * 1024), file);
                return false;
            }
            return fileSize > 0; // 空ファイルは除外
        } catch (IOException e) {
            logger.warn("ファイルサイズ取得エラー: {} - {}", file, e.getMessage());
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
        logger.info("対象ディレクトリ: {}個", stats.get("directoryCount"));
    }
}