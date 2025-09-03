import requests
import json

# Dot in float number means the decimal point, not the thousands separator.

"""
# https://binance-docs.github.io/apidocs/spot/en/#uiklines

# Get candlestick price of a coin with an interval of 1 sec.
url = "https://data-api.binance.vision/api/v3/uiKlines?symbol=BLURUSDT&interval=1s"
resp = requests.get(url)
result = json.loads(resp.text)

for r in result:
    print(r[1])
    
print(len(result))
"""

# https://binance-docs.github.io/apidocs/spot/en/#symbol-order-book-ticker
# Get lastest bid & ask price information from api/v3/depth (real-time)


# IP Weight = 2
def get_latest_price(sym):
    url = f"https://data-api.binance.vision/api/v3/ticker/bookTicker?symbol={sym}"
    resp = requests.get(url)
    result = json.loads(resp.text)

    return result


# c = get_latest_price("USDT")
# print(c)


def get_bookTicker(tradeable_coins):
    list_prices = []

    for i, pair in enumerate(tradeable_coins):
        symbol = "".join(pair)
        print(f"\nPair-{i+1}:", symbol)

        list_prices.append(get_latest_price(symbol))

    # print(list_prices)
    return list_prices


# get_bookTicker(["ETHBTC", "QUICKTUSD"])


"""
Output example:
Pair-1: BNBBTC
[{'symbol': 'BNBBTC', 'bidPrice': '0.00591700', 'bidQty': '2.50000000', 'askPrice': '0.00591800', 'askQty': '20.65500000'}]

Pair-2: QUICKTUSD
[{'symbol': 'BNBBTC', 'bidPrice': '0.00591700', 'bidQty': '2.50000000', 'askPrice': '0.00591800', 'askQty': '20.65500000'}, {'symbol': 'QUICKTUSD', 'bidPrice': '0.04924000', 'bidQty': '2030.00000000', 'askPrice': '0.04952000', 'askQty': '119.00000000'}]
"""


# Function to check the ask and bid price for each triangular group
def get_price_for_t_pair(t_pair):
    for pair in t_pair:
        pair_a = pair["pair_a"]
        pair_b = pair["pair_b"]
        pair_c = pair["pair_c"]

        pair_a_ask = get_latest_price("".join(pair_a))["askPrice"]
        pair_a_bid = get_latest_price("".join(pair_a))["bidPrice"]

        pair_b_ask = get_latest_price("".join(pair_b))["askPrice"]
        pair_b_bid = get_latest_price("".join(pair_b))["bidPrice"]

        pair_c_ask = get_latest_price("".join(pair_c))["askPrice"]
        pair_c_bid = get_latest_price("".join(pair_c))["bidPrice"]

        # Return price information for each coin pair in a triangular match pair.
        yield {
            "pair_a_ask": pair_a_ask,
            "pair_a_bid": pair_a_bid,
            "pair_b_ask": pair_b_ask,
            "pair_b_bid": pair_b_bid,
            "pair_c_ask": pair_c_ask,
            "pair_c_bid": pair_c_bid,
        }


t_pair = [
    {
        "a_base": "ETH",
        "a_quote": "BTC",
        "pair_a": ["ETH", "BTC"],
        "b_base": "LTC",
        "b_quote": "BTC",
        "pair_b": ["LTC", "BTC"],
        "c_base": "LTC",
        "c_quote": "ETH",
        "pair_c": ["LTC", "ETH"],
        "combine": ["ETHBTC", "LTCBTC", "LTCETH"],
    },
    {
        "a_base": "ETH",
        "a_quote": "BTC",
        "pair_a": ["ETH", "BTC"],
        "b_base": "BTC",
        "b_quote": "TRY",
        "pair_b": ["BTC", "TRY"],
        "c_base": "ETH",
        "c_quote": "TRY",
        "pair_c": ["ETH", "TRY"],
        "combine": ["ETHBTC", "BTCTRY", "ETHTRY"],
    },
]
# {
#     "a_base": "BTC",
#     "a_quote": "USDT",
#     "pair_a": ["BTC", "USDT"],
#     "b_base": "BTC",
#     "b_quote": "TRY",
#     "pair_b": ["BTC", "TRY"],
#     "c_base": "TRB",
#     "c_quote": "TRY",
#     "pair_c": ["TRB", "TRY"],
#     "combine": ["BTCUSDT", "BTCTRY", "TRBTRY"],
# },


