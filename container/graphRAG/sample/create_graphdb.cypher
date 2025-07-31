// ============================================
// E-Commerce Application GraphDB Creation Script
// ============================================

// Clear existing data
MATCH (n) DETACH DELETE n;

// ============================================
// 1. Create Constraints and Indexes
// ============================================

// Unique constraints
CREATE CONSTRAINT app_name_unique FOR (a:Application) REQUIRE a.name IS UNIQUE;
CREATE CONSTRAINT table_name_unique FOR (t:Table) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT crud_id_unique FOR (c:CRUDOperation) REQUIRE c.function_name IS UNIQUE;

// Performance indexes
CREATE INDEX crud_operation_type FOR (c:CRUDOperation) ON (c.operation_type);
CREATE INDEX table_type FOR (t:Table) ON (t.table_type);
CREATE INDEX app_language FOR (a:Application) ON (a.language);

// ============================================
// 2. Create Application Nodes
// ============================================

CREATE (:Application {
  name: 'E-Commerce System',
  type: 'web_application',
  language: 'C',
  framework: 'MySQL/C',
  version: '1.0',
  created_date: datetime(),
  last_updated: datetime(),
  business_criticality: 'high'
});

CREATE (:Application {
  name: 'user_operations',
  type: 'module',
  language: 'C',
  framework: 'MySQL/C',
  version: '1.0',
  created_date: datetime(),
  last_updated: datetime(),
  business_criticality: 'high'
});

CREATE (:Application {
  name: 'product_operations',
  type: 'module',
  language: 'C',
  framework: 'MySQL/C',
  version: '1.0',
  created_date: datetime(),
  last_updated: datetime(),
  business_criticality: 'high'
});

CREATE (:Application {
  name: 'cart_operations',
  type: 'module',
  language: 'C',
  framework: 'MySQL/C',
  version: '1.0',
  created_date: datetime(),
  last_updated: datetime(),
  business_criticality: 'medium'
});

CREATE (:Application {
  name: 'order_operations',
  type: 'module',
  language: 'C',
  framework: 'MySQL/C',
  version: '1.0',
  created_date: datetime(),
  last_updated: datetime(),
  business_criticality: 'high'
});

// ============================================
// 3. Create Table Nodes
// ============================================

CREATE (:Table {
  name: 'users',
  schema: 'ec_site',
  table_type: 'master',
  created_date: datetime(),
  business_criticality: 'high',
  estimated_records: 10000,
  primary_key: 'user_id',
  description: 'User account information'
});

CREATE (:Table {
  name: 'categories',
  schema: 'ec_site',
  table_type: 'reference',
  created_date: datetime(),
  business_criticality: 'medium',
  estimated_records: 100,
  primary_key: 'category_id',
  description: 'Product categories (hierarchical)'
});

CREATE (:Table {
  name: 'products',
  schema: 'ec_site',
  table_type: 'master',
  created_date: datetime(),
  business_criticality: 'high',
  estimated_records: 50000,
  primary_key: 'product_id',
  description: 'Product catalog'
});

CREATE (:Table {
  name: 'addresses',
  schema: 'ec_site',
  table_type: 'detail',
  created_date: datetime(),
  business_criticality: 'medium',
  estimated_records: 25000,
  primary_key: 'address_id',
  description: 'User shipping/billing addresses'
});

CREATE (:Table {
  name: 'orders',
  schema: 'ec_site',
  table_type: 'transaction',
  created_date: datetime(),
  business_criticality: 'high',
  estimated_records: 100000,
  primary_key: 'order_id',
  description: 'Order transactions'
});

CREATE (:Table {
  name: 'order_items',
  schema: 'ec_site',
  table_type: 'detail',
  created_date: datetime(),
  business_criticality: 'high',
  estimated_records: 500000,
  primary_key: 'order_item_id',
  description: 'Order line items'
});

CREATE (:Table {
  name: 'cart_items',
  schema: 'ec_site',
  table_type: 'temporary',
  created_date: datetime(),
  business_criticality: 'medium',
  estimated_records: 50000,
  primary_key: 'cart_item_id',
  description: 'Shopping cart contents'
});

CREATE (:Table {
  name: 'reviews',
  schema: 'ec_site',
  table_type: 'detail',
  created_date: datetime(),
  business_criticality: 'low',
  estimated_records: 75000,
  primary_key: 'review_id',
  description: 'Product reviews'
});

// ============================================
// 4. Create Column Nodes
// ============================================

// Users table columns
CREATE (:Column {name: 'user_id', table_name: 'users', data_type: 'NUMBER', is_primary_key: true, is_foreign_key: false, is_nullable: false, is_identity: true});
CREATE (:Column {name: 'username', table_name: 'users', data_type: 'VARCHAR2', is_primary_key: false, is_foreign_key: false, is_nullable: false, max_length: 50, has_unique_constraint: true});
CREATE (:Column {name: 'email', table_name: 'users', data_type: 'VARCHAR2', is_primary_key: false, is_foreign_key: false, is_nullable: false, max_length: 100, has_unique_constraint: true});
CREATE (:Column {name: 'password_hash', table_name: 'users', data_type: 'VARCHAR2', is_primary_key: false, is_foreign_key: false, is_nullable: false, max_length: 255});
CREATE (:Column {name: 'first_name', table_name: 'users', data_type: 'VARCHAR2', is_primary_key: false, is_foreign_key: false, is_nullable: true, max_length: 50});
CREATE (:Column {name: 'last_name', table_name: 'users', data_type: 'VARCHAR2', is_primary_key: false, is_foreign_key: false, is_nullable: true, max_length: 50});
CREATE (:Column {name: 'phone', table_name: 'users', data_type: 'VARCHAR2', is_primary_key: false, is_foreign_key: false, is_nullable: true, max_length: 20});
CREATE (:Column {name: 'created_at', table_name: 'users', data_type: 'DATE', is_primary_key: false, is_foreign_key: false, is_nullable: false, default_value: 'SYSDATE'});
CREATE (:Column {name: 'updated_at', table_name: 'users', data_type: 'DATE', is_primary_key: false, is_foreign_key: false, is_nullable: false, default_value: 'SYSDATE'});
CREATE (:Column {name: 'is_active', table_name: 'users', data_type: 'NUMBER', is_primary_key: false, is_foreign_key: false, is_nullable: false, default_value: '1'});

// Categories table columns
CREATE (:Column {name: 'category_id', table_name: 'categories', data_type: 'NUMBER', is_primary_key: true, is_foreign_key: false, is_nullable: false, is_identity: true});
CREATE (:Column {name: 'category_name', table_name: 'categories', data_type: 'VARCHAR2', is_primary_key: false, is_foreign_key: false, is_nullable: false, max_length: 100});
CREATE (:Column {name: 'description', table_name: 'categories', data_type: 'CLOB', is_primary_key: false, is_foreign_key: false, is_nullable: true});
CREATE (:Column {name: 'parent_category_id', table_name: 'categories', data_type: 'NUMBER', is_primary_key: false, is_foreign_key: true, is_nullable: true});
CREATE (:Column {name: 'created_at', table_name: 'categories', data_type: 'DATE', is_primary_key: false, is_foreign_key: false, is_nullable: false, default_value: 'SYSDATE'});

