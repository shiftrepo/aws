package com.javadocenhancer.core;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;
import java.util.stream.Collectors;

/**
 * ソースファイルとテストファイルをスキャンするクラス
 *
 * 既存のFolderScannerをベースに、拡張JavaDoc生成に必要な
 * ソースファイルとテストファイルの両方を効率的にスキャンします。
 */
public class SourceFileScanner {

    private static final Logger logger = LoggerFactory.getLogger(SourceFileScanner.class);

    // Javaファイルの拡張子
    private static final String JAVA_FILE_EXTENSION = ".java";

    // 除外するディレクトリパターン
    private static final Set<String> EXCLUDED_DIRECTORIES = Set.of(
            ".git",
            ".svn",
            "node_modules",
            "target",
            "build",
            "out",
            ".idea",
            ".vscode",
            "bin",
            "dist",
            "generated-sources",
            "generated-test-sources"
    );

    // 除外するファイルパターン
    private static final Set<String> EXCLUDED_FILE_PATTERNS = Set.of(
            "module-info.java",      // Java 9+ モジュールファイル
            "package-info.java"      // パッケージ情報ファイル
    );

    // 最大ファイルサイズ (10MB)
    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024;

    /**
     * 指定ディレクトリからソースファイルを再帰的にスキャン
     *
     * @param sourceDirectory スキャンするソースディレクトリ
     * @return 発見されたソースファイルのリスト
     */
    public List<Path> scanForSourceFiles(Path sourceDirectory) {
        logger.info("ソースファイルスキャン開始: {}", sourceDirectory);

        if (!validateDirectory(sourceDirectory)) {
            return new ArrayList<>();
        }

        List<Path> sourceFiles = new ArrayList<>();

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
                        if (isSourceFile(file) && isFileSizeValid(file)) {
                            sourceFiles.add(file);
                            logger.debug("ソースファイル発見: {}", file);
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
            logger.error("ソースディレクトリスキャン中にエラー", e);
            return new ArrayList<>();
        }

        // ファイル名でソート
        sourceFiles.sort(Comparator.comparing(Path::toString));

        logger.info("ソースファイルスキャン完了: {}個のファイルを発見", sourceFiles.size());
        return sourceFiles;
    }

