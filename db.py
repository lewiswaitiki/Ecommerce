import psycopg2
import logging
import bcrypt

Logger = logging.getLogger(__name__)


#set the level 
Logger.setLevel(logging.DEBUG)



def get_connection():
  ##Database connection parameters
  conn_params = {
    'dbname':'ecommerce_db',
    'user':'ecommerce_admin',
    'password':"password",
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
                          firstname VARCHAR(50) NOT NULL,
                          lastname VARCHAR(50) NOT NULL,
                          username VARCHAR(50) UNIQUE NOT NULL,
                          email VARCHAR(100) UNIQUE NOT NULL,
                          phone VARCHAR(15),
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
  
  
def insert_product(name,description,price,stock,image_url,category):
  conn = get_connection()
  cursor = get_cursor(conn)
  
  query= '''INSERT INTO products(name,description,price,stock,image_url,category)VALUES(%s,%s,%s,%s,%s,%s);'''
  cursor.execute(query , (name,description,price,stock,image_url,category))
  
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
  try:
    
    select_product_query = '''
    SELECT id,name,description,price,stock,image_url,category FROM products
    WHERE id =%s;
    '''
    cursor.execute(select_product_query,(product_id,))
    product =cursor.fetchone()
    if not product:
      return None
    
    return {
      'id':product[0],
      'name':product[1],
      'description':product[2],
      'price':float(product[3]),
      'stock':product[4],
      'image_url':product[5],
      'category':product[6]
    }
    
  except Exception as ex:
    Logger.error(f"Error fetching product by ID: {ex}")
    return None
  
  finally:
    cursor.close()
    conn.close()


  def generate_password_hash(password):
    #hashing function to generate password hash
    return psycopg2.extensions.PYCHARS(password)
  
  

# return all categories  
def get_all_categories():
  
  conn = get_connection()
  cursor = get_cursor(conn)
  
  query = '''SELECT DISTINCT category FROM products ORDER BY category'''
  
  try:
    cursor.execute(query)
    # categories = cursor.fetchall()
    categories = [row[0] for row in cursor.fetchall()]
    print(type(categories))
    return categories
  except Exception as e:
    print(f"Error getting categories {e}")
    return []
  finally:
    cursor.close()
    conn.close()
  
# categories = get_all_categories()
# print(f"categories {categories}")


# get fltered products
def get_filtered_products(search_query='', categories=None, min_price=None, max_price=None, 
                        rating=None, in_stock_only=False, sort_by='featured'):
  conn = get_connection()
  cursor=get_cursor(conn)
  
  
  try:
        # Base query
        query = """
            SELECT * FROM products 
            WHERE 1=1
        """
        params = []
        
        # Search filter
        if search_query:
            query += " AND (name ILIKE %s OR description ILIKE %s)"
            params.extend([f'%{search_query}%', f'%{search_query}%'])
        
        # Category filter
        if categories:
            placeholders = ','.join(['%s'] * len(categories))
            query += f" AND category IN ({placeholders})"
            params.extend(categories)
        
        # Price range filter
        if min_price is not None:
            query += " AND price >= %s"
            params.append(min_price)
        
        if max_price is not None:
            query += " AND price <= %s"
            params.append(max_price)
        
        # Rating filter
        if rating is not None:
            query += " AND rating >= %s"
            params.append(rating)
        
        # Stock filter
        if in_stock_only:
            query += " AND stock > 0"
        
        # Sorting
        sort_options = {
            'featured': 'id DESC',
            'price-low': 'price ASC',
            'price-high': 'price DESC',
            'name': 'name ASC',
            'rating': 'rating DESC',
            'newest': 'created_at DESC'
        }
        sort_clause = sort_options.get(sort_by, 'id DESC')
        query += f" ORDER BY {sort_clause}"
        print(f'paramsssss {params}')
        cursor.execute(query, params)
        products = cursor.fetchall()
        return products
        
  except Exception as e:
        print(f"Error filtering products: {e}")
        return []
  finally:
        cursor.close()
        conn.close()
    
# products_filtered=get_filtered_products(search_query='Sample', categories=['electronics'], min_price=10, max_price=30, in_stock_only=True, sort_by='price-low')
# print(f"filtered products: {products_filtered}")
  
  
# get product by category
def get_product_by_category(category):
  conn = get_connection()
  cursor = get_cursor(conn)
  query = '''SELECT * FROM products WHERE category = %s ORDER BY name'''
  try:
    cursor.execute(query,(category,))
    products= cursor.fetchall()
    return(products)
  except Exception as ex:
    print(f"Error getting products by category:{ex}")
    
  finally :
    conn.close()
    cursor.close()
    
    
# products_by_category = get_product_by_category('food')
# print(f"products by category {products_by_category}")





# hash passwords
def hash_paswrd(password):
  password = password.encode('utf-8')
  hashed = bcrypt.hashpw(password,bcrypt.gensalt())
  hashed_password = hashed
  return hashed_password
  
  


# password,hashed_password = hash_paswrd('password')


# print(f'encoded password {password}, {hashed_password}')




def check_password(password,hashed):
  password = password.encode('utf-8')
  print(type(hashed))
  hashed = hashed.encode('utf-8')
  value = bcrypt.checkpw(password,hashed)
  return value



# verify user for login
def verify_user_login(username,password):
  conn = get_connection()
  cusror = get_cursor(conn)
  
  try:
    query = '''SELECT password_hash, username FROM users  where username = %s'''
    
    cusror.execute(query,(username,))
    row = cusror.fetchone()
    if row is None:
      return {'Failed': 'invalid username or password'}
    password_hash,username  = row
    print(type(username))
    print('password hash')
    print(type(password_hash))
    print(username)
    print(f'password_hash:{password_hash}')
    print(f'password {password}')
    # if password == password_hash:
    #   return {
    #     'success':'verification successfull',
    #   }
    # else:
    #   return {
    #     'Failed':'invalid username or password'
    #   }
    
    status = check_password(password,password_hash)
    if status ==True:
      return {
        'success':'verification successfull',
      }
    else:
      return {
        'Failed':'invalid username or password'
      }
      
  except Exception as ex:
        print(f' verify user login error {ex}')
      
  finally:
    cusror.close()
    conn.close()


# signup helper
def register_details(*args):
  conn = get_connection()
  cursor = get_cursor(conn)
  print('function called')
  print(f'args received {args}')
  password = args[5]
  print(password)
  password = hash_paswrd(password).decode('utf-8')
  print(password)
  
  try:
    query = '''INSERT into USERS (firstname,lastname,username,email,phone,password_hash) VALUES (%s,%s,%s,%s,%s,%s)'''
    cursor.execute(query,(args[0],args[0],args[0],args[0],args[0],password))
    conn.commit()
    print('user registered successfully')
  except Exception as e:
    print(f'error registering details {e}')
  finally:
    cursor.close()
    conn.close()
  
  
  
# status = verify_user_login('kiki','password')
# print(status)