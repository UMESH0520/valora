from fetch_prices import fetch

def test_fetch():
    prices = fetch()
    assert "product1" in prices
    assert prices["product1"] == 1000
