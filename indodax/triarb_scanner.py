import sys
import os
import json
import time
import requests
from datetime import datetime
from func_slack_notif import arb_notif

# Fee Structure (Maker & Taker Fees)
# https://help.indodax.com/hc/id/articles/4416646599705-Rincian-Biaya-Transaksi-di-INDODAX

# Flowchart: https://www.mermaidchart.com/app/projects/8bd4d867-a503-4f14-ba86-d8bb10756720/diagrams/6b4c73bd-4393-46aa-967a-7dcd6dce81e6/share/invite/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkb2N1bWVudElEIjoiNmI0YzczYmQtNDM5My00NmFhLTk2N2EtN2RjZDZkY2U4MWU2IiwiYWNjZXNzIjoiVmlldyIsImlhdCI6MTc2MzczMDAyNn0.YfBHf-lCabopJDvd0HViGIM-PdJngjiN72VWN3m60tM

# IDR Pairs
# FEE_IDR_BUY = 0.002222  # 0.2222%
# FEE_IDR_SELL = 0.004322 # 0.4322%

# USDT Pairs
# FEE_USDT_BUY = 0.003144  # 0.3144%
# FEE_USDT_SELL = 0.003144 # 0.3144%

# For testing only
FEE_IDR_BUY = 0
FEE_IDR_SELL = 0

FEE_USDT_BUY = 0
FEE_USDT_SELL = 0

FEE_OTHERS = 0

def get_fee(pair_id, action):
    """Returns the taker fee based on pair and action."""
    pair_id = pair_id.lower()

    if pair_id.endswith('idr'):
        return FEE_IDR_BUY if action == 'buy' else FEE_IDR_SELL
    elif pair_id.endswith('usdt'):
        return FEE_USDT_BUY if action == 'buy' else FEE_USDT_SELL
    else:
        # Fallback for other pairs (if any)
        return FEE_OTHERS

def get_ticker_summaries():
    """Fetches the summary of all tickers (prices) from Indodax."""
    try:
        # Using summaries endpoint to get all prices at once
        response = requests.get("https://indodax.com/api/summaries")
        response.raise_for_status()
        return response.json()['tickers']
    except Exception as e:
        print(f"Error fetching summaries: {e}")
        return {}

def get_depth(pair_id):
    """Fetches the order book depth for a specific pair."""
    try:
        # Remove underscore for API call (e.g., btc_idr -> btcidr)
        formatted_pair_id = pair_id.replace('_', '')
        response = requests.get(f"https://indodax.com/api/depth/{formatted_pair_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching depth for {pair_id}: {e}")
        return None

