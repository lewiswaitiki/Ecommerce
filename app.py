from flask import Flask, request, redirect , flash ,session,url_for , render_template
import psycopg2
import werkzeug.security
import db
import werkzeug
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import logging
from db import get_connection , create_product_table,get_cursor , insert_sample_products,get_all_products,get_product_by_id
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from base64 import b64decode


logging.basicConfig(level=logging.INFO)


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
    #hash password
    # password_hash= werkzeug.security.generate_password_hash(password)
    password_hash= generate_password_hash(password)
    #create user data
    user = {'username':username,
            'email':email,
            'password_hash':password_hash
            }
    #save user to the database
    conn = get_connection()
    cursor = get_cursor(conn)
    insert_user_query = '''INSERT INTO users (username,email,password_hash)
    VALUES(%s,%s,%s);'''
    cursor.execute(insert_user_query,(username,email,password_hash))
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
    
    
    if not username or not password:
      flash('please enter both username and password')
      return redirect(url_for('login'))
    
    conn = db.get_connection()
    try:
      # cursor=conn.cursor()
      with conn.cursor() as cursor:
        select_user_query = '''SELECT id,password_hash FROM users WHERE username = %s ;'''
        cursor.execute(select_user_query , (username,))
        user = cursor.fetchone()
        print("user")
        print(user)
      if user and check_password_hash(user[1],password):
        flash('Login successful!')
        session['user_id']= user[0]
        return redirect(url_for('home'))
      else:
          flash('invalid username or password')
    except Exception as e:
      flash(f'An error occurred.please try again later.{e}')
      app.logger.error(f"Login error: {e}")
    finally:
      conn.close()
  return render_template(('login.html'))


@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
  product =get_product_by_id(product_id)
  if product is None:
    flash(f"product with ID {product_id} not found!")
    return redirect(url_for('home'))
  if 'cart' not in session:
    session['cart']={}
    
  cart = {int(k): v for k , v in session['cart'].items()}
  
  if product_id in cart:
    cart[product_id] +=1
  else:
    cart[product_id]=1
    
  session['cart']= cart
  logging.info("------session cart after adding item------")
  print(session['cart'])
  flash('Product added to cart!')
  print('Added to cart')
  return redirect(url_for('home'))



@app.route('/cart')
def view_cart():
  if 'cart' not in session or len(session['cart'])==0:
    print("cart is empty")
    flash('Your cart is empty!')
    return redirect(url_for('home'))
  
  cart = {int(k):v for k,v in session['cart'].items()}
  cart_products = []
  product_ids = session['cart']
  for product_id , quantity  in cart.items():
    product =db.get_product_by_id(product_id)
    if product:
      cart_products.append((product,quantity))
      logging.info("---cart products----")
      print(cart_products)
    else:
      flash(f"Product with ID {product_id} not found!")
  
  return render_template('cart.html',products=cart_products)  


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
  if 'cart' in session:
    logging.info("----cart to be deleted-----")
    cart ={ int(k):v for k,v in session['cart'].items()}
    print(cart)
    try:
      
      del cart[product_id]
      print(f"product with id {product_id} removed")
      flash(f'product {product_id} removed from cart!')
    except ValueError:
      flash(f'product {product_id} not found in cart!')
      
    else:
      flash(f'No products in cart to remove.')
    session['cart'] = cart
  return redirect(url_for('view_cart'))
      
      
@app.route('/clear_session')
def clear_session():
  session.clear()
  flash('Session cleared!')
  return redirect(url_for('home'))
  
  
@app.route('/update_quantity/<int:product_id>',methods=['POST'])
def update_quantity(product_id):
  try:
    quantity = int(request.form['quantity'])
    
    if 'cart' in session:
      cart = {int(k):v for k,v in session['cart'].items()}
      if product_id in cart:
        if quantity <=0:
          del cart[product_id]
        else:
          cart[product_id] = quantity
          session['cart']= cart
          flash(f"Quantity for product {product_id} updated! ")
      else:
        flash(f"product {product_id} not found in cart")
    else:
      flash("No items in cart to update")
    return redirect(url_for('view_cart'))
  except Exception as e:
    flash(f"An error eccurred: {e}")
    return redirect(url_for('view_cart'))
  
@app.route('/profile' , methods = ['GET', 'POST'])
def profile():
  if 'user_id' not in session:
    flash(f"please log in to  access your profile")
    print(f"please log in to  access your profile")
    return redirect(url_for('login'))
  
  user_id = session['user_id']
  
  if request.method == "POST":
    username = request.form['username']
    email = request.form['email']

    conn = get_connection()
  
    try:
      with conn.cursor()  as cursor:
        update_user_query ='''UPDATE users SET username=%s, email=%s WHERE id =%s;'''
        cursor.execute(update_user_query, (username,email,user_id))
        conn.commit()
        flash('profile updated successfully!')
    except Exception as e:
      flash(f"An error occurred.please try again later. {e}")
      app.logger.error(f"profile update error {e}")
      print(f"{e}")
    
    finally:
      conn.close()
  
  conn = db.get_connection()
  try:
    with conn.cursor() as cursor:
      select_user_query = '''SELECT  username,email FROM users  WHERE id=%s;'''
      cursor.execute(select_user_query, (user_id,))
      user = cursor.fetchone()
  finally:
    conn.close()
    
  print(user)
  return render_template('profile.html',user=user)


@app.route('/mpesa_callback' , methods = ['POST'])
def call_back_url():
  data = request.get_json()

  #process the callback data recieved
  print(f"Callback data recieved: {data}")
  if data:
    print(data)
  else:
    print(f"No data ")
  
  return "Callback received",200



if __name__=='__main__':
  app.run(debug=True)
  
  print()