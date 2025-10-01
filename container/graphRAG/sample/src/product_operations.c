#include "product_operations.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int create_product(MYSQL* conn, const Product* product) {
    char query[2048];
    snprintf(query, sizeof(query),
        "INSERT INTO products (product_name, description, price, stock_quantity, category_id, sku, weight, dimensions, is_active) "
        "VALUES ('%s', '%s', %.2f, %d, %d, '%s', %.2f, '%s', %d)",
        product->product_name, product->description, product->price, product->stock_quantity,
        product->category_id, product->sku, product->weight, product->dimensions, product->is_active);
    
    if (!execute_query(conn, query)) {
        return -1;
    }
    
    return (int)mysql_insert_id(conn);
}

Product* get_product_by_id(MYSQL* conn, int product_id) {
    char query[256];
    snprintf(query, sizeof(query), "SELECT * FROM products WHERE product_id = %d", product_id);
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        return NULL;
    }
    
    MYSQL_ROW row = mysql_fetch_row(result);
    if (row == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    Product* product = malloc(sizeof(Product));
    if (product == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    product->product_id = atoi(row[0]);
    strncpy(product->product_name, row[1] ? row[1] : "", sizeof(product->product_name) - 1);
    strncpy(product->description, row[2] ? row[2] : "", sizeof(product->description) - 1);
    product->price = row[3] ? atof(row[3]) : 0.0;
    product->stock_quantity = row[4] ? atoi(row[4]) : 0;
    product->category_id = row[5] ? atoi(row[5]) : 0;
    strncpy(product->sku, row[6] ? row[6] : "", sizeof(product->sku) - 1);
    product->weight = row[7] ? atof(row[7]) : 0.0;
    strncpy(product->dimensions, row[8] ? row[8] : "", sizeof(product->dimensions) - 1);
    strncpy(product->created_at, row[9] ? row[9] : "", sizeof(product->created_at) - 1);
    strncpy(product->updated_at, row[10] ? row[10] : "", sizeof(product->updated_at) - 1);
    product->is_active = (row[11] && atoi(row[11]) == 1);
    
    mysql_free_result(result);
    return product;
}

Product* get_product_by_sku(MYSQL* conn, const char* sku) {
    char query[256];
    snprintf(query, sizeof(query), "SELECT * FROM products WHERE sku = '%s'", sku);
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        return NULL;
    }
    
    MYSQL_ROW row = mysql_fetch_row(result);
    if (row == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    Product* product = malloc(sizeof(Product));
    if (product == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    product->product_id = atoi(row[0]);
    strncpy(product->product_name, row[1] ? row[1] : "", sizeof(product->product_name) - 1);
    strncpy(product->description, row[2] ? row[2] : "", sizeof(product->description) - 1);
    product->price = row[3] ? atof(row[3]) : 0.0;
    product->stock_quantity = row[4] ? atoi(row[4]) : 0;
    product->category_id = row[5] ? atoi(row[5]) : 0;
    strncpy(product->sku, row[6] ? row[6] : "", sizeof(product->sku) - 1);
    product->weight = row[7] ? atof(row[7]) : 0.0;
    strncpy(product->dimensions, row[8] ? row[8] : "", sizeof(product->dimensions) - 1);
    strncpy(product->created_at, row[9] ? row[9] : "", sizeof(product->created_at) - 1);
    strncpy(product->updated_at, row[10] ? row[10] : "", sizeof(product->updated_at) - 1);
    product->is_active = (row[11] && atoi(row[11]) == 1);
    
    mysql_free_result(result);
    return product;
}

bool update_product(MYSQL* conn, const Product* product) {
    char query[2048];
    snprintf(query, sizeof(query),
        "UPDATE products SET product_name='%s', description='%s', price=%.2f, stock_quantity=%d, "
        "category_id=%d, sku='%s', weight=%.2f, dimensions='%s', is_active=%d "
        "WHERE product_id=%d",
        product->product_name, product->description, product->price, product->stock_quantity,
        product->category_id, product->sku, product->weight, product->dimensions,
        product->is_active, product->product_id);
    
    return execute_query(conn, query);
}

bool delete_product(MYSQL* conn, int product_id) {
    char query[256];
    snprintf(query, sizeof(query), "DELETE FROM products WHERE product_id = %d", product_id);
    
    return execute_query(conn, query);
}

Product** get_all_products(MYSQL* conn, int* count) {
    const char* query = "SELECT * FROM products ORDER BY product_id";
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        *count = 0;
        return NULL;
    }
    
    int num_rows = (int)mysql_num_rows(result);
    if (num_rows == 0) {
        mysql_free_result(result);
        *count = 0;
        return NULL;
    }
    
    Product** products = malloc(num_rows * sizeof(Product*));
    if (products == NULL) {
        mysql_free_result(result);
        *count = 0;
        return NULL;
    }
    
    int i = 0;
    MYSQL_ROW row;
    while ((row = mysql_fetch_row(result)) != NULL) {
        products[i] = malloc(sizeof(Product));
        if (products[i] == NULL) {
            for (int j = 0; j < i; j++) {
                free(products[j]);
            }
            free(products);
            mysql_free_result(result);
            *count = 0;
            return NULL;
        }
        
        products[i]->product_id = atoi(row[0]);
        strncpy(products[i]->product_name, row[1] ? row[1] : "", sizeof(products[i]->product_name) - 1);
        strncpy(products[i]->description, row[2] ? row[2] : "", sizeof(products[i]->description) - 1);
        products[i]->price = row[3] ? atof(row[3]) : 0.0;
        products[i]->stock_quantity = row[4] ? atoi(row[4]) : 0;
        products[i]->category_id = row[5] ? atoi(row[5]) : 0;
        strncpy(products[i]->sku, row[6] ? row[6] : "", sizeof(products[i]->sku) - 1);
        products[i]->weight = row[7] ? atof(row[7]) : 0.0;
        strncpy(products[i]->dimensions, row[8] ? row[8] : "", sizeof(products[i]->dimensions) - 1);
        strncpy(products[i]->created_at, row[9] ? row[9] : "", sizeof(products[i]->created_at) - 1);
        strncpy(products[i]->updated_at, row[10] ? row[10] : "", sizeof(products[i]->updated_at) - 1);
        products[i]->is_active = (row[11] && atoi(row[11]) == 1);
        
        i++;
    }
    
    mysql_free_result(result);
    *count = num_rows;
    return products;
}

Product** get_products_by_category(MYSQL* conn, int category_id, int* count) {
    char query[256];
    snprintf(query, sizeof(query), "SELECT * FROM products WHERE category_id = %d ORDER BY product_id", category_id);
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        *count = 0;
        return NULL;
    }
    
    int num_rows = (int)mysql_num_rows(result);
    if (num_rows == 0) {
        mysql_free_result(result);
        *count = 0;
        return NULL;
    }
    
    Product** products = malloc(num_rows * sizeof(Product*));
    if (products == NULL) {
        mysql_free_result(result);
        *count = 0;
        return NULL;
    }
    
    int i = 0;
    MYSQL_ROW row;
    while ((row = mysql_fetch_row(result)) != NULL) {
        products[i] = malloc(sizeof(Product));
        if (products[i] == NULL) {
            for (int j = 0; j < i; j++) {
                free(products[j]);
            }
            free(products);
            mysql_free_result(result);
            *count = 0;
            return NULL;
        }
        
        products[i]->product_id = atoi(row[0]);
        strncpy(products[i]->product_name, row[1] ? row[1] : "", sizeof(products[i]->product_name) - 1);
        strncpy(products[i]->description, row[2] ? row[2] : "", sizeof(products[i]->description) - 1);
        products[i]->price = row[3] ? atof(row[3]) : 0.0;
        products[i]->stock_quantity = row[4] ? atoi(row[4]) : 0;
        products[i]->category_id = row[5] ? atoi(row[5]) : 0;
        strncpy(products[i]->sku, row[6] ? row[6] : "", sizeof(products[i]->sku) - 1);
        products[i]->weight = row[7] ? atof(row[7]) : 0.0;
        strncpy(products[i]->dimensions, row[8] ? row[8] : "", sizeof(products[i]->dimensions) - 1);
        strncpy(products[i]->created_at, row[9] ? row[9] : "", sizeof(products[i]->created_at) - 1);
        strncpy(products[i]->updated_at, row[10] ? row[10] : "", sizeof(products[i]->updated_at) - 1);
        products[i]->is_active = (row[11] && atoi(row[11]) == 1);
        
        i++;
    }
    
    mysql_free_result(result);
    *count = num_rows;
    return products;
}

