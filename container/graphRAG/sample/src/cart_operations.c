#include "cart_operations.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int add_to_cart(MYSQL* conn, const CartItem* item) {
    char query[512];
    snprintf(query, sizeof(query),
        "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (%d, %d, %d) "
        "ON DUPLICATE KEY UPDATE quantity = quantity + %d",
        item->user_id, item->product_id, item->quantity, item->quantity);
    
    if (!execute_query(conn, query)) {
        return -1;
    }
    
    return (int)mysql_insert_id(conn);
}

CartItem* get_cart_item_by_id(MYSQL* conn, int cart_item_id) {
    char query[256];
    snprintf(query, sizeof(query), "SELECT * FROM cart_items WHERE cart_item_id = %d", cart_item_id);
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        return NULL;
    }
    
    MYSQL_ROW row = mysql_fetch_row(result);
    if (row == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    CartItem* item = malloc(sizeof(CartItem));
    if (item == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    item->cart_item_id = atoi(row[0]);
    item->user_id = row[1] ? atoi(row[1]) : 0;
    item->product_id = row[2] ? atoi(row[2]) : 0;
    item->quantity = row[3] ? atoi(row[3]) : 0;
    strncpy(item->added_at, row[4] ? row[4] : "", sizeof(item->added_at) - 1);
    
    mysql_free_result(result);
    return item;
}

bool update_cart_item(MYSQL* conn, const CartItem* item) {
    char query[512];
    snprintf(query, sizeof(query),
        "UPDATE cart_items SET user_id=%d, product_id=%d, quantity=%d WHERE cart_item_id=%d",
        item->user_id, item->product_id, item->quantity, item->cart_item_id);
    
    return execute_query(conn, query);
}

bool remove_from_cart(MYSQL* conn, int cart_item_id) {
    char query[256];
    snprintf(query, sizeof(query), "DELETE FROM cart_items WHERE cart_item_id = %d", cart_item_id);
    
    return execute_query(conn, query);
}

bool remove_from_cart_by_user_product(MYSQL* conn, int user_id, int product_id) {
    char query[256];
    snprintf(query, sizeof(query), "DELETE FROM cart_items WHERE user_id = %d AND product_id = %d", user_id, product_id);
    
    return execute_query(conn, query);
}

CartItem** get_cart_items_by_user(MYSQL* conn, int user_id, int* count) {
    char query[256];
    snprintf(query, sizeof(query), "SELECT * FROM cart_items WHERE user_id = %d ORDER BY added_at DESC", user_id);
    
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
    
    CartItem** items = malloc(num_rows * sizeof(CartItem*));
    if (items == NULL) {
        mysql_free_result(result);
        *count = 0;
        return NULL;
    }
    
    int i = 0;
    MYSQL_ROW row;
    while ((row = mysql_fetch_row(result)) != NULL) {
        items[i] = malloc(sizeof(CartItem));
        if (items[i] == NULL) {
            for (int j = 0; j < i; j++) {
                free(items[j]);
            }
            free(items);
            mysql_free_result(result);
            *count = 0;
            return NULL;
        }
        
        items[i]->cart_item_id = atoi(row[0]);
        items[i]->user_id = row[1] ? atoi(row[1]) : 0;
        items[i]->product_id = row[2] ? atoi(row[2]) : 0;
        items[i]->quantity = row[3] ? atoi(row[3]) : 0;
        strncpy(items[i]->added_at, row[4] ? row[4] : "", sizeof(items[i]->added_at) - 1);
        
        i++;
    }
    
    mysql_free_result(result);
    *count = num_rows;
    return items;
}

bool clear_cart(MYSQL* conn, int user_id) {
    char query[256];
    snprintf(query, sizeof(query), "DELETE FROM cart_items WHERE user_id = %d", user_id);
    
    return execute_query(conn, query);
}

bool update_cart_item_quantity(MYSQL* conn, int cart_item_id, int new_quantity) {
    char query[256];
    snprintf(query, sizeof(query),
        "UPDATE cart_items SET quantity = %d WHERE cart_item_id = %d",
        new_quantity, cart_item_id);
    
    return execute_query(conn, query);
}

double calculate_cart_total(MYSQL* conn, int user_id) {
    char query[512];
    snprintf(query, sizeof(query),
        "SELECT SUM(c.quantity * p.price) FROM cart_items c "
        "JOIN products p ON c.product_id = p.product_id "
        "WHERE c.user_id = %d", user_id);
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        return 0.0;
    }
    
    MYSQL_ROW row = mysql_fetch_row(result);
    double total = 0.0;
    if (row != NULL && row[0] != NULL) {
        total = atof(row[0]);
    }
    
    mysql_free_result(result);
    return total;
}

int get_cart_item_count(MYSQL* conn, int user_id) {
    char query[256];
    snprintf(query, sizeof(query), "SELECT COUNT(*) FROM cart_items WHERE user_id = %d", user_id);
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        return 0;
    }
    
    MYSQL_ROW row = mysql_fetch_row(result);
    int count = 0;
    if (row != NULL && row[0] != NULL) {
        count = atoi(row[0]);
    }
    
    mysql_free_result(result);
    return count;
}

void free_cart_item(CartItem* item) {
    if (item != NULL) {
        free(item);
    }
}

void free_cart_item_array(CartItem** items, int count) {
    if (items != NULL) {
        for (int i = 0; i < count; i++) {
            free_cart_item(items[i]);
        }
        free(items);
    }
}