from flask import Flask, request, redirect , flash ,session,url_for , render_template,session,jsonify
import db
import logging
from db import get_connection , create_product_table,get_cursor , insert_sample_products,get_all_products,get_product_by_id,update_cart_helper,delete_from_cart,get_cart_item_count,fetch_cart,create_order
logging.basicConfig(level=logging.INFO)


#initialize the flask app
app = Flask(__name__)
app.secret_key = 'key'






@app.route('/login',methods=['GET', 'POST'])
def login():
  
  if request.method =='POST':
    username = request.form.get('username', '')
    password = request.form['password']
    
    result = db.verify_user_login(username,password)
    print(result)    
    if result and 'success' in result:
      session['user_id'] = result.get('id')
      print(session)
      print(f'id{result.get("id")}')
      return redirect(url_for('home'))
    
    else:
      flash("Invalid username or password", "error")
      return render_template('login.html')
  
  return render_template('login.html')
  
  


@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method =='POST':
    first_name = request.form.get('firstname', '')
    lastname = request.form.get('secondname', '')
    username = request.form.get('username', '')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    password_confirm = request.form.get('password_confirm', '')
    print(first_name,lastname,username,phone,email,password,password_confirm)
    db.register_details(first_name,lastname,username,phone,email,password,password_confirm)
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
    
    if 'user_id' in session:
      user_id = session['user_id']
      cart_count = get_cart_item_count(user_id)
      
    
    return render_template('home.html' , 
                          products=products,
                          categories = categories,
                          search_query=search_query,
                          selected_categories=category_filter,
                          min_price=min_price,
                          max_price=max_price,
                          rating_filter=rating_filter,
                          in_stock_only=in_stock_only,
                          sort_by=sort_by,
                          cart_count =cart_count
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



# add to cart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
  if 'user_id' not in session:
    flash('please log in to add items to your cart','error')
    return jsonify({'success':False,"message":"please log in"})
  
  data = request.get_json()
  product_id = data.get('product_id')
  user_id = session['user_id']
  quantity = int(data.get('quantity',1))
  print(f'data{data},product_id{product_id},user_id{user_id},quantity{quantity}')
  result = db.add_to_cart(user_id,product_id,quantity)
  
  return jsonify(result)

@app.route('/cart')
def view_cart():
  if 'user_id' not in session:
    return redirect(url_for('login'))
  
  user_id = session.get('user_id')
  cart_items, total,item_count =  db.fetch_cart(user_id)
  print(f"cart_items: {cart_items}, total: {total}")
  print(cart_items)
  return render_template('cart.html',cart_items=cart_items, total=total,item_count=item_count)  


@app.route('/update_cart',methods=['POST'])
def update_cart():
  if 'user_id' not in session:
    return jsonify({'success':False}),401
  
  data = request.get_json()
  user_id = session['user_id']
  product_id = data['product_id']
  quantity = data['quantity']
  
  result = update_cart_helper(quantity,user_id,product_id)
  
  return jsonify(result)


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'user_id' not in session:
        return jsonify({"success": False}), 401
    data = request.get_json()
    print(f"data: {data}")
    user_id = session['user_id']
    product_id = data['product_id']
    result = delete_from_cart(user_id,product_id)
    return jsonify(result)
  

@app.route('/checkout', methods=['POST','GET'])
def checkout():
    if request.method == 'GET':
      return render_template('checkout.html')
    
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart_items, total,item_count = fetch_cart(user_id)

    if not cart_items:
        return jsonify({"success": False, "message": "Cart is Empty"})

    result = create_order(user_id, total, cart_items)

    if result["success"]:
        return render_template(
            'checkout.html',
            order_id=result["order_id"],
            total=result["total"],
            cart_items=cart_items
        )
    else:
        return jsonify(result)


@app.route('/orders')
def orders():
    # fetch user orders from DB
    return 'orders'




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