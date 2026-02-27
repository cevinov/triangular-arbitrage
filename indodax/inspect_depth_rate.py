import requests
import json

pairs = ["btcidr", "btcusdt", "usdtidr"]
for pair_id in pairs:
    # https://github.com/btcid/indodax-official-api-docs/blob/master/Public-RestAPI.md#depth
    url = f"https://indodax.com/api/depth/{pair_id}"
    try:
        response = requests.get(url)
        data = response.json()
        print(f"Pair: {pair_id}, Keys: {list(data.keys())}")
    except Exception as e:
        print(f"Pair: {pair_id}, Error: {e}")


pair_id = "btcidr"
url = f"https://indodax.com/api/depth/{pair_id}"
print("\n\nTest get volume price Buy and Sell on each pair in exchange")
try:
    response = requests.get(url)
    data = response.json()
    print(json.dumps(data, indent=2)[:500]) # Print first 500 chars
except Exception as e:
    print(e)
