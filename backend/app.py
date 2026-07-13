from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return jsonify({
        "project": "Event Ticket Booking System",
        "status": "Backend Running"
    })


@app.route("/api/health")
def health():
    return jsonify({
        "success": True,
        "message": "API is running successfully"
    })


if __name__ == "__main__":
    app.run(debug=True)