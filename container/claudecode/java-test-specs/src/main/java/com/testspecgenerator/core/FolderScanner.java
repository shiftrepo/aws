package com.testspecgenerator.core;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
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
    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024;

    /**
     * 指定ディレクトリからJavaファイルを再帰的にスキャン
     *
     * @param sourceDirectory スキャンするディレクトリ
     * @return 発見されたJavaファイルのリスト
     */
    public List<Path> scanForJavaFiles(Path sourceDirectory) {
        logger.info("Javaファイルスキャン開始: {}", sourceDirectory);

        if (!Files.exists(sourceDirectory)) {
            logger.warn("指定されたディレクトリが存在しません: {}", sourceDirectory);
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
        logger.info("カバレッジレポートスキャン開始: {}", sourceDirectory);

        if (!Files.exists(sourceDirectory)) {
            logger.warn("指定されたディレクトリが存在しません: {}", sourceDirectory);
            return new ArrayList<>();
        }

        if (!Files.isDirectory(sourceDirectory)) {
            logger.warn("指定されたパスはディレクトリではありません: {}", sourceDirectory);
            return new ArrayList<>();
        }

        List<Path> coverageFiles = new ArrayList<>();

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
                        if (isCoverageFile(file) && isFileSizeValid(file)) {
                            coverageFiles.add(file);
                            logger.debug("カバレッジファイル発見: {}", file);
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
        coverageFiles.sort(Comparator.comparing(Path::toString));

        logger.info("カバレッジレポートスキャン完了: {}個のファイルを発見", coverageFiles.size());
        return coverageFiles;
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
        String fileName = file.getFileName().toString().toLowerCase();

        // XMLファイルパターンチェック
        if (fileName.endsWith(".xml")) {
            return fileName.contains("jacoco") || fileName.contains("coverage");
        }

        // HTMLファイルパターンチェック
        if (fileName.endsWith(".html")) {
            return fileName.equals("index.html") || fileName.contains("coverage");
        }

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