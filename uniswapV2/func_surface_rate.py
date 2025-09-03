import json


# Function to calculate the surface rate of a uniswap pool
def calc_surface_rate(pair):
    # Set a variable to check if the result of the bid (sell) - ask (buy) price is a positive number.
    min_rate = 0  # 1%
    starting_amount = 0
    surface_dict = {}
    pool_contract_1 = ""
    pool_contract_2 = ""
    pool_contract_3 = ""
    pool_direction_trade_1 = ""
    pool_direction_trade_2 = ""
    pool_direction_trade_3 = ""
    acquired_coin_t1 = 0
    acquired_coin_t2 = 0
    acquired_coin_t3 = 0

    # If you complete calculating the whole triangular group (3 pairs), then the value will be changed t1. Print out the output.
    calculated = 0
    a_base = pair["a_base"]
    a_quote = pair["a_quote"]
    b_base = pair["b_base"]
    b_quote = pair["b_quote"]
    c_base = pair["c_base"]
    c_quote = pair["c_quote"]
    pair_a = pair["a_pair"]
    pair_b = pair["b_pair"]
    pair_c = pair["c_pair"]
    combine = pair["combine"]

    # print(
    #     "\n\n\nCombine:",
    #     pair_a,
    #     pair_b,
    #     pair_c,
    # )

    # Set price information; in this case, we don't need to calculate the BID and ASK prices because Uniswap already gave us the price for them (token0_price & token1_price).
    # The ASK price came from this calculation: 1 divided by the base price. And the result of that calculation is the same with token1_price.
    # The BID price came from this calculation: 1 divided by the quote price. And the result of that calculation is the same with token0_price.
    a_token0_price = float(pair["a_base_price"])
    a_token1_price = float(pair["a_quote_price"])
    b_token0_price = float(pair["b_base_price"])
    b_token1_price = float(pair["b_quote_price"])
    c_token0_price = float(pair["c_base_price"])
    c_token1_price = float(pair["c_quote_price"])

    # Set address information
    a_address = pair["a_address"]
    b_address = pair["b_address"]
    c_address = pair["c_address"]
    a_base_id = pair["a_base_id"]
    b_base_id = pair["b_base_id"]
    c_base_id = pair["c_base_id"]
    a_quote_id = pair["a_quote_id"]
    b_quote_id = pair["b_quote_id"]
    c_quote_id = pair["c_quote_id"]

    # print("a:", a_token0_price, a_token1_price, pair_a, a_address)
    # print("b:", b_token0_price, b_token1_price, pair_b, b_address)
    # print("c:", c_token0_price, c_token1_price, pair_c, c_address)

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
        1. Direction Base to Quote (Forward): Will use token1_price
        2. Direction Quote to Base (Reverse): Will use token0_price
        """
        # Quote to Base means have the same quote coin between 2 pairs but have different base coin (EX: ETH/BTC & LTC\BTC).
        # Base to Quote means quote coin pair A is the same as base coin pair B (EX: ETH/BTC and ETH/TRY).

        """
        FORWARD DIRECTION (Base to Quote)
        If a_quote matches with pair B either base or quote, then we can swap the coin from pair A to pair B.
        """
        # Assume starting capital with Quote coin of pair A (Forward)
        if direction == "forward" and calculated == 0:
            with open("converter_usd.json", "r") as f:
                converter = json.load(f)
                for pair in converter:
                    if a_base in pair:
                        starting_amount = pair[a_base]

            if starting_amount <= 0:
                starting_amount = 10
                print(starting_amount)

            swap_1 = a_base
            swap_2 = a_quote
            print(f"\n\nFirst Trade (FORWARD): swap {a_base}/{a_quote}")
            pool_direction_trade_1 = "base_to_quote"

            # Use ask price for the first trade for buying
            swap_1_rate = a_token1_price
            acquired_coin_t1 = starting_amount * swap_1_rate
            pool_contract_1 = pair_a
            print(
                f"Rate ({a_base}) -- Acquired T1: {swap_1_rate} -- {acquired_coin_t1} ({a_base})"
            )

            """
            # Scenario 1: Check if a_quote (acquired coin) matches with b_quote
            """
            if a_quote == b_quote and calculated == 0:
                swap_3 = b_base
                pool_direction_trade_2 = "quote_to_base"
                swap_2_rate = b_token0_price
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate

                # Place second trade
                pool_contract_2 = pair_b

                print("\n1 a_quote MATCH with b_quote", pool_direction_trade_2)

                # Check if b_base (acquired coin) matches with c_base
                if b_base == c_base:
                    swap_4 = c_quote
                    pool_direction_trade_3 = "base_to_quote"
                    swap_3_rate = c_token1_price
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    pool_contract_3 = pair_c
                    print(
                        "\n1 Final Trade: b_base MATCH with c_base",
                        pool_direction_trade_3,
                    )

                # Check if b_base (acquired coin) matches with c_quote
                if b_base == c_quote:
                    swap_4 = c_base
                    pool_direction_trade_3 = "quote_to_base"
                    swap_3_rate = c_token0_price
                    pool_contract_3 = pair_c
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n1 Final Trade: b_base MATCH with c_quote",
                        pool_direction_trade_3,
                    )

                calculated = 1

            """
            Scenario 2: Check possibility if a_quote (acquired coin) matches with b_base
            """
            # Check if a_quote (acquired coin) matches with b_base
            if a_quote == b_base and calculated == 0:
                swap_3 = b_quote
                swap_2_rate = b_token1_price
                pool_direction_trade_2 = "base_to_quote"
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate

                # Place second trade
                pool_contract_2 = pair_b
                print("\n2 a_quote MATCH with b_base", pool_direction_trade_2)

                # Check if b_quote (acquired coin) matches with c_base
                if b_quote == c_base:
                    swap_4 = c_quote
                    swap_3_rate = c_token1_price
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    pool_contract_3 = pair_c
                    pool_direction_trade_3 = "base_to_quote"
                    print(
                        "\n2 Final Trade: b_quote MATCH with c_base",
                        pool_direction_trade_3,
                    )

                # Check if b_quote (acquired coin) matches with c_quote
                if b_quote == c_quote:
                    swap_4 = c_base
                    swap_3_rate = c_token0_price
                    pool_direction_trade_3 = "quote_to_base"
                    pool_contract_3 = pair_c
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n2 Final Trade: b_quote MATCH with c_quote",
                        pool_direction_trade_3,
                    )

                calculated = 1

            """
            # Scenario 3: Check if a_quote (acquired coin) matches with c_quote, If so then the flow will be from pair A to pair C to pair B.
            """
            if a_quote == c_quote and calculated == 0:
                swap_3 = c_base
                pool_direction_trade_2 = "quote_to_base"
                swap_2_rate = c_token0_price
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate

                # Place second trade but now starting with pair C
                pool_contract_2 = pair_c
                print("\n3 a_quote MATCH with c_quote", pool_direction_trade_2)

                # Check if c_base (acquired coin) matches with b_base
                if c_base == b_base:
                    swap_4 = b_quote
                    # Next direction will be base to quote, use ASK price because quote coin different.
                    swap_3_rate = b_token1_price
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    pool_direction_trade_3 = "base_to_quote"
                    pool_contract_3 = pair_b
                    print(
                        "\n3 Final Trade: c_base MATCH with b_base",
                        pool_direction_trade_3,
                    )

                # Check if c_base (acquired coin) matches with b_quote
                if c_base == b_quote:
                    swap_4 = b_base
                    swap_3_rate = b_token0_price
                    pool_direction_trade_3 = "quote_to_base"
                    pool_contract_3 = pair_b
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n3 Final Trade: c_base MATCH with b_quote",
                        pool_direction_trade_3,
                    )

                calculated = 1

            """
            Scenario 4: Check possibility if a_quote (acquired coin) matches with c_base
            """
            # Check if a_quote (acquired coin) matches with c_base
            if a_quote == c_base and calculated == 0:
                swap_3 = c_quote
                pool_direction_trade_2 = "base_to_quote"
                swap_2_rate = c_token1_price
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                print("\n4 a_quote MATCH with c_base", pool_direction_trade_2)

                # Place second trade
                pool_contract_2 = pair_c

                # Check if c_quote (acquired coin) matches with b_base
                if c_quote == b_base:
                    swap_4 = b_quote
                    swap_3_rate = b_token1_price
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    pool_direction_trade_3 = "base_to_quote"
                    pool_contract_3 = pair_b
                    print(
                        "\n4 Final Trade: c_quote MATCH with b_base",
                        pool_direction_trade_3,
                    )

                # Check if c_quote (acquired coin) matches with b_quote
                if c_quote == b_quote:
                    swap_4 = b_base
                    swap_3_rate = b_token0_price
                    pool_direction_trade_3 = "quote_to_base"
                    pool_contract_3 = pair_b
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n4 Final Trade: c_quote MATCH with b_quote",
                        pool_direction_trade_3,
                    )
                calculated = 1

            # Create trade description
            trade_desc_1 = f"1. Start with {swap_1} of {starting_amount}. Swap at rate {swap_1_rate} for {swap_2} acquiring {acquired_coin_t1}."
            trade_desc_2 = f"2. Swap {acquired_coin_t1} of {swap_2} at rate {swap_2_rate} for {swap_3} acquiring {acquired_coin_t2}."
            trade_desc_3 = f"3. Swap {acquired_coin_t2} of {swap_3} at rate {swap_3_rate} for {swap_4} acquiring {acquired_coin_t3}."

            # PROFIT & LOSS CALCULATION
            profit_surface = acquired_coin_t3 - starting_amount
            profit_percentage = (
                profit_surface / starting_amount if profit_surface != 0 else 0
            )

        # Complete the trade if all 3 trades are valid
        # Take profit if profit equals or greater than 1%
        if profit_surface > 0 and profit_percentage >= min_rate:
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
                "pool_contract_1": pool_contract_1,
                "pool_contract_2": pool_contract_2,
                "pool_contract_3": pool_contract_3,
                "pool_direction_trade_1": pool_direction_trade_1,
                "pool_direction_trade_2": pool_direction_trade_2,
                "pool_direction_trade_3": pool_direction_trade_3,
                "a_address": a_address,
                "b_address": b_address,
                "c_address": c_address,
                "a_base_id": a_base_id,
                "a_quote_id": a_quote_id,
                "b_base_id": b_base_id,
                "b_quote_id": b_quote_id,
                "c_base_id": c_base_id,
                "c_quote_id": c_quote_id,
                "trade_desc_1": trade_desc_1,
                "trade_desc_2": trade_desc_2,
                "trade_desc_3": trade_desc_3,
                "profit_surface": profit_surface,
                "profit_percentage": profit_percentage,
                "combine": combine,
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
            with open("converter_usd.json", "r") as f:
                converter = json.load(f)
                for pair in converter:
                    if a_quote in pair:
                        starting_amount = pair[a_quote]

            if starting_amount <= 0:
                starting_amount = 10
                print(starting_amount)

            swap_1 = a_quote
            swap_2 = a_base
            print(f"\n\nFirst Trade (REVERSE): swap {a_quote}/{a_base}")
            pool_direction_trade_1 = "quote_to_base"

            # Use bid price for the first tr0de for buying
            swap_1_rate = a_token0_price
            acquired_coin_t1 = starting_amount * swap_1_rate
            pool_contract_1 = pair_a

            """
            # Scenario 1: Check if a_base (acquired coin) matches with b_quote
            """
            if a_base == b_quote and calculated == 0:
                swap_3 = b_base
                pool_direction_trade_2 = "quote_to_base"
                swap_2_rate = b_token0_price
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                print("1 a_base MATCH with b_quote", pool_direction_trade_2)

                # Place second trade
                pool_contract_2 = pair_b

                # Check if b_base (acquired coin) matches with c_base
                if b_base == c_base:
                    swap_4 = c_quote
                    swap_3_rate = c_token1_price
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    pool_direction_trade_3 = "base_to_quote"
                    pool_contract_3 = pair_c
                    print(
                        "\n1 Final Trade: b_base MATCH with c_base",
                        pool_direction_trade_3,
                    )

                # Check if b_base (acquired coin) matches with c_quote
                if b_base == c_quote:
                    swap_4 = c_base
                    swap_3_rate = c_token0_price
                    pool_direction_trade_3 = "quote_to_base"
                    pool_contract_3 = pair_c
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n1 Final Trade: b_base MATCH with c_quote",
                        pool_direction_trade_3,
                    )

                calculated = 1

            """
            Scenario 2: Check possibility if a_base (acquired coin) matches with b_base
            """
            if a_base == b_base and calculated == 0:
                swap_3 = b_quote
                swap_2_rate = b_token1_price
                pool_direction_trade_2 = "base_to_quote"
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                print("\n2 a_base MATCH with b_base", pool_direction_trade_2)

                # Place second trade
                pool_contract_2 = pair_b

                # Check if b_quote (acquired coin) matches with c_base
                if b_quote == c_base:
                    swap_4 = c_quote
                    swap_3_rate = c_token1_price
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    pool_direction_trade_3 = "base_to_quote"
                    pool_contract_3 = pair_c
                    print(
                        "\n2 Final Trade: b_quote MATCH with c_base",
                        pool_direction_trade_3,
                    )

                # Check if b_quote (acquired coin) matches with c_quote
                if b_quote == c_quote:
                    swap_4 = c_base
                    swap_3_rate = c_token0_price
                    pool_direction_trade_3 = "quote_to_base"
                    pool_contract_3 = pair_c
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n2 Final Trade: b_quote MATCH with c_quote",
                        pool_direction_trade_3,
                    )

                calculated = 1

            """
            # Scenario 3: Check if a_base (acquired coin) matches with c_quote, If so then the flow will be from pair A to pair C to pair B.
            """
            if a_base == c_quote and calculated == 0:
                swap_3 = c_base
                pool_direction_trade_2 = "quote_to_base"
                swap_2_rate = c_token0_price
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                print("\n3 a_base MATCH with c_quote", pool_direction_trade_2)

                # Place second trade but now starting with pair C
                pool_contract_2 = pair_c

                # Check if c_base (acquired coin) matches with b_base
                if c_base == b_base:
                    swap_4 = b_quote
                    # Next direction will be base to quote, use ASK price because quote coin different.
                    swap_3_rate = b_token1_price
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    pool_direction_trade_3 = "base_to_quote"
                    pool_contract_3 = pair_b
                    print(
                        "\n3 Final Trade: c_base MATCH with b_base",
                        pool_direction_trade_3,
                    )

                # Check if c_base (acquired coin) matches with b_quote
                if c_base == b_quote:
                    swap_4 = b_base
                    swap_3_rate = b_token0_price
                    pool_direction_trade_3 = "quote_to_base"
                    pool_contract_3 = pair_b
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n3 Final Trade: c_base MATCH with b_quote",
                        pool_direction_trade_3,
                    )

                calculated = 1

            """
            Scenario 4: Check possibility if a_base (acquired coin) matches with c_base
            """
            # Check if a_base (acquired coin) matches with c_base
            if a_base == c_base and calculated == 0:
                swap_3 = c_quote
                pool_direction_trade_2 = "base_to_quote"
                swap_2_rate = c_token1_price
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                print("\n4 a_base MATCH with c_base", pool_direction_trade_2)

                # Place second trade
                pool_contract_2 = pair_c

                # Check if c_quote (acquired coin) matches with b_base
                if c_quote == b_base:
                    swap_4 = b_quote
                    swap_3_rate = b_token1_price
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    pool_direction_trade_3 = "base_to_quote"
                    pool_contract_3 = pair_b
                    print(
                        "\n4 Final Trade: c_quote MATCH with b_base",
                        pool_direction_trade_3,
                    )

                # Check if c_quote (acquired coin) matches with b_quote
                if c_quote == b_quote:
                    swap_4 = b_base
                    swap_3_rate = b_token0_price
                    pool_direction_trade_3 = "quote_to_base"
                    pool_contract_3 = pair_b
                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    print(
                        "\n4 Final Trade: c_quote MATCH with b_quote",
                        pool_direction_trade_3,
                    )

                calculated = 1

            # Create trade description
            trade_desc_1 = f"1. Start with {swap_1} of {starting_amount}. Swap at rate {swap_1_rate} for {swap_2} acquiring {acquired_coin_t1}."
            trade_desc_2 = f"2. Swap {acquired_coin_t1} of {swap_2} at rate {swap_2_rate} for {swap_3} acquiring {acquired_coin_t2}."
            trade_desc_3 = f"3. Swap {acquired_coin_t2} of {swap_3} at rate {swap_3_rate} for {swap_4} acquiring {acquired_coin_t3}."

            # PROFIT & LOSS CALCULATION
            profit_surface = acquired_coin_t3 - starting_amount
            profit_percentage = (
                profit_surface / starting_amount if profit_surface != 0 else 0
            )

        # Complete the trade if all 3 trades are valid
        # Take profit if profit equals or greater than 1%
        if profit_surface > 0 and profit_percentage >= min_rate:
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
                "pool_contract_1": pool_contract_1,
                "pool_contract_2": pool_contract_2,
                "pool_contract_3": pool_contract_3,
                "pool_direction_trade_1": pool_direction_trade_1,
                "pool_direction_trade_2": pool_direction_trade_2,
                "pool_direction_trade_3": pool_direction_trade_3,
                "a_address": a_address,
                "b_address": b_address,
                "c_address": c_address,
                "a_base_id": a_base_id,
                "a_quote_id": a_quote_id,
                "b_base_id": b_base_id,
                "b_quote_id": b_quote_id,
                "c_base_id": c_base_id,
                "c_quote_id": c_quote_id,
                "trade_desc_1": trade_desc_1,
                "trade_desc_2": trade_desc_2,
                "trade_desc_3": trade_desc_3,
                "profit_surface": profit_surface,
                "profit_percentage": profit_percentage,
                "combine": combine,
            }
            return surface_dict
        else:
            calculated = 0


def save_surf_rate():
    # List to store only profitable surface rates
    profit_surf_rate = []

    # Open the json file that contains the list of all the triangular pairs in the uniswap protocol.
    with open("triangular_pairs_uniswap.json", "r") as f:
        structured_pairs = json.load(f)

    # Extract pair information.
    for i, pair in enumerate(structured_pairs):
        surface_dict = calc_surface_rate(pair)

        try:
            if len(surface_dict) > 0:
                profit_surf_rate.append(surface_dict)
        except TypeError:
            pass

            # Save the list of profitable surface rates to a json file.
        with open("profit_surf_rate_uniswap.json", "w") as f:
            json.dump(profit_surf_rate, f)

    print("File saved!")

    # Return False value to stop the while loop in the main function (If needed).
    return False


def open_file():
    with open("profit_surf_rate_uniswap.json", "r") as f:
        list_opportunity = json.load(f)

    for i, pair in enumerate(list_opportunity):
        print("\n\n", i + 1, pair)


# open_file()

"""
Output:

