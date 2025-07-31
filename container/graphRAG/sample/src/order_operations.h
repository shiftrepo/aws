#ifndef ORDER_OPERATIONS_H
#define ORDER_OPERATIONS_H

#include "database.h"

int create_order(MYSQL* conn, const Order* order);
Order* get_order_by_id(MYSQL* conn, int order_id);
bool update_order(MYSQL* conn, const Order* order);
bool delete_order(MYSQL* conn, int order_id);
Order** get_orders_by_user(MYSQL* conn, int user_id, int* count);
Order** get_all_orders(MYSQL* conn, int* count);
bool update_order_status(MYSQL* conn, int order_id, const char* status);
Order** get_orders_by_status(MYSQL* conn, const char* status, int* count);

int create_order_item(MYSQL* conn, const OrderItem* item);
OrderItem* get_order_item_by_id(MYSQL* conn, int order_item_id);
bool update_order_item(MYSQL* conn, const OrderItem* item);
bool delete_order_item(MYSQL* conn, int order_item_id);
OrderItem** get_order_items_by_order(MYSQL* conn, int order_id, int* count);

void free_order(Order* order);
void free_order_array(Order** orders, int count);
void free_order_item(OrderItem* item);
void free_order_item_array(OrderItem** items, int count);

#endif