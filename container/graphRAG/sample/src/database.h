#ifndef DATABASE_H
#define DATABASE_H

#include <mysql/mysql.h>
#include <stdbool.h>

#define MAX_STRING_LENGTH 256
#define MAX_TEXT_LENGTH 1024
#define DB_HOST "localhost"
#define DB_USER "root"
#define DB_PASSWORD "password"
#define DB_NAME "ec_site"

typedef struct {
    int user_id;
    char username[51];
    char email[101];
    char password_hash[256];
    char first_name[51];
    char last_name[51];
    char phone[21];
    char created_at[20];
    char updated_at[20];
    bool is_active;
} User;

typedef struct {
    int category_id;
    char category_name[101];
    char description[MAX_TEXT_LENGTH];
    int parent_category_id;
    char created_at[20];
} Category;

typedef struct {
    int product_id;
    char product_name[201];
    char description[MAX_TEXT_LENGTH];
    double price;
    int stock_quantity;
    int category_id;
    char sku[51];
    double weight;
    char dimensions[101];
    char created_at[20];
    char updated_at[20];
    bool is_active;
} Product;

typedef struct {
    int address_id;
    int user_id;
    char address_type[10];
    char first_name[51];
    char last_name[51];
    char company[101];
    char address_line1[256];
    char address_line2[256];
    char city[101];
    char state_province[101];
    char postal_code[21];
    char country[101];
    char created_at[20];
    bool is_default;
} Address;

typedef struct {
    int order_id;
    int user_id;
    char order_date[20];
    char status[20];
    double total_amount;
    int shipping_address_id;
    int billing_address_id;
    char payment_method[51];
    double shipping_cost;
    double tax_amount;
    char notes[MAX_TEXT_LENGTH];
} Order;

typedef struct {
    int order_item_id;
    int order_id;
    int product_id;
    int quantity;
    double unit_price;
    double total_price;
} OrderItem;

typedef struct {
    int cart_item_id;
    int user_id;
    int product_id;
    int quantity;
    char added_at[20];
} CartItem;

typedef struct {
    int review_id;
    int product_id;
    int user_id;
    int rating;
    char title[201];
    char comment[MAX_TEXT_LENGTH];
    char created_at[20];
    bool is_verified;
} Review;

MYSQL* db_connect(void);
void db_disconnect(MYSQL* conn);
bool execute_query(MYSQL* conn, const char* query);
MYSQL_RES* execute_select_query(MYSQL* conn, const char* query);

#endif