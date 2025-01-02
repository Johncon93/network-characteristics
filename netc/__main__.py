from flask import Flask, request, jsonify
from netc.net_test import measure_network_performance

app = Flask(__name__)


@app.route("/netc", methods=["POST"])
def netc():
    data = request.get_json()
    host = data.get("host")
    results = measure_network_performance(host)
    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