// Products table columns
CREATE (:Column {name: 'product_id', table_name: 'products', data_type: 'NUMBER', is_primary_key: true, is_foreign_key: false, is_nullable: false, is_identity: true});
CREATE (:Column {name: 'product_name', table_name: 'products', data_type: 'VARCHAR2', is_primary_key: false, is_foreign_key: false, is_nullable: false, max_length: 200});
CREATE (:Column {name: 'description', table_name: 'products', data_type: 'CLOB', is_primary_key: false, is_foreign_key: false, is_nullable: true});
CREATE (:Column {name: 'price', table_name: 'products', data_type: 'NUMBER', is_primary_key: false, is_foreign_key: false, is_nullable: false, precision: 10, scale: 2});
CREATE (:Column {name: 'stock_quantity', table_name: 'products', data_type: 'NUMBER', is_primary_key: false, is_foreign_key: false, is_nullable: false, default_value: '0'});
CREATE (:Column {name: 'category_id', table_name: 'products', data_type: 'NUMBER', is_primary_key: false, is_foreign_key: true, is_nullable: true});
CREATE (:Column {name: 'sku', table_name: 'products', data_type: 'VARCHAR2', is_primary_key: false, is_foreign_key: false, is_nullable: true, max_length: 50, has_unique_constraint: true});
CREATE (:Column {name: 'weight', table_name: 'products', data_type: 'NUMBER', is_primary_key: false, is_foreign_key: false, is_nullable: true, precision: 8, scale: 2});
CREATE (:Column {name: 'dimensions', table_name: 'products', data_type: 'VARCHAR2', is_primary_key: false, is_foreign_key: false, is_nullable: true, max_length: 100});
CREATE (:Column {name: 'created_at', table_name: 'products', data_type: 'DATE', is_primary_key: false, is_foreign_key: false, is_nullable: false, default_value: 'SYSDATE'});
CREATE (:Column {name: 'updated_at', table_name: 'products', data_type: 'DATE', is_primary_key: false, is_foreign_key: false, is_nullable: false, default_value: 'SYSDATE'});
CREATE (:Column {name: 'is_active', table_name: 'products', data_type: 'NUMBER', is_primary_key: false, is_foreign_key: false, is_nullable: false, default_value: '1'});

// Continue with other tables...
// (Similar column definitions for addresses, orders, order_items, cart_items, reviews)

// ============================================
// 5. Create CRUD Operation Nodes
// ============================================

// User Operations
CREATE (:CRUDOperation {
  function_name: 'create_user',
  operation_type: 'CREATE',
  module_name: 'user_operations',
  file_path: 'sample/src/user_operations.c',
  line_number: 6,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'users'
});

CREATE (:CRUDOperation {
  function_name: 'get_user_by_id',
  operation_type: 'READ',
  module_name: 'user_operations',
  file_path: 'sample/src/user_operations.c',
  line_number: 21,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'users'
});

CREATE (:CRUDOperation {
  function_name: 'get_user_by_username',
  operation_type: 'READ',
  module_name: 'user_operations',
  file_path: 'sample/src/user_operations.c',
  line_number: 57,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'users'
});

CREATE (:CRUDOperation {
  function_name: 'get_user_by_email',
  operation_type: 'READ',
  module_name: 'user_operations',
  file_path: 'sample/src/user_operations.c',
  line_number: 93,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'users'
});

CREATE (:CRUDOperation {
  function_name: 'update_user',
  operation_type: 'UPDATE',
  module_name: 'user_operations',
  file_path: 'sample/src/user_operations.c',
  line_number: 129,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'users'
});

CREATE (:CRUDOperation {
  function_name: 'delete_user',
  operation_type: 'DELETE',
  module_name: 'user_operations',
  file_path: 'sample/src/user_operations.c',
  line_number: 142,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'users',
  cascade_impact: 'high'
});

CREATE (:CRUDOperation {
  function_name: 'get_all_users',
  operation_type: 'READ',
  module_name: 'user_operations',
  file_path: 'sample/src/user_operations.c',
  line_number: 149,
  complexity: 'batch',
  transaction_scope: false,
  performance_category: 'slow',
  error_handling: true,
  target_table: 'users',
  risk_level: 'high'
});

CREATE (:CRUDOperation {
  function_name: 'verify_user_credentials',
  operation_type: 'READ',
  module_name: 'user_operations',
  file_path: 'sample/src/user_operations.c',
  line_number: 205,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'users',
  security_sensitive: true
});

