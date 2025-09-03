from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

# Coinmarketcap API rate limit: 30 calls/minute (Give delay 2 seconds between each call)


# Function to get price from coingecko.
def get_simple_price(amount, coin, currency="USD"):
    url = f"https://pro-api.coinmarketcap.com/v2/tools/price-conversion?amount={amount}&symbol={coin}&convert={currency}"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": "22cf2e17-3fa4-4aa3-86e1-210756342704",
    }

    session = Session()
    session.headers.update(headers)

    # Parse a valid JSON string and convert it into a Python Dictionary
    try:
        response = session.get(url)
        data = json.loads(response.text)

        # Divide by 100 to get the price of 1 token
        price = 100 / data["data"][0]["quote"][currency]["price"]
        return {coin: price}
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        return 0


def func_converter():
    unique_names = set()
    unique_coins = set()
    with open("triangular_pairs_uniswap.json", "r") as json_file:
        structured_pairs = json.load(json_file)
        for pair in structured_pairs:
            unique_coins.add(pair["a_base"])
            unique_names.add(pair["a_base_name"])
            unique_coins.add(pair["a_quote"])
            unique_names.add(pair["a_quote_name"])
            unique_coins.add(pair["b_base"])
            unique_names.add(pair["b_base_name"])
            unique_coins.add(pair["b_quote"])
            unique_names.add(pair["b_quote_name"])
            unique_coins.add(pair["c_base"])
            unique_names.add(pair["c_base_name"])
            unique_coins.add(pair["c_quote"])
            unique_names.add(pair["c_quote_name"])
    print(unique_coins)

    list_convert = []
    for coin in unique_coins:
        list_convert.append(get_simple_price(10, coin))

    with open("converter_usd.json", "w") as f:
        json.dump(list_convert, f)


# func_converter()

# g = "WETH"
# with open("converter_usd.json", "r") as f:
#     converter = json.load(f)
#     for pair in converter:
#         if g in pair:
#             print(pair[g])
