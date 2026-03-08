import time
import requests
import json

# https://www.binance.com/en/fee/trading
# TRADING_FEE = 0 # 0.1% per trade

# For testing
# TRADING_FEE = 0

# Function to find depth price for each pair
def find_depth(sym):
    limit = 5
    url = f"https://data-api.binance.vision/api/v3/depth?symbol={sym}&limit={limit}"  # Total 5 weight * 3 calls = 15 weight
    resp = requests.get(url)
    data = resp.json()
    return data

    """
    Example output:
    {'lastUpdateId': 41472101646, 'bids': [['42754.99000000', '11.00231000'], ['42754.97000000', '1.02631000'], ['42754.72000000', '0.46838000'], ['42754.71000000', '0.34418000'], ['42754.46000000', '0.00062000']], 'asks': [['42755.00000000', '1.31529000'], ['42755.07000000', '000000'], ['42755.24000000', '0.00062000'], ['42755.49000000', '0.01018000'], ['42755.50000000', '0.12720000']]}
    """


# Function to reformat depth data from order book
def reformat_depth_orderbook(ask, bid, direction):
    price_list_main = []
    if direction == "base_to_quote":
        # We hold Base. We want Quote. We sell Base to BIDS.
        for i in range(len(bid)):
            bid_price = float(bid[i][0])
            bid_amount = float(bid[i][1])

            adj_price = bid_price if bid_price != 0 else 0
            adj_quantity = bid_amount  # Capacity in Base

            price_list_main.append([adj_price, adj_quantity])

    if direction == "quote_to_base":
        # We hold Quote. We want Base. We buy Base from ASKS.
        for i in range(len(ask)):
            ask_price = float(ask[i][0])
            ask_amount = float(ask[i][1])

            adj_price = 1 / ask_price if ask_price != 0 else 0
            # Capacity in Quote = price * amount
            adj_quantity = ask_price * ask_amount

            price_list_main.append([adj_price, adj_quantity])

    return price_list_main


# Function to get acquired coin, do depth rate calculation, and get the profit
def calculate_acquired_coin(pair, amount_in, orderbook, fee=0):
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
                quantity_bought = trading_balance
                trading_balance = 0
                amount_bought = (quantity_bought * level_price) * (1 - fee)
                
            # If amount in > a given level quantity, then we buy the coin with the level quantity until the balance is 0
            else:
                quantity_bought = level_quantity
                trading_balance -= level_quantity
                amount_bought = (quantity_bought * level_price) * (1 - fee)

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
def get_depth_from_orderbook(pair, fee=0):
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

    for i, c_pair in enumerate(list_contract):
        symbol = "".join(c_pair)
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
        list_contract[0], starting_amount, real_rate[0], fee
    )
    acquired_coin_t2 = calculate_acquired_coin(
        list_contract[1], acquired_coin_t1, real_rate[1], fee
    )
    acquired_coin_t3 = calculate_acquired_coin(
        list_contract[2], acquired_coin_t2, real_rate[2], fee
    )

    # Calculate profit loss
    profit_loss = acquired_coin_t3 - starting_amount
    real_rate_percentage = profit_loss / starting_amount if profit_loss != 0 else 0
    print(f"\nStarting amount: {starting_amount}, End amount: {acquired_coin_t3}")

    # Hypothesis Testing Balances
    gross_t1 = calculate_acquired_coin(
        list_contract[0], starting_amount, real_rate[0], 0
    )
    gross_t2 = calculate_acquired_coin(
        list_contract[1], gross_t1, real_rate[1], 0
    )
    gross_t3 = calculate_acquired_coin(
        list_contract[2], gross_t2, real_rate[2], 0
    )

    gross_depth_balance = gross_t3
    ideal_surface_balance = pair.get("acquired_coin_t3", 0)
    net_surface_balance = ideal_surface_balance * ((1 - fee) ** 3)

    # Take +x% profit
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
            "gross_depth_balance": gross_depth_balance,
            "ideal_surface_balance": ideal_surface_balance,
            "net_surface_balance": net_surface_balance,
        }
        return return_dict
    else:
        print(f"Loss: {profit_loss} {real_rate_percentage}")
        return {}


# get_depth_from_orderbook()
