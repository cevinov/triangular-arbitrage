import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'binance')))
import calc_depth_rate as depth

print("--- Test Scenario 1: Base to Quote (e.g., Sell ETH for BTC) ---")
# Mocking reformat_depth_orderbook logic for 'base_to_quote'
# Real world: Price 0.05 BTC/ETH. 
# Code logic: adj_price = 1/0.05 = 20. adj_quantity = 20 * 10 = 200.
# Input: 5 ETH.
# Code calculation: 5 * 20 * (1 - 0.001) = 99.9

result_b2q = depth.calculate_acquired_coin(
    pair=["ETH", "BTC"],
    amount_in=5.0,
    orderbook=[[20.0, 200.0]]
)
print(f"Input: 5.0 (Base), Adj Price: 20.0")
print(f"Result: {result_b2q}")
expected_b2q = 5.0 * 20.0 * (1 - 0.001)
print(f"Expected (with fee): {expected_b2q}")

if abs(result_b2q - expected_b2q) < 0.0001:
    print("SUCCESS: Fee applied correctly for Base to Quote.")
else:
    print("FAILURE: Fee not applied correctly for Base to Quote.")


print("\n--- Test Scenario 2: Quote to Base (e.g., Buy ETH with BTC) ---")
# Mocking reformat_depth_orderbook logic for 'quote_to_base'
# Real world: Price 0.05 BTC/ETH.
# Code logic: adj_price = 0.05. adj_quantity = 10.
# Input: 0.1 BTC.
# Code calculation: 0.1 * 0.05 * (1 - 0.001) = 0.004995
#
result_q2b = depth.calculate_acquired_coin(
    pair=["ETH", "BTC"],
    amount_in=0.1,
    orderbook=[[0.05, 10.0]]
)
print(f"Input: 0.1 (Quote), Adj Price: 0.05")
print(f"Result: {result_q2b}")
expected_q2b = 0.1 * 0.05 * (1 - 0.001)
print(f"Expected (with fee): {expected_q2b}")

if abs(result_q2b - expected_q2b) < 0.000001:
    print("SUCCESS: Fee applied correctly for Quote to Base.")
else:
    print("FAILURE: Fee not applied correctly for Quote to Base.")
