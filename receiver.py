from flask import Flask, request

app = Flask(__name__)

latest_message = "No messages yet"

@app.route('/message', methods=['POST'])
def receive_message():
    global latest_message
    data = request.json
    latest_message = data.get("message", "")
    print("Received:", latest_message)
    return {"status": "ok"}

@app.route('/get')
def get_message():
    return {"message": latest_message}

app.run(host='0.0.0.0', port=5000)
