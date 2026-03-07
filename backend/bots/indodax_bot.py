import threading
import time
import datetime
import json
import sys
import os
import requests

# Creates the full path to the indodax directory
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'indodax'))

try:
    from binance.func_slack_notif import arb_notif
    from triarb_scanner import get_ticker_summaries, calculate_profit, get_depth
except ImportError as e:
    print(f"Error importing Indodax modules: {e}")

class IndodaxBot:
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.initial_amount = 50000.0 # Default IDR
        self.fee = 0.003 # Default to 0.3%
        self.status_message = "Stopped"
        self.session_file = None

    def start(self):
        if self.is_running:
            return "Bot is already running"
        
        self.is_running = True
        self.status_message = "Running"
        
        # Generate a unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = f"indodax_opportunities_{timestamp}.json"
        
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        return f"Bot started. Saving results to {self.session_file}"

    def stop(self):
        self.is_running = False
        self.status_message = "Stopping..."
        if self.thread:
            self.thread.join()
        self.status_message = "Stopped"
        return "Bot stopped"

    def get_status(self):
        return {
            "running": self.is_running,
            "message": self.status_message,
            "initial_amount": self.initial_amount,
            "fee": self.fee
        }

    def _loop(self):
        print("Indodax Bot Loop Started")
        
        triangles_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../indodax/triangles.json'))
        
        try:
            with open(triangles_path, 'r') as f:
                triangles = json.load(f)
        except FileNotFoundError:
            print(f"triangles.json not found at {triangles_path}")
            self.is_running = False
            self.status_message = "Error: triangles.json not found"
            return

        print(f"Loaded {len(triangles)} triangles")
        
        while self.is_running:
            try:
                tickers = get_ticker_summaries()
                if not tickers:
                    time.sleep(5)
                    continue

                current_fee = self.fee if self.fee is not None else 0.0
                print(f"Scanning Indodax... (Fee: {current_fee*100:.2f}%) (Last Update: {time.strftime('%H:%M:%S')})")

                for i, t in enumerate(triangles, 1):
                    if not self.is_running:
                        break
                        
                    final_balance, details = calculate_profit(t, tickers, self.initial_amount, self.fee)

                    if final_balance > self.initial_amount:
                        profit_pct = ((final_balance - self.initial_amount) / self.initial_amount) * 100
                        profit_amount = final_balance - self.initial_amount

                        print(f"OPPORTUNITY: Profit: {profit_pct:.2f}% | Gain: {profit_amount:,.2f} IDR")

                        result = details
                        result['starting_amount'] = self.initial_amount
                        result['final_balance'] = final_balance
                        result['profit_loss'] = profit_amount
                        result['real_rate_percentage'] = profit_pct
                        
                        # Store hypothesis metrics
                        result['gross_depth_profit'] = details['gross_depth_balance'] - self.initial_amount
                        result['ideal_surface_profit'] = details['ideal_surface_balance'] - self.initial_amount
                        result['net_surface_profit'] = details['net_surface_balance'] - self.initial_amount
                        result['gross_depth_balance'] = details['gross_depth_balance']
                        result['ideal_surface_balance'] = details['ideal_surface_balance']
                        result['net_surface_balance'] = details['net_surface_balance']

                        result['fee'] = self.fee
                        result['foundAt'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        try:
                            arb_notif("Indodax", result)
                        except Exception as e:
                            print(f"Failed to send Slack notification: {e}")

                        # Save opportunity to JSON file
                        try:
                            results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../results'))
                            if not os.path.exists(results_dir):
                                os.makedirs(results_dir)
                            
                            results_file = os.path.join(results_dir, self.session_file)
                            
                            existing_data = []
                            if os.path.exists(results_file):
                                try:
                                    with open(results_file, 'r') as f:
                                        existing_data = json.load(f)
                                except json.JSONDecodeError:
                                    pass # File might be empty or corrupted
                            
                            existing_data.append(result)
                            
                            with open(results_file, 'w') as f:
                                json.dump(existing_data, f, indent=4)
                                
                            print(f"Saved opportunity to {results_file}")
                        except Exception as e:
                            print(f"Failed to save opportunity to JSON: {e}")

                # Stop after one pass as requested (uncomment 3 lines in the below for single loop)
                # print("Completed one pass of all triangles. Stopping bot.")
                # self.is_running = False
                # break
                
                time.sleep(3) # Set delay to 3 seconds if run the bot infinitely
                
            except Exception as e:
                print(f"Error in Indodax Bot Loop: {e}")
                time.sleep(5)
        
        print("Indodax Bot Loop Stopped")

bot = IndodaxBot()
