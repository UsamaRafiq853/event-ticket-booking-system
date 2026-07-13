from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from database import check_database_connection

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


@app.route("/api/database-health")
def database_health():
    success, message = check_database_connection()

    status_code = 200 if success else 500

    return jsonify({
        "success": success,
        "message": message
    }), status_code


if __name__ == "__main__":
    app.run(
        debug=Config.FLASK_DEBUG,
        port=Config.PORT
    )