// Product Operations
CREATE (:CRUDOperation {
  function_name: 'create_product',
  operation_type: 'CREATE',
  module_name: 'product_operations',
  file_path: 'sample/src/product_operations.c',
  line_number: 6,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'products'
});

CREATE (:CRUDOperation {
  function_name: 'get_product_by_id',
  operation_type: 'READ',
  module_name: 'product_operations',
  file_path: 'sample/src/product_operations.c',
  line_number: 21,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'products'
});

CREATE (:CRUDOperation {
  function_name: 'get_product_by_sku',
  operation_type: 'READ',
  module_name: 'product_operations',
  file_path: 'sample/src/product_operations.c',
  line_number: 59,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'products'
});

CREATE (:CRUDOperation {
  function_name: 'update_product',
  operation_type: 'UPDATE',
  module_name: 'product_operations',
  file_path: 'sample/src/product_operations.c',
  line_number: 97,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'products'
});

CREATE (:CRUDOperation {
  function_name: 'delete_product',
  operation_type: 'DELETE',
  module_name: 'product_operations',
  file_path: 'sample/src/product_operations.c',
  line_number: 110,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'products',
  cascade_impact: 'medium'
});

CREATE (:CRUDOperation {
  function_name: 'get_all_products',
  operation_type: 'READ',
  module_name: 'product_operations',
  file_path: 'sample/src/product_operations.c',
  line_number: 117,
  complexity: 'batch',
  transaction_scope: false,
  performance_category: 'slow',
  error_handling: true,
  target_table: 'products',
  risk_level: 'high'
});

CREATE (:CRUDOperation {
  function_name: 'get_products_by_category',
  operation_type: 'READ',
  module_name: 'product_operations',
  file_path: 'sample/src/product_operations.c',
  line_number: 175,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'products',
  joins_tables: ['categories']
});

CREATE (:CRUDOperation {
  function_name: 'search_products_by_name',
  operation_type: 'READ',
  module_name: 'product_operations',
  file_path: 'sample/src/product_operations.c',
  line_number: 234,
  complexity: 'complex',
  transaction_scope: false,
  performance_category: 'slow',
  error_handling: true,
  target_table: 'products',
  uses_like_query: true
});

CREATE (:CRUDOperation {
  function_name: 'update_product_stock',
  operation_type: 'UPDATE',
  module_name: 'product_operations',
  file_path: 'sample/src/product_operations.c',
  line_number: 294,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'products',
  business_critical: true
});

CREATE (:CRUDOperation {
  function_name: 'get_products_by_price_range',
  operation_type: 'READ',
  module_name: 'product_operations',
  file_path: 'sample/src/product_operations.c',
  line_number: 303,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'products'
});

// Cart Operations
CREATE (:CRUDOperation {
  function_name: 'add_to_cart',
  operation_type: 'CREATE',
  module_name: 'cart_operations',
  file_path: 'sample/src/cart_operations.c',
  line_number: 6,
  complexity: 'complex',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'cart_items',
  uses_upsert: true
});

CREATE (:CRUDOperation {
  function_name: 'get_cart_item_by_id',
  operation_type: 'READ',
  module_name: 'cart_operations',
  file_path: 'sample/src/cart_operations.c',
  line_number: 20,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'cart_items'
});

CREATE (:CRUDOperation {
  function_name: 'update_cart_item',
  operation_type: 'UPDATE',
  module_name: 'cart_operations',
  file_path: 'sample/src/cart_operations.c',
  line_number: 51,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'cart_items'
});

CREATE (:CRUDOperation {
  function_name: 'remove_from_cart',
  operation_type: 'DELETE',
  module_name: 'cart_operations',
  file_path: 'sample/src/cart_operations.c',
  line_number: 60,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'cart_items'
});

CREATE (:CRUDOperation {
  function_name: 'remove_from_cart_by_user_product',
  operation_type: 'DELETE',
  module_name: 'cart_operations',
  file_path: 'sample/src/cart_operations.c',
  line_number: 67,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'cart_items'
});

