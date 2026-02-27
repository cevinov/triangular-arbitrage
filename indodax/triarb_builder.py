import requests
import json
from collections import defaultdict

def get_pairs():
    """Fetches all pairs from Indodax."""
    try:
        response = requests.get("https://indodax.com/api/pairs")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching pairs: {e}")
        return []

def build_graph(pairs):
    """
    Builds a graph where nodes are currencies and edges are trading pairs.
    Returns a dictionary: graph[currency] = [(neighbor_currency, pair_id, type)]
    Type is 'buy' (if pair is neighbor_currency/currency) or 'sell' (if pair is currency/neighbor_currency)
    """
    graph = defaultdict(list)
    
    for pair in pairs:
        base = pair['base_currency']   # e.g., 'idr' in 'btc_idr'
        traded = pair['traded_currency'] # e.g., 'btc' in 'btc_idr'
        pair_id = pair['ticker_id']
        
        # If I have 'idr' (base), I can BUY 'btc' (traded).
        # Edge: idr -> btc (Action: BUY)
        graph[base].append((traded, pair_id, 'buy'))
        
        # If I have 'btc' (traded), I can SELL it for 'idr' (base).
        # Edge: btc -> idr (Action: SELL)
        graph[traded].append((base, pair_id, 'sell'))
        
    return graph

def find_triangles(graph, start_currency='idr'):
    """
    Finds all triangular paths starting and ending at start_currency.
    Path: Start -> A -> B -> Start
    """
    triangles = []
    
    # Step 1: Start -> A
    for node_a, pair1, action1 in graph[start_currency]:
        
        # Step 2: A -> B
        for node_b, pair2, action2 in graph[node_a]:
            if node_b == start_currency: continue # Don't go back immediately
            
            # Step 3: B -> Start
            for node_c, pair3, action3 in graph[node_b]:
                if node_c == start_currency:
                    # Found a triangle!
                    triangles.append({
                        'step1': {'from': start_currency, 'to': node_a, 'pair': pair1, 'action': action1},
                        'step2': {'from': node_a, 'to': node_b, 'pair': pair2, 'action': action2},
                        'step3': {'from': node_b, 'to': start_currency, 'pair': pair3, 'action': action3}
                    })
                    
    return triangles

def main():
    print("Fetching pairs...")
    pairs = get_pairs()
    print(f"Found {len(pairs)} pairs.")
    
    print("Building market graph...")
    graph = build_graph(pairs)
    
    print("Finding triangles starting with IDR...")
    triangles = find_triangles(graph, 'idr')
    
    print(f"Found {len(triangles)} triangular paths.")
    
    # Save to file for the scanner to use
    with open('triangles.json', 'w') as f:
        json.dump(triangles, f, indent=2)
    print("Saved triangles to triangles.json")
    
    # Print first 5 examples
    print("\nExample Paths:")
    for t in triangles[:5]:
        s1 = t['step1']
        s2 = t['step2']
        s3 = t['step3']
        print(f"{s1['from']} -> {s1['to']} ({s1['pair']}) -> {s2['to']} ({s2['pair']}) -> {s3['to']} ({s3['pair']})")

if __name__ == "__main__":
    main()
