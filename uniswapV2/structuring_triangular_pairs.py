import json


# Function to create triangular pairs
def structuring_triarb_pairs(pairs):
    # Initialize variables
    triangular_pairs_list = []
    remove_duplicates_list = []
    pairs_list = []

    for pair_a in pairs:
        # Get pair A information (First)
        pair_a_list = []
        a_address = pair_a["id"]
        a_base = pair_a["token0"]["symbol"]
        a_base_name = pair_a["token0"]["name"]
        a_quote = pair_a["token1"]["symbol"]
        a_quote_name = pair_a["token1"]["name"]
        a_base_price = float(pair_a["token0Price"])
        a_quote_price = float(pair_a["token1Price"])
        pair_a_list.append(a_base)
        pair_a_list.append(a_quote)
        a_base_id = pair_a["token0"]["id"]
        a_quote_id = pair_a["token1"]["id"]
        a_base_decimals = pair_a["token0"]["decimals"]
        a_quote_decimals = pair_a["token1"]["decimals"]
        # print(pair_a)
        # print(
        #     "\n\n(A) Base: {} / Quote: {} -- {} -- {} -- {} -- {} -- {}".format(
        #         a_base,
        #         a_quote,
        #         pair_a_list,
        #         a_base_id,
        #         a_quote_id,
        #         a_base_decimals,
        #         a_quote_decimals,
        #     )
        # )

        # Get pair B information (Second)
        for pair_b in pairs:
            pair_b_list = []
            b_address = pair_b["id"]
            b_base = pair_b["token0"]["symbol"]
            b_base_name = pair_b["token0"]["name"]
            b_quote = pair_b["token1"]["symbol"]
            b_quote_name = pair_b["token1"]["name"]
            b_base_price = float(pair_b["token0Price"])
            b_quote_price = float(pair_b["token1Price"])
            pair_b_list.append(b_base)
            pair_b_list.append(b_quote)
            b_base_id = pair_b["token0"]["id"]
            b_quote_id = pair_b["token1"]["id"]
            b_base_decimals = pair_b["token0"]["decimals"]
            b_quote_decimals = pair_b["token1"]["decimals"]

            if (
                b_base in pair_a_list or b_quote in pair_a_list
            ) and pair_b_list != pair_a_list:
                # print(
                #     "(B) Base: {} / Quote: {} -- {}".format(
                #         b_base,
                #         b_quote,
                #         pair_b_list,
                #     )
                # )

                # Get pair C information (Third)
                for pair_c in pairs:
                    pair_c_list = []
                    c_address = pair_c["id"]
                    c_base = pair_c["token0"]["symbol"]
                    c_base_name = pair_c["token0"]["name"]
                    c_quote = pair_c["token1"]["symbol"]
                    c_quote_name = pair_c["token1"]["name"]
                    c_base_price = float(pair_c["token0Price"])
                    c_quote_price = float(pair_c["token1Price"])
                    pair_c_list.append(c_base)
                    pair_c_list.append(c_quote)
                    c_base_id = pair_c["token0"]["id"]
                    c_quote_id = pair_c["token1"]["id"]
                    c_base_decimals = pair_c["token0"]["decimals"]
                    c_quote_decimals = pair_c["token1"]["decimals"]

                    counts_c_base = 0
                    counts_c_quote = 0

                    if pair_c_list != pair_a_list and pair_c_list != pair_b_list:
                        all_combination = []
                        all_combination.extend(pair_a_list)
                        all_combination.extend(pair_b_list)
                        all_combination.extend(pair_c_list)

                        for coin in all_combination:
                            if coin == c_base:
                                counts_c_base += 1

                        for coin in all_combination:
                            if coin == c_quote:
                                counts_c_quote += 1

                        # Make sure the counts for the c_base & c_quote coin are equal to two. From all_base_quote (pair_a & pair_b), there are two coins that are the same, either with c_base or c_quote. And c_base and c_quote are not the same.
                        if (
                            counts_c_base == 2
                            and counts_c_quote == 2
                            and c_base != c_quote
                        ):
                            # print(
                            #     "(C) Base: {} / Quote: {} -- {}".format(
                            #         c_base,
                            #         c_quote,
                            #         pair_c_list,
                            #     )
                            # )

                            if all_combination not in remove_duplicates_list:
                                remove_duplicates_list.append(all_combination)
                                combine = []
                                combine.append("".join(pair_a_list))
                                combine.append("".join(pair_b_list))
                                combine.append("".join(pair_c_list))

                                unique_dict = {
                                    "a_address": a_address,
                                    "a_base": a_base,
                                    "a_base_name": a_base_name,
                                    "a_quote": a_quote,
                                    "a_quote_name": a_quote_name,
                                    "a_pair": "_".join(pair_a_list),
                                    "a_base_id": a_base_id,
                                    "a_quote_id": a_quote_id,
                                    "a_base_price": a_base_price,
                                    "a_base_decimals": a_base_decimals,
                                    "a_quote_price": a_quote_price,
                                    "a_quote_decimals": a_quote_decimals,
                                    "b_address": b_address,
                                    "b_base": b_base,
                                    "b_base_name": b_base_name,
                                    "b_quote": b_quote,
                                    "b_quote_name": b_quote_name,
                                    "b_pair": "_".join(pair_b_list),
                                    "b_base_id": b_base_id,
                                    "b_quote_id": b_quote_id,
                                    "b_base_price": b_base_price,
                                    "b_base_decimals": b_base_decimals,
                                    "b_quote_price": b_quote_price,
                                    "b_quote_decimals": b_quote_decimals,
                                    "c_address": c_address,
                                    "c_base": c_base,
                                    "c_base_name": c_base_name,
                                    "c_quote": c_quote,
                                    "c_quote_name": c_quote_name,
                                    "c_pair": "_".join(pair_c_list),
                                    "c_base_id": c_base_id,
                                    "c_quote_id": c_quote_id,
                                    "c_base_price": c_base_price,
                                    "c_base_decimals": c_base_decimals,
                                    "c_quote_decimals": c_quote_decimals,
                                    "c_quote_price": c_quote_price,
                                    "combine": combine,
                                }
                                triangular_pairs_list.append(unique_dict)

                                # print(triangular_pairs_list)

                                yield triangular_pairs_list