    /**
     * 指定ディレクトリからテストファイルを再帰的にスキャン
     *
     * @param testDirectory スキャンするテストディレクトリ
     * @return 発見されたテストファイルのリスト
     */
    public List<Path> scanForTestFiles(Path testDirectory) {
        logger.info("テストファイルスキャン開始: {}", testDirectory);

        if (!validateDirectory(testDirectory)) {
            return new ArrayList<>();
        }

        List<Path> testFiles = new ArrayList<>();

        try {
            Files.walkFileTree(testDirectory, new SimpleFileVisitor<Path>() {
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
                        if (isTestFile(file) && isFileSizeValid(file)) {
                            testFiles.add(file);
                            logger.debug("テストファイル発見: {}", file);
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
            logger.error("テストディレクトリスキャン中にエラー", e);
            return new ArrayList<>();
        }

        // ファイル名でソート
        testFiles.sort(Comparator.comparing(Path::toString));

        logger.info("テストファイルスキャン完了: {}個のファイルを発見", testFiles.size());
        return testFiles;
    }

    /**
     * ディレクトリの検証
     */
    private boolean validateDirectory(Path directory) {
        if (directory == null) {
            logger.warn("ディレクトリパスがnullです");
            return false;
        }

        if (!Files.exists(directory)) {
            logger.warn("指定されたディレクトリが存在しません: {}", directory);
            return false;
        }

        if (!Files.isDirectory(directory)) {
            logger.warn("指定されたパスはディレクトリではありません: {}", directory);
            return false;
        }

        return true;
    }

    /**
     * ファイルがソースファイルかどうかをチェック
     */
    private boolean isSourceFile(Path file) {
        String fileName = file.getFileName().toString();

        // 拡張子チェック
        if (!fileName.endsWith(JAVA_FILE_EXTENSION)) {
            return false;
        }

        // 除外ファイルパターンチェック
        if (EXCLUDED_FILE_PATTERNS.contains(fileName)) {
            return false;
        }

        // テストファイルは除外（ソースファイル用）
        String lowerFileName = fileName.toLowerCase();
        if (lowerFileName.contains("test") &&
            (lowerFileName.endsWith("test.java") ||
             lowerFileName.endsWith("tests.java") ||
             lowerFileName.contains("test"))) {
            return false;
        }

        return true;
    }

    /**
     * ファイルがテストファイルかどうかをチェック
     */
    private boolean isTestFile(Path file) {
        String fileName = file.getFileName().toString();

        // 拡張子チェック
        if (!fileName.endsWith(JAVA_FILE_EXTENSION)) {
            return false;
        }

        // 除外ファイルパターンチェック
        if (EXCLUDED_FILE_PATTERNS.contains(fileName)) {
            return false;
        }

        // テストファイルの判定
        String lowerFileName = fileName.toLowerCase();
        return lowerFileName.contains("test") &&
               (lowerFileName.endsWith("test.java") ||
                lowerFileName.endsWith("tests.java") ||
                lowerFileName.startsWith("test") ||
                fileName.matches(".*Test[A-Z].*\\.java") ||
                fileName.matches(".*Tests\\.java"));
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
    public Map<String, Object> getStatistics(List<Path> sourceFiles, List<Path> testFiles) {
        Map<String, Object> stats = new HashMap<>();

        // ファイル統計
        stats.put("sourceFileCount", sourceFiles.size());
        stats.put("testFileCount", testFiles.size());
        stats.put("totalFileCount", sourceFiles.size() + testFiles.size());

        // パッケージ統計（ディレクトリ構造から推定）
        Set<Path> sourcePackages = sourceFiles.stream()
                .map(Path::getParent)
                .collect(Collectors.toSet());
        Set<Path> testPackages = testFiles.stream()
                .map(Path::getParent)
                .collect(Collectors.toSet());

        stats.put("sourcePackageCount", sourcePackages.size());
        stats.put("testPackageCount", testPackages.size());

        // ファイルサイズ統計
        long totalSourceSize = sourceFiles.stream()
                .mapToLong(this::getFileSize)
                .sum();
        long totalTestSize = testFiles.stream()
                .mapToLong(this::getFileSize)
                .sum();

        stats.put("totalSourceSize", totalSourceSize);
        stats.put("totalTestSize", totalTestSize);
        stats.put("averageSourceFileSize", sourceFiles.isEmpty() ? 0 : totalSourceSize / sourceFiles.size());
        stats.put("averageTestFileSize", testFiles.isEmpty() ? 0 : totalTestSize / testFiles.size());

        return stats;
    }

    /**
     * ファイルサイズを取得（エラー時は0を返す）
     */
    private long getFileSize(Path file) {
        try {
            return Files.size(file);
        } catch (IOException e) {
            return 0;
        }
    }

    /**
     * スキャンのサマリー情報をログ出力
     */
    public void logScanSummary(List<Path> sourceFiles, List<Path> testFiles) {
        Map<String, Object> stats = getStatistics(sourceFiles, testFiles);

        logger.info("=== スキャン結果サマリー ===");
        logger.info("ソースファイル: {}個", stats.get("sourceFileCount"));
        logger.info("テストファイル: {}個", stats.get("testFileCount"));
        logger.info("総ファイル数: {}個", stats.get("totalFileCount"));
        logger.info("ソースパッケージ: {}個", stats.get("sourcePackageCount"));
        logger.info("テストパッケージ: {}個", stats.get("testPackageCount"));
        logger.info("総ソースサイズ: {}KB", (Long) stats.get("totalSourceSize") / 1024);
        logger.info("総テストサイズ: {}KB", (Long) stats.get("totalTestSize") / 1024);
    }

    /**
     * 重複ファイルのチェック
     *
     * @param sourceFiles ソースファイルリスト
     * @param testFiles テストファイルリスト
     * @return 重複が見つかった場合のファイル名リスト
     */
    public List<String> findDuplicateFiles(List<Path> sourceFiles, List<Path> testFiles) {
        Set<String> sourceFileNames = sourceFiles.stream()
                .map(path -> path.getFileName().toString())
                .collect(Collectors.toSet());

        List<String> duplicates = testFiles.stream()
                .map(path -> path.getFileName().toString())
                .filter(sourceFileNames::contains)
                .collect(Collectors.toList());

        if (!duplicates.isEmpty()) {
            logger.warn("重複ファイル名が発見されました: {}", duplicates);
        }

        return duplicates;
    }

    /**
     * パッケージ構造の解析
     *
     * @param files ファイルリスト
     * @param baseDir ベースディレクトリ
     * @return パッケージ名とファイル数のマッピング
     */
    public Map<String, Integer> analyzePackageStructure(List<Path> files, Path baseDir) {
        Map<String, Integer> packageStructure = new HashMap<>();

        for (Path file : files) {
            try {
                Path relativePath = baseDir.relativize(file.getParent());
                String packageName = relativePath.toString().replace(File.separator, ".");

                // java/com/example -> com.example
                if (packageName.startsWith("java.")) {
                    packageName = packageName.substring(5);
                }

                packageStructure.merge(packageName, 1, Integer::sum);
            } catch (Exception e) {
                logger.debug("パッケージ構造解析エラー: {} - {}", file, e.getMessage());
            }
        }

        return packageStructure;
    }
}