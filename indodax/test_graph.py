import requests
from triarb_builder import build_graph, find_triangles

pairs = requests.get("https://indodax.com/api/pairs").json()
graph = build_graph(pairs)

# Let's inspect edges for 'usdt' and 'btc'
print(f"Edges from 'btc': {len(graph['btc'])}")
print(f"Edges from 'usdt': {len(graph['usdt'])}")

triangles = find_triangles(graph, 'idr')
print(f"\nFound {len(triangles)} triangles")
