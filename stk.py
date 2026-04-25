import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
load_dotenv()
import os
import base64
from datetime import datetime

passkey = os.getenv("PASSKEY")
print('Passkey from env:', passkey)
shortcode = os.getenv("SHORTCODE")
callback = os.getenv("BASE_URL")
print('Callback URL from env:', callback)
test = os.getenv("TEST")


def sanitize_phone(phone):
    phone = phone.strip().replace(" ", "")
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif phone.startswith("+254"):
        phone = phone[1:]
    return phone



def get_access_token(consumer_key, consumer_secret):

    token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth = HTTPBasicAuth(consumer_key, consumer_secret)
    headers = {"Content-Type": "application/json"}
    data = {"grant_type": "client_credentials"}

    response =requests.get(token_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token
    else:
        raise Exception("Failed to obtain access token: {}".format(response.text))
    
    






def generate_password():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = shortcode + passkey + timestamp
    return base64.b64encode(data_to_encode.encode()).decode(), timestamp


def initiate_stk_push(phone_number, amount, account_reference, transaction_desc):
    phone_number = sanitize_phone(phone_number)
    password =generate_password()[0]
    timestamp =generate_password()[1]
    access_token = get_access_token(os.getenv("CONSUMER_KEY"), os.getenv("CONSUMER_SECRET"))
    print('Callback URL from env:', callback)
    callback_url = f"{callback}/callback"
    print('Test variable from env:', test)
    print('Passkey from env:', passkey)
    print('callback url:', callback_url)
    print("Generated Password:", password)
    stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "BusinessShortCode": "174379",
        "Password": password,  # You need to generate this password
        "Timestamp": timestamp,  # Current timestamp in the format YYYYMMDDHHMMSS
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": "174379",
        "PhoneNumber": phone_number,
        "CallBackURL":F'{callback}/callback' ,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }

    response = requests.post(stk_push_url, json=payload, headers=headers)

    if response.status_code == 200:
        print("STK Push initiated successfully:", response.json())
        return response.json()
    else:
        raise Exception("STK Push request failed: {}".format(response.text))
    
    
