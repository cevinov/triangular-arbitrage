import requests
import os
# https://api.slack.com/messaging/webhooks
# https://api.slack.com/block-kit

def arb_notif(exchange, result):
    # Defining the endpoint
    url = os.environ.get("SLACK_WEBHOOK_URL")
    message = f"ARBITRAGE OPPORTUNITY FOUND for {exchange}!"

    if exchange == "Binance":
        # Payload
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": message},
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Exchange:*\n{exchange}"},
                        {"type": "mrkdwn", "text": f"*Found At:*\n{result['foundAt']}"},
                        {"type": "mrkdwn", "text": f"*Starting Amount (USD):*\n${result.get('initial_amount', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Starting Amount (Coin):*\n{result.get('starting_amount', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Final Amount:*\n{result['acquired_coin_t3']}"},
                        {"type": "mrkdwn", "text": f"*Profit/Loss:*\n{result['profit_loss']}"},
                        {"type": "mrkdwn", "text": f"*Real Rate %:*\n{result['real_rate_percentage']}%"},
                        {"type": "mrkdwn", "text": f"*Fee:*\n{result.get('fee', 'N/A')}"},
                    ]
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*Trade Details*"},
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Contract 1:*\n{result['contract_1'][0]}/{result['contract_1'][1]}"},
                        {"type": "mrkdwn", "text": f"*Direction 1:*\n{result['contract_direction_1']}"},
                        {"type": "mrkdwn", "text": f"*Acquired T1:*\n{result['acquired_coin_t1']}"},
                        {"type": "mrkdwn", "text": f"*Contract 2:*\n{result['contract_2'][0]}/{result['contract_2'][1]}"},
                        {"type": "mrkdwn", "text": f"*Direction 2:*\n{result['contract_direction_2']}"},
                        {"type": "mrkdwn", "text": f"*Acquired T2:*\n{result['acquired_coin_t2']}"},
                        {"type": "mrkdwn", "text": f"*Contract 3:*\n{result['contract_3'][0]}/{result['contract_3'][1]}"},
                        {"type": "mrkdwn", "text": f"*Direction 3:*\n{result['contract_direction_3']}"},
                        {"type": "mrkdwn", "text": f"*Acquired T3:*\n{result['acquired_coin_t3']}"},
                    ]
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"*🔬 Hypothesis Metrics (Compared to Start)*\n"
                            f"• *Ideal Surface Profit* (No fees/slippage): `{result.get('ideal_surface_profit', 0)}`\n"
                            f"• *Gross Depth Profit* (With slippage, no fees): `{result.get('gross_depth_profit', 0)}`\n"
                            f"• *Net Depth Profit* (Real): `{result.get('net_surface_profit', result['profit_loss'])}`"
                        )
                    }
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Detailed Execution Path:*\n{result.get('trade_desc_1', 'N/A')}\n{result.get('trade_desc_2', 'N/A')}\n{result.get('trade_desc_3', 'N/A')}"
                    }
                }
            ]
        }
    else:
        # Default Payload for other exchanges (e.g., Indodax)
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": message},
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Exchange:*\n{exchange}"},
                        {"type": "mrkdwn", "text": f"*Found At:*\n{result.get('foundAt', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Starting Amount:*\n{result.get('starting_amount', 'N/A')} IDR"},
                        {"type": "mrkdwn", "text": f"*Final Amount:*\n{result.get('final_balance', 'N/A')} IDR"},
                        {"type": "mrkdwn", "text": f"*Profit:*\n{result.get('profit_loss', 'N/A')} IDR ({result.get('real_rate_percentage', 'N/A')}%)"},
                    ]
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*Trade Details*"},
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Contract 1:*\n{result.get('contract_1', ['N/A', 'N/A'])[0]}/{result.get('contract_1', ['N/A', 'N/A'])[1]}"},
                        {"type": "mrkdwn", "text": f"*Direction 1:*\n{result.get('contract_direction_1', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Acquired T1:*\n{result.get('acquired_coin_t1', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Contract 2:*\n{result.get('contract_2', ['N/A', 'N/A'])[0]}/{result.get('contract_2', ['N/A', 'N/A'])[1]}"},
                        {"type": "mrkdwn", "text": f"*Direction 2:*\n{result.get('contract_direction_2', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Acquired T2:*\n{result.get('acquired_coin_t2', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Contract 3:*\n{result.get('contract_3', ['N/A', 'N/A'])[0]}/{result.get('contract_3', ['N/A', 'N/A'])[1]}"},
                        {"type": "mrkdwn", "text": f"*Direction 3:*\n{result.get('contract_direction_3', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Acquired T3:*\n{result.get('acquired_coin_t3', 'N/A')}"},
                    ]
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Detailed Execution Path:*\n{result.get('trade_desc_1', 'N/A')}\n{result.get('trade_desc_2', 'N/A')}\n{result.get('trade_desc_3', 'N/A')}"
                    }
                }
            ]
        }

    # Adding empty header as parameters
    headers = {}

    # Posting the payload to the URL
    response = requests.request("POST", url, headers=headers, json=payload)

    # Return response
    return response.text.encode("utf8")


# res = {"contract_1": ["ETH", "USDT"], "acquired_coin_t1": 2.995}
# test = arb_notif("Binance", res)
# print(test)

# Testing notification with CURL
# curl -X POST -H 'Content-type: application/json' --data '{"text":"Hello, World!"}' $SLACK_WEBHOOK_URL