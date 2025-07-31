#ifndef USER_OPERATIONS_H
#define USER_OPERATIONS_H

#include "database.h"

int create_user(MYSQL* conn, const User* user);
User* get_user_by_id(MYSQL* conn, int user_id);
User* get_user_by_username(MYSQL* conn, const char* username);
User* get_user_by_email(MYSQL* conn, const char* email);
bool update_user(MYSQL* conn, const User* user);
bool delete_user(MYSQL* conn, int user_id);
User** get_all_users(MYSQL* conn, int* count);
bool verify_user_credentials(MYSQL* conn, const char* username, const char* password_hash);
void free_user(User* user);
void free_user_array(User** users, int count);

#endif