#!/usr/bin/env python3

import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = "/app/data/db/database.sqlite"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_test_db():
    """Initialize a test database with sample tables and data"""
    logger.info(f"Creating test database at {DB_PATH}")
    
    # Connect to the database (will create it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create users table
    logger.info("Creating users table")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        first_name TEXT,
        last_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create products table
    logger.info("Creating products table")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        category TEXT,
        stock INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create orders table
    logger.info("Creating orders table")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending',
        total_amount REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create order_items table
    logger.info("Creating order_items table")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')
    
    # Insert sample users
    logger.info("Inserting sample users")
    sample_users = [
        (1, 'johndoe', 'john@example.com', 'John', 'Doe'),
        (2, 'janedoe', 'jane@example.com', 'Jane', 'Doe'),
        (3, 'bobsmith', 'bob@example.com', 'Bob', 'Smith'),
        (4, 'alicejones', 'alice@example.com', 'Alice', 'Jones'),
        (5, 'mikebrown', 'mike@example.com', 'Mike', 'Brown')
    ]
    
    cursor.executemany(
        "INSERT OR REPLACE INTO users (id, username, email, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
        sample_users
    )
    
    # Insert sample products
    logger.info("Inserting sample products")
    sample_products = [
        (1, 'Laptop', 'High-performance laptop with 16GB RAM', 1200.00, 'Electronics', 10),
        (2, 'Smartphone', 'Latest model with triple camera', 800.00, 'Electronics', 15),
        (3, 'Headphones', 'Noise-cancelling wireless headphones', 150.00, 'Audio', 20),
        (4, 'Coffee Maker', 'Automatic drip coffee maker', 50.00, 'Kitchen', 8),
        (5, 'Desk Chair', 'Ergonomic office chair', 120.00, 'Furniture', 5),
        (6, 'Tablet', '10-inch tablet with stylus', 300.00, 'Electronics', 12),
        (7, 'Monitor', '27-inch 4K monitor', 350.00, 'Electronics', 7),
        (8, 'Keyboard', 'Mechanical keyboard with RGB lighting', 80.00, 'Computer Accessories', 18),
        (9, 'Mouse', 'Wireless gaming mouse', 45.00, 'Computer Accessories', 22),
        (10, 'Speakers', 'Bluetooth speakers with subwoofer', 90.00, 'Audio', 13)
    ]
    
    cursor.executemany(
        "INSERT OR REPLACE INTO products (id, name, description, price, category, stock) VALUES (?, ?, ?, ?, ?, ?)",
        sample_products
    )
    
    # Insert sample orders
    logger.info("Inserting sample orders")
    sample_orders = [
        (1, 1, '2025-01-05', 'completed', 1350.00),
        (2, 2, '2025-01-10', 'completed', 800.00),
        (3, 3, '2025-01-15', 'processing', 195.00),
        (4, 4, '2025-01-20', 'completed', 350.00),
        (5, 1, '2025-01-25', 'processing', 150.00),
        (6, 2, '2025-02-01', 'pending', 525.00),
        (7, 5, '2025-02-05', 'completed', 1200.00),
        (8, 3, '2025-02-10', 'pending', 90.00)
    ]
    
    cursor.executemany(
        "INSERT OR REPLACE INTO orders (id, user_id, order_date, status, total_amount) VALUES (?, ?, ?, ?, ?)",
        sample_orders
    )
    
    # Insert sample order items
    logger.info("Inserting sample order items")
    sample_order_items = [
        (1, 1, 1, 1, 1200.00),
        (2, 1, 3, 1, 150.00),
        (3, 2, 2, 1, 800.00),
        (4, 3, 3, 1, 150.00),
        (5, 3, 9, 1, 45.00),
        (6, 4, 7, 1, 350.00),
        (7, 5, 3, 1, 150.00),
        (8, 6, 4, 1, 50.00),
        (9, 6, 5, 1, 120.00),
        (10, 6, 8, 1, 80.00),
        (11, 6, 9, 1, 45.00),
        (12, 6, 10, 1, 90.00),
        (13, 6, 3, 1, 150.00),
        (14, 7, 1, 1, 1200.00),
        (15, 8, 10, 1, 90.00)
    ]
    
    cursor.executemany(
        "INSERT OR REPLACE INTO order_items (id, order_id, product_id, quantity, price) VALUES (?, ?, ?, ?, ?)",
        sample_order_items
    )
    
    # Commit and close
    conn.commit()
    conn.close()
    
    logger.info("Test database created successfully with sample data")

if __name__ == "__main__":
    init_test_db()