CREATE (:CRUDOperation {
  function_name: 'get_cart_items_by_user',
  operation_type: 'READ',
  module_name: 'cart_operations',
  file_path: 'sample/src/cart_operations.c',
  line_number: 74,
  complexity: 'batch',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'cart_items'
});

CREATE (:CRUDOperation {
  function_name: 'clear_cart',
  operation_type: 'DELETE',
  module_name: 'cart_operations',
  file_path: 'sample/src/cart_operations.c',
  line_number: 126,
  complexity: 'batch',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'cart_items',
  bulk_operation: true
});

CREATE (:CRUDOperation {
  function_name: 'update_cart_item_quantity',
  operation_type: 'UPDATE',
  module_name: 'cart_operations',
  file_path: 'sample/src/cart_operations.c',
  line_number: 133,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'cart_items'
});

CREATE (:CRUDOperation {
  function_name: 'calculate_cart_total',
  operation_type: 'READ',
  module_name: 'cart_operations',
  file_path: 'sample/src/cart_operations.c',
  line_number: 142,
  complexity: 'complex',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'cart_items',
  joins_tables: ['products'],
  uses_aggregation: true
});

CREATE (:CRUDOperation {
  function_name: 'get_cart_item_count',
  operation_type: 'READ',
  module_name: 'cart_operations',
  file_path: 'sample/src/cart_operations.c',
  line_number: 164,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'cart_items',
  uses_aggregation: true
});

// Order Operations
CREATE (:CRUDOperation {
  function_name: 'create_order',
  operation_type: 'CREATE',
  module_name: 'order_operations',
  file_path: 'sample/src/order_operations.c',
  line_number: 6,
  complexity: 'complex',
  transaction_scope: true,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'orders',
  business_critical: true
});

CREATE (:CRUDOperation {
  function_name: 'get_order_by_id',
  operation_type: 'READ',
  module_name: 'order_operations',
  file_path: 'sample/src/order_operations.c',
  line_number: 23,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'orders'
});

CREATE (:CRUDOperation {
  function_name: 'update_order',
  operation_type: 'UPDATE',
  module_name: 'order_operations',
  file_path: 'sample/src/order_operations.c',
  line_number: 60,
  complexity: 'complex',
  transaction_scope: true,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'orders'
});

CREATE (:CRUDOperation {
  function_name: 'delete_order',
  operation_type: 'DELETE',
  module_name: 'order_operations',
  file_path: 'sample/src/order_operations.c',
  line_number: 73,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'orders',
  cascade_impact: 'high'
});

CREATE (:CRUDOperation {
  function_name: 'get_orders_by_user',
  operation_type: 'READ',
  module_name: 'order_operations',
  file_path: 'sample/src/order_operations.c',
  line_number: 80,
  complexity: 'batch',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'orders'
});

CREATE (:CRUDOperation {
  function_name: 'get_all_orders',
  operation_type: 'READ',
  module_name: 'order_operations',
  file_path: 'sample/src/order_operations.c',
  line_number: 138,
  complexity: 'batch',
  transaction_scope: false,
  performance_category: 'slow',
  error_handling: true,
  target_table: 'orders',
  risk_level: 'high'
});

CREATE (:CRUDOperation {
  function_name: 'update_order_status',
  operation_type: 'UPDATE',
  module_name: 'order_operations',
  file_path: 'sample/src/order_operations.c',
  line_number: 195,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'orders',
  business_critical: true
});

CREATE (:CRUDOperation {
  function_name: 'get_orders_by_status',
  operation_type: 'READ',
  module_name: 'order_operations',
  file_path: 'sample/src/order_operations.c',
  line_number: 203,
  complexity: 'batch',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'orders'
});

CREATE (:CRUDOperation {
  function_name: 'create_order_item',
  operation_type: 'CREATE',
  module_name: 'order_operations',
  file_path: 'sample/src/order_operations.c',
  line_number: 261,
  complexity: 'simple',
  transaction_scope: true,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'order_items'
});

