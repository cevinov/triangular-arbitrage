# Funtion to create a triangular pair structure from a list of tradeable coins.

import get_tradeable_coins as get
import surface_rate_bookTicker as surf_rate

# After listing all tradable coin pairs, The next step is to structuring triangular pairs.
# This function will create triangular groups.
# For example, if there are 3 coin pairs in a group, then it should have 2 coins that match either base or quote.
def create_triangular_pairs(coin_pairs):
    remove_duplicates = []
    triangular_pairs_list = []

    # Get pair A
    for pair_a in coin_pairs:
        a_base = pair_a[0]
        a_quote = pair_a[1]
        # print("1", pair_a)

        # Get pair B
        for pair_b in coin_pairs:
            b_base = pair_b[0]
            b_quote = pair_b[1]
            # print("2", pair_b)

            # This will check all base and quote in pair B that is included in pair A.
            # But make sure pair_b and pair_a are not the same.
            if (b_base in pair_a or b_quote in pair_a) and (pair_b != pair_a):
                pass

                # Get pair C
                for pair_c in coin_pairs:
                    c_base = pair_c[0]
                    c_quote = pair_c[1]

                    # This will check pair_c is not the same as pair_a and pair_b.
                    if pair_c != pair_a and pair_c != pair_b:
                        all_base_quote = [
                            a_base,
                            a_quote,
                            b_base,
                            b_quote,
                            c_base,
                            c_quote,
                        ]

                        counts_c_base = 0
                        for coin in all_base_quote:
                            if coin == c_base:
                                counts_c_base += 1

                        counts_c_quote = 0
                        for coin in all_base_quote:
                            if coin == c_quote:
                                counts_c_quote += 1

                        # Determining triangular match
                        # Make sure the counts for the c_base & c_quote coin are equal to two. From all_base_quote (pair_a & pair_b),
                        # there are two coins that are the same, either with c_base or c_quote. And c_base and c_quote are not the same.
                        if (
                            counts_c_base == 2
                            and counts_c_quote == 2
                            and c_base != c_quote
                        ):
                            # Combine all pairs into a list.
                            combine = []
                            combine.append("".join(pair_a))
                            combine.append("".join(pair_b))
                            combine.append("".join(pair_c))

                            # Check if there's no duplication between all triangular group pairs that are structured.
                            if combine not in remove_duplicates:
                                # In this case, pair_a, pair_b, and pair_c will have the same two coins as other pairs.
                                remove_duplicates.append(combine)

                                #                                 Create dictionaries from unique triangular pairs.
                                unique_dict = {
                                    "a_base": a_base,
                                    "a_quote": a_quote,
                                    "pair_a": pair_a,
                                    "b_base": b_base,
                                    "b_quote": b_quote,
                                    "pair_b": pair_b,
                                    "c_base": c_base,
                                    "c_quote": c_quote,
                                    "pair_c": pair_c,
                                    "combine": combine,
                                }
                                triangular_pairs_list.append(unique_dict)

                                # Use the yield keyword to perform generator comprehension.
                                # This will make the process faster, then store all pairs.
                                yield triangular_pairs_list


# IP Weight = 20
def save_triarb_groups():
    import json

    # Get all coins that are ready for trade.
    coin_pairs = get.get_coins() # Limit to 100 pairs for testing
    # Format: [base, quote]

    # Return the latest ask and bid price from the book order level (depth).
    surface_rate = surf_rate.get_bookTicker(coin_pairs)
    print("\n\n", coin_pairs, "--", len(coin_pairs))

    triarb_groups = create_triangular_pairs(coin_pairs)

    for group in triarb_groups:
        # print(group)  # Print each triangular pair group.

        # Save triangular pairs list into JSON file
        with open("triangular_groups.json", "w") as fp:  # fp stands for file pointer
            json.dump(group, fp)

    print("\n\nStructuring Complete !!!")


# save_triarb_groups()
"""
# Testing logic for checking for duplication
all_pairs = []
duplicate = []

pair_a = ['MAV','USDT']
pair_b = ['USDT', 'BTC']

all_pairs.append("".join(pair_a))
all_pairs.append("".join(pair_b))

duplicate.append(['BTTTRX', 'BNBETH'])
print("Duplicate :", duplicate,"\n")

if all_pairs not in duplicate:
    print("Same ?:", all_pairs == duplicate)
    duplicate.append(all_pairs)
    
else:
    print("duplicate")
"""
