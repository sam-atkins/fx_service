import json

from flask import Flask, jsonify, request
from manageconf import Config, get_config  # noqa F401
import requests

app = Flask(__name__)


@app.route("/health")
def health_check():
    return jsonify({"statusCode": 200, "message": "Service is healthy"})


@app.route("/rates", methods=["POST"])
def get_rates():
    payload = json.loads(request.data)
    print(payload)
    if payload is None:
        # TODO(sam) raise exception
        pass
    base_currency = payload.get("base")

    try:
        response = _make_api_request(base_currency=base_currency)
        return response, 200
    except Exception:
        return jsonify({"statusCode": 500, "message": "Something went wrong"})


@app.route("/conversion", methods=["POST"])
def get_conversion():
    payload = json.loads(request.data)
    print(payload)
    if payload is None:
        # TODO(sam) raise exception
        pass
    base_currency = payload.get("base")
    target_currency = payload.get("target")
    amount = payload.get("amount")
    try:
        response = _make_api_request(base_currency=base_currency)
        payload = json.loads(response)
    except Exception:
        return jsonify({"statusCode": 500, "message": "Something went wrong"})

    target_currency_exchange_rate = payload.get("rates", {}).get(target_currency)
    print(f"target_currency_exchange_rate: {target_currency_exchange_rate}")
    converted_amount = _convert_amount_to_target_currency(
        amount=amount, exchange_rate=target_currency_exchange_rate
    )
    return jsonify({"statusCode": 200, "payload": converted_amount})


def _make_api_request(base_currency: str = None):
    # TODO(sam) move url to config?
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


def _convert_amount_to_target_currency(amount: int, exchange_rate: int):
    return amount * exchange_rate
