import websocket
import json
import threading
import time
import sys

# Constants from Indodax Docs
WS_URL = "wss://ws3.indodax.com/ws/"
STATIC_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE5NDY2MTg0MTV9.UR1lBM6Eqh0yWz-PVirw1uPCxe60FdchR8eNVdsskeo"

class IndodaxWS:
    def __init__(self, pair="btcidr"):
        self.pair = pair
        self.ws = None
        self.id_counter = 1

    def get_next_id(self):
        current_id = self.id_counter
        self.id_counter += 1
        return current_id

    def on_message(self, ws, message):
        data = json.loads(message)
        
        # Handle Auth Response
        if 'result' in data and 'client' in data['result']:
            print("Authenticated successfully.")
            self.subscribe()
            return

        # Handle Order Book Data
        if 'result' in data and 'data' in data['result']:
            channel = data['result'].get('channel')
            if channel == f"market:order-book-{self.pair}":
                order_data = data['result']['data']['data']
                
                # Structure: {'ask': [{'price': '...', ...}, ...], 'bid': [{'price': '...', ...}, ...]}
                
                bids = order_data.get('bid', [])
                asks = order_data.get('ask', [])
                
                # Bids are sorted high to low (best bid is first)
                # Asks are sorted low to high (best ask is first)
                
                best_bid = bids[0]['price'] if bids else "N/A"
                best_ask = asks[0]['price'] if asks else "N/A"
                
                print(f"Best Bid (Sell to): {best_bid} | Best Ask (Buy from): {best_ask}")

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection closed")

    def on_open(self, ws):
        print("Connected to Indodax WebSocket")
        self.authenticate()

    def authenticate(self):
        print("Authenticating...")
        auth_msg = {
            "params": {
                "token": STATIC_TOKEN
            },
            "id": self.get_next_id()
        }
        self.ws.send(json.dumps(auth_msg))

    def subscribe(self):
        channel = f"market:order-book-{self.pair}"
        print(f"Subscribing to {channel}...")
        sub_msg = {
            "method": 1,
            "params": {
                "channel": channel
            },
            "id": self.get_next_id()
        }
        self.ws.send(json.dumps(sub_msg))

    def run(self):
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(WS_URL,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever()

if __name__ == "__main__":
    pair = sys.argv[1] if len(sys.argv) > 1 else "btcidr"
    # Ensure pair is lowercase and has no underscore if user typed 'btc_idr'
    pair = pair.lower().replace("_", "")
    
    client = IndodaxWS(pair)
    try:
        client.run()
    except KeyboardInterrupt:
        print("\nExiting...")
