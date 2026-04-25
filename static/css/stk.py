import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
load_dotenv()
import os

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
    
    
print(os.getenv("CONSUMER_KEY"))

# access_token = get_access_token(os.getenv("CONSUMER_KEY"), os.getenv("CONSUMER_SECRET"))
# print("Access Token:", access_token)