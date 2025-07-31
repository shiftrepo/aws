#include "order_operations.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int create_order(MYSQL* conn, const Order* order) {
    char query[2048];
    snprintf(query, sizeof(query),
        "INSERT INTO orders (user_id, status, total_amount, shipping_address_id, billing_address_id, "
        "payment_method, shipping_cost, tax_amount, notes) "
        "VALUES (%d, '%s', %.2f, %d, %d, '%s', %.2f, %.2f, '%s')",
        order->user_id, order->status, order->total_amount, order->shipping_address_id,
        order->billing_address_id, order->payment_method, order->shipping_cost,
        order->tax_amount, order->notes);
    
    if (!execute_query(conn, query)) {
        return -1;
    }
    
    return (int)mysql_insert_id(conn);
}

Order* get_order_by_id(MYSQL* conn, int order_id) {
    char query[256];
    snprintf(query, sizeof(query), "SELECT * FROM orders WHERE order_id = %d", order_id);
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        return NULL;
    }
    
    MYSQL_ROW row = mysql_fetch_row(result);
    if (row == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    Order* order = malloc(sizeof(Order));
    if (order == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    order->order_id = atoi(row[0]);
    order->user_id = row[1] ? atoi(row[1]) : 0;
    strncpy(order->order_date, row[2] ? row[2] : "", sizeof(order->order_date) - 1);
    strncpy(order->status, row[3] ? row[3] : "", sizeof(order->status) - 1);
    order->total_amount = row[4] ? atof(row[4]) : 0.0;
    order->shipping_address_id = row[5] ? atoi(row[5]) : 0;
    order->billing_address_id = row[6] ? atoi(row[6]) : 0;
    strncpy(order->payment_method, row[7] ? row[7] : "", sizeof(order->payment_method) - 1);
    order->shipping_cost = row[8] ? atof(row[8]) : 0.0;
    order->tax_amount = row[9] ? atof(row[9]) : 0.0;
    strncpy(order->notes, row[10] ? row[10] : "", sizeof(order->notes) - 1);
    
    mysql_free_result(result);
    return order;
}

bool update_order(MYSQL* conn, const Order* order) {
    char query[2048];
    snprintf(query, sizeof(query),
        "UPDATE orders SET user_id=%d, status='%s', total_amount=%.2f, "
        "shipping_address_id=%d, billing_address_id=%d, payment_method='%s', "
        "shipping_cost=%.2f, tax_amount=%.2f, notes='%s' WHERE order_id=%d",
        order->user_id, order->status, order->total_amount, order->shipping_address_id,
        order->billing_address_id, order->payment_method, order->shipping_cost,
        order->tax_amount, order->notes, order->order_id);
    
    return execute_query(conn, query);
}

bool delete_order(MYSQL* conn, int order_id) {
    char query[256];
    snprintf(query, sizeof(query), "DELETE FROM orders WHERE order_id = %d", order_id);
    
    return execute_query(conn, query);
}

Order** get_orders_by_user(MYSQL* conn, int user_id, int* count) {
    char query[256];
    snprintf(query, sizeof(query), "SELECT * FROM orders WHERE user_id = %d ORDER BY order_date DESC", user_id);
    
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
    
    Order** orders = malloc(num_rows * sizeof(Order*));
    if (orders == NULL) {
        mysql_free_result(result);
        *count = 0;
        return NULL;
    }
    
    int i = 0;
    MYSQL_ROW row;
    while ((row = mysql_fetch_row(result)) != NULL) {
        orders[i] = malloc(sizeof(Order));
        if (orders[i] == NULL) {
            for (int j = 0; j < i; j++) {
                free(orders[j]);
            }
            free(orders);
            mysql_free_result(result);
            *count = 0;
            return NULL;
        }
        
        orders[i]->order_id = atoi(row[0]);
        orders[i]->user_id = row[1] ? atoi(row[1]) : 0;
        strncpy(orders[i]->order_date, row[2] ? row[2] : "", sizeof(orders[i]->order_date) - 1);
        strncpy(orders[i]->status, row[3] ? row[3] : "", sizeof(orders[i]->status) - 1);
        orders[i]->total_amount = row[4] ? atof(row[4]) : 0.0;
        orders[i]->shipping_address_id = row[5] ? atoi(row[5]) : 0;
        orders[i]->billing_address_id = row[6] ? atoi(row[6]) : 0;
        strncpy(orders[i]->payment_method, row[7] ? row[7] : "", sizeof(orders[i]->payment_method) - 1);
        orders[i]->shipping_cost = row[8] ? atof(row[8]) : 0.0;
        orders[i]->tax_amount = row[9] ? atof(row[9]) : 0.0;
        strncpy(orders[i]->notes, row[10] ? row[10] : "", sizeof(orders[i]->notes) - 1);
        
        i++;
    }
    
    mysql_free_result(result);
    *count = num_rows;
    return orders;
}

Order** get_all_orders(MYSQL* conn, int* count) {
    const char* query = "SELECT * FROM orders ORDER BY order_date DESC";
    
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
    
    Order** orders = malloc(num_rows * sizeof(Order*));
    if (orders == NULL) {
        mysql_free_result(result);
        *count = 0;
        return NULL;
    }
    
    int i = 0;
    MYSQL_ROW row;
    while ((row = mysql_fetch_row(result)) != NULL) {
        orders[i] = malloc(sizeof(Order));
        if (orders[i] == NULL) {
            for (int j = 0; j < i; j++) {
                free(orders[j]);
            }
            free(orders);
            mysql_free_result(result);
            *count = 0;
            return NULL;
        }
        
        orders[i]->order_id = atoi(row[0]);
        orders[i]->user_id = row[1] ? atoi(row[1]) : 0;
        strncpy(orders[i]->order_date, row[2] ? row[2] : "", sizeof(orders[i]->order_date) - 1);
        strncpy(orders[i]->status, row[3] ? row[3] : "", sizeof(orders[i]->status) - 1);
        orders[i]->total_amount = row[4] ? atof(row[4]) : 0.0;
        orders[i]->shipping_address_id = row[5] ? atoi(row[5]) : 0;
        orders[i]->billing_address_id = row[6] ? atoi(row[6]) : 0;
        strncpy(orders[i]->payment_method, row[7] ? row[7] : "", sizeof(orders[i]->payment_method) - 1);
        orders[i]->shipping_cost = row[8] ? atof(row[8]) : 0.0;
        orders[i]->tax_amount = row[9] ? atof(row[9]) : 0.0;
        strncpy(orders[i]->notes, row[10] ? row[10] : "", sizeof(orders[i]->notes) - 1);
        
        i++;
    }
    
    mysql_free_result(result);
    *count = num_rows;
    return orders;
}

bool update_order_status(MYSQL* conn, int order_id, const char* status) {
    char query[256];
    snprintf(query, sizeof(query),
        "UPDATE orders SET status = '%s' WHERE order_id = %d", status, order_id);
    
    return execute_query(conn, query);
}

Order** get_orders_by_status(MYSQL* conn, const char* status, int* count) {
    char query[256];
    snprintf(query, sizeof(query), "SELECT * FROM orders WHERE status = '%s' ORDER BY order_date DESC", status);
    
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
    
    Order** orders = malloc(num_rows * sizeof(Order*));
    if (orders == NULL) {
        mysql_free_result(result);
        *count = 0;
        return NULL;
    }
    
    int i = 0;
    MYSQL_ROW row;
    while ((row = mysql_fetch_row(result)) != NULL) {
        orders[i] = malloc(sizeof(Order));
        if (orders[i] == NULL) {
            for (int j = 0; j < i; j++) {
                free(orders[j]);
            }
            free(orders);
            mysql_free_result(result);
            *count = 0;
            return NULL;
        }
        
        orders[i]->order_id = atoi(row[0]);
        orders[i]->user_id = row[1] ? atoi(row[1]) : 0;
        strncpy(orders[i]->order_date, row[2] ? row[2] : "", sizeof(orders[i]->order_date) - 1);
        strncpy(orders[i]->status, row[3] ? row[3] : "", sizeof(orders[i]->status) - 1);
        orders[i]->total_amount = row[4] ? atof(row[4]) : 0.0;
        orders[i]->shipping_address_id = row[5] ? atoi(row[5]) : 0;
        orders[i]->billing_address_id = row[6] ? atoi(row[6]) : 0;
        strncpy(orders[i]->payment_method, row[7] ? row[7] : "", sizeof(orders[i]->payment_method) - 1);
        orders[i]->shipping_cost = row[8] ? atof(row[8]) : 0.0;
        orders[i]->tax_amount = row[9] ? atof(row[9]) : 0.0;
        strncpy(orders[i]->notes, row[10] ? row[10] : "", sizeof(orders[i]->notes) - 1);
        
        i++;
    }
    
    mysql_free_result(result);
    *count = num_rows;
    return orders;
}

int create_order_item(MYSQL* conn, const OrderItem* item) {
    char query[512];
    snprintf(query, sizeof(query),
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) "
        "VALUES (%d, %d, %d, %.2f, %.2f)",
        item->order_id, item->product_id, item->quantity, item->unit_price, item->total_price);
    
    if (!execute_query(conn, query)) {
        return -1;
    }
    
    return (int)mysql_insert_id(conn);
}

