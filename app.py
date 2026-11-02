from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

import os

from services.detector import detect_product
from services.billing import (
    add_item,
    remove_item,
    calculate_bill,
    clear_bill
)
from services.inventory import get_inventory

app = Flask(__name__)

UPLOAD_FOLDER = "data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("data", exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/data/<path:filename>")
def serve_data(filename):
    return send_from_directory("data", filename)


@app.route("/api/detect", methods=["POST"])
def detect():
    if "image" not in request.files:
        return jsonify({
            "success": False,
            "message": "Image is missing."
        }), 400

    image = request.files["image"]
    filename = secure_filename(image.filename)
    image_path = os.path.join(UPLOAD_FOLDER, filename)

    image.save(image_path)

    result = detect_product(image_path)

    return jsonify({
        "success": True,
        **result
    })


@app.route("/api/add-item", methods=["POST"])
def add_product():
    data = request.get_json()
    product_class = data.get("product_class")

    success, message = add_item(product_class)

    return jsonify({
        "success": success,
        "message": message,
        "bill": calculate_bill(),
        "inventory": get_inventory()
    })


@app.route("/api/remove-item/<product_class>", methods=["DELETE"])
def remove_product(product_class):
    success, message = remove_item(product_class)

    return jsonify({
        "success": success,
        "message": message,
        "bill": calculate_bill(),
        "inventory": get_inventory()
    })


@app.route("/api/bill", methods=["GET"])
def get_bill():
    return jsonify(calculate_bill())


@app.route("/api/inventory", methods=["GET"])
def inventory():
    return jsonify(get_inventory())


@app.route("/api/clear-bill", methods=["POST"])
def clear_current_bill():
    clear_bill()

    return jsonify({
        "success": True,
        "message": "Bill cleared successfully.",
        "bill": calculate_bill(),
        "inventory": get_inventory()
    })


if __name__ == "__main__":
    import socket
    port = int(os.environ.get("PORT", 5000))

    # Auto-detect if port is occupied (e.g. by macOS AirPlay on port 5000)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("0.0.0.0", port))
        s.close()
    except OSError:
        port = 5001
        print(f"Port 5000 is in use by macOS AirPlay. Starting server on port {port} instead.")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )
