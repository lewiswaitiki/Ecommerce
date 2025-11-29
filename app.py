from flask import Flask, request, redirect , flash ,session,url_for , render_template
import db
import logging
from db import get_connection , create_product_table,get_cursor , insert_sample_products,get_all_products,get_product_by_id
logging.basicConfig(level=logging.INFO)


#initialize the flask app
app = Flask(__name__)
app.secret_key = 'key'






@app.route('/login',methods=['GET', 'POST'])
def login():
  
  if request.method =='POST':
    username = request.form.get('username', '')
    password = request.form['password']
    
    login = db.verify_user_login(username,password)
    print(login,'login result')
    
    if 'success' in login:
      return redirect(url_for('home'))
    
    else:
      flash("Invalid username or password", "error")
      return render_template('login.html')
  
  return render_template('login.html')
  
  


@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method =='POST':
    first_name = request.form.get('firstname', '')
    secondname = request.form.get('secondname', '')
    username = request.form.get('username', '')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    password_confirm = request.form.get('password_confirm', '')
    print(first_name,secondname,username,phone,email,password,password_confirm)
    db.register_details(first_name,secondname,username,phone,email,password,password_confirm)
  return render_template('register.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
  # db.create_user_table()
  # db.create_product_table()
  # db.insert_sample_products()
  # products =db.get_all_products()
  # return render_template('home.html',products=products)
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.getlist('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    rating_filter = request.args.get('rating', type=int)
    in_stock_only = request.args.get('in_stock', type=bool)
    sort_by = request.args.get('sort', 'featured')
    
    # get filtered products
    products = db.get_filtered_products(
      search_query =search_query,
      categories = category_filter,
      min_price = min_price,
      max_price = max_price,
      rating = rating_filter,
      in_stock_only = in_stock_only,
      sort_by = sort_by
    )
    
    # Get unique categories for filter sidebar
    categories = db.get_all_categories()
    
    
    return render_template('home.html' , 
                          products=products,
                          categories = categories,
                          search_query=search_query,
                          selected_categories=category_filter,
                          min_price=min_price,
                          max_price=max_price,
                          rating_filter=rating_filter,
                          in_stock_only=in_stock_only,
                          sort_by=sort_by
                          )

  
  
@app.route('/products')
def products():
  # get filter parameters from query string
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.getlist('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    rating_filter = request.args.get('rating', type=int)
    in_stock_only = request.args.get('in_stock', type=bool)
    sort_by = request.args.get('sort', 'featured')
    
    # get filtered products
    products = db.get_filtered_products(
      search_query =search_query,
      categories = category_filter,
      min_price = min_price,
      max_price = max_price,
      rating = rating_filter,
      in_stock_only = in_stock_only,
      sort_by = sort_by
    )
    
    # Get unique categories for filter sidebar
    categories = db.get_all_categories()
    
    
    return render_template('products.html' , 
                          products=products,
                          categories = categories,
                          search_query=search_query,
                          selected_categories=category_filter,
                          min_price=min_price,
                          max_price=max_price,
                          rating_filter=rating_filter,
                          in_stock_only=in_stock_only,
                          sort_by=sort_by
                          )


@app.route('/product/<int:product_id>')
def product_detail(product_id):
  product = db.get_product_by_id(product_id)
  if product is None:
    flash(f"Product with ID {product_id} not found!", "error")
    return redirect(url_for('home'))
  return render_template('product_detail.html', product=product)


# add product route
@app.route('/add_product',methods=['GET','POST'])
def add_product():
  if request.method == 'POST':
    product_name = request.form['name']
    price= request.form['price']
    price = float(price)
    quantity = request.form['quantity']
    quantity = int(quantity)
    image_url = request.form['image_url']
    category = request.form['category']
    description = request.form['description']
    
    db.insert_product(product_name,description,price,quantity,image_url,category)
    flash("Product added successfully!", "success")
    return redirect(url_for('home'))
  return render_template('add_product.html')

# @app.route('/register', methods = ['GET','POST'])
# def register():
#   if request.method == 'POST':
#     username = request.form['username']
#     email = request.form['email']
#     password = request.form['password']
#     user = {'username':username,
#             'email':email,
#             # 'password_hash':generate_password_hash(password)
#             'password':password
#             }
#     conn = get_connection()
#     cursor = get_cursor(conn)
#     insert_user_query = '''INSERT INTO users (username,email,password_hash)
#     VALUES(%s,%s,%s);'''
#     cursor.execute(insert_user_query,(username,email,password))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     flash('Registration successful!')
#     return redirect(url_for('login'))
  
#   return render_template('register.html')

# @app.route('/login', methods=['GET','POST'])
# def login():
#   if request.method == 'POST':
#     username = request.form['username']
#     password  = request.form['password']
    
#     print(f"{username}\n{password}")
    
#     if not username or not password:
#       flash('please enter both username and password')
#       return redirect(url_for('login'))
    
#     conn = db.get_connection()
#     try:
#       # cursor=conn.cursor()
#       with conn.cursor() as cursor:
#         select_user_query = '''SELECT id,password_hash FROM users WHERE username = %s AND password_hash = %s;'''
#         cursor.execute(select_user_query,(username,password))
#         user = cursor.fetchone()
#         print("user")
#         print(user)
#       if user:
#         flash('Login successful!')
#         return redirect(url_for('home'))
#       else:
#           flash('invalid username or password')
#     except Exception as e:
#       flash(f'An error occurred.please try again later.{e}')
#       app.logger.error(f"Login error: {e}")
#     finally:
#       conn.close()
#   return render_template(('login.html'))


# @app.route('/add_to_cart/<int:product_id>')
# def add_to_cart(product_id):
#   product =get_product_by_id(product_id)
#   if product is None:
#     flash(f"product with ID {product_id} not found!")
#     return redirect(url_for('home'))
#   if 'cart' not in session:
#     session['cart']=[]
#   session['cart'].append(product_id)
#   flash('Product added to cart!')
#   print('Added to cart')
#   return redirect(url_for('home'))



# @app.route('/cart')
# def view_cart():
#   if 'cart' not in session or len(session['cart'])==0:
#     print("cart is empty")
#     flash('Your cart is empty!')
#     return redirect(url_for('home'))
  
#   cart_products = []
#   product_ids = session['cart']
#   for product_id in product_ids:
#     product =db.get_product_by_id(product_id)
#     if product:
#       cart_products.append(product)
#     else:
#       flash(f"Product with ID {product_id} not found!")
  
#   return render_template('cart.html',products=cart_products)  


# @app.route('/remove_from_cart/<int:product_id>')
# def remove_from_cart(product_id):
#   if 'cart' in session:
#     try:
#       session['cart'].remove(product_id)
#       flash(f'product {product_id} removed from cart!')
#     except ValueError:
#       flash(f'product {product_id} not found in cart!')
      
#     else:
#       flash(f'No products in cart to remove.')
#     return redirect(url_for('view_cart'))
      
if __name__=='__main__':
  app.run(debug=True)
  
  print()