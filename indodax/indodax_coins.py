import requests

def get_pairs():
    """
    Fetches the list of supported pairs from Indodax.
    """
    url = "https://indodax.com/api/pairs"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def main():
    print("Fetching supported pairs from Indodax...")
    pairs = get_pairs()
    
    if pairs:
        print(f"Found {len(pairs)} pairs:")
        print(f"{'Ticker ID':<15} | {'Description':<20} | {'Base Currency':<10} | {'Traded Currency':<10}")
        print("-" * 65)
        for pair in pairs:
            ticker_id = pair.get('ticker_id', 'N/A')
            description = pair.get('description', 'N/A')
            base = pair.get('base_currency', 'N/A')
            traded = pair.get('traded_currency', 'N/A')
            print(f"{ticker_id:<15} | {description:<20} | {base:<10} | {traded:<10}")
    else:
        print("No pairs found.")

if __name__ == "__main__":
    main()
