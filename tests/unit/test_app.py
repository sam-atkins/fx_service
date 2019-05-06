from unittest.mock import Mock, patch

import pytest
import requests

from src.server import app
from src.app import _convert_amount_to_target_currency
from tests.datasets.rates import RATES


@pytest.fixture
def client():
    client = app.test_client()

    yield client


def test_health_returns_200(client):
    response = client.get("/health")
    json_data = response.get_json()
    assert json_data == {"statusCode": 200, "message": "Service is healthy"}


@patch("src.app._make_api_request", return_value=RATES)
def test_get_rates_returns_200(mock_api_request, client):
    response = client.post("/rates", json={"base": "GBP"})
    json_data = response.get_json()
    assert json_data == {
        "payload": {
            "base": "GBP",
            "date": "2019-05-03",
            "rates": {
                "AUD": 1.8584834178,
                "BGN": 2.2798857609,
                "BRL": 5.1517165006,
                "CAD": 1.7507722795,
                "CHF": 1.3269219561,
                "CNY": 8.7572419421,
                "CZK": 29.9726059334,
                "DKK": 8.7028035204,
                "EUR": 1.1657049601,
                "GBP": 1,
                "HKD": 10.2013172466,
                "HRK": 8.6428862855,
                "HUF": 376.9656699889,
                "IDR": 18536.3991373783,
                "ILS": 4.6770414408,
                "INR": 90.0611995104,
                "ISK": 159.2352975462,
                "JPY": 145.0136970333,
                "KRW": 1521.3382292942,
                "MXN": 24.8734627266,
                "MYR": 5.3840414991,
                "NOK": 11.3986128111,
                "NZD": 1.9649122807,
                "PHP": 67.4476889899,
                "PLN": 4.9953954654,
                "RON": 5.5432767966,
                "RUB": 84.9452701521,
                "SEK": 12.4780556041,
                "SGD": 1.7729206738,
                "THB": 41.6436439937,
                "TRY": 7.7687241359,
                "USD": 1.300343883,
                "ZAR": 18.8928134289,
            },
        },
        "statusCode": 200,
    }


def test_get_rates_returns_400_if_no_request_body(client):
    response = client.post("/rates")
    json_data = response.get_json()
    assert json_data == {"statusCode": 400, "message": "Missing or incorrect payload"}


@patch("src.app._make_api_request", return_value=RATES)
def test_get_conversion_returns_200(mock_api_request, client):
    response = client.post(
        "/conversion", json={"base": "EUR", "target": "GBP", "amount": 100}
    )
    json_data = response.get_json()
    assert json_data == {"payload": 100, "statusCode": 200}


def test_get_conversion_returns_400_if_no_request_body(client):
    response = client.post("/conversion")
    json_data = response.get_json()
    assert json_data == {"statusCode": 400, "message": "Missing or incorrect payload"}


@patch("src.app._make_api_request", return_value=RATES)
def test_get_conversion_bad_payload_currency_returns_400(mock_api_request, client):
    response = client.post(
        "/conversion", json={"base": "XXX", "target": "GBP", "amount": 100}
    )
    json_data = response.get_json()
    assert json_data == {
        "message": "Incorrect currency code. Available rates: AUD, BGN, BRL, CAD, "
        "CHF, CNY, CZK, DKK, EUR, GBP, HKD, HRK, HUF, IDR, ILS, INR, ISK, JPY, KRW,"
        " MXN, MYR, NOK, NZD, PHP, PLN, RON, RUB, SEK, SGD, THB, TRY, USD, ZAR",
        "statusCode": 400,
    }


@patch("src.app._make_api_request", return_value=RATES)
def test_get_conversion_bad_payload_amount_returns_400(mock_api_request, client):
    response = client.post("/conversion", json={"base": "EUR", "target": "GBP"})
    json_data = response.get_json()
    assert json_data == {"statusCode": 400, "message": "Missing or incorrect payload"}


@patch("src.app._make_api_request")
def test_get_conversion_bad_http_returns_500(mock_api_request, client):
    with pytest.raises(requests.exceptions.HTTPError):
        mock_api_request = Mock(side_effect=requests.exceptions.HTTPError)
        mock_api_request()
        response = client.post(
            "/conversion", json={"base": "EUR", "target": "GBP", "amount": 100}
        )
        json_data = response.get_json()
        assert json_data == {"statusCode": 500, "message": "Something went wrong"}


def test_convert_amount_to_target_currency():
    converted_amount = _convert_amount_to_target_currency(amount=10, exchange_rate=1.16)
    assert converted_amount == 11.6
