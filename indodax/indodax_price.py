import requests
import sys

def get_ticker(pair):
    """
    Fetches the ticker data for a given trading pair from Indodax.
    
    Args:
        pair (str): The trading pair, e.g., 'btc_idr'.
        
    Returns:
        dict: The ticker data if successful, None otherwise.
    """
    import time
    # Add a timestamp to prevent caching
    url = f"https://indodax.com/api/{pair}/ticker?t={int(time.time())}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def main():
    # Default to btc_idr if no argument is provided
    pair = sys.argv[1] if len(sys.argv) > 1 else "btc_idr"
    
    print(f"Fetching price for {pair}...")
    data = get_ticker(pair)
    
    if data and 'ticker' in data:
        ticker = data['ticker']
        print(f"--- {pair.upper()} ---")
        print(f"Last Price: {ticker.get('last')}")
        print(f"High: {ticker.get('high')}")
        print(f"Low: {ticker.get('low')}")
        print(f"Volume: {ticker.get('vol_idr')}")
        
        server_time = ticker.get('server_time')
        if server_time:
            from datetime import datetime
            dt = datetime.fromtimestamp(server_time)
            print(f"Server Time: {dt}")
    else:
        print("Failed to retrieve ticker data.")

if __name__ == "__main__":
    main()
