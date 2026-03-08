import func_slack_notif as slack
import json
import datetime
from unittest.mock import patch

# Mock result dictionary with fee
result_dict = {
    "contract_1": ["ETH", "BTC"],
    "contract_direction_1": "base_to_quote",
    "acquired_coin_t1": 5.251,
    "contract_2": ["ETH", "USDC"],
    "contract_direction_2": "base_to_quote",
    "acquired_coin_t2": 0.00229,
    "contract_3": ["BTC", "USDC"],
    "contract_direction_3": "quote_to_base",
    "acquired_coin_t3": 5.15,
    "starting_amount": 5.0,
    "initial_amount": 5.0,
    "profit_loss": 0.15,
    "real_rate_percentage": 0.06,
    "trade_desc_1": "1. Start with ETH of 5.0. Swap at rate 1.05 for BTC acquiring 5.251.",
    "trade_desc_2": "2. Swap 5.251 of BTC at rate 0.0004 for USDC acquiring 0.00229.",
    "trade_desc_3": "3. Swap 0.00229 of USDC at rate 43621.47 for BTC acquiring 5.15.",
    "foundAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "fee": 0.001
}

print("Verifying notification payload...")

# Mock requests.request to capture payload
with patch('requests.request') as mock_post:
    mock_post.return_value.text = "ok"
    
    slack.arb_notif("Binance", result_dict)
    
    # Get the arguments passed to requests.request
    args, kwargs = mock_post.call_args
    payload = kwargs['json']
    
    # Check if fee is in the payload
    blocks = payload['blocks']
    fee_found = False
    for block in blocks:
        if block['type'] == 'section' and 'fields' in block:
            for field in block['fields']:
                if "*Fee:*" in field['text']:
                    print(f"Found Fee field: {field['text']}")
                    fee_found = True
                    break
    
    if fee_found:
        print("SUCCESS: Fee field found in notification payload.")
    else:
        print("FAILURE: Fee field NOT found in notification payload.")
