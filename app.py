from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

@app.route('/')
def root():
    return "Working"

@app.route('/hello')
def new_one_function():
    username = request.args.get('name')
    print(username)
    return 'Hi ' + username

# 127.0.0.1:5000/sum?a=1&b=2
@app.route('/sum')
def my_sum():
    a = request.args.get('a')
    a = int(a)
    b = int(request.args.get('b'))
    answer = a + b
    return str(answer)

# http://127.0.0.1:5000/mypage?name=Wattanai
@app.route('/mypage')
def mypage():
    username = request.args.get('name')
    return render_template('home.html', name=username)

if __name__ == "__main__":
    app.run(debug = True, host="0.0.0.0", port=5000)