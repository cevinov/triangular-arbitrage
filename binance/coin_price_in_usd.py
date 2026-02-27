import get_tradeable_coins as get
import requests
from requests.structures import CaseInsensitiveDict
import json

# import the necessary packages to get the token price from the API
import freecurrencyapi

# 1. Get current price from USD to IDR
# API for currency exchange rates
# https://app.freecurrencyapi.com/
# https://github.com/everapihq/freecurrencyapi-python
client = freecurrencyapi.Client("fca_live_KI0u106qZ1ST3R83QnGP0dK2zUXe3HzpMr1qsHMq")
print("API Usage :", client.status())

# Retrieve currencies
result = client.currencies(currencies=["USD", "IDR"])
print("\nRetrieve Currencies :", result)

# Retrieve exchange rates for USD to IDR
url = "https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_KI0u106qZ1ST3R83QnGP0dK2zUXe3HzpMr1qsHMq&currencies=IDR&base_currency=USD"
resp = requests.get(url)
print("\nStatus =", resp.status_code)

# Get convertion rates for USD to IDR
result = resp.json()
rate_idr = float(result["data"]["IDR"])
print(f"USD to IDR = {rate_idr}")


# 2. Next get amount of each tradeable coin with 10 USD.
def amount_in_usd(symbol, base, amount):
    url = f"https://data-api.binance.vision/api/v3/ticker/price?symbol={symbol}"
    resp = requests.get(url)
    result = json.loads(resp.text)
    qty = amount / float(result["price"])
    return {base: qty}

    # print(
    #     f"\nAmount: {symbol} {amount} -- {balance_in_usd} = Rp {balance_in_usd * rate_idr:_}"
    # )
    # Output: Amount: BTCUSDT 0.0002315688022173176 -- 10 = Rp 154_121.92848854


# 3. Get all coins that are ready for trade, and do the conversion (if quote is USDT).
def convert_to_usdt(amount=10):
    list_tradeable_coins = get.get_coins()
    dict_usdt = {}

    for base, quote in list_tradeable_coins:
        if quote == "USDT" or quote == "USDC" or quote == "TUSD" or quote == "FDUSD":
            symbol = base + quote
            result = amount_in_usd(symbol, base, amount)
            print(result)

            dict_usdt.update(result)
            with open("convert_usdt.json", "w") as fp:  # fp stands for file pointer
                json.dump(dict_usdt, fp)

    print(f"\n\nCalculation amount to {amount} USD Completed!!!")


convert_to_usdt()