CREATE (:CRUDOperation {
  function_name: 'get_order_item_by_id',
  operation_type: 'READ',
  module_name: 'order_operations',
  file_path: 'sample/src/order_operations.c',
  line_number: 275,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'order_items'
});

CREATE (:CRUDOperation {
  function_name: 'update_order_item',
  operation_type: 'UPDATE',
  module_name: 'order_operations',
  file_path: 'sample/src/order_operations.c',
  line_number: 307,
  complexity: 'simple',
  transaction_scope: true,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'order_items'
});

CREATE (:CRUDOperation {
  function_name: 'delete_order_item',
  operation_type: 'DELETE',
  module_name: 'order_operations',
  file_path: 'sample/src/order_operations.c',
  line_number: 317,
  complexity: 'simple',
  transaction_scope: false,
  performance_category: 'fast',
  error_handling: true,
  target_table: 'order_items'
});

CREATE (:CRUDOperation {
  function_name: 'get_order_items_by_order',
  operation_type: 'READ',
  module_name: 'order_operations',
  file_path: 'sample/src/order_operations.c',
  line_number: 324,
  complexity: 'batch',
  transaction_scope: false,
  performance_category: 'normal',
  error_handling: true,
  target_table: 'order_items'
});

// ============================================
// 6. Create Relationships
// ============================================

// Application-Module relationships
MATCH (app:Application {name: 'E-Commerce System'}), (module:Application)
WHERE module.type = 'module'
CREATE (app)-[:CONTAINS {
  relationship_type: 'composition',
  dependency_level: 'critical'
}]->(module);

// Module-CRUD relationships (IMPLEMENTS)
MATCH (app:Application {name: 'user_operations'}), (crud:CRUDOperation)
WHERE crud.module_name = 'user_operations'
CREATE (app)-[:IMPLEMENTS {
  implementation_date: datetime(),
  code_quality: 'good',
  test_coverage: 0.75,
  maintenance_frequency: 'medium'
}]->(crud);

MATCH (app:Application {name: 'product_operations'}), (crud:CRUDOperation)
WHERE crud.module_name = 'product_operations'
CREATE (app)-[:IMPLEMENTS {
  implementation_date: datetime(),
  code_quality: 'good',
  test_coverage: 0.80,
  maintenance_frequency: 'medium'
}]->(crud);

MATCH (app:Application {name: 'cart_operations'}), (crud:CRUDOperation)
WHERE crud.module_name = 'cart_operations'
CREATE (app)-[:IMPLEMENTS {
  implementation_date: datetime(),
  code_quality: 'good',
  test_coverage: 0.70,
  maintenance_frequency: 'low'
}]->(crud);

MATCH (app:Application {name: 'order_operations'}), (crud:CRUDOperation)
WHERE crud.module_name = 'order_operations'
CREATE (app)-[:IMPLEMENTS {
  implementation_date: datetime(),
  code_quality: 'excellent',
  test_coverage: 0.85,
  maintenance_frequency: 'high'
}]->(crud);

// CRUD-Table relationships (TARGETS)
MATCH (crud:CRUDOperation), (table:Table)
WHERE crud.target_table = table.name
CREATE (crud)-[:TARGETS {
  affected_rows: CASE crud.complexity
    WHEN 'batch' THEN 'multiple'
    ELSE 'single'
  END,
  performance_impact: CASE crud.performance_category
    WHEN 'slow' THEN 'high'
    WHEN 'normal' THEN 'medium'
    ELSE 'low'
  END,
  data_volume: CASE crud.operation_type
    WHEN 'READ' THEN 'variable'
    ELSE 'small'
  END,
  concurrent_access: crud.operation_type IN ['READ'],
  transaction_required: CASE 
    WHEN crud.transaction_scope IS NOT NULL THEN crud.transaction_scope
    ELSE false
  END
}];

