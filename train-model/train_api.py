from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/trainModel', methods = ['POST'])
def post():
    print("x")

