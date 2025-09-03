import time
import requests
import json

# Dot in float number means the decimal point, not the thousands separator.


# Function to find depth price for each pair
def find_depth(sym):
    limit = 5
    url = f"https://data-api.binance.vision/api/v3/depth?symbol={sym}&limit={limit}"  # Total 5 weight * 3 calls = 15 weight
    resp = requests.get(url)
    data = resp.json()
    return data

    """
    Example output:
    {'lastUpdateId': 41472101646, 'bids': [['42754.99000000', '11.00231000'], ['42754.97000000', '1.02631000'], ['42754.72000000', '0.46838000'], ['42754.71000000', '0.34418000'], ['42754.46000000', '0.00062000']], 'asks': [['42755.00000000', '1.31529000'], ['42755.07000000', '0.00100000'], ['42755.24000000', '0.00062000'], ['42755.49000000', '0.01018000'], ['42755.50000000', '0.12720000']]}
    """


# Function to reformat depth data from order book
def reformat_depth_orderbook(ask, bid, direction):
    price_list_main = []
    if direction == "base_to_quote":
        # print("\n-------Base to Quote-------")
        for i in range(len(ask)):
            ask_price = float(ask[i][0])
            ask_amount = float(ask[i][1])

            # Calculate the coin price (adjusted price) to buy and the quantity of coins we get (adjusted quantity).
            adj_price = 1 / ask_price if ask_price != 0 else 0
            adj_quantity = adj_price * ask_amount

            # print(f"\nAsk: {ask_price}, Amount: {ask_amount}")
            # print(f"Adj Price: {adj_price}, Adj Quantity: {adj_quantity}")
            price_list_main.append([adj_price, adj_quantity])

    if direction == "quote_to_base":
        # print("\n-------Quote to Base-------")
        for i in range(len(bid)):
            bid_price = float(bid[i][0])
            bid_amount = float(bid[i][1])

            adj_price = bid_price if bid_price != 0 else 0
            adj_quantity = bid_amount

            # print(
            #     f"\nBid: {bid_price}, Amount: {bid_amount}, Adj Quantity: {adj_quantity}"
            # )
            price_list_main.append([adj_price, adj_quantity])

    return price_list_main


# Function to get acquired coin, do depth rate calculation, and get the profit
def calculate_acquired_coin(pair, amount_in, orderbook):
    """
    Challenges:
    1. Starting amount can be eaten on the first level of order book (Level 0), as long as the amount in the order book is enough.
    2. Some amount of starting amount can be eaten up by multiple levels, if first level is not enough.
    3. There is a possibility that if the depth of the order book level is not enough because of liquidation or coin, it's a new coin and not popular.
    """

    # Initialize variables
    trading_balance = amount_in  # Starting amount to trade
    quantity_bought = 0  # Monitored every spent amount for each level
    acquired_coin = 0
    counts = 0

    for level in orderbook:
        level_price = level[0]
        level_quantity = level[1]

        # If amount in <= level quantity, then we buy the coin with all balance amount
        try:
            if trading_balance <= level_quantity:
                quantity_bought = trading_balance  # Amount of base coin we bought, if the direction is base to quote
                trading_balance = 0

                # No need divided by 1, because we already get the adjusted price and quantity
                amount_bought = (
                    quantity_bought * level_price
                )  # Amount of quote coin that we get, if the direction is quote to base

                # print(
                #     "less",
                #     trading_balance,
                #     quantity_bought,
                #     amount_bought,
                #     level_price,
                #     level_quantity,
                # )

            # If amount in > a given level quantity, then we buy the coin with the level quantity until the balance is 0
            if trading_balance > level_quantity:
                quantity_bought = level_quantity
                trading_balance -= level_price
                amount_bought = quantity_bought * level_price
                # print(
                #     "greater",
                #     trading_balance,
                #     quantity_bought,
                #     amount_bought,
                #     level_price,
                #     level_quantity,
                # )

            # Stop if already at the last level of order book, to avoid an error
            counts += 1

            # Accumulate the acquired coin
            acquired_coin += amount_bought

            # Exit trade if trading balance is 0
            if trading_balance == 0 or trading_balance < 0:
                print(
                    f"Exit trade at level {counts} {acquired_coin} -- balance {trading_balance}"
                )
                return acquired_coin

            # Exit if orderbook levels is not enough
            if counts == len(orderbook) - 1:
                print(
                    f"Order book is not enough, {amount_in}, {trading_balance}, {acquired_coin}"
                )
                return 0
        except TypeError:
            print("Type error")
            return 0


