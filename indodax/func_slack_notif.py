import requests
import json
import os
# https://api.slack.com/messaging/webhooks
# https://api.slack.com/block-kit
# https://api.slack.com/apps/A06F7GVTDNV/incoming-webhooks?success=1

def arb_notif(exchange, result):
    # Defining the endpoint
    url = os.environ.get("SLACK_WEBHOOK_URL")
    message = f"🚀 ARBITRAGE OPPORTUNITY on {exchange}!"

    c1 = result["contract_1"]
    d1 = result["contract_direction_1"]
    acq1 = result["acquired_coin_t1"]
    acq_unit1 = c1[0] if d1 == "buy" else c1[1]

    c2 = result["contract_2"]
    d2 = result["contract_direction_2"]
    acq2 = result["acquired_coin_t2"]
    acq_unit2 = c2[0] if d2 == "buy" else c2[1]

    c3 = result["contract_3"]
    d3 = result["contract_direction_3"]
    acq3 = result["acquired_coin_t3"]
    acq_unit3 = c3[0] if d3 == "buy" else c3[1]

    start_amt = result["starting_amount"]
    final_bal = result["final_balance"]
    profit = result["profit_loss"]
    rate_pct = result["real_rate_percentage"]
    timestamp = result["foundAt"]

    if exchange == "Indodax":
        # Payload
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": message},
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🔄 Step 1*\n• *Contract:* `{c1[0]}/{c1[1]}`\n• *Direction:* {d1.upper()}\n• *Acquired:* `{acq1:.6f}` `{acq_unit1}`"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🔄 Step 2*\n• *Contract:* `{c2[0]}/{c2[1]}`\n• *Direction:* {d2.upper()}\n• *Acquired:* `{acq2:.6f}` `{acq_unit2}`"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🔄 Step 3*\n• *Contract:* `{c3[0]}/{c3[1]}`\n• *Direction:* {d3.upper()}\n• *Acquired:* `{acq3:.6f}` `{acq_unit3}`"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📊 Summary*\n• *Starting Amount:* `{start_amt:,.0f}` IDR\n• *Final Balance:* `{final_bal:,.0f}` IDR\n• *Profit:* `+{profit:,.0f}` IDR\n• *Rate:* `{rate_pct:.2f}%`\n• *Fee:* `{result.get('fee', 'N/A')}`\n• *Found At:* {timestamp}"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"*🔬 Hypothesis Metrics (Compared to Start)*\n"
                            f"• *Ideal Surface Profit* (No fees/slippage): `{result.get('ideal_surface_profit', 0):,.0f}` IDR\n"
                            f"• *Gross Depth Profit* (With slippage, no fees): `{result.get('gross_depth_profit', 0):,.0f}` IDR\n"
                            f"• *Net Depth Profit* (Real): `{result.get('net_surface_profit', profit):,.0f}` IDR"
                        )
                    }
                },
            ]
        }
        
        # Add Detailed Execution Path
        payload["blocks"].append({"type": "divider"})
        payload["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Detailed Execution Path:*\n{result.get('trade_desc_1', 'N/A')}\n{result.get('trade_desc_2', 'N/A')}\n{result.get('trade_desc_3', 'N/A')}"
            }
        })

    # Adding empty header as parameters
    headers = {}

    # Posting the payload to the URL
    response = requests.request("POST", url, headers=headers, json=payload)

    # Return response
    return response.text.encode("utf8")


# Testing notification with CURL
# curl -X POST -H 'Content-type: application/json' --data '{"text":"Hello, World!"}' $url