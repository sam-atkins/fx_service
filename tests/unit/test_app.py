from src.app import _convert_amount_to_target_currency


def test_convert_amount_to_target_currency():
    converted_amount = _convert_amount_to_target_currency(amount=10, exchange_rate=1.16)
    assert converted_amount == 11.6