# Function to calculate arbitrage opportunity based on ask/bid price from the bookTicker API (Surface rate)
def find_arb_opportunity_surf(pair):
    # Set a variable to check if the result of the bid (sell) - ask (buy) price is a positive number.
    min_surface_rate = 0  # 5% profit
    starting_amount = 0
    surface_dict = {}
    contract_1 = ""
    contract_2 = ""
    contract_3 = ""
    direction_trade_1 = ""
    direction_trade_2 = ""
    direction_trade_3 = ""
    acquired_coin_t1 = 0
    acquired_coin_t2 = 0
    acquired_coin_t3 = 0

    # List to store price value for each coin pair from triangular group
    price_data = []

    # If you complete calculating the whole triangular group (3 pairs), then the value will be changed t1. Print out the output.
    calculated = 0

    a_base = pair["a_base"]
    a_quote = pair["a_quote"]
    b_base = pair["b_base"]
    b_quote = pair["b_quote"]
    c_base = pair["c_base"]
    c_quote = pair["c_quote"]
    pair_a = pair["pair_a"]
    pair_b = pair["pair_b"]
    pair_c = pair["pair_c"]

    print("\n\n\nCombine:", pair["combine"])

    for pair in pair["combine"]:
        price_data.append(get_latest_price(pair))

    # Extract price information for each coin pair in a triangular match pair.
    # Ask for buy, bid for sell
    a_ask = float(price_data[0]["askPrice"])
    a_bid = float(price_data[0]["bidPrice"])
    b_ask = float(price_data[1]["askPrice"])
    b_bid = float(price_data[1]["bidPrice"])
    c_ask = float(price_data[2]["askPrice"])
    c_bid = float(price_data[2]["bidPrice"])

    print("a:", a_ask, a_bid, pair_a)
    print("b:", b_ask, b_bid, pair_b)
    print("c:", c_ask, c_bid, pair_c)

    # Create looping for direction of trade forward (base to quote) and reverse (quote to base).
    direction_list = ["forward", "reverse"]
    for direction in direction_list:
        # Set a variable to store swap information for each coin pair.
        swap_1 = 0
        swap_2 = 0
        swap_3 = 0
        swap_4 = 0
        swap_1_rate = 0
        swap_2_rate = 0
        swap_3_rate = 0

        """
        Rule:
        1. FORWARD: If we are swapping the coin on the left (Base) to the right (Quote) then * (1 / Ask)
        2. REVERSE: If we are swapping the coin on the right (Quote) to the left (Base) then * Bid

        Example triangular pair: ['ETHBTC', 'LTCBTC', 'LTCETH']
        Buy ETH/BTC (ASK) > Sell ETH/BTC buy LTC/BTC (BID) > Sell LTC/BTC and buy LTC/ETH (ASK), start with ETH and end with ETH
        """

        # Quote to Base means have the same quote coin between 2 pairs but have different base coin (EX: ETH/BTC & LTC\BTC).
        # Base to Quote means quote coin pair A is the same as base coin pair B (EX: ETH/BTC and ETH/TRY).

        """
        FORWARD DIRECTION (Base to Quote)
        If a_quote matches with pair B either base or quote, then we can swap the coin from pair A to pair B.
        """
        # Assume starting capital with Base coin of pair A (Forward)
        if direction == "forward":
            swap_1 = a_base
            swap_2 = a_quote

            # Determine the total coin that we have (initial capital) based on the convert_usdt.json file with an amount of 10 USD.
            with open("convert_usdt.json", "r") as fp:
                data = json.load(fp)

                if a_base in data:
                    starting_amount = data[a_base]
                    print(f"\n\n------Amount------: {starting_amount}")
                else:
                    starting_amount = 10
                    print(f"\n\n------Amount------: {starting_amount}")

            print(f"\n\nFirst Trade (FORWARD): swap {a_base}/{a_quote}")
            direction_trade_1 = "base_to_quote"

            # Use ask price for the first trade for buying
            try:
                swap_1_rate = 1 / a_ask
                acquired_coin_t1 = starting_amount * swap_1_rate
                contract_1 = pair_a
                print(
                    f"Rate ({a_base}) -- Acquired T1: {swap_1_rate} -- {acquired_coin_t1} ({a_base})"
                )
            except ZeroDivisionError:
                pass

            """
            # Scenario 1: Check if a_quote (acquired coin) matches with b_quote
            """
            if a_quote == b_quote and calculated == 0:
                swap_3 = b_base
                direction_trade_2 = "quote_to_base"

                # We will use the BID price because we still have the same quote coin (ETH/BTC & LTC/BTC). In this case sell the coin (ETH/BTC) that we have, and buy new base coin with the same quote coin (LTC/BTC) with BID price (SELL).
                swap_2_rate = b_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate

                # Place second trade
                contract_2 = pair_b

                print("\n1 a_quote MATCH with b_quote", direction_trade_2)

                # Check if b_base (acquired coin) matches with c_base
                if b_base == c_base:
                    # Next direction will be base to quote, because it has different quote coin (LTC/BTC & LTC/ETH). So we will use ASK price to buy LTC/ETH with amount of LTC/BTC.
                    try:
                        swap_4 = c_quote
                        direction_trade_3 = "base_to_quote"
                        swap_3_rate = 1 / c_ask
                        acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                        contract_3 = pair_c
                        print(
                            "\n1 Final Trade: b_base MATCH with c_base",
                            direction_trade_3,
                        )

                    except ZeroDivisionError:
                        pass

                # Check if b_base (acquired coin) matches with c_quote
                if b_base == c_quote:
                    swap_4 = c_base
                    direction_trade_3 = "quote_to_base"
                    swap_3_rate = c_bid
                    contract_3 = pair_c
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n1 Final Trade:  b_base MATCH with c_quote", direction_trade_3
                    )

                calculated = 1

            """
            Scenario 2: Check possibility if a_quote (acquired coin) matches with b_base
            """
            # Check if a_quote (acquired coin) matches with b_base
            if a_quote == b_base and calculated == 0:
                try:
                    swap_3 = b_quote
                    # We will use the ASK price because we have different quote coins (ETH/BTC & BTC/TRY). Divided by 1 to represent the inverse of the price, example from ETH/BTC to BTC/ETH. Then amount of ETH/BTC multiplied by 1 divide by ASK price BTC/TRY (BUY) = amount of BTC/TRY that we will get.
                    swap_2_rate = 1 / b_ask
                    direction_trade_2 = "base_to_quote"
                    acquired_coin_t2 = acquired_coin_t1 * swap_2_rate

                    # Place second trade
                    contract_2 = pair_b
                    print("\n2 a_quote MATCH with b_base", direction_trade_2)
                except ZeroDivisionError:
                    pass

                # Check if b_quote (acquired coin) matches with c_base
                if b_quote == c_base:
                    try:
                        swap_4 = c_quote
                        swap_3_rate = 1 / c_ask
                        acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                        contract_3 = pair_c
                        direction_trade_3 = "base_to_quote"
                        print(
                            "\n2 Final Trade: b_quote MATCH with c_base",
                            direction_trade_3,
                        )
                    except ZeroDivisionError:
                        pass

                # Check if b_quote (acquired coin) matches with c_quote
                if b_quote == c_quote:
                    swap_4 = c_base
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n2 Final Trade: b_quote MATCH with c_quote", direction_trade_3
                    )

                calculated = 1

            """
            # Scenario 3: Check if a_quote (acquired coin) matches with c_quote, If so then the flow will be from pair A to pair C to pair B.
            """
            if a_quote == c_quote and calculated == 0:
                swap_3 = c_base
                direction_trade_2 = "quote_to_base"
                swap_2_rate = c_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate

                # Place second trade but now starting with pair C
                contract_2 = pair_c

                print("\n3 a_quote MATCH with c_quote", direction_trade_2)

                # Check if c_base (acquired coin) matches with b_base
                if c_base == b_base:
                    try:
                        swap_4 = b_quote
                        # Next direction will be base to quote, use ASK price because quote coin different.
                        swap_3_rate = 1 / b_ask
                        acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                        direction_trade_3 = "base_to_quote"
                        contract_3 = pair_b
                        print(
                            "\n3 Final Trade: c_base MATCH with b_base",
                            direction_trade_3,
                        )
                    except ZeroDivisionError:
                        pass

                # Check if c_base (acquired coin) matches with b_quote
                if c_base == b_quote:
                    swap_4 = b_base
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n3 Final Trade: c_base MATCH with b_quote", direction_trade_3
                    )

                calculated = 1

            """
            Scenario 4: Check possibility if a_quote (acquired coin) matches with c_base
            """
            # Check if a_quote (acquired coin) matches with c_base
            if a_quote == c_base and calculated == 0:
                try:
                    swap_3 = c_quote
                    direction_trade_2 = "base_to_quote"
                    swap_2_rate = 1 / c_ask
                    acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                    print("\n4 a_quote MATCH with c_base", direction_trade_2)
                except ZeroDivisionError:
                    pass

                # Place second trade
                contract_2 = pair_c

                # Check if c_quote (acquired coin) matches with b_base
                if c_quote == b_base:
                    try:
                        swap_4 = b_quote
                        swap_3_rate = 1 / b_ask
                        acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                        direction_trade_3 = "base_to_quote"
                        contract_3 = pair_b
                        print(
                            "\n4 Final Trade: c_quote MATCH with b_base",
                            direction_trade_3,
                        )
                    except ZeroDivisionError:
                        pass

                # Check if c_quote (acquired coin) matches with b_quote
                if c_quote == b_quote:
                    swap_4 = b_base
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n4 Final Trade: c_quote MATCH with b_quote", direction_trade_3
                    )

                calculated = 1

            # Create trade description
            trade_desc_1 = f"1. Start with {swap_1} of {starting_amount}. Swap at rate {swap_1_rate} for {swap_2} acquiring {acquired_coin_t1}."
            trade_desc_2 = f"2. Swap {acquired_coin_t1} of {swap_2} at rate {swap_2_rate} for {swap_3} acquiring {acquired_coin_t2}."
            trade_desc_3 = f"3. Swap {acquired_coin_t2} of {swap_3} at rate {swap_3_rate} for {swap_4} acquiring {acquired_coin_t3}."

            # PROFIT & LOSS CALCULATION
            profit_surface = acquired_coin_t3 - starting_amount
            profit_percentage = (
                (profit_surface / starting_amount) * 100 if profit_surface != 0 else 0
            )

            # Complete the trade if all 3 trades are valid
            if profit_surface > min_surface_rate:
                surface_dict = {
                    "starting_amount": starting_amount,
                    "direction": direction,
                    "swap_1": swap_1,
                    "swap_2": swap_2,
                    "swap_3": swap_3,
                    "swap_1_rate": swap_1_rate,
                    "swap_2_rate": swap_2_rate,
                    "swap_3_rate": swap_3_rate,
                    "acquired_coin_t1": acquired_coin_t1,
                    "acquired_coin_t2": acquired_coin_t2,
                    "acquired_coin_t3": acquired_coin_t3,
                    "contract_1": contract_1,
                    "contract_2": contract_2,
                    "contract_3": contract_3,
                    "direction_trade_1": direction_trade_1,
                    "direction_trade_2": direction_trade_2,
                    "direction_trade_3": direction_trade_3,
                    "trade_desc_1": trade_desc_1,
                    "trade_desc_2": trade_desc_2,
                    "trade_desc_3": trade_desc_3,
                    "profit_surface": profit_surface,
                    "profit_surface_percentage": profit_percentage,
                }
                return surface_dict
            else:
                calculated = 0

        """
        REVERSE DIRECTION (Quote to Base)
        If a_base matches with pair B either base or quote, then we can swap the coin from pair A to pair B.
        """
        # Assume starting capital with Quote coin of pair A
        if direction == "reverse" and calculated == 0:
            # Determine the total coin that we have (initial capital) based on the convert_usdt.json file with an amount of 10 USD.
            with open("convert_usdt.json", "r") as fp:
                data = json.load(fp)

                if a_quote in data:
                    starting_amount = data[a_quote]
                    print(f"\n\n------Amount------: {starting_amount}")
                else:
                    starting_amount = 10
                    print(f"\n\n------Amount------: {starting_amount}")

            print(f"\n\nFirst Trade (REVERSE): swap {a_quote}/{a_base}")
            direction_trade_1 = "quote_to_base"

            # Use bid price for the first trade for buying
            swap_1 = a_quote
            swap_2 = a_base
            swap_1_rate = a_bid
            acquired_coin_t1 = starting_amount * swap_1_rate
            contract_1 = pair_a

            """
            # Scenario 1: Check if a_base (acquired coin) matches with b_quote
            """
            if a_base == b_quote and calculated == 0:
                swap_3 = b_base
                direction_trade_2 = "quote_to_base"
                swap_2_rate = b_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                print("1 a_base MATCH with b_quote", direction_trade_2)

                # Place second trade
                contract_2 = pair_b

                # Check if b_base (acquired coin) matches with c_base
                if b_base == c_base:
                    swap_3 = c_base

                    try:
                        swap_4 = c_quote
                        swap_3_rate = 1 / c_ask
                        acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                        direction_trade_3 = "base_to_quote"
                        contract_3 = pair_c
                        print(
                            "\n1 Final Trade: b_base MATCH with c_base",
                            direction_trade_3,
                        )
                    except ZeroDivisionError:
                        pass

                # Check if b_base (acquired coin) matches with c_quote
                if b_base == c_quote:
                    swap_4 = c_base
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n1 Final Trade: b_base MATCH with c_quote", direction_trade_3
                    )

                calculated = 1

            """
            Scenario 2: Check possibility if a_base (acquired coin) matches with b_base
            """
            if a_base == b_base and calculated == 0:
                try:
                    swap_3 = b_quote
                    swap_2_rate = 1 / b_ask
                    direction_trade_2 = "base_to_quote"
                    acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                    print("\n2 a_base MATCH with b_base", direction_trade_2)
                except ZeroDivisionError:
                    pass

                # Place second trade
                contract_2 = pair_b

                # Check if b_quote (acquired coin) matches with c_base
                if b_quote == c_base:
                    try:
                        swap_4 = c_quote
                        swap_3_rate = 1 / c_ask
                        acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                        direction_trade_3 = "base_to_quote"
                        contract_3 = pair_c
                        print(
                            "\n2 Final Trade: b_quote MATCH with c_base",
                            direction_trade_3,
                        )
                    except ZeroDivisionError:
                        pass

                # Check if b_quote (acquired coin) matches with c_quote
                if b_quote == c_quote:
                    swap_4 = c_base
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n2 Final Trade: b_quote MATCH with c_quote", direction_trade_3
                    )

                calculated = 1

            """
            # Scenario 3: Check if a_base (acquired coin) matches with c_quote, If so then the flow will be from pair A to pair C to pair B.
            """
            if a_base == c_quote and calculated == 0:
                swap_3 = c_base
                direction_trade_2 = "quote_to_base"
                swap_2_rate = c_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                print("\n3 a_base MATCH with c_quote", direction_trade_2)

                # Place second trade but now starting with pair C
                contract_2 = pair_c

                # Check if c_base (acquired coin) matches with b_base
                if c_base == b_base:
                    try:
                        swap_4 = b_quote
                        # Next direction will be base to quote, use ASK price because quote coin different.
                        swap_3_rate = 1 / b_ask
                        acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                        direction_trade_3 = "base_to_quote"
                        contract_3 = pair_b
                        print(
                            "\n3 Final Trade: c_base MATCH with b_base",
                            direction_trade_3,
                        )
                    except ZeroDivisionError:
                        pass

                # Check if c_base (acquired coin) matches with b_quote
                if c_base == b_quote:
                    swap_4 = b_base
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n3 Final Trade: c_base MATCH with b_quote", direction_trade_3
                    )

                calculated = 1

            """
            Scenario 4: Check possibility if a_base (acquired coin) matches with c_base
            """
            # Check if a_base (acquired coin) matches with c_base
            if a_base == c_base and calculated == 0:
                try:
                    swap_3 = c_quote
                    direction_trade_2 = "base_to_quote"
                    swap_2_rate = 1 / c_ask
                    acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                    print("\n4 a_base MATCH with c_base", direction_trade_2)
                except ZeroDivisionError:
                    pass

                # Place second trade
                contract_2 = pair_c

                # Check if c_quote (acquired coin) matches with b_base
                if c_quote == b_base:
                    try:
                        swap_4 = b_quote
                        swap_3_rate = 1 / b_ask
                        acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                        direction_trade_3 = "base_to_quote"
                        contract_3 = pair_b
                        print(
                            "\n4 Final Trade: c_quote MATCH with b_base",
                            direction_trade_3,
                        )
                    except ZeroDivisionError:
                        pass

                # Check if c_quote (acquired coin) matches with b_quote
                if c_quote == b_quote:
                    swap_3 = c_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n4 Final Trade: c_quote MATCH with b_quote", direction_trade_3
                    )

                calculated = 1

            # Create trade description
            trade_desc_1 = f"1. Start with {swap_1} of {starting_amount}. Swap at rate {swap_1_rate} for {swap_2} acquiring {acquired_coin_t1}."
            trade_desc_2 = f"2. Swap {acquired_coin_t1} of {swap_2} at rate {swap_2_rate} for {swap_3} acquiring {acquired_coin_t2}."
            trade_desc_3 = f"3. Swap {acquired_coin_t2} of {swap_3} at rate {swap_3_rate} for {swap_4} acquiring {acquired_coin_t3}."

            # PROFIT & LOSS CALCULATION
            profit_surface = acquired_coin_t3 - starting_amount
            profit_percentage = (
                (profit_surface / starting_amount) * 100 if profit_surface != 0 else 0
            )

            # Complete the trade if all 3 trades are valid
            if profit_surface > min_surface_rate:
                surface_dict = {
                    "starting_amount": starting_amount,
                    "direction": direction,
                    "swap_1": swap_1,
                    "swap_2": swap_2,
                    "swap_3": swap_3,
                    "swap_1_rate": swap_1_rate,
                    "swap_2_rate": swap_2_rate,
                    "swap_3_rate": swap_3_rate,
                    "acquired_coin_t1": acquired_coin_t1,
                    "acquired_coin_t2": acquired_coin_t2,
                    "acquired_coin_t3": acquired_coin_t3,
                    "contract_1": contract_1,
                    "contract_2": contract_2,
                    "contract_3": contract_3,
                    "direction_trade_1": direction_trade_1,
                    "direction_trade_2": direction_trade_2,
                    "direction_trade_3": direction_trade_3,
                    "trade_desc_1": trade_desc_1,
                    "trade_desc_2": trade_desc_2,
                    "trade_desc_3": trade_desc_3,
                    "profit_surface": profit_surface,
                    "profit_percentage": profit_percentage,
                }
                return surface_dict
            else:
                calculated = 0

    return surface_dict


"""
Scientific Notation
6.432e-05 = 0,00006432
2e5 = 200.0000 (2 * 10 ^ 5)
"""
