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
    query = '''SELECT password_hash,id FROM users  where username = %s'''
    
    cusror.execute(query,(username,))
    row = cusror.fetchone()
    if row is None:
      return {'Failed': 'invalid username or password'}
    password_hash,id  = row
    # print(type(username))
    # print('password hash')
    # print(type(password_hash))
    # print(username)
    # print(f'password_hash:{password_hash}')
    # print(f'password {password}')
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
        'id':id
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
    query = '''INSERT into USERS (firstname,lastname,username,phone,email,password_hash) VALUES (%s,%s,%s,%s,%s,%s)'''
    cursor.execute(query,(args[0],args[1],args[2],args[3],args[4],password))
    conn.commit()
    print('user registered successfully')
  except Exception as e:
    print(f'error registering details {e}')
  finally:
    cursor.close()
    conn.close()
  
  
  
# status = verify_user_login('kiki','password')
# print(status)



# retrieve cart details
def fetch_cart(user_id):
  conn = get_connection()
  cursor = get_cursor(conn)
  
  try:
    query = '''SELECT p.name, p.price ,p.image_url, c.quantity, p.id FROM cart_items c JOIN products p ON c.product_id = p.id WHERE c.user_id = %s'''
    cursor.execute(query,(user_id,))
    cart_items = cursor.fetchall()
    print (f'cart items {cart_items}')
    total = sum([row[1] * row[3] for row in cart_items])
    item_count = get_cart_item_count(user_id)
    return cart_items,total,item_count
  
  except Exception as e:
    print(f'Error {e}')
    
  finally:
    cursor.close()
    conn.close()
    


# add to cart 
def add_to_cart(user_id,product_id,quantity):
  conn =get_connection()
  cursor = get_cursor(conn)
  
  try:
    query =(
      '''SELECT id, quantity FROM cart_items WHERE user_id=%s AND product_id =%s'''
    )
    
    cursor.execute(query,(user_id,product_id))
    row = cursor.fetchone()
    
    if row:
      new_quantity = row[1] + quantity
      query = '''UPDATE cart_items SET  quantity =%s WHERE id =%s'''
      cursor.execute(query,(new_quantity,row[0]))
    
    else:
      
      query = '''INSERT INTO cart_items(user_id,product_id,quantity)VALUES(%s,%s,%s)''' 
      cursor.execute(query,(user_id,product_id,quantity))
    
    conn.commit()
    # get updated cart count
    cursor.execute("SELECT COALESCE(SUM(quantity),0) FROM cart_items WHERE user_id=%s", (user_id,))
    cart_count = cursor.fetchone()[0]
    
    return {"success": True, "message": "Item added to cart", "cart_count": cart_count}
      
  except Exception as e:
    print("Error",e)
    return ({"success":False,"message": "Error adding to cart"})
  
  
  finally:
      cursor.close()
      conn.close()
      
      
# update cart
def update_cart_helper(quantity,user_id,product_id):
  conn = get_connection()
  cursor = get_cursor(conn)
  
  try:
    query='''UPDATE cart_items SET quantity=%s WHERE user_id=%s AND product_id=%s'''
    cursor.execute(query,(quantity, user_id, product_id))
    conn.commit()
    
    # get updated individual product count and total 
    query = '''SELECT COALESCE(SUM(quantity),0) FROM cart_items WHERE user_id=%s AND product_id=%s'''
    cursor.execute(query, (user_id, product_id))
    product_count = cursor.fetchone()[0]
    
    query = '''SELECT COALESCE(SUM(p.price * c.quantity),0) FROM cart_items c JOIN products p ON c.product_id=p.id WHERE c.user_id=%s AND c.product_id=%s'''
    cursor.execute(query, (user_id, product_id))
    product_total = cursor.fetchone()[0]
    
    # get updated individual product count and total
    query = '''SELECT COALESCE(SUM(quantity),0) FROM cart_items WHERE user_id=%s'''
    cursor.execute(query, (user_id,))
    cart_count = cursor.fetchone()[0]
    
    query = '''SELECT COALESCE(SUM(p.price * c.quantity),0) FROM cart_items c JOIN products p ON c.product_id=p.id WHERE c.user_id=%s'''
    cursor.execute(query, (user_id,))
    total = cursor.fetchone()[0]

    return {"success": True, "message": "Item count updated", "cart_count": cart_count, "total": float(total), "product_count": product_count, "product_total": float(product_total)}
    
  except Exception as e:
    print(f'error updating cart {e}')
    return {"success": False, "message": "Error updating cart"}
  finally:
    cursor.close()
    conn.close()
    
    
# delete item from cart
def delete_from_cart(user_id,product_id):
  conn = get_connection()
  cursor = get_cursor(conn)

  try:
    query = '''DELETE FROM cart_items WHERE user_id=%s AND product_id=%s'''
    cursor.execute(query,(user_id, product_id))
    conn.commit()
    # get updated cart count and total
    cursor.execute("SELECT COALESCE(SUM(quantity),0) FROM cart_items WHERE user_id=%s", (user_id,))
    cart_count = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(p.price * c.quantity),0) FROM cart_items c JOIN products p ON c.product_id=p.id WHERE c.user_id=%s", (user_id,))
    total = cursor.fetchone()[0]

    return {"success": True, "cart_count": cart_count, "total": float(total)}
  
  except Exception as e:
    print(f'error deleting cart item {e}')
    return {"success": False, "message": "Error deleting cart item"}
    
  finally:
    cursor.close()
    conn.close()
    
    
# cart total
def get_cart_total(user_id):
  conn = get_connection()
  cursor = get_cursor(conn)
  
  try:
    query = '''SELECT COALESCE(SUM(p.price * c.quantity),0) FROM cart_items c JOIN products p ON c.product_id=p.id WHERE c.user_id=%s'''
    cursor.execute(query,(user_id,))
    total = cursor.fetchone()[0]
    return float(total)
    
  except Exception as e:
    print(f'error getting cart total {e}')
    return 0.0
  finally:
    cursor.close()
    conn.close()
    

# get total items in cart
def get_cart_item_count(user_id):
  conn = get_connection()
  cursor = get_cursor(conn)
  
  try:
    query = '''SELECT COALESCE(SUM(quantity),0) FROM cart_items WHERE user_id=%s'''
    cursor.execute(query,(user_id,))
    count = cursor.fetchone()[0]
    return count
  except Exception as e:
    print(f'error getting cart item count {e}')
    return 0
  finally:
    cursor.close()
    conn.close()
    
    

# crete order
def create_order(user_id, total, cart_items):
    conn = get_connection()
    cursor = get_cursor(conn)
    try:
        # Insert order and get its ID
        cursor.execute(
            '''INSERT INTO orders (user_id, total) VALUES (%s, %s) RETURNING id''',
            (user_id, total)
        )
        order_id = cursor.fetchone()[0]

        # Insert all items into order_items
        for item in cart_items:
            cursor.execute(
                '''INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)''',
                (order_id, item[4], item[3], item[1])
            )

        # Clear cart once after inserting all items
        cursor.execute("DELETE FROM cart_items WHERE user_id=%s", (user_id,))
        conn.commit()

        return {"success": True, "order_id": order_id, "total": float(total)}

    except Exception as e:
        print("Checkout error:", e)
        return {"success": False, "message": "Checkout failed"}

    finally:
        cursor.close()
        conn.close()
