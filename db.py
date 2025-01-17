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


def register_user(username,email,password):
  conn = get_connection()
  cursor = get_cursor(conn)
  
  insert_user_query = '''INSERT INTO users (username,email,password_hash)
  VALUES(%s,%s,%s);''' 
  cursor.execute(insert_user_query,(username,email,generate_password_hash(password)))
  conn.commit()
  cursor.close()
  conn.close()
  
  def generate_password_hash(password):
    #hashing function to generate password hash
    return psycopg2.extensions.PYCHARS(password)
  