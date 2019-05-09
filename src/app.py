import json

from flask import Flask, jsonify, request
from manageconf import Config, get_config  # noqa F401
import requests

from src.currencies import AVAILABLE_CURRENCIES

MISSING_PAYLOAD_ERROR = {"statusCode": 400, "message": "Missing or incorrect payload"}

app = Flask(__name__)


@app.route("/health")
def health_check():
    """Endpoint for health checks"""
    return jsonify({"statusCode": 200, "message": "Service is healthy"}), 200


@app.route("/rates", methods=["POST"])
def get_rates():
    """Endpoint to get FX rates

    Requires a request body e.g.

    "{
        "base": "GBP"
    }"

    Returns:
        JSON: response includes FX rates
    """
    if request.data:
        payload = json.loads(request.data)
    else:
        return jsonify(MISSING_PAYLOAD_ERROR)
    base_currency = payload.get("base")

    try:
        response = _make_api_request(base_currency=base_currency)
        return jsonify({"statusCode": 200, "payload": response}), 200
    except Exception:
        return jsonify({"statusCode": 500, "message": "Something went wrong"}), 500


@app.route("/conversion", methods=["POST"])
def get_conversion():
    """Endpoint to calculate a FX conversion

    Requires a request body e.g.

    "{
        "base": "EUR",
        "target": "GBP",
        "amount": 100
    }"

    Returns:
        JSON: payload includes the converted amount
    """
    if request.data:
        payload = json.loads(request.data)
    else:
        return jsonify(MISSING_PAYLOAD_ERROR)
    base_currency = payload.get("base")
    target_currency = payload.get("target")
    if not set([base_currency, target_currency]).issubset(AVAILABLE_CURRENCIES):
        return (
            jsonify(
                {
                    "statusCode": 400,
                    "message": "Incorrect currency code. "
                    f"Available rates: {', '.join(AVAILABLE_CURRENCIES)}",
                }
            ),
            400,
        )
    amount = payload.get("amount")
    if amount is None:
        return jsonify(MISSING_PAYLOAD_ERROR), 400

    try:
        payload = _make_api_request(base_currency=base_currency)
    except Exception:
        return jsonify({"statusCode": 500, "message": "Something went wrong"}), 500

    target_currency_exchange_rate = payload.get("rates", {}).get(target_currency)
    converted_amount = _convert_amount_to_target_currency(
        amount=int(amount), exchange_rate=target_currency_exchange_rate
    )
    return jsonify({"statusCode": 200, "payload": converted_amount}), 200


def _make_api_request(base_currency: str = None):
    """API request to 3rd party FX rate provider

    Args:
        base_currency (str): the base currency required for exchange rates

    Returns:
        JSON: text response from API provider
    """
    url = "https://api.exchangeratesapi.io/latest"

    if base_currency:
        url = f"{url}?base={base_currency}"

    try:
        response = requests.get(url=url)
        if response.status_code == 200:
            return json.loads(response.text)
    except requests.RequestException as e:
        # log to cloudwatch
        print(e)
        raise e


def _convert_amount_to_target_currency(amount: int, exchange_rate: int) -> int:
    """Calculation to convert currency

    Args:
        amount (int): the amount to convert
        exchange_rate (int): the exchange rate to use to calculate the conversion

    Returns:
        int: the converted amount
    """
    return amount * exchange_rate
