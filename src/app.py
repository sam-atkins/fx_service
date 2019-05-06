import json

from flask import Flask, jsonify, request
from manageconf import Config, get_config  # noqa F401
import requests

MISSING_PAYLOAD_ERROR = {"statusCode": 400, "message": "Missing or incorrect payload"}

app = Flask(__name__)


@app.route("/health")
def health_check():
    return jsonify({"statusCode": 200, "message": "Service is healthy"}), 200


@app.route("/rates", methods=["POST"])
def get_rates():
    if request.data:
        payload = json.loads(request.data)
    else:
        return jsonify(MISSING_PAYLOAD_ERROR)
    base_currency = payload.get("base")

    try:
        response = _make_api_request(base_currency=base_currency)
        return response, 200
    except Exception:
        return jsonify({"statusCode": 500, "message": "Something went wrong"}), 500


@app.route("/conversion", methods=["POST"])
def get_conversion():
    if request.data:
        payload = json.loads(request.data)
    else:
        return jsonify(MISSING_PAYLOAD_ERROR)
    base_currency = payload.get("base")
    target_currency = payload.get("target")
    available_currencies = get_config("available_currencies")
    if not set([base_currency, target_currency]).issubset(available_currencies):
        return (
            jsonify(
                {
                    "statusCode": 400,
                    "message": "Incorrect currency code. "
                    f"Available rates: {', '.join(available_currencies)}",
                }
            ),
            400,
        )
    amount = payload.get("amount")
    if amount is None:
        return jsonify(MISSING_PAYLOAD_ERROR), 400

    try:
        response = _make_api_request(base_currency=base_currency)
        payload = json.loads(response)
    except Exception:
        return jsonify({"statusCode": 500, "message": "Something went wrong"}), 500

    target_currency_exchange_rate = payload.get("rates", {}).get(target_currency)
    converted_amount = _convert_amount_to_target_currency(
        amount=int(amount), exchange_rate=target_currency_exchange_rate
    )
    return jsonify({"statusCode": 200, "payload": converted_amount}), 200


def _make_api_request(base_currency: str = None):
    url = "https://api.exchangeratesapi.io/latest"

    if base_currency:
        url = f"{url}?base={base_currency}"

    try:
        response = requests.get(url=url)
        if response.status_code == 200:
            return response.text
    except requests.RequestException as e:
        # log to cloudwatch
        print(e)
        raise e


def _convert_amount_to_target_currency(amount: int, exchange_rate: int) -> int:
    return amount * exchange_rate