Forward trade:
{"starting_amount": 10.006003602161297, "direction": "forward", "swap_1": "USDC", "swap_2": "WETH", "swap_3": "XMON", "swap_1_rate": 0.00044469956980515164, "swap_2_rate": 2.1790971314357765, "swap_3_rate": 1179.1906086350907, "acquired_coin_t1": 0.004449665497349926, "acquired_coin_t2": 0.009696253321123971, "acquired_coin_t3": 11.433730855216195, "pool_contract_1": "USDC_WETH", "pool_contract_2": "XMON_WETH", "pool_contract_3": "XMON_USDC", "pool_direction_trade_1": "base_to_quote", "pool_direction_trade_2": "quote_to_base", "pool_direction_trade_3": "base_to_quote", "a_address": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640", "b_address": "0xd3ca35355106cb8bc5fd7c534275509673319d83", "c_address": "0x59b4bb1f5d943cf71a10df63f6b743ee4a4489ee", "a_base_id": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "a_quote_id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", "b_base_id": "0x3aada3e213abf8529606924d8d1c55cbdc70bf74", "b_quote_id": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "c_base_id": "0x3aada3e213abf8529606924d8d1c55cbdc70bf74", "c_quote_id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", "trade_desc_1": "1. Start with USDC of 10.006003602161297. Swap at rate 0.00044469956980515164 for WETH acquiring 0.004449665497349926.", "trade_desc_2": "2. Swap 0.004449665497349926 of WETH at rate 2.1790971314357765 for XMON acquiring 0.009696253321123971.", "trade_desc_3": "3. Swap 0.009696253321123971 of XMON at rate 1179.1906086350907 for USDC acquiring 11.433730855216195.", "profit_surface": 1.4277272530548988, "profit_percentage": 14.26870616703066, "combine": ["USDCWETH", "XMONUSDC", "XMONWETH"]}


Reverse trade:
{"starting_amount": 10.006003602161297, "direction": "reverse", "swap_1": "USDC", "swap_2": "YGG", "swap_3": "WETH", "swap_1_rate": 0.9876745286232395, "swap_2_rate": 0.0005262956188800737, "swap_3_rate": 2248.709168839892, "acquired_coin_t1": 9.882674891167095, "acquired_coin_t2": 0.0052012084980373515, "acquired_coin_t3": 11.696005238584554, "pool_contract_1": "YGG_USDC", "pool_contract_2": "YGG_WETH", "pool_contract_3": "USDC_WETH", "pool_direction_trade_1": "quote_to_base", "pool_direction_trade_2": "base_to_quote", "pool_direction_trade_3": "quote_to_base", "a_address": "0x7ec0b75a98997c927ace6d87958147a105147ea0", "b_address": "0x319f4366b2ec8b0120d09522c88f919bedbb18ff", "c_address": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640", "a_base_id": "0x25f8087ead173b73d6e8b84329989a8eea16cf73", "a_quote_id": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "b_base_id": "0x25f8087ead173b73d6e8b84329989a8eea16cf73", "b_quote_id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", "c_base_id": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "c_quote_id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", "trade_desc_1": "1. Start with USDC of 10.006003602161297. Swap at rate 0.9876745286232395 for YGG acquiring 9.882674891167095.", "trade_desc_2": "2. Swap 9.882674891167095 of YGG at rate 0.0005262956188800737 for WETH acquiring 0.0052012084980373515.", "trade_desc_3": "3. Swap 0.0052012084980373515 of WETH at rate 2248.709168839892 for USDC acquiring 11.696005238584554.", "profit_surface": 1.6900016364232577, "profit_percentage": 16.88987635441404, "combine": ["YGGUSDC", "YGGWETH", "USDCWETH"]}
"""
