#ifndef PRODUCT_OPERATIONS_H
#define PRODUCT_OPERATIONS_H

#include "database.h"

int create_product(MYSQL* conn, const Product* product);
Product* get_product_by_id(MYSQL* conn, int product_id);
Product* get_product_by_sku(MYSQL* conn, const char* sku);
bool update_product(MYSQL* conn, const Product* product);
bool delete_product(MYSQL* conn, int product_id);
Product** get_all_products(MYSQL* conn, int* count);
Product** get_products_by_category(MYSQL* conn, int category_id, int* count);
Product** search_products_by_name(MYSQL* conn, const char* search_term, int* count);
bool update_product_stock(MYSQL* conn, int product_id, int new_stock);
Product** get_products_by_price_range(MYSQL* conn, double min_price, double max_price, int* count);
void free_product(Product* product);
void free_product_array(Product** products, int count);

#endif