-- V4: Insert sample data
-- サンプルデータ挿入

-- 1. 組織データ挿入
INSERT INTO organizations (name, description) VALUES
('テクノロジー株式会社', '最先端技術の研究開発を行う企業'),
('ビジネスソリューションズ', 'ビジネス課題の解決を支援する企業');

-- 2. 部門データ挿入（階層構造）
-- トップレベル部門
INSERT INTO departments (name, description, organization_id, parent_department_id) VALUES
('技術部', '技術開発全般を統括', 1, NULL),
('営業部', '営業活動を統括', 1, NULL),
('管理部', '経営管理を統括', 1, NULL),
('コンサルティング部', 'ビジネスコンサルティング', 2, NULL),
('マーケティング部', 'マーケティング戦略立案', 2, NULL);

-- 子部門（技術部配下）
INSERT INTO departments (name, description, organization_id, parent_department_id) VALUES
('開発課', 'システム開発', 1, 1),
('インフラ課', 'インフラストラクチャ管理', 1, 1),
('品質管理課', '品質保証・テスト', 1, 1);

-- 子部門（営業部配下）
INSERT INTO departments (name, description, organization_id, parent_department_id) VALUES
('法人営業課', '法人向け営業', 1, 2),
('個人営業課', '個人向け営業', 1, 2);

-- 3. ユーザーデータ挿入
INSERT INTO users (name, email, department_id, position) VALUES
-- 技術部
('田中 太郎', 'tanaka@example.com', 1, '部長'),
('佐藤 花子', 'sato@example.com', 6, '課長'),
('鈴木 一郎', 'suzuki@example.com', 6, 'シニアエンジニア'),
('高橋 美咲', 'takahashi@example.com', 6, 'エンジニア'),
('伊藤 健太', 'ito@example.com', 7, '課長'),
('渡辺 由美', 'watanabe@example.com', 7, 'インフラエンジニア'),
('山田 拓也', 'yamada@example.com', 8, '課長'),
('中村 恵子', 'nakamura@example.com', 8, 'QAエンジニア'),

-- 営業部
('小林 正雄', 'kobayashi@example.com', 2, '部長'),
('加藤 真理', 'kato@example.com', 9, '課長'),
('吉田 裕司', 'yoshida@example.com', 9, '主任'),
('松本 愛', 'matsumoto@example.com', 10, '課長'),
('井上 大輔', 'inoue@example.com', 10, '営業'),

-- 管理部
('木村 博', 'kimura@example.com', 3, '部長'),
('林 麻由美', 'hayashi@example.com', 3, '経理担当'),

-- ビジネスソリューションズ
('清水 達也', 'shimizu@example.com', 4, '部長'),
('森田 亜紀', 'morita@example.com', 4, 'シニアコンサルタント'),
('斎藤 雄介', 'saito@example.com', 4, 'コンサルタント'),
('岡田 優子', 'okada@example.com', 5, '部長'),
('石川 慎一', 'ishikawa@example.com', 5, 'マーケティングスペシャリスト');