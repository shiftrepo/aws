#ifndef CART_OPERATIONS_H
#define CART_OPERATIONS_H

#include "database.h"

int add_to_cart(MYSQL* conn, const CartItem* item);
CartItem* get_cart_item_by_id(MYSQL* conn, int cart_item_id);
bool update_cart_item(MYSQL* conn, const CartItem* item);
bool remove_from_cart(MYSQL* conn, int cart_item_id);
bool remove_from_cart_by_user_product(MYSQL* conn, int user_id, int product_id);
CartItem** get_cart_items_by_user(MYSQL* conn, int user_id, int* count);
bool clear_cart(MYSQL* conn, int user_id);
bool update_cart_item_quantity(MYSQL* conn, int cart_item_id, int new_quantity);
double calculate_cart_total(MYSQL* conn, int user_id);
int get_cart_item_count(MYSQL* conn, int user_id);
void free_cart_item(CartItem* item);
void free_cart_item_array(CartItem** items, int count);

#endif