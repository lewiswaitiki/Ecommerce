from flask import Flask, request, redirect , flash ,session,url_for , render_template,session,jsonify
import json
from dotenv import load_dotenv
import os
# import db
import logging
from db import fetch_all_users, get_connection , create_product_table,get_cursor, get_filtered_products, get_user_by_id, insert_product , insert_sample_products,get_all_products,get_product_by_id, save_payments,update_cart_helper,delete_from_cart,get_cart_item_count,fetch_cart,create_order,get_order_details,register_details,get_all_categories, verify_user_login,add_item_to_cart,mpesa_payment_mapping,find_order_id_from_checkout_map,get_user_by_order_id,get_payment_by_order_id,fetch_admin_order_stats
from stk import initiate_stk_push
logging.basicConfig(level=logging.INFO)
import requests
import time
load_dotenv('.env')

#initialize the flask app
app = Flask(__name__)
app.secret_key = 'key'






@app.route('/login',methods=['GET', 'POST'])
def login():
  
  if request.method =='POST':
    username = request.form.get('username', '')
    password = request.form['password']
    
    result =verify_user_login(username,password)
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
  
  
@app.route('/logout')
def logout():
  session.pop('user_id',None)
  return redirect(url_for('home'))


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
    register_details(first_name,lastname,username,phone,email,password,password_confirm)
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
    products = get_filtered_products(
      search_query =search_query,
      categories = category_filter,
      min_price = min_price,
      max_price = max_price,
      rating = rating_filter,
      in_stock_only = in_stock_only,
      sort_by = sort_by
    )
    
    # Get unique categories for filter sidebar
    categories = get_all_categories()
    cart_count = 0
    username = ""
    if 'user_id' in session:
      user_id = session['user_id']
      cart_count = get_cart_item_count(user_id)
      print(f'cart_count: {cart_count}')
      username =get_user_by_id(user_id)['username']
    
    return render_template('home.html', 
                          products=products,
                          categories = categories,
                          search_query=search_query,
                          selected_categories=category_filter,
                          min_price=min_price,
                          max_price=max_price,
                          rating_filter=rating_filter,
                          in_stock_only=in_stock_only,
                          sort_by=sort_by,
                          cart_count =cart_count,
                          username = username 
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
    products = get_filtered_products(
      search_query =search_query,
      categories = category_filter,
      min_price = min_price,
      max_price = max_price,
      rating = rating_filter,
      in_stock_only = in_stock_only,
      sort_by = sort_by
    )
    
    # Get unique categories for filter sidebar
    categories = get_all_categories()
    
    
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
  product = get_product_by_id(product_id)
  if product is None:
    flash(f"Product with ID {product_id} not found!", "error")
    return redirect(url_for('home'))
  cart_count = 0
  if 'user_id' in session:
      user_id = session['user_id']
      cart_count = get_cart_item_count(user_id)
      print(f'cart_count: {cart_count}')
  return render_template('product_detail.html', product=product, cart_count=cart_count)


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
    
    insert_product(product_name,description,price,quantity,image_url,category)
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
  result = add_item_to_cart(user_id,product_id,quantity)
  
  return jsonify(result)

@app.route('/cart')
def view_cart():
  if 'user_id' not in session:
    return redirect(url_for('login'))
  
  user_id = session.get('user_id')
  cart_items, total,item_count =  fetch_cart(user_id)
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


@app.route('/get_cart_item_count')
def get_cart_items_count():
    cart_count = 0
    if 'user_id' in session:
        user_id = session['user_id']
        cart_count = get_cart_item_count(user_id)
    return jsonify({'cart_count': cart_count})

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
  

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart_items, total, item_count = fetch_cart(user_id)

    if not cart_items:
      return render_template('cart.html', message="Your cart is empty.")

    # GET request: just show checkout page with current cart
    return render_template('checkout.html', cart_items=cart_items, total=total, item_count=item_count)


@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    # fetch all orders for this user
    conn = get_connection()
    cursor = get_cursor(conn)
    cursor.execute("SELECT id, total, created_at FROM orders WHERE user_id=%s", (user_id,))
    orders_list = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('orders.html', orders=orders_list)


@app.route('/confirm_order', methods=['POST'])


@app.route('/order/<int:order_id>')
def order_confirmation(order_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    result = get_order_details(order_id, session['user_id'])
    if result and result["success"]:
        return render_template('confirm_order.html', 
                            order_details=result['order_details'])
    return redirect(url_for('home'))



@app.route('/pay/mpesa', methods=['POST'])
def pay_mpesa():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Not logged in"})

    user_id = session['user_id']

    # ✅ Parse JSON safely
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON payload"}), 400

    phone_number = data.get('phone_number')
    amount = data.get('amount')
    amount = int(float(amount)) 
    print(type(amount))
    print(f'phone {phone_number}, amount {amount}')

    # Fetch cart items
    cart_items, total, item_count = fetch_cart(user_id)
    if not cart_items:
        return jsonify({"success": False, "message": "Cart is empty"})

    
    
    # Initiate STK Push
    try:
        stk_response = initiate_stk_push(phone_number, amount, 'UnityStore', 'Unity payment')
        checkout_id = stk_response.get('CheckoutRequestID')
        # # Create order in DB
        result = create_order(user_id, total, cart_items)
        if not result["success"]:
            return jsonify(result)
        order_id = result["order_id"]
        print(f"Created order ID: {order_id}")
        # save mapping in DB
        mpesa_payment_mapping(order_id, checkout_id)
        # You can also save order_id here if you want
    
        return jsonify(
          {"success": True, 
                        "stk_response": stk_response
                        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
      
      

@app.route('/callback', methods=['POST', 'GET'])
def callback():
  if request.method == 'POST':
    
    data = request.get_json()
    body = data.get('Body', {})
    print(f'"Received callback data:" {json.dumps(data, indent=4)}')
    stkCallback = body.get('stkCallback', {})
    resultCode = stkCallback.get('ResultCode')
    resultDesc = stkCallback.get('ResultDesc')
    metadata = stkCallback.get('CallbackMetadata', {})
    checkout_id = stkCallback.get('CheckoutRequestID')
    print(f'metadata: {json.dumps(metadata, indent=4)}')
    items = metadata.get('Item', []) if metadata else [] #transaction details
    print(f'items: {json.dumps(items, indent=4)}')
    meta = {} # to hold parsed metadata
    meta = {item.get('Name'): item.get('Value') for item in items}
    print("Parsed metadata:", json.dumps(meta, indent=4))
    order_id = find_order_id_from_checkout_map(checkout_id)
    if resultCode == 0:
        # Payment successful
        receipt = meta.get('MpesaReceiptNumber')
        amount = meta.get('Amount')
        phone = meta.get('PhoneNumber')
        transaction_date = meta.get('TransactionDate')
        user_id = get_user_by_order_id(order_id)
        print(f'order_id: {order_id}, user_id: {user_id}, amount: {amount}, receipt: {receipt}, phone: {phone}, transaction_date: {transaction_date}')
        save_payments(order_id,user_id,'mpesa',amount,receipt,phone,'success',resultCode,resultDesc,transaction_date)
        
        print("Payment successful:", resultDesc)
        # Here you can update order status in your database
        return jsonify(
          { 
            "success": True,
            "order_id": order_id, 
            "message": "Payment successful", 
            "receipt": receipt, 
            "amount": amount, 
            "phone": phone })
        # Payment failed
    else:
      print("Payment failed:", resultDesc)
      user_id = get_user_by_order_id(order_id)
      save_payments(
          order_id,
          user_id,
          'mpesa',
          meta.get('Amount') or 0,
          meta.get('MpesaReceiptNumber') or 'N/A',
          meta.get('PhoneNumber') or 'N/A',
          'failed',
          resultCode,
          resultDesc,
          meta.get('TransactionDate')
      )

      return jsonify({
          "success": False,
          "order_id": order_id,
          "message": f"Payment failed: {resultDesc}"
      })

  else:
    return "MPESA Callback Endpoint"



@app.route('/payment_status/<checkout_id>', methods=['GET'])
def payment_status(checkout_id):
    # Look up order/payment by checkout_id
    order_id = find_order_id_from_checkout_map(checkout_id)
    payment = get_payment_by_order_id(order_id)  # implement this to query DB

    if payment:
        return jsonify({
            "success": payment['status'] == 'success',
            "order_id": order_id,
            "status": payment['status'],
            "message": payment['result_desc'],
            "amount": payment['amount'],
            "receipt": payment.get('receipt')
        })
    else:
        return jsonify({
            "success": False,
            "order_id": order_id,
            "status": "pending",
            "message": "Payment not yet processed"
        })
        
        

@app.route('/admin/users')
def admin_all_users():
  raw_users = fetch_all_users()
  print(f'raw users{raw_users}')
  users = []
  total_users = len(raw_users)
  logging.info(f"users:{raw_users}")
  for user in raw_users:
        user_dict = {
            "id": user[0],
            "name": f"{user[1]} {user[2]}",
            "email": user[4],
            "joinDate": "2023-01-01",   # TODO: replace with real date column
            "status": "active" if user[7] else "inactive"
        }
        users.append(user_dict)
        print(f"users dic:{users}")

  return jsonify({"users": users, 
                  "total_users": total_users})
        

@app.route('/admin', methods=['GET', 'POST'])
def admin():
  return render_template('admin_dashboard.html')


# admin orders stats
@app.route('/admin/orders/stats')
def admin_orders_stats():
    total_orders = fetch_admin_order_stats()
    return jsonify({
        "total_orders": total_orders
    })






@app.route('/pay/pesapal', methods=['POST'])
def pay_pesapal():
    """
    Simple Pesapal payment integration
    Sends request to terminal service running on port 8080
    """
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid JSON"}), 400
        
        user_id = session['user_id']
        amount = data.get('amount', 0)
        payload = data.get('payload', {})
        
        # Get cart items
        cart_items, total, item_count = fetch_cart(user_id)
        if not cart_items:
            return jsonify({"success": False, "message": "Cart is empty"}), 400
        
        # Create order in database
        order_result = create_order(user_id, total, cart_items)
        if not order_result["success"]:
            return jsonify(order_result)
        
        order_id = order_result["order_id"]
        
        # Update payload with order reference
        payload['reference'] = f"Order_{order_id}_{int(time.time())}"
        payload['paymentdetails']['amount'] = float(total)
        
        # SEND TO TERMINAL SERVICE
        terminal_url = 'http://127.0.0.1:8080/'
        
        print(f"📤 Sending to terminal service: {payload}")
        
        try:
            response = requests.post(
                terminal_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"📥 Terminal service response: {response.status_code}")
            print(f"📥 Response body: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check if payment was successful
                response_msg = response_data.get('responsemsg', '').upper()
                response_code = response_data.get('responsecode', '')
                
                # Consider "APPROVAL" or "APPROVED" as success
                if response_msg in ['APPROVAL', 'APPROVED'] or response_code in ['00', '0']:
                    # Success - save payment
                    save_pesapal_payment(
                        order_id=order_id,
                        user_id=user_id,
                        amount=total,
                        status='success',
                        response_code=response_code or '00',
                        response_msg=response_data.get('responsemsg', 'APPROVED'),
                        response_desc=response_data.get('responsedesc', 'Payment approved')
                    )
                    
                    # Return success with 200 status
                    return jsonify({
                        "success": True,
                        "order_id": order_id,
                        "message": "Payment successful",
                        "response": response_data
                    }), 200
                else:
                    # Payment declined
                    save_pesapal_payment(
                        order_id=order_id,
                        user_id=user_id,
                        amount=total,
                        status='failed',
                        response_code=response_code or '99',
                        response_msg=response_data.get('responsemsg', 'DECLINED'),
                        response_desc=response_data.get('responsedesc', 'Payment declined')
                    )
                    
                    return jsonify({
                        "success": False,
                        "order_id": order_id,
                        "message": f"Payment declined: {response_data.get('responsedesc', 'Unknown error')}",
                        "response": response_data
                    }), 200  # Changed to 200 to handle error gracefully
            else:
                return jsonify({
                    "success": False,
                    "message": f"Terminal service returned status {response.status_code}"
                }), 200  # Changed to 200
                
        except requests.exceptions.ConnectionError:
            return jsonify({
                "success": False,
                "message": "Cannot connect to terminal service on port 8080. Is it running?"
            }), 200  # Changed to 200
        except requests.exceptions.Timeout:
            return jsonify({
                "success": False,
                "message": "Terminal service timeout. Please try again."
            }), 200  # Changed to 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Terminal service error: {str(e)}"
            }), 200  # Changed to 200
            
    except Exception as e:
        print(f"❌ Error in pay_pesapal: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 200  # Changed to 200


def save_pesapal_payment(order_id, user_id, amount, status, response_code, response_msg, response_desc):
    """Save Pesapal payment to database"""
    conn = get_connection()
    cursor = get_cursor(conn)
    
    try:
        cursor.execute("""
            INSERT INTO payments 
            (order_id, user_id, provider, amount, receipt_number, phone, status, result_code, result_desc, transaction_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            order_id,
            user_id,
            'pesapal',
            amount,
            response_code,
            '',
            status,
            response_code,
            f"{response_msg}: {response_desc}"
        ))
        
        conn.commit()
        print(f"✅ Pesapal payment saved for order {order_id}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Error saving Pesapal payment: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()
      
if __name__=='__main__':
  app.run(debug=True)
  
  print()