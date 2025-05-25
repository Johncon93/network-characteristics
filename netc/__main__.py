from flask import Flask, request, jsonify
from netc.net_test import measure_network_performance

app = Flask(__name__)


@app.route("/netc", methods=["POST"])
def netc() -> dict:
    data: dict | None = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"})

    host: str = data.get("host")
    time: int = data.get("time", 10)
    interval: float = data.get("interval", 0.2)

    print(
        f"Received request to measure network performance for host: {host}, time: {time}, interval: {interval}"
    )
    if not host:
        return jsonify({"error": "No host provided"})

    results: dict | None = measure_network_performance(
        host, test_time=time, interval=interval
    )

    if not results:
        return jsonify({"error": "Failed to measure network performance"})

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