def calculate_profit(triangle, tickers, initial_amount, fee_percent=None):
    """
    Calculates the profit multiplier for a given triangle using order book depth.
    Returns (final_balance, details)
    """
    balance = initial_amount
    steps = [triangle['step1'], triangle['step2'], triangle['step3']]
    details = {}

    for i, step in enumerate(steps):
        input_balance = balance
        pair_id = step['pair']
        action = step['action']

        # Fetch depth for the pair
        depth = get_depth(pair_id)
        if not depth or 'buy' not in depth or 'sell' not in depth:
            # print(f"Depth data missing or invalid for {pair_id}: {depth}")
            return 0.0, {}

        # Determine and Apply Fee
        if fee_percent is not None:
            fee = fee_percent
        else:
            fee = get_fee(pair_id, action)
        
        # Calculate acquired amount based on depth
        acquired_amount = 0
        remaining_balance = balance
        
        if action == 'buy':
            # Buying: Look at 'sell' orders (asks)
            orders = depth['sell']
            for price, volume in orders:
                price = float(price)
                volume = float(volume)
                
                # Calculate cost for this order level
                cost = price * volume
                
                if remaining_balance <= cost:
                    # Can fill remaining balance at this price
                    amount = remaining_balance / price
                    acquired_amount += amount
                    remaining_balance = 0
                    break
                else:
                    # Fill entire level and continue
                    acquired_amount += volume
                    remaining_balance -= cost
            
            if remaining_balance > 0:
                # Not enough liquidity to fill the order
                return 0.0, {}
                
        elif action == 'sell':
            # Selling: Look at 'buy' orders (bids)
            orders = depth['buy']
            for price, volume in orders:
                price = float(price)
                volume = float(volume)
                
                if remaining_balance <= volume:
                    # Can sell remaining balance at this price
                    amount = remaining_balance * price
                    acquired_amount += amount
                    remaining_balance = 0
                    break
                else:
                    # Fill entire level and continue
                    amount = volume * price
                    acquired_amount += amount
                    remaining_balance -= volume
            
            if remaining_balance > 0:
                # Not enough liquidity to fill the order
                return 0.0, {}

        # Apply fee to the acquired amount
        balance = acquired_amount * (1 - fee)

        # Store details for notification
        parts = pair_id.split('_')
        contract = [parts[0].upper(), parts[1].upper()] if len(parts) > 1 else [pair_id, ""]
        
        base = contract[0]
        quote = contract[1]

        if action == 'buy':
            input_coin = quote
            output_coin = base
            # Rate = output / input
            # For buy, we divide by price, so rate = 1/avg_price
            rate = acquired_amount / input_balance if input_balance > 0 else 0
            avg_price = 1 / rate if rate > 0 else 0
            rate_desc = f"1 / Avg Ask = {avg_price:.8f}"
            direction_desc = "Quote to Base"
        else:
            input_coin = base
            output_coin = quote
            # For sell, we multiply by price, so rate = avg_price
            rate = acquired_amount / input_balance if input_balance > 0 else 0
            avg_price = rate
            rate_desc = f"Avg Bid = {avg_price:.8f}"
            direction_desc = "Base to Quote"

        details[f'contract_{i+1}'] = contract
        details[f'contract_direction_{i+1}'] = action
        details[f'acquired_coin_t{i+1}'] = balance
        details[f'trade_desc_{i+1}'] = f"{i+1}. Start with {input_coin} of {input_balance}. Swap at rate {rate:.8f} ({rate_desc}) for {output_coin} acquiring {balance} ({input_balance} * {rate:.8f} = {balance}) -- {direction_desc}."

    return balance, details

def main():
    # Default to 50,000 IDR if no argument provided
    initial_amount = float(sys.argv[1]) if len(sys.argv) > 1 else 50000.0

    # Load triangles
    try:
        with open('triangles.json', 'r') as f:
            triangles = json.load(f)
    except FileNotFoundError:
        print("triangles.json not found. Run triarb_builder.py first.")
        return

    print(f"Loaded {len(triangles)} triangles: {triangles}\n\n")
    print(f"Scanning with initial amount: {initial_amount:,.2f} IDR")
    print("Scanning for opportunities (Press Ctrl+C to stop)...")

    try:
        while True:
            tickers = get_ticker_summaries()
            if not tickers:
                time.sleep(5)
                continue

            print(f"\n\n\rScanning... (Last Update: {time.strftime('%H:%M:%S')})\n", end="")

            # For each triangle in order (e.g., group pair of A then B then C).
            for i, t in enumerate(triangles, 1):
                path = f"{t['step1']['from']} > {t['step1']['to']} -> {t['step2']['from']} > {t['step1']['to']} -> {t['step3']['from']} > {t['step3']['to']}"
                print(f"Scanning triangle {i}/{len(triangles)}: {path}")
                final_balance, details = calculate_profit(t, tickers, initial_amount)

                # Calculate profit
                if final_balance > initial_amount:
                    profit_pct = ((final_balance - initial_amount) / initial_amount) * 100
                    profit_amount = final_balance - initial_amount

                    print(f"\n[OPPORTUNITY] Profit: {profit_pct:.2f}% | Gain: {profit_amount:,.2f} IDR")
                    print(f"Path: {t['step1']['from']} -> {t['step2']['from']} -> {t['step3']['from']} -> {t['step3']['to']}")
                    print(f"Start: {initial_amount:,.2f} -> End: {final_balance:,.2f}")
                    print("-" * 30)

                    # Prepare result for slack notification
                    result = details
                    result['starting_amount'] = initial_amount
                    result['final_balance'] = final_balance
                    result['profit_loss'] = profit_amount
                    result['real_rate_percentage'] = profit_pct
                    result['foundAt'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    try:
                        arb_notif("Indodax", result)
                        print("Slack notification sent.")
                    except Exception as e:
                        print(f"Failed to send Slack notification: {e}")

            print("\nScan cycle complete. Waiting 3 seconds...\n")
            time.sleep(3) # Wait 3 seconds before next scan

    except KeyboardInterrupt:
        print("\nScanner stopped.")

if __name__ == "__main__":
    main()
