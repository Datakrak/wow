import os
import sys
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/default')
def default():
    return "Default gateway. No exit."

if __name__ == "__main__":
    app.run()
