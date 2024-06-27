from flask import Flask, render_template, jsonify, request
from utils import predictTags, tags
app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/getOutput', methods=['POST'])
def getOutput():
    inp = request.json["tetxtInput"]
    output = predictTags(inp, 35, 18)
    return jsonify({"output":output})

@app.route('/getTags')
def getTags():
    return jsonify(tags)

if __name__ == '__main__':
    app.run(debug=True)