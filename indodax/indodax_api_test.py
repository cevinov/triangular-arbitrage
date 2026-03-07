import requests
import json

pairs = requests.get("https://indodax.com/api/pairs").json()

# How many altcoins are paired with USDT?
usdt_pairs = [p for p in pairs if p['base_currency'] == 'usdt']
print(f"USDT Base Pairs (Quote=USDT): {len(usdt_pairs)}")

# How many altcoins are paired with IDR?
idr_pairs = [p for p in pairs if p['base_currency'] == 'idr']
print(f"IDR Base Pairs (Quote=IDR): {len(idr_pairs)}")

# How many altcoins are paired with BTC?
btc_pairs = [p for p in pairs if p['base_currency'] == 'btc']
print(f"BTC Base Pairs (Quote=BTC): {len(btc_pairs)}")

