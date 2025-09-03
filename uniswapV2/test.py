# Code block testing logic for checking duplication on structuring_triangular_pairs.py

# counts = 0
# c_base = "ez-cvxsteCRV"

# dupli = []
# dupli.append(["RBN", "USDC", "USDC", "WETH", "WETH", "RBN"])
# dupli.append(["WBTC", "WETH", "WBTC", "USDT", "WETH", "USDT"])

# c = []
# c.extend(["ease.org", "ez-cvxsteCRV"])
# c.extend(["ease.org", "ez-SLP-WBTC-WETH"])
# c.extend(["ez-cvxsteCRV", "ez-SLP-WBTC-WETH"])

# # c = [
# #     ["ease.org", "ez-cvxsteCRV"],
# #     ["ease.org", "ez-SLP-WBTC-WETH"],
# #     ["ez-cvxsteCRV", "ez-SLP-WBTC-WETH"],
# # ]

# # for coin in c:
# #     if coin == c_base:
# #         counts += 1
# # print("cc", counts)

# for i in range(0, 2):
#     if c not in dupli:
#         dupli.append(c)
#         print("\nNOT DUPLICATE", dupli, len(dupli))
#     else:
#         print("\nDUPLICATE", dupli, len(dupli))
import json

a_quote = "WETH"
starting_amount = 0
with open("converter_usd.json", "r") as f:
    converter = json.load(f)
    for pair in converter:
        if a_quote in pair:
            starting_amount = pair[a_quote]
            print(starting_amount)

if starting_amount <= 0:
    starting_amount = 10
    print(starting_amount)