# Get depth rate for each triangular pair.
# https://binance-docs.github.io/apidocs/spot/en/#order-book
def get_depth_from_orderbook(pair):
    # Extract initial variables
    starting_amount = pair["starting_amount"]
    base = pair["contract_1"][0]

    # Will using real data from surface rate for the contract pair and direction trade
    # Define pairs
    contract_1 = pair["contract_1"]
    contract_2 = pair["contract_2"]
    contract_3 = pair["contract_3"]
    list_contract = [contract_1, contract_2, contract_3]

    # Define direction of the trade
    direction_trade_1 = pair[
        "direction_trade_1"
    ]  # Convert base coin price first in USD, then convert from USD to quote coin price
    direction_trade_2 = pair[
        "direction_trade_2"
    ]  # Convert quote coin price first in USD, then convert from USD to base coin price
    direction_trade_3 = pair["direction_trade_3"]

    list_direction_trade = [direction_trade_1, direction_trade_2, direction_trade_3]

    real_rate = []

    # Limit the API call using time.sleep()
    time.sleep(0.5)  # 5 weight * 3 calls = 15 weight

    for i, pair in enumerate(list_contract):
        symbol = "".join(pair)
        # Get depth price for each pair
        result = find_depth(symbol)

        # Reformat depth price from order book
        real_rate.append(
            reformat_depth_orderbook(
                result["asks"], result["bids"], list_direction_trade[i]
            )
        )

    print("\nReal Rate: ", real_rate, len(real_rate))

    # Do depth rate calculation
    print("\n")
    acquired_coin_t1 = calculate_acquired_coin(
        list_contract[0], starting_amount, real_rate[0]
    )
    acquired_coin_t2 = calculate_acquired_coin(
        list_contract[1], acquired_coin_t1, real_rate[1]
    )
    acquired_coin_t3 = calculate_acquired_coin(
        list_contract[2], acquired_coin_t2, real_rate[2]
    )

    # Calculate profit loss
    profit_loss = acquired_coin_t3 - starting_amount
    real_rate_percentage = profit_loss / starting_amount if profit_loss != 0 else 0
    print(f"\nStarting amount: {starting_amount}, End amount: {acquired_coin_t3}")

    # Take 5% profit
    if profit_loss > 0 and real_rate_percentage > 0:
        return_dict = {
            "acquired_coin_t1": acquired_coin_t1,
            "acquired_coin_t2": acquired_coin_t2,
            "acquired_coin_t3": acquired_coin_t3,
            "profit_loss": profit_loss,
            "real_rate_percentage": real_rate_percentage,
            "contract_1": contract_1,
            "contract_2": contract_2,
            "contract_3": contract_3,
            "contract_direction_1": direction_trade_1,
            "contract_direction_2": direction_trade_2,
            "contract_direction_3": direction_trade_3,
        }
        return return_dict
    else:
        print(f"Loss: {profit_loss} {real_rate_percentage}")
        return {}


# get_depth_from_orderbook()


"""
Output:

------Amount------: 0.004


--ETHBTC--

Ask: 0.05543, Amount: 16.985
Adj Price: 18.040772145047807, Adj Quantity: 306.422514883637

Ask: 0.05544, Amount: 34.045
Adj Price: 18.037518037518037, Adj Quantity: 614.0873015873016

Ask: 0.05545, Amount: 19.2764
Adj Price: 18.034265103697024, Adj Quantity: 347.6357078449053

Ask: 0.05546, Amount: 6.9785
Adj Price: 18.031013342949873, Adj Quantity: 125.8294266137757

Ask: 0.05547, Amount: 9.9402
Adj Price: 18.02776275464215, Adj Quantity: 179.19956733369392


--LTCBTC--

Bid: 0.001755, Amount: 289.281, Adj Quantity: 289.281

Bid: 0.001754, Amount: 397.841, Adj Quantity: 397.841

Bid: 0.001753, Amount: 246.851, Adj Quantity: 246.851

Bid: 0.001752, Amount: 265.915, Adj Quantity: 265.915

Bid: 0.001751, Amount: 380.97, Adj Quantity: 380.97


--LTCETH--

Ask: 0.0317, Amount: 4.143
Adj Price: 31.545741324921135, Adj Quantity: 130.69400630914825

Ask: 0.03171, Amount: 8.714
Adj Price: 31.535793125197095, Adj Quantity: 274.8029012929675

Ask: 0.03172, Amount: 24.166
Adj Price: 31.525851197982348, Adj Quantity: 761.8537200504414

Ask: 0.03173, Amount: 152.459
Adj Price: 31.51591553734636, Adj Quantity: 4804.884966908288

Ask: 0.03174, Amount: 52.125
Adj Price: 31.5059861373661, Adj Quantity: 1642.249527410208

Real Rate:  [[[18.040772145047807, 306.422514883637], [18.037518037518037, 614.0873015873016], [18.034265103697024, 347.6357078449053], [18.031013342949873, 125.8294266137757], [18.02776275464215, 179.19956733369392]], [[0.001755, 289.281], [0.001754, 397.841], [0.001753, 246.851], [0.001752, 265.915], [0.001751, 380.97]], [[31.545741324921135, 130.69400630914825], [31.535793125197095, 274.8029012929675], [31.525851197982348, 761.8537200504414], [31.51591553734636, 4804.884966908288], [31.5059861373661, 1642.249527410208]]] 3

trading_balance, quantity_bought, amount_bought, level_price, level_quantity
less 0 0.004 0.07216308858019123 18.040772145047807 306.422514883637
Exit trade at level 1 0.07216308858019123 -- balance 0
less 0 0.07216308858019123 0.0001266462204582356 0.001755 289.281
Exit trade at level 1 0.0001266462204582356 -- balance 0
less 0 0.0001266462204582356 0.0039951489103544355 31.545741324921135 130.69400630914825
Exit trade at level 1 0.0039951489103544355 -- balance 0

Starting amount: 0.004, End amount: 0.0039951489103544355
Loss: -4.85108964556457e-06 -0.12127724113911426
"""
