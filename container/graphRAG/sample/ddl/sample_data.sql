-- ECサイト用サンプルデータ

-- カテゴリデータ
INSERT INTO categories (category_name, description) VALUES
('Electronics', '電子機器・家電製品'),
('Books', '書籍・雑誌'),
('Clothing', '衣類・アパレル'),
('Home & Garden', '家庭・園芸用品'),
('Sports', 'スポーツ・アウトドア');

INSERT INTO categories (category_name, description, parent_category_id) VALUES
('Smartphones', 'スマートフォン・携帯電話', 1),
('Laptops', 'ノートパソコン', 1),
('Fiction', '小説・文学', 2),
('Technical', '技術書・専門書', 2),
('Men Clothing', '紳士服', 3),
('Women Clothing', '婦人服', 3);

-- ユーザーデータ
INSERT INTO users (username, email, password_hash, first_name, last_name, phone) VALUES
('john_doe', 'john@example.com', 'hashed_password_1', 'John', 'Doe', '090-1234-5678'),
('jane_smith', 'jane@example.com', 'hashed_password_2', 'Jane', 'Smith', '090-2345-6789'),
('bob_wilson', 'bob@example.com', 'hashed_password_3', 'Bob', 'Wilson', '090-3456-7890'),
('alice_brown', 'alice@example.com', 'hashed_password_4', 'Alice', 'Brown', '090-4567-8901'),
('charlie_davis', 'charlie@example.com', 'hashed_password_5', 'Charlie', 'Davis', '090-5678-9012');

-- 商品データ
INSERT INTO products (product_name, description, price, stock_quantity, category_id, sku, weight) VALUES
('iPhone 15 Pro', 'Apple iPhone 15 Pro 128GB', 149800.00, 50, 6, 'IPH15PRO128', 0.187),
('MacBook Air M2', 'Apple MacBook Air 13インチ M2チップ', 134800.00, 25, 7, 'MBA13M2256', 1.24),
('Samsung Galaxy S24', 'Samsung Galaxy S24 256GB', 119800.00, 35, 6, 'SGS24256', 0.167),
('プログラミング入門', 'C言語プログラミング入門書', 2980.00, 100, 9, 'BOOK_C_001', 0.4),
('メンズTシャツ', '綿100%半袖Tシャツ', 1980.00, 200, 10, 'MENS_TEE_001', 0.2),
('レディースワンピース', '花柄ワンピース', 5980.00, 75, 11, 'WOMEN_DRESS_001', 0.3),
('Bluetooth ヘッドフォン', 'ワイヤレスノイズキャンセリングヘッドフォン', 15800.00, 60, 1, 'BT_HEAD_001', 0.25),
('Java完全ガイド', 'Java言語完全リファレンス', 4580.00, 80, 9, 'BOOK_JAVA_001', 0.6);

-- 住所データ
INSERT INTO addresses (user_id, address_type, first_name, last_name, address_line1, city, state_province, postal_code, country, is_default) VALUES
(1, 'shipping', 'John', 'Doe', '1-2-3 Shibuya', 'Tokyo', 'Tokyo', '150-0002', 'Japan', TRUE),
(1, 'billing', 'John', 'Doe', '1-2-3 Shibuya', 'Tokyo', 'Tokyo', '150-0002', 'Japan', TRUE),
(2, 'shipping', 'Jane', 'Smith', '4-5-6 Shinjuku', 'Tokyo', 'Tokyo', '160-0022', 'Japan', TRUE),
(3, 'shipping', 'Bob', 'Wilson', '7-8-9 Harajuku', 'Tokyo', 'Tokyo', '150-0001', 'Japan', TRUE),
(4, 'shipping', 'Alice', 'Brown', '10-11-12 Ginza', 'Tokyo', 'Tokyo', '104-0061', 'Japan', TRUE);

-- 注文データ
INSERT INTO orders (user_id, status, total_amount, shipping_address_id, billing_address_id, payment_method, shipping_cost, tax_amount) VALUES
(1, 'delivered', 152780.00, 1, 2, 'credit_card', 500.00, 2480.00),
(2, 'shipped', 20560.00, 3, 3, 'credit_card', 800.00, 1780.00),
(3, 'processing', 7960.00, 4, 4, 'paypal', 300.00, 680.00),
(1, 'pending', 4580.00, 1, 2, 'credit_card', 250.00, 330.00);

-- 注文詳細データ
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
(1, 1, 1, 149800.00, 149800.00),
(2, 4, 2, 2980.00, 5960.00),
(2, 7, 1, 15800.00, 15800.00),
(3, 5, 3, 1980.00, 5940.00),
(3, 6, 1, 5980.00, 5980.00),
(4, 8, 1, 4580.00, 4580.00);

-- カートデータ
INSERT INTO cart_items (user_id, product_id, quantity) VALUES
(2, 2, 1),
(3, 3, 1),
(4, 5, 2),
(4, 4, 1),
(1, 7, 1);

-- レビューデータ
INSERT INTO reviews (product_id, user_id, rating, title, comment, is_verified) VALUES
(1, 1, 5, '素晴らしい製品', 'iPhone 15 Proは期待通りの性能でした。カメラの画質が特に良い。', TRUE),
(4, 2, 4, '初心者に最適', 'C言語の入門書として分かりやすく書かれています。', TRUE),
(7, 2, 5, '音質最高', 'ノイズキャンセリング機能が優秀で、音質も非常に良いです。', TRUE),
(5, 3, 3, '普通のTシャツ', '値段相応の品質です。可もなく不可もなく。', TRUE),
(1, 4, 4, 'コスパ良し', '高価ですが、それに見合う価値があると思います。', FALSE);