"""
Output:
[{"a_address": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640", "a_base": "USDC", "a_quote": "WETH", "a_pair": "USDC_WETH", "a_base_id": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "a_quote_id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", "a_base_price": 2237.4744910656386, "a_base_decimals": "6", "a_quote_price": 0.00044693246961833807, "a_quote_decimals": "18", "b_address": "0xcbcdf9626bc03e24f779434178a73a0b4bad62ed", "b_base": "WBTC", "b_quote": "WETH", "b_pair": "WBTC_WETH", "b_base_id": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599", "b_quote_id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", "b_base_price": 0.05178158854114097, "b_base_decimals": "8", "b_quote_price": 19.311883396653435, "b_quote_decimals": "18", "c_address": "0x99ac8ca7087fa4a2a1fb6357269965a2014abc35", "c_base": "WBTC", "c_quote": "USDC", "c_pair": "WBTC_USDC", "c_base_id": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599", "c_quote_id": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "c_base_price": 2.3184389431839624e-05, "c_base_decimals": "8", "c_quote_decimals": "6", "c_quote_price": 43132.470792035536, "combine": ["USDCWETH", "WBTCWETH", "WBTCUSDC"]}]
"""


def save_triarb_groups(pairs):
    triangular_groups = structuring_triarb_pairs(pairs)
    for pair in triangular_groups:
        with open("triangular_pairs_uniswap.json", "w") as f:
            json.dump(pair, f)
