from flask import Flask
import psycopg2
import flask

#initialize the flask app
app = Flask(__name__)


##Database connection parameters
conn = {
  'dbname':'ecommerce',
  'user':'ecom',
  'password':"ecom",
  'host':'localhost',
  "port":5432
}

@app.route('/')
def home():
  return "Welcom eto the E-commerce Site!"


if __name__=='__main__':
  app.run(debug=True)