OrderItem* get_order_item_by_id(MYSQL* conn, int order_item_id) {
    char query[256];
    snprintf(query, sizeof(query), "SELECT * FROM order_items WHERE order_item_id = %d", order_item_id);
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        return NULL;
    }
    
    MYSQL_ROW row = mysql_fetch_row(result);
    if (row == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    OrderItem* item = malloc(sizeof(OrderItem));
    if (item == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    item->order_item_id = atoi(row[0]);
    item->order_id = row[1] ? atoi(row[1]) : 0;
    item->product_id = row[2] ? atoi(row[2]) : 0;
    item->quantity = row[3] ? atoi(row[3]) : 0;
    item->unit_price = row[4] ? atof(row[4]) : 0.0;
    item->total_price = row[5] ? atof(row[5]) : 0.0;
    
    mysql_free_result(result);
    return item;
}

bool update_order_item(MYSQL* conn, const OrderItem* item) {
    char query[512];
    snprintf(query, sizeof(query),
        "UPDATE order_items SET order_id=%d, product_id=%d, quantity=%d, unit_price=%.2f, total_price=%.2f "
        "WHERE order_item_id=%d",
        item->order_id, item->product_id, item->quantity, item->unit_price, item->total_price, item->order_item_id);
    
    return execute_query(conn, query);
}

bool delete_order_item(MYSQL* conn, int order_item_id) {
    char query[256];
    snprintf(query, sizeof(query), "DELETE FROM order_items WHERE order_item_id = %d", order_item_id);
    
    return execute_query(conn, query);
}

OrderItem** get_order_items_by_order(MYSQL* conn, int order_id, int* count) {
    char query[256];
    snprintf(query, sizeof(query), "SELECT * FROM order_items WHERE order_id = %d", order_id);
    
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
    
    OrderItem** items = malloc(num_rows * sizeof(OrderItem*));
    if (items == NULL) {
        mysql_free_result(result);
        *count = 0;
        return NULL;
    }
    
    int i = 0;
    MYSQL_ROW row;
    while ((row = mysql_fetch_row(result)) != NULL) {
        items[i] = malloc(sizeof(OrderItem));
        if (items[i] == NULL) {
            for (int j = 0; j < i; j++) {
                free(items[j]);
            }
            free(items);
            mysql_free_result(result);
            *count = 0;
            return NULL;
        }
        
        items[i]->order_item_id = atoi(row[0]);
        items[i]->order_id = row[1] ? atoi(row[1]) : 0;
        items[i]->product_id = row[2] ? atoi(row[2]) : 0;
        items[i]->quantity = row[3] ? atoi(row[3]) : 0;
        items[i]->unit_price = row[4] ? atof(row[4]) : 0.0;
        items[i]->total_price = row[5] ? atof(row[5]) : 0.0;
        
        i++;
    }
    
    mysql_free_result(result);
    *count = num_rows;
    return items;
}

void free_order(Order* order) {
    if (order != NULL) {
        free(order);
    }
}

void free_order_array(Order** orders, int count) {
    if (orders != NULL) {
        for (int i = 0; i < count; i++) {
            free_order(orders[i]);
        }
        free(orders);
    }
}

void free_order_item(OrderItem* item) {
    if (item != NULL) {
        free(item);
    }
}

void free_order_item_array(OrderItem** items, int count) {
    if (items != NULL) {
        for (int i = 0; i < count; i++) {
            free_order_item(items[i]);
        }
        free(items);
    }
}