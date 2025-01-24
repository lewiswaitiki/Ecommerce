import psycopg2
import logging

Logger = logging.getLogger(__name__)


#set the level 
Logger.setLevel(logging.DEBUG)



def get_connection():
  ##Database connection parameters
  conn_params = {
    'dbname':'ecommerce',
    'user':'ecom',
    'password':"ecom",
    'host':'localhost',
    "port":5432
  }
  try:
    #establish the connection
    conn = psycopg2.connect(**conn_params)
    return conn
  except psycopg2.Error as e:
    print(f"Error connecting to the database: {e}")
    return None


def get_cursor(conn):
  try:
    return conn.cursor()
  except psycopg2.Error as e:
    print(f"Error creating cursor as {e}")
    return None
    
def create_user_table():
  conn = get_connection()
  if conn:
    print("connection")
    cursor = get_cursor(conn)
    if cursor:
      try:
        create_table_query = '''CREATE TABlE IF NOT EXISTS users(id SERIAL PRIMARY KEY,
                          username VARCHAR(50) UNIQUE NOT NULL,
                          email VARCHAR(100) UNIQUE NOT NULL,
                          password_hash VARCHAR(128) NOT NULL); '''
                          
        cursor.execute(create_table_query) 
        conn.commit()
        print("User table created successfully")
      except psycopg2.Error as e:
        print(f"Error executing query: {e}")
        raise
      
      finally:
        cursor.close()
        conn.close()
        print("Connection closed")
    
    else:
      print("Failed to create cursor")
  else:   
    print("no connection")


def create_product_table():
  conn = get_connection()
  if conn:
    
    cursor = get_cursor(conn)
    
    if cursor:
      try:
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS products(
          id SERIAL PRIMARY KEY,
          name VARCHAR(100) NOT NULL,
          description TEXT,
          price NUMERIC(10,2) NOT NULL,
          stock INT NOT NULL,
          image_url VARCHAR(255),
          category VARCHAR(50)
          );
          '''
        cursor.execute(create_table_query)
        conn.commit()
        print("product table craeated successfully")
      except psycopg2.Error as e:
        print(f"Error executing query: {e}")
      finally:
        cursor.close()
        conn.close()
        print("Connection closed")
    else:
      print("Failed to create cursor")
  else:
    print("No connection")
  
def insert_sample_products():
  conn = get_connection()
  cursor = get_cursor(conn)
  
  insert_product_query= '''INSERT INTO products(name,description,price,stock,image_url,category)VALUES(%s,%s,%s,%s,%s,%s);'''
  
 
  
  sample_products = [ ('Sample Product 1', 'Description for product 1', 19.99, 10, 'static/images/camera.jpg', 'electronics'), ('Sample Product 2', 'Description for product 2', 29.99, 5, 'static/images/icecream.jpg', 'food'), ('Sample Product 3', 'Description for product 3', 9.99, 20, 'static/images/cocacola.jpg', 'food') ]

  
  cursor.executemany(insert_product_query,sample_products)
  conn.commit()
  cursor.close()
  conn.close()

def get_all_products():
  conn = get_connection()
  cursor = get_cursor(conn)
  select_products_query = '''SELECT id,name,description,price,stock,image_url,category FROM products;'''
  cursor.execute(select_products_query)
  products = cursor.fetchall()
  cursor.close()
  conn.close()
  return products

def get_product_by_id(product_id):
  conn = get_connection()
  cursor=get_cursor(conn)
  select_product_query = '''
  SELECT id,name,description,price,stock,image_url,category FROM products
  WHERE id =%s;
  '''
  
  cursor.execute(select_product_query,(product_id,))
  product =cursor.fetchone()
  cursor.close()
  conn.close()
  return product


  def generate_password_hash(password):
    #hashing function to generate password hash
    return psycopg2.extensions.PYCHARS(password)
  
  