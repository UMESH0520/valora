def test_price_update():
    lowest_price = 1000
    margin_percent = 3
    display_price = lowest_price * (100 - margin_percent) / 100
    assert display_price == 970
