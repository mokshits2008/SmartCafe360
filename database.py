import mysql.connector
from mysql.connector import Error, pooling
from datetime import datetime
from config import DB_CONFIG, POOL_CONFIG

# Connection pool will be created on first use
connection_pool = None

def get_connection_pool():
    """Get or create the connection pool"""
    global connection_pool
    if connection_pool is None:
        try:
            connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                **DB_CONFIG,
                **POOL_CONFIG
            )
        except Error as e:
            print(f"Error creating connection pool: {e}")
            print(f"Trying direct connection instead...")
    return connection_pool

def get_connection():
    """Get a connection from the pool or create a new one"""
    try:
        pool = get_connection_pool()
        if pool:
            return pool.get_connection()
        else:
            # Fallback to direct connection if pool creation failed
            return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise

#Initialize the MySQL database with required tables
def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create items table
        cursor.execute('''CREATE TABLE IF NOT EXISTS items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            quantity INT DEFAULT 0,
            image_path VARCHAR(500)
        )''')
        
        # Create managers table
        cursor.execute('''CREATE TABLE IF NOT EXISTS managers (
            username VARCHAR(100) PRIMARY KEY,
            password VARCHAR(255) NOT NULL
        )''')
        
        # Create sales table
        cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
            id INT AUTO_INCREMENT PRIMARY KEY,
            item_id INT NOT NULL,
            quantity_sold INT NOT NULL,
            total_price DECIMAL(10, 2) NOT NULL,
            sale_date DATETIME NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
        )''')
        
        # Insert default admin account
        cursor.execute(
            "INSERT IGNORE INTO managers (username, password) VALUES (%s, %s)",
            ("admin", "pass123")
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully!")
    except Error as e:
        print(f"Error initializing database: {e}")
        raise

#Retrieve all items from the database
def get_all_items():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, quantity, image_path FROM items")
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return items
    except Error as e:
        print(f"Error fetching items: {e}")
        return []

#Record a sale in the database
def add_sale(item_id, quantity_sold, total_price):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sales (item_id, quantity_sold, total_price, sale_date) VALUES (%s, %s, %s, %s)",
            (item_id, quantity_sold, total_price, datetime.now())
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error adding sale: {e}")
        raise

#Verify manager login credentials
def check_manager_login(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM managers WHERE username = %s AND password = %s",
            (username, password)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Error as e:
        print(f"Error checking login: {e}")
        return False

#Add a new item to the database
def add_item(name, price, image_path):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO items (name, price, quantity, image_path) VALUES (%s, %s, 0, %s)",
            (name, price, image_path)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error adding item: {e}")
        raise

#Update an existing item in the database
def update_item(item_id, name, price, image_path):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE items SET name = %s, price = %s, image_path = %s WHERE id = %s",
            (name, price, image_path, item_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error updating item: {e}")
        raise

#Delete an item from the database
def delete_item(item_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error deleting item: {e}")
        raise

#Retrieve all sales records from the database
def get_sales():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, item_id, quantity_sold, total_price, sale_date FROM sales")
        sales = cursor.fetchall()
        cursor.close()
        conn.close()
        return sales
    except Error as e:
        print(f"Error fetching sales: {e}")
        return []

#Retrieve all manager credentials from the database
def get_all_managers():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM managers")
        managers = cursor.fetchall()
        cursor.close()
        conn.close()
        return managers
    except Error as e:
        print(f"Error fetching managers: {e}")
        return []

#Add a new manager to the database
def add_manager(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO managers (username, password) VALUES (%s, %s)",
            (username, password)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error adding manager: {e}")
        raise

#Update a manager's credentials in the database
def update_manager(old_username, new_username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE managers SET username = %s, password = %s WHERE username = %s",
            (new_username, password, old_username)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error updating manager: {e}")
        raise

#Delete a manager from the database
def delete_manager(username):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM managers WHERE username = %s", (username,))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error deleting manager: {e}")
        raise