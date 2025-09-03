import requests
import json

# https://api.slack.com/messaging/webhooks
# https://api.slack.com/block-kit


def arb_notif(exchange, result):
    # Defining the endpoint
    url = "https://hooks.slack.com/services/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"
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
                    # "text": {
                    #     "type": "plain_text",
                    #     "text": "Contract 1:"
                    #     + result["contract_1"][1]
                    #     + "\n"
                    #     + "Acquired Coin T1: "
                    #     + " "
                    #     + str(result["acquired_coin_t1"])
                    #     + "\n",
                    # }
                    "text": {
                        "type": "plain_text",
                        "text": "Exchange: "
                        + " "
                        + exchange
                        + "\n"
                        + "Contract 1: "
                        + " "
                        + result["contract_1"][0]
                        + " "
                        + result["contract_1"][1]
                        + "\n"
                        + "Contract Direction 1: "
                        + " "
                        + result["contract_direction_1"]
                        + "\n"
                        + "Acquired Coin T1: "
                        + " "
                        + str(result["acquired_coin_t1"])
                        + "\n"
                        + "Contract 2: "
                        + " "
                        + result["contract_2"][0]
                        + " "
                        + result["contract_2"][1]
                        + "\n"
                        + "Contract Direction 2: "
                        + " "
                        + result["contract_direction_2"]
                        + "\n"
                        + "Acquired Coin T2: "
                        + " "
                        + str(result["acquired_coin_t2"])
                        + "\n"
                        + "Contract 3: "
                        + " "
                        + result["contract_3"][0]
                        + " "
                        + result["contract_3"][1]
                        + "\n"
                        + "Contract Direction 3: "
                        + " "
                        + result["contract_direction_3"]
                        + "\n"
                        + "Acquired Coin T3: "
                        + " "
                        + str(result["acquired_coin_t3"])
                        + "\n"
                        + "Starting Amount: "
                        + " "
                        + str(result["starting_amount"])
                        + "\n"
                        + "Profit/Loss: "
                        + " "
                        + str(result["profit_loss"])
                        + "\n"
                        + "Real Rate Percentage: "
                        + " "
                        + str(result["real_rate_percentage"])
                        + "\n"
                        + "Found At: "
                        + " "
                        + str(result["foundAt"])
                        + "\n",
                    },
                },
            ]
        }

    # Adding empty header as parameters
    headers = {}

    # Posting the payload to the URL
    response = requests.request("POST", url, headers=headers, json=payload)

    # Return response
    return response.text 


#res = {"contract_1": ["ETH", "USDT"], "acquired_coin_t1": 2.995}
#test = arb_notif("Binance", res)
#print(test)