Product** search_products_by_name(MYSQL* conn, const char* search_term, int* count) {
    char query[512];
    snprintf(query, sizeof(query), 
        "SELECT * FROM products WHERE product_name LIKE '%%%s%%' ORDER BY product_id", search_term);
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        *count = 0;
        return NULL;
    }
    
    int num_rows = (int)mysql_num_rows(result);
    if (num_rows == 0) {
        mysql_free_result(result);
        *count = 0;
        return NULL;
    }
    
    Product** products = malloc(num_rows * sizeof(Product*));
    if (products == NULL) {
        mysql_free_result(result);
        *count = 0;
        return NULL;
    }
    
    int i = 0;
    MYSQL_ROW row;
    while ((row = mysql_fetch_row(result)) != NULL) {
        products[i] = malloc(sizeof(Product));
        if (products[i] == NULL) {
            for (int j = 0; j < i; j++) {
                free(products[j]);
            }
            free(products);
            mysql_free_result(result);
            *count = 0;
            return NULL;
        }
        
        products[i]->product_id = atoi(row[0]);
        strncpy(products[i]->product_name, row[1] ? row[1] : "", sizeof(products[i]->product_name) - 1);
        strncpy(products[i]->description, row[2] ? row[2] : "", sizeof(products[i]->description) - 1);
        products[i]->price = row[3] ? atof(row[3]) : 0.0;
        products[i]->stock_quantity = row[4] ? atoi(row[4]) : 0;
        products[i]->category_id = row[5] ? atoi(row[5]) : 0;
        strncpy(products[i]->sku, row[6] ? row[6] : "", sizeof(products[i]->sku) - 1);
        products[i]->weight = row[7] ? atof(row[7]) : 0.0;
        strncpy(products[i]->dimensions, row[8] ? row[8] : "", sizeof(products[i]->dimensions) - 1);
        strncpy(products[i]->created_at, row[9] ? row[9] : "", sizeof(products[i]->created_at) - 1);
        strncpy(products[i]->updated_at, row[10] ? row[10] : "", sizeof(products[i]->updated_at) - 1);
        products[i]->is_active = (row[11] && atoi(row[11]) == 1);
        
        i++;
    }
    
    mysql_free_result(result);
    *count = num_rows;
    return products;
}

