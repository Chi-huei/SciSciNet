from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import process_user_query

app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    result = process_user_query(user_message)

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
