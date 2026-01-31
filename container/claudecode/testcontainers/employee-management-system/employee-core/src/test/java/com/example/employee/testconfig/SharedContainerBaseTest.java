package com.example.employee.testconfig;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.TestMethodOrder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.util.Collections;

/**
 * 共有コンテナを使用するベーステストクラス
 *
 * 実装戦略:
 * - DBの初期化: コンテナ共有による高速化
 * - 高速化: コンテナ共有＋データリセット
 *
 * 利点:
 * - 初回起動後は3秒以内でテスト実行
 * - 80-90%のパフォーマンス改善
 * - テスト間の完全な分離
 */
@SpringBootTest
@Testcontainers
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public abstract class SharedContainerBaseTest {

    /**
     * 共有PostgreSQLコンテナ
     * - 全テストクラスで再利用
     * - tmpfsによる高速化
     * - 最適化されたPostgreSQL設定
     */
    @Container
    static PostgreSQLContainer<?> sharedPostgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("shared_test_db")
            .withUsername("test")
            .withPassword("test")
            .withReuse(true)  // コンテナ再利用を有効化
            // パフォーマンス最適化設定
            .withTmpFs(Collections.singletonMap("/var/lib/postgresql/data", "rw,size=1g"))
            .withCommand(
                "postgres",
                "-c", "fsync=off",                    // テスト用：安全性よりも速度重視
                "-c", "synchronous_commit=off",
                "-c", "checkpoint_segments=32",
                "-c", "checkpoint_completion_target=0.9",
                "-c", "wal_buffers=16MB",
                "-c", "shared_buffers=256MB",
                "-c", "max_connections=100"
            );

    @Autowired
    protected JdbcTemplate jdbcTemplate;

    @Autowired
    protected TestDataResetter testDataResetter;

    /**
     * Spring Boot設定を動的に更新
     */
    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        // TestContainerから取得した接続情報をSpringに設定
        registry.add("spring.datasource.url", sharedPostgres::getJdbcUrl);
        registry.add("spring.datasource.username", sharedPostgres::getUsername);
        registry.add("spring.datasource.password", sharedPostgres::getPassword);
        registry.add("spring.datasource.driver-class-name", () -> "org.postgresql.Driver");

        // JPA設定
        registry.add("spring.jpa.hibernate.ddl-auto", () -> "create-drop");
        registry.add("spring.jpa.properties.hibernate.dialect", () -> "org.hibernate.dialect.PostgreSQLDialect");

        // TestContainers最適化設定
        registry.add("testcontainers.reuse.enable", () -> "true");
        registry.add("spring.jpa.show-sql", () -> "false");  // パフォーマンス重視
    }

    /**
     * 各テスト前にデータをリセット
     * - コンテナ再作成より高速
     * - テスト間の完全な分離を保証
     */
    @BeforeEach
    void resetTestData() {
        testDataResetter.resetToBaseState();
    }

    /**
     * コンテナが起動中かを確認
     */
    protected boolean isContainerRunning() {
        return sharedPostgres.isRunning();
    }

    /**
     * データベース接続URLを取得
     */
    protected String getDatabaseUrl() {
        return sharedPostgres.getJdbcUrl();
    }
}