// Table-Column relationships (CONTAINS)
MATCH (table:Table), (column:Column)
WHERE table.name = column.table_name
CREATE (table)-[:CONTAINS {
  ordinal_position: 1, // Would be actual position in real implementation
  is_indexed: CASE 
    WHEN column.is_primary_key OR column.is_foreign_key OR column.has_unique_constraint THEN true
    ELSE false
  END,
  constraint_type: CASE 
    WHEN column.is_primary_key THEN 'primary'
    WHEN column.is_foreign_key THEN 'foreign'
    WHEN column.has_unique_constraint THEN 'unique'
    ELSE 'none'
  END
}]->(column);

// Inter-table references (Foreign Keys)
MATCH (t1:Table {name: 'categories'}), (t2:Table {name: 'categories'})
CREATE (t1)-[:REFERENCES {
  constraint_name: 'fk_categories_parent',
  cascade_type: 'RESTRICT',
  relationship_type: 'one-to-many',
  referential_integrity: true,
  business_rule: 'Category hierarchy'
}]->(t2);

MATCH (t1:Table {name: 'products'}), (t2:Table {name: 'categories'})
CREATE (t1)-[:REFERENCES {
  constraint_name: 'fk_products_category',
  cascade_type: 'RESTRICT',
  relationship_type: 'many-to-one',
  referential_integrity: true,
  business_rule: 'Product categorization'
}]->(t2);

MATCH (t1:Table {name: 'addresses'}), (t2:Table {name: 'users'})
CREATE (t1)-[:REFERENCES {
  constraint_name: 'fk_addresses_user',
  cascade_type: 'CASCADE',
  relationship_type: 'many-to-one',
  referential_integrity: true,
  business_rule: 'User addresses'
}]->(t2);

MATCH (t1:Table {name: 'orders'}), (t2:Table {name: 'users'})
CREATE (t1)-[:REFERENCES {
  constraint_name: 'fk_orders_user',
  cascade_type: 'RESTRICT',
  relationship_type: 'many-to-one',
  referential_integrity: true,
  business_rule: 'Order ownership'
}]->(t2);

MATCH (t1:Table {name: 'orders'}), (t2:Table {name: 'addresses'})
CREATE (t1)-[:REFERENCES {
  constraint_name: 'fk_orders_shipping_addr',
  cascade_type: 'RESTRICT',
  relationship_type: 'many-to-one',
  referential_integrity: true,
  business_rule: 'Shipping address'
}]->(t2);

MATCH (t1:Table {name: 'orders'}), (t2:Table {name: 'addresses'})
CREATE (t1)-[:REFERENCES_BILLING {
  constraint_name: 'fk_orders_billing_addr',
  cascade_type: 'RESTRICT',
  relationship_type: 'many-to-one',
  referential_integrity: true,
  business_rule: 'Billing address'
}]->(t2);

MATCH (t1:Table {name: 'order_items'}), (t2:Table {name: 'orders'})
CREATE (t1)-[:REFERENCES {
  constraint_name: 'fk_order_items_order',
  cascade_type: 'CASCADE',
  relationship_type: 'many-to-one',
  referential_integrity: true,
  business_rule: 'Order line items'
}]->(t2);

MATCH (t1:Table {name: 'order_items'}), (t2:Table {name: 'products'})
CREATE (t1)-[:REFERENCES {
  constraint_name: 'fk_order_items_product',
  cascade_type: 'RESTRICT',
  relationship_type: 'many-to-one',
  referential_integrity: true,
  business_rule: 'Product ordering'
}]->(t2);

MATCH (t1:Table {name: 'cart_items'}), (t2:Table {name: 'users'})
CREATE (t1)-[:REFERENCES {
  constraint_name: 'fk_cart_items_user',
  cascade_type: 'CASCADE',
  relationship_type: 'many-to-one',
  referential_integrity: true,
  business_rule: 'User cart'
}]->(t2);

