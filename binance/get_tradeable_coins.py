import requests
import json


# IP Weight = 20
def get_coins():
    url = "https://data-api.binance.vision/api/v3/exchangeInfo"
    resp = requests.get(url)
    result = json.loads(resp.text)

    coin_lists = []

    for i, data in enumerate(result["symbols"]):
        #  Limit to 100 pairs for testing
        if len(coin_lists) >= 100:
            break # Exit the loop if we have 100 pairs.
        
        # List all coins that are ready for trade.
        if (len(coin_lists) <= 100 and data["status"] == "TRADING"):
            # Format [base, quote]
            base_quote = [data["baseAsset"], data["quoteAsset"]]
            coin_lists.append(base_quote)

        # print(coin_lists, "--", len(coin_lists))
    return coin_lists

# get_coins()
