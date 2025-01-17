from flask import Flask, request, redirect , flash , url_for , render_template
import psycopg2
import db
import logging
from db import get_connection , create_product_table,get_cursor , insert_sample_products,get_all_products

logging.basicConfig(level=logging.DEBUG)


#initialize the flask app
app = Flask(__name__)
app.secret_key = 'key'


@app.route('/')
def home():
  db.create_user_table()
  db.create_product_table()
  # db.insert_sample_products()
  products =db.get_all_products()
  print("products")
  print(products)
  return render_template('home.html',products=products)
  
@app.route('/products')
def products():
  products = db.get_all_products()
  return render_template('products.html' , products=products)

@app.route('/register', methods = ['GET','POST'])
def register():
  if request.method == 'POST':
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    user = {'username':username,
            'email':email,
            # 'password_hash':generate_password_hash(password)
            'password':password
            }
    conn = get_connection()
    cursor = get_cursor(conn)
    insert_user_query = '''INSERT INTO users (username,email,password_hash)
    VALUES(%s,%s,%s);'''
    cursor.execute(insert_user_query,(username,email,password))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Registration successful!')
    return redirect(url_for('login'))
  
  return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password  = request.form['password']
    
    print(f"{username}\n{password}")
    
    if not username or not password:
      flash('please enter both username and password')
      return redirect(url_for('login'))
    
    conn = db.get_connection()
    try:
      # cursor=conn.cursor()
      with conn.cursor() as cursor:
        select_user_query = '''SELECT id,password_hash FROM users WHERE username = %s AND password_hash = %s;'''
        cursor.execute(select_user_query,(username,password))
        user = cursor.fetchone()
        print("user")
        print(user)
      if user:
        flash('Login successful!')
        return redirect(url_for('home'))
      else:
          flash('invalid username or password')
    except Exception as e:
      flash(f'An error occurred.please try again later.{e}')
      app.logger.error(f"Login error: {e}")
    finally:
      conn.close()
  return render_template(('login.html'))
      
if __name__=='__main__':
  app.run(debug=True)