-- インデックス作成
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_name ON products(product_name);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_cart_items_user ON cart_items(user_id);
CREATE INDEX idx_cart_items_product ON cart_items(product_id);
CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_reviews_user ON reviews(user_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_addresses_user ON addresses(user_id);
CREATE INDEX idx_addresses_type ON addresses(address_type);
CREATE INDEX idx_categories_parent ON categories(parent_category_id);

-- インデックスコメント
COMMENT ON INDEX idx_products_category IS '商品カテゴリ検索用インデックス';
COMMENT ON INDEX idx_products_sku IS '商品SKU検索用インデックス';
COMMENT ON INDEX idx_products_name IS '商品名検索用インデックス';
COMMENT ON INDEX idx_orders_user IS 'ユーザー別注文検索用インデックス';
COMMENT ON INDEX idx_orders_date IS '注文日順検索用インデックス';
COMMENT ON INDEX idx_orders_status IS '注文状態検索用インデックス';
COMMENT ON INDEX idx_order_items_order IS '注文別明細検索用インデックス';
COMMENT ON INDEX idx_order_items_product IS '商品別注文履歴検索用インデックス';
COMMENT ON INDEX idx_cart_items_user IS 'ユーザー別カート検索用インデックス';
COMMENT ON INDEX idx_cart_items_product IS '商品別カート入り検索用インデックス';
COMMENT ON INDEX idx_reviews_product IS '商品別レビュー検索用インデックス';
COMMENT ON INDEX idx_reviews_user IS 'ユーザー別レビュー検索用インデックス';
COMMENT ON INDEX idx_reviews_rating IS '評価別レビュー検索用インデックス';
COMMENT ON INDEX idx_addresses_user IS 'ユーザー別住所検索用インデックス';
COMMENT ON INDEX idx_addresses_type IS '住所タイプ別検索用インデックス';
COMMENT ON INDEX idx_categories_parent IS '親カテゴリ検索用インデックス';