MATCH (t1:Table {name: 'cart_items'}), (t2:Table {name: 'products'})
CREATE (t1)-[:REFERENCES {
  constraint_name: 'fk_cart_items_product',
  cascade_type: 'CASCADE',
  relationship_type: 'many-to-one',
  referential_integrity: true,
  business_rule: 'Cart contents'
}]->(t2);

MATCH (t1:Table {name: 'reviews'}), (t2:Table {name: 'products'})
CREATE (t1)-[:REFERENCES {
  constraint_name: 'fk_reviews_product',
  cascade_type: 'CASCADE',
  relationship_type: 'many-to-one',
  referential_integrity: true,
  business_rule: 'Product reviews'
}]->(t2);

MATCH (t1:Table {name: 'reviews'}), (t2:Table {name: 'users'})
CREATE (t1)-[:REFERENCES {
  constraint_name: 'fk_reviews_user',
  cascade_type: 'CASCADE',
  relationship_type: 'many-to-one',
  referential_integrity: true,
  business_rule: 'User reviews'
}]->(t2);

// Application usage patterns (USES)
MATCH (app:Application {name: 'user_operations'}), (table:Table {name: 'users'})
CREATE (app)-[:USES {
  frequency: 'high',
  access_pattern: 'balanced',
  last_accessed: datetime(),
  dependency_level: 'critical'
}]->(table);

MATCH (app:Application {name: 'product_operations'}), (table:Table {name: 'products'})
CREATE (app)-[:USES {
  frequency: 'high',
  access_pattern: 'read-heavy',
  last_accessed: datetime(),
  dependency_level: 'critical'
}]->(table);

MATCH (app:Application {name: 'product_operations'}), (table:Table {name: 'categories'})
CREATE (app)-[:USES {
  frequency: 'medium',
  access_pattern: 'read-heavy',
  last_accessed: datetime(),
  dependency_level: 'important'
}]->(table);

MATCH (app:Application {name: 'cart_operations'}), (table:Table {name: 'cart_items'})
CREATE (app)-[:USES {
  frequency: 'high',
  access_pattern: 'write-heavy',
  last_accessed: datetime(),
  dependency_level: 'critical'
}]->(table);

MATCH (app:Application {name: 'cart_operations'}), (table:Table {name: 'products'})
CREATE (app)-[:USES {
  frequency: 'medium',
  access_pattern: 'read-heavy',
  last_accessed: datetime(),
  dependency_level: 'important'
}]->(table);

MATCH (app:Application {name: 'order_operations'}), (table:Table {name: 'orders'})
CREATE (app)-[:USES {
  frequency: 'high',
  access_pattern: 'balanced',
  last_accessed: datetime(),
  dependency_level: 'critical'
}]->(table);

MATCH (app:Application {name: 'order_operations'}), (table:Table {name: 'order_items'})
CREATE (app)-[:USES {
  frequency: 'high',
  access_pattern: 'balanced',
  last_accessed: datetime(),
  dependency_level: 'critical'
}]->(table);

// ============================================
// 7. Create Additional Metadata
// ============================================

// Add complexity scores to operations
MATCH (crud:CRUDOperation)
SET crud.complexity_score = CASE crud.complexity
  WHEN 'simple' THEN 1
  WHEN 'complex' THEN 3
  WHEN 'batch' THEN 5
  ELSE 2
END;

// Add risk scores
MATCH (crud:CRUDOperation)
SET crud.risk_score = CASE 
  WHEN crud.operation_type = 'DELETE' AND crud.cascade_impact IS NOT NULL THEN 5
  WHEN crud.bulk_operation = true THEN 4
  WHEN crud.performance_category = 'slow' THEN 3
  WHEN crud.uses_like_query = true THEN 2
  ELSE 1
END;

// Add testing priorities
MATCH (crud:CRUDOperation)
SET crud.testing_priority = CASE 
  WHEN crud.business_critical = true OR crud.security_sensitive = true THEN 'critical'
  WHEN crud.risk_score >= 4 THEN 'high'
  WHEN crud.risk_score >= 2 THEN 'medium'
  ELSE 'low'
END;