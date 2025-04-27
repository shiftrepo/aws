-- サンプルSQLクエリ集
-- このファイルには、J-PlatPatデータベースに対する様々なSQLクエリの例が含まれています。

-- 基本クエリ: 特許一覧の取得
SELECT * FROM patents LIMIT 10;

-- 特許とその出願者を結合して取得
SELECT p.application_number, p.title, a.name as applicant_name 
FROM patents p 
JOIN applicants a ON p.id = a.patent_id 
LIMIT 10;

-- 発明者ごとの特許数をカウント
SELECT i.name, COUNT(*) as patent_count 
FROM inventors i 
JOIN patents p ON i.patent_id = p.id 
GROUP BY i.name 
ORDER BY patent_count DESC 
LIMIT 10;

-- IPCコード別の特許数
SELECT ic.code, COUNT(*) as patent_count 
FROM ipc_classifications ic 
GROUP BY ic.code 
ORDER BY patent_count DESC 
LIMIT 10;

-- 年別の特許出願数
SELECT strftime('%Y', application_date) as year, COUNT(*) as application_count 
FROM patents 
WHERE application_date IS NOT NULL 
GROUP BY year 
ORDER BY year DESC;

-- 特定の企業の特許取得
SELECT p.application_number, p.title, p.application_date 
FROM patents p 
JOIN applicants a ON p.id = a.patent_id 
WHERE a.name LIKE '%トヨタ%' 
LIMIT 10;

-- 特定のキーワードを含む特許
SELECT p.application_number, p.title 
FROM patents p 
WHERE p.title LIKE '%人工知能%' OR p.abstract LIKE '%人工知能%' 
LIMIT 10;
