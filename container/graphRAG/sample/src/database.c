#include "database.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

MYSQL* db_connect(void) {
    MYSQL* conn = mysql_init(NULL);
    
    if (conn == NULL) {
        fprintf(stderr, "mysql_init() failed\n");
        return NULL;
    }
    
    if (mysql_real_connect(conn, DB_HOST, DB_USER, DB_PASSWORD, 
                          DB_NAME, 0, NULL, 0) == NULL) {
        fprintf(stderr, "mysql_real_connect() failed: %s\n", mysql_error(conn));
        mysql_close(conn);
        return NULL;
    }
    
    if (mysql_set_character_set(conn, "utf8mb4") != 0) {
        fprintf(stderr, "mysql_set_character_set() failed: %s\n", mysql_error(conn));
        mysql_close(conn);
        return NULL;
    }
    
    return conn;
}

void db_disconnect(MYSQL* conn) {
    if (conn != NULL) {
        mysql_close(conn);
    }
}

bool execute_query(MYSQL* conn, const char* query) {
    if (mysql_query(conn, query) != 0) {
        fprintf(stderr, "Query failed: %s\n", mysql_error(conn));
        return false;
    }
    return true;
}

MYSQL_RES* execute_select_query(MYSQL* conn, const char* query) {
    if (mysql_query(conn, query) != 0) {
        fprintf(stderr, "Query failed: %s\n", mysql_error(conn));
        return NULL;
    }
    
    MYSQL_RES* result = mysql_store_result(conn);
    if (result == NULL) {
        fprintf(stderr, "mysql_store_result() failed: %s\n", mysql_error(conn));
        return NULL;
    }
    
    return result;
}