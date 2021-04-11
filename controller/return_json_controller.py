from flask import Flask, jsonify, abort, request

app = Flask(__name__)


@app.route('/hello', methods=['GET'])
def get_tasks():
    return 'hello'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5050', debug=True)