bool update_product_stock(MYSQL* conn, int product_id, int new_stock) {
    char query[256];
    snprintf(query, sizeof(query),
        "UPDATE products SET stock_quantity = %d WHERE product_id = %d",
        new_stock, product_id);
    
    return execute_query(conn, query);
}

Product** get_products_by_price_range(MYSQL* conn, double min_price, double max_price, int* count) {
    char query[512];
    snprintf(query, sizeof(query),
        "SELECT * FROM products WHERE price >= %.2f AND price <= %.2f ORDER BY price",
        min_price, max_price);
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        *count = 0;
        return NULL;
    }
    
    int num_rows = (int)mysql_num_rows(result);
    if (num_rows == 0) {
        mysql_free_result(result);
        *count = 0;
        return NULL;
    }
    
    Product** products = malloc(num_rows * sizeof(Product*));
    if (products == NULL) {
        mysql_free_result(result);
        *count = 0;
        return NULL;
    }
    
    int i = 0;
    MYSQL_ROW row;
    while ((row = mysql_fetch_row(result)) != NULL) {
        products[i] = malloc(sizeof(Product));
        if (products[i] == NULL) {
            for (int j = 0; j < i; j++) {
                free(products[j]);
            }
            free(products);
            mysql_free_result(result);
            *count = 0;
            return NULL;
        }
        
        products[i]->product_id = atoi(row[0]);
        strncpy(products[i]->product_name, row[1] ? row[1] : "", sizeof(products[i]->product_name) - 1);
        strncpy(products[i]->description, row[2] ? row[2] : "", sizeof(products[i]->description) - 1);
        products[i]->price = row[3] ? atof(row[3]) : 0.0;
        products[i]->stock_quantity = row[4] ? atoi(row[4]) : 0;
        products[i]->category_id = row[5] ? atoi(row[5]) : 0;
        strncpy(products[i]->sku, row[6] ? row[6] : "", sizeof(products[i]->sku) - 1);
        products[i]->weight = row[7] ? atof(row[7]) : 0.0;
        strncpy(products[i]->dimensions, row[8] ? row[8] : "", sizeof(products[i]->dimensions) - 1);
        strncpy(products[i]->created_at, row[9] ? row[9] : "", sizeof(products[i]->created_at) - 1);
        strncpy(products[i]->updated_at, row[10] ? row[10] : "", sizeof(products[i]->updated_at) - 1);
        products[i]->is_active = (row[11] && atoi(row[11]) == 1);
        
        i++;
    }
    
    mysql_free_result(result);
    *count = num_rows;
    return products;
}

void free_product(Product* product) {
    if (product != NULL) {
        free(product);
    }
}

void free_product_array(Product** products, int count) {
    if (products != NULL) {
        for (int i = 0; i < count; i++) {
            free_product(products[i]);
        }
        free(products);
    }
}