import json
import time
import datetime
import get_tradeable_coins as get
import surface_rate_bookTicker as surf_rate
import structuring_triangular_pairs as struct_triarb
import calc_depth_rate as depth
import func_slack_notif as slack

# Dot in float number means the decimal point, not the thousands separator.

# RUN Step 1 for coin update / testing
# Step 1: Structuring triangular pairs.
# struct_triarb.save_triarb_groups()

# # Step 2 (Optional): Check the surface rate for each triangular pair.
# with open("triangular_groups.json", "r") as json_file:
#     structured_pairs = json.load(json_file)
# all_surface_rate = surf_rate.get_price_for_t_pair(structured_pairs[0:5])  # Limit to 5 triangular pairs for testing

# print("\n")
# for rate in all_surface_rate:
#     print("Rate: ", rate)

if __name__ == "__main__":
    is_run = True
    while is_run:
        # Give a 60 seconds break before checking the next triangular pair. To avoid API limit.
        # time.sleep(60)
        start = datetime.datetime.now()
        print("MAIN\n")

        # Open triangular_groups.json to list all triangular match pairs.
        with open("triangular_groups.json", "r") as json_file:
            structured_pairs = json.load(json_file)

        # Print out list triangular group pairs.
        # print(structured_pairs, "\n\n")

        goal_arb = []
        result_arb = None
        for pair in structured_pairs:
            # result_surface = {
            #     "starting_amount": 100,
            #     "direction": "reverse",
            #     "swap_1": "ETH",
            #     "swap_2": "BTC",
            #     "swap_3": "USDC",
            #     "swap_1_rate": 0.05251,
            #     "swap_2_rate": 0.00043658780435627316,
            #     "swap_3_rate": 43621.47,
            #     "acquired_coin_t1": 5.251,
            #     "acquired_coin_t2": 0.0022925225606747904,
            #     "acquired_coin_t3": 100.00320410479856,
            #     "contract_1": ["ETH", "BTC"],
            #     "contract_2": ["ETH", "USDC"],
            #     "contract_3": ["BTC", "USDC"],
            #     "direction_trade_1": "quote_to_base",
            #     "direction_trade_2": "base_to_quote",
            #     "direction_trade_3": "quote_to_base",
            #     "trade_desc_1": "\n1. Start with ETH/BTC of $100. Swap at rate 0.05251 for BTC/USDC acquiring 5.251.",
            #     "trade_desc_2": "2. Swap 5.251 of BTC/USDC at rate 0.00043658780435627316 for ETH/USDC acquiring 0.0022925225606747904.",
            #     "trade_desc_3": "3. Swap 0.0022925225606747904 of ETH/USDC at rate 43621.47 for BTC/USDC acquiring 100.00320410479856.",
            #     "profit": 0.003204104798555818,
            #     "profit_percentage": 0.003204104798555818,
            # }

            # IP Weight = 2 * 3 calls = 6 weight
            result_surface = surf_rate.find_arb_opportunity_surf(pair)

            if len(result_surface) > 0:
                # IP Weight = 5 * 3 calls = 15 weight
                foundAt = datetime.datetime.now()
                result_depth = depth.get_depth_from_orderbook(result_surface)

                if len(result_depth) > 0:
                    # IP Weight = 5 * 3 calls = 15 weight
                    result_dict = {
                        "contract_1": result_depth["contract_1"],
                        "contract_direction_1": result_depth["contract_direction_1"],
                        "acquired_coin_t1": result_depth["acquired_coin_t1"],
                        "contract_2": result_depth["contract_2"],
                        "contract_direction_2": result_depth["contract_direction_2"],
                        "acquired_coin_t2": result_depth["acquired_coin_t2"],
                        "contract_3": result_depth["contract_3"],
                        "contract_direction_3": result_depth["contract_direction_3"],
                        "acquired_coin_t3": result_depth["acquired_coin_t3"],
                        "trade_desc_1": result_surface["trade_desc_1"],
                        "trade_desc_2": result_surface["trade_desc_2"],
                        "trade_desc_3": result_surface["trade_desc_3"],
                        "starting_amount": result_surface["starting_amount"],
                        "profit_loss": result_depth["profit_loss"],
                        "real_rate_percentage": result_depth["real_rate_percentage"],
                        "foundAt": foundAt.strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    # Send notification to Slack
                    notif = slack.arb_notif("Binance", result_dict)

                    if notif != b"ok":
                        print(f"Error: {notif.decode('utf-8')}")
                        with open("error_notif.txt", "w") as fp:
                            json.dump(notif, fp)

                    goal_arb.append(result_dict)

                    # Store the result to a file.
                    with open("profitable_triarb_binance.json", "w") as fp:
                        json.dump(goal_arb, fp)

        # If all the triangular pairs have been checked, then collect timestamp for logging.
        end = datetime.datetime.now()
        log = f"Start: {start}\nEnd: {end}\nDiff: {end - start}\n\n"

        with open("log_binance.txt", "a") as fp:
            fp.write(log)

        print("File saved!")
        is_run = False
else:
    print("NOT MAIN")
