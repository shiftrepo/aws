#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "database.h"
#include "user_operations.h"
#include "product_operations.h"
#include "order_operations.h"
#include "cart_operations.h"

void print_menu() {
    printf("\n=== ECサイト管理システム ===\n");
    printf("1. ユーザー管理\n");
    printf("2. 商品管理\n");
    printf("3. 注文管理\n");
    printf("4. カート管理\n");
    printf("0. 終了\n");
    printf("選択: ");
}

void print_user_menu() {
    printf("\n=== ユーザー管理 ===\n");
    printf("1. 全ユーザー表示\n");
    printf("2. ユーザー検索（ID）\n");
    printf("3. ユーザー作成\n");
    printf("4. ユーザー更新\n");
    printf("5. ユーザー削除\n");
    printf("0. メインメニューに戻る\n");
    printf("選択: ");
}

void print_product_menu() {
    printf("\n=== 商品管理 ===\n");
    printf("1. 全商品表示\n");
    printf("2. 商品検索（ID）\n");
    printf("3. 商品作成\n");
    printf("4. 商品更新\n");
    printf("5. 商品削除\n");
    printf("6. 在庫更新\n");
    printf("0. メインメニューに戻る\n");
    printf("選択: ");
}

void handle_user_management(MYSQL* conn) {
    int choice;
    do {
        print_user_menu();
        scanf("%d", &choice);
        
        switch (choice) {
            case 1: {
                int count;
                User** users = get_all_users(conn, &count);
                if (users != NULL) {
                    printf("\n=== 全ユーザー一覧 ===\n");
                    for (int i = 0; i < count; i++) {
                        printf("ID: %d, ユーザー名: %s, メール: %s, 氏名: %s %s\n",
                               users[i]->user_id, users[i]->username, users[i]->email,
                               users[i]->first_name, users[i]->last_name);
                    }
                    free_user_array(users, count);
                } else {
                    printf("ユーザーが見つかりませんでした。\n");
                }
                break;
            }
            
            case 2: {
                int user_id;
                printf("ユーザーID: ");
                scanf("%d", &user_id);
                
                User* user = get_user_by_id(conn, user_id);
                if (user != NULL) {
                    printf("\n=== ユーザー詳細 ===\n");
                    printf("ID: %d\n", user->user_id);
                    printf("ユーザー名: %s\n", user->username);
                    printf("メール: %s\n", user->email);
                    printf("氏名: %s %s\n", user->first_name, user->last_name);
                    printf("電話: %s\n", user->phone);
                    printf("有効: %s\n", user->is_active ? "はい" : "いいえ");
                    free_user(user);
                } else {
                    printf("ユーザーが見つかりませんでした。\n");
                }
                break;
            }
            
            case 3: {
                User new_user = {0};
                printf("ユーザー名: ");
                scanf("%s", new_user.username);
                printf("メール: ");
                scanf("%s", new_user.email);
                printf("パスワードハッシュ: ");
                scanf("%s", new_user.password_hash);
                printf("名: ");
                scanf("%s", new_user.first_name);
                printf("姓: ");
                scanf("%s", new_user.last_name);
                printf("電話: ");
                scanf("%s", new_user.phone);
                new_user.is_active = true;
                
                int user_id = create_user(conn, &new_user);
                if (user_id > 0) {
                    printf("ユーザーを作成しました。ID: %d\n", user_id);
                } else {
                    printf("ユーザーの作成に失敗しました。\n");
                }
                break;
            }
        }
    } while (choice != 0);
}

void handle_product_management(MYSQL* conn) {
    int choice;
    do {
        print_product_menu();
        scanf("%d", &choice);
        
        switch (choice) {
            case 1: {
                int count;
                Product** products = get_all_products(conn, &count);
                if (products != NULL) {
                    printf("\n=== 全商品一覧 ===\n");
                    for (int i = 0; i < count; i++) {
                        printf("ID: %d, 商品名: %s, 価格: %.2f円, 在庫: %d\n",
                               products[i]->product_id, products[i]->product_name, 
                               products[i]->price, products[i]->stock_quantity);
                    }
                    free_product_array(products, count);
                } else {
                    printf("商品が見つかりませんでした。\n");
                }
                break;
            }
            
            case 2: {
                int product_id;
                printf("商品ID: ");
                scanf("%d", &product_id);
                
                Product* product = get_product_by_id(conn, product_id);
                if (product != NULL) {
                    printf("\n=== 商品詳細 ===\n");
                    printf("ID: %d\n", product->product_id);
                    printf("商品名: %s\n", product->product_name);
                    printf("説明: %s\n", product->description);
                    printf("価格: %.2f円\n", product->price);
                    printf("在庫: %d\n", product->stock_quantity);
                    printf("SKU: %s\n", product->sku);
                    free_product(product);
                } else {
                    printf("商品が見つかりませんでした。\n");
                }
                break;
            }
            
            case 6: {
                int product_id, new_stock;
                printf("商品ID: ");
                scanf("%d", &product_id);
                printf("新しい在庫数: ");
                scanf("%d", &new_stock);
                
                if (update_product_stock(conn, product_id, new_stock)) {
                    printf("在庫を更新しました。\n");
                } else {
                    printf("在庫の更新に失敗しました。\n");
                }
                break;
            }
        }
    } while (choice != 0);
}

int main() {
    MYSQL* conn = db_connect();
    if (conn == NULL) {
        fprintf(stderr, "データベースに接続できませんでした。\n");
        return 1;
    }
    
    printf("ECサイト管理システムに接続しました。\n");
    
    int choice;
    do {
        print_menu();
        scanf("%d", &choice);
        
        switch (choice) {
            case 1:
                handle_user_management(conn);
                break;
            case 2:
                handle_product_management(conn);
                break;
            case 3:
                printf("注文管理機能は実装中です。\n");
                break;
            case 4:
                printf("カート管理機能は実装中です。\n");
                break;
            case 0:
                printf("システムを終了します。\n");
                break;
            default:
                printf("無効な選択です。\n");
                break;
        }
    } while (choice != 0);
    
    db_disconnect(conn);
    return 0;
}