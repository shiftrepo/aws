#include "user_operations.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int create_user(MYSQL* conn, const User* user) {
    char query[1024];
    snprintf(query, sizeof(query),
        "INSERT INTO users (username, email, password_hash, first_name, last_name, phone, is_active) "
        "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', %d)",
        user->username, user->email, user->password_hash,
        user->first_name, user->last_name, user->phone, user->is_active);
    
    if (!execute_query(conn, query)) {
        return -1;
    }
    
    return (int)mysql_insert_id(conn);
}

User* get_user_by_id(MYSQL* conn, int user_id) {
    char query[256];
    snprintf(query, sizeof(query), "SELECT * FROM users WHERE user_id = %d", user_id);
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        return NULL;
    }
    
    MYSQL_ROW row = mysql_fetch_row(result);
    if (row == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    User* user = malloc(sizeof(User));
    if (user == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    user->user_id = atoi(row[0]);
    strncpy(user->username, row[1] ? row[1] : "", sizeof(user->username) - 1);
    strncpy(user->email, row[2] ? row[2] : "", sizeof(user->email) - 1);
    strncpy(user->password_hash, row[3] ? row[3] : "", sizeof(user->password_hash) - 1);
    strncpy(user->first_name, row[4] ? row[4] : "", sizeof(user->first_name) - 1);
    strncpy(user->last_name, row[5] ? row[5] : "", sizeof(user->last_name) - 1);
    strncpy(user->phone, row[6] ? row[6] : "", sizeof(user->phone) - 1);
    strncpy(user->created_at, row[7] ? row[7] : "", sizeof(user->created_at) - 1);
    strncpy(user->updated_at, row[8] ? row[8] : "", sizeof(user->updated_at) - 1);
    user->is_active = (row[9] && atoi(row[9]) == 1);
    
    mysql_free_result(result);
    return user;
}

User* get_user_by_username(MYSQL* conn, const char* username) {
    char query[256];
    snprintf(query, sizeof(query), "SELECT * FROM users WHERE username = '%s'", username);
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        return NULL;
    }
    
    MYSQL_ROW row = mysql_fetch_row(result);
    if (row == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    User* user = malloc(sizeof(User));
    if (user == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    user->user_id = atoi(row[0]);
    strncpy(user->username, row[1] ? row[1] : "", sizeof(user->username) - 1);
    strncpy(user->email, row[2] ? row[2] : "", sizeof(user->email) - 1);
    strncpy(user->password_hash, row[3] ? row[3] : "", sizeof(user->password_hash) - 1);
    strncpy(user->first_name, row[4] ? row[4] : "", sizeof(user->first_name) - 1);
    strncpy(user->last_name, row[5] ? row[5] : "", sizeof(user->last_name) - 1);
    strncpy(user->phone, row[6] ? row[6] : "", sizeof(user->phone) - 1);
    strncpy(user->created_at, row[7] ? row[7] : "", sizeof(user->created_at) - 1);
    strncpy(user->updated_at, row[8] ? row[8] : "", sizeof(user->updated_at) - 1);
    user->is_active = (row[9] && atoi(row[9]) == 1);
    
    mysql_free_result(result);
    return user;
}

User* get_user_by_email(MYSQL* conn, const char* email) {
    char query[256];
    snprintf(query, sizeof(query), "SELECT * FROM users WHERE email = '%s'", email);
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        return NULL;
    }
    
    MYSQL_ROW row = mysql_fetch_row(result);
    if (row == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    User* user = malloc(sizeof(User));
    if (user == NULL) {
        mysql_free_result(result);
        return NULL;
    }
    
    user->user_id = atoi(row[0]);
    strncpy(user->username, row[1] ? row[1] : "", sizeof(user->username) - 1);
    strncpy(user->email, row[2] ? row[2] : "", sizeof(user->email) - 1);
    strncpy(user->password_hash, row[3] ? row[3] : "", sizeof(user->password_hash) - 1);
    strncpy(user->first_name, row[4] ? row[4] : "", sizeof(user->first_name) - 1);
    strncpy(user->last_name, row[5] ? row[5] : "", sizeof(user->last_name) - 1);
    strncpy(user->phone, row[6] ? row[6] : "", sizeof(user->phone) - 1);
    strncpy(user->created_at, row[7] ? row[7] : "", sizeof(user->created_at) - 1);
    strncpy(user->updated_at, row[8] ? row[8] : "", sizeof(user->updated_at) - 1);
    user->is_active = (row[9] && atoi(row[9]) == 1);
    
    mysql_free_result(result);
    return user;
}

bool update_user(MYSQL* conn, const User* user) {
    char query[1024];
    snprintf(query, sizeof(query),
        "UPDATE users SET username='%s', email='%s', password_hash='%s', "
        "first_name='%s', last_name='%s', phone='%s', is_active=%d "
        "WHERE user_id=%d",
        user->username, user->email, user->password_hash,
        user->first_name, user->last_name, user->phone,
        user->is_active, user->user_id);
    
    return execute_query(conn, query);
}

bool delete_user(MYSQL* conn, int user_id) {
    char query[256];
    snprintf(query, sizeof(query), "DELETE FROM users WHERE user_id = %d", user_id);
    
    return execute_query(conn, query);
}

User** get_all_users(MYSQL* conn, int* count) {
    const char* query = "SELECT * FROM users ORDER BY user_id";
    
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
    
    User** users = malloc(num_rows * sizeof(User*));
    if (users == NULL) {
        mysql_free_result(result);
        *count = 0;
        return NULL;
    }
    
    int i = 0;
    MYSQL_ROW row;
    while ((row = mysql_fetch_row(result)) != NULL) {
        users[i] = malloc(sizeof(User));
        if (users[i] == NULL) {
            for (int j = 0; j < i; j++) {
                free(users[j]);
            }
            free(users);
            mysql_free_result(result);
            *count = 0;
            return NULL;
        }
        
        users[i]->user_id = atoi(row[0]);
        strncpy(users[i]->username, row[1] ? row[1] : "", sizeof(users[i]->username) - 1);
        strncpy(users[i]->email, row[2] ? row[2] : "", sizeof(users[i]->email) - 1);
        strncpy(users[i]->password_hash, row[3] ? row[3] : "", sizeof(users[i]->password_hash) - 1);
        strncpy(users[i]->first_name, row[4] ? row[4] : "", sizeof(users[i]->first_name) - 1);
        strncpy(users[i]->last_name, row[5] ? row[5] : "", sizeof(users[i]->last_name) - 1);
        strncpy(users[i]->phone, row[6] ? row[6] : "", sizeof(users[i]->phone) - 1);
        strncpy(users[i]->created_at, row[7] ? row[7] : "", sizeof(users[i]->created_at) - 1);
        strncpy(users[i]->updated_at, row[8] ? row[8] : "", sizeof(users[i]->updated_at) - 1);
        users[i]->is_active = (row[9] && atoi(row[9]) == 1);
        
        i++;
    }
    
    mysql_free_result(result);
    *count = num_rows;
    return users;
}

bool verify_user_credentials(MYSQL* conn, const char* username, const char* password_hash) {
    char query[512];
    snprintf(query, sizeof(query),
        "SELECT user_id FROM users WHERE username = '%s' AND password_hash = '%s' AND is_active = 1",
        username, password_hash);
    
    MYSQL_RES* result = execute_select_query(conn, query);
    if (result == NULL) {
        return false;
    }
    
    MYSQL_ROW row = mysql_fetch_row(result);
    bool valid = (row != NULL);
    
    mysql_free_result(result);
    return valid;
}

void free_user(User* user) {
    if (user != NULL) {
        free(user);
    }
}

void free_user_array(User** users, int count) {
    if (users != NULL) {
        for (int i = 0; i < count; i++) {
            free_user(users[i]);
        }
        free(users);
    }
}