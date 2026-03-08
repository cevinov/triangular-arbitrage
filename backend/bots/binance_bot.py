import threading
import time
import datetime
import json
import sys
import os

# Add binance directory to path to import existing modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../binance')))

try:
    import surface_rate_bookTicker as surf_rate
    import calc_depth_rate as depth
    import func_slack_notif as slack
except ImportError as e:
    print(f"Error importing Binance modules: {e}")

class BinanceBot:
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.initial_amount = 10000000000 # Default 10M
        self.fee = 0.00001 # Default 0.001%
        self.status_message = "Stopped"
        self.session_file = None

    def start(self):
        if self.is_running:
            return "Bot is already running"
        
        self.is_running = True
        self.status_message = "Running"

        # Generate a unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = f"binance_opportunities_{timestamp}.json"
        self.loss_session_file = f"binance_loss_{timestamp}.json"

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
        print("Binance Bot Loop Started")
        
        # Load structured pairs
        triangular_groups_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../binance/triangular_groups.json'))
        
        while self.is_running:
            try:
                start = datetime.datetime.now()
                print(f"Scanning Binance... {start}")

                with open(triangular_groups_path, "r") as json_file:
                    structured_pairs = json.load(json_file)

                goal_arb = []
                
                for pair in structured_pairs:
                    if not self.is_running:
                        break

                    result_surface = surf_rate.find_arb_opportunity_surf(pair, self.initial_amount)

                    if len(result_surface) > 0:
                        foundAt = datetime.datetime.now()
                        result_depth = depth.get_depth_from_orderbook(result_surface, self.fee)

                        if len(result_depth) > 0:
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
                                "initial_amount": result_surface["initial_amount"],
                                "profit_loss": result_depth["profit_loss"],
                                "real_rate_percentage": result_depth["real_rate_percentage"],
                                "gross_depth_balance": result_depth.get("gross_depth_balance", 0),
                                "ideal_surface_balance": result_depth.get("ideal_surface_balance", 0),
                                "net_surface_balance": result_depth.get("net_surface_balance", 0),
                                "gross_depth_profit": result_depth.get("gross_depth_balance", 0) - result_surface["starting_amount"],
                                "ideal_surface_profit": result_depth.get("ideal_surface_balance", 0) - result_surface["starting_amount"],
                                "net_surface_profit": result_depth.get("net_surface_balance", 0) - result_surface["starting_amount"],
                                "foundAt": foundAt.strftime("%Y-%m-%d %H:%M:%S"),
                                "fee": self.fee
                            }

                            if result_dict['profit_loss'] > 0:
                                print(f"\n[OPPORTUNITY] Profit: {result_depth['real_rate_percentage']:.2f}% | Gain: ${result_depth['profit_loss']:.4f}")
                                print(f"Path: {result_dict['contract_1'][0]} -> {result_dict['contract_2'][0]} -> {result_dict['contract_3'][0]}")
                                print(f"Start: ${result_dict['starting_amount']:.2f} -> End: ${result_dict['starting_amount'] + result_dict['profit_loss']:.2f}")
                                print("-" * 30)
                                print(f"Execution Path:\n{result_dict['trade_desc_1']}\n{result_dict['trade_desc_2']}\n{result_dict['trade_desc_3']}")
                                print("-" * 30)

                                # Send notification to Slack
                                notif = slack.arb_notif("Binance", result_dict)
                                if notif != b"ok":
                                    print("Error sending notification: " + str(notif))

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
                                    
                                    existing_data.append(result_dict)
                                    
                                    with open(results_file, 'w') as f:
                                        json.dump(existing_data, f, indent=4)
                                        
                                    print(f"Saved opportunity to {results_file}")
                                except Exception as e:
                                    print(f"Failed to save opportunity to JSON: {e}")

                                goal_arb.append(result_dict)
                            else:
                                # Save loss to JSON file
                                try:
                                    loss_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../results/loss'))
                                    if not os.path.exists(loss_dir):
                                        os.makedirs(loss_dir)
                                    
                                    loss_file = os.path.join(loss_dir, self.loss_session_file)
                                    
                                    existing_data = []
                                    if os.path.exists(loss_file):
                                        try:
                                            with open(loss_file, 'r') as f:
                                                existing_data = json.load(f)
                                        except json.JSONDecodeError:
                                            pass
                                    
                                    existing_data.append(result_dict)
                                    
                                    with open(loss_file, 'w') as f:
                                        json.dump(existing_data, f, indent=4)
                                        
                                except Exception as e:
                                    print(f"Failed to save loss to JSON: {e}")

                # Sleep to avoid spamming if loop is fast, or just wait for next cycle
                time.sleep(5) 
                
            except Exception as e:
                print(f"Error in Binance Bot Loop: {e}")
                time.sleep(5)
        
        print("Binance Bot Loop Stopped")

bot = BinanceBot()
