import requests
import json
import time
import datetime
import structuring_triangular_pairs as struct_arb
import func_surface_rate as func_surf

# For uniswap we pull the data with graphQL queries from the subgraph api endpoint:
# https://docs.uniswap.org/api/subgraph/overview

# Check swap between two tokens, with parameters: TotalValueLocked (TVL), first to limit the results, and orderBy to sort the results
# Total Value Locked (TVL) is a pivotal metric used to understand liquidity in DeFI protocols.
# https://app.uniswap.org/swap
# https://thegraph.com/hosted-service/subgraph/uniswap/uniswap-v3

"""
Example:
{
  pools(first: 1, orderBy: totalValueLockedETH, orderDirection: desc){
    id
    token0Price
    token1Price
    feeTier
    feesUSD
    liquidity
    totalValueLockedETH
    token0 {
      id
      symbol
      volume
      decimals
      totalSupply
    }
    token1 {
      id
      symbol
      volume
      decimals
      totalSupply
    }
  }

Output:
{
  "data": {
    "pools": [
      {
        "id": "0x277667eb3e34f134adf870be9550e9f323d0dc24",
        "token0Price": "10201983.52821130596040573863212092",
        "token1Price": "0.00000009802015433907763482013950488687576",
        "feeTier": "100",
        "feesUSD": "0",
        "liquidity": "313521001529099829406",
        "totalValueLockedETH": "834419413.0127326409251168468344917",
        "token0": {
          "id": "0x160de4468586b6b2f8a92feb0c260fc6cfc743b1",
          "symbol": "ease.org",
          "volume": "0.000003",
          "decimals": "18",
          "totalSupply": "28368"
        },
        "token1": {
          "id": "0xea5edef1c6ed1be1bcba4617a1c5a994e9018a43",
          "symbol": "ez-cvxsteCRV",
          "volume": "0.000000000000108977",
          "decimals": "18",
          "totalSupply": "18368"
        }
      }
    ]
  }
}
"""


# Retrieve price of token from pools (GraphQL)

# https://docs.uniswap.org/api/subgraph/overview
url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
# Different than rest API, we need to do a post request with the query as a JSON object. After that we retrieve the information.
query = """
{
pools(first: 200, orderBy: totalValueLockedETH, orderDirection: desc)
{
  id
  token0Price
  token1Price
  feeTier
  feesUSD
  liquidity
  totalValueLockedETH
  token0 {id name symbol volume decimals totalSupply}
  token1 {id name symbol volume decimals totalSupply}
}
}
"""

url_v2 = "https://thegraph.com/hosted-service/subgraph/uniswap/uniswap-v2"
# Different than rest API, we need to do a post request with the query as a JSON object. After that we retrieve the information.
# Graph Uniswap V2: https://thegraph.com/hosted-service/subgraph/uniswap/uniswap-v2
query_v2 = """
{
pairs(first: 200, orderBy: reserveETH, orderDirection: desc) {
id
token0Price
token1Price
reserve0
reserve1
reserveETH
token0 {
  id
  name
  symbol
  decimals
  totalSupply
}
token1 {
  id
  name
  symbol
  decimals
  totalSupply
}
}
}"""


if __name__ == "__main__":
    is_run = True
    with open("univ2_listToken.json", "r") as f:
        pairs = json.load(f)["data"]["pairs"]

    """
    print("pairs:", pairs[0])

    Output:    
    {'id': '0xe6c78983b07a07e0523b57e18aa23d3ae2519e05', 'token0Price': '3.000000602598460910663681445296255', 'token1Price': '0.3333332663779622367718928917204297', 'reserve0': '3000000.303498494970661021', 'reserve1': '999999.900300031379681661', 'reserveETH': '3054879.156087123647945100225370331', 'token0': {'id': '0x395c8db957d743a62ac3aaaa4574553bcf2380b3', 'name': 'ulock.eth Wrapped Ether', 'symbol': 'UETH', 'decimals': '18', 'totalSupply': '14448'}, 'token1': {'id': '0x598a754c5d678119e67574ff811da61d83c0e629', 'name': 'uLock', 'symbol': 'ULCK', 'decimals': '18', 'totalSupply': '14448'}}

    Check parent id as contract address in etherscan
    """
    struct_arb.save_triarb_groups(pairs[:100]) # Limiting to first 100 pairs for testing

    while is_run:
        # Give 5 mins delay to avoid spamming the graphQL API of uniswap
        # time.sleep(300)
        start = datetime.datetime.now()

        # Save surface rate calculations that have a profit rate of at least 1%.
        is_run = func_surf.save_surf_rate()

    end = datetime.datetime.now()
    log = f"Start: {start}\nEnd: {end}\nDiff: {end - start}\n\n"
    with open("log_uniswap.txt", "a") as f:
        f.write(log)
