import asyncio
from binance import AsyncClient, BinanceSocketManager

# https://python-binance.readthedocs.io/en/latest/websockets.html#id2


async def main():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)

    # start with partial book depth and then get the updates
    # partial book response
    pbd = bm.depth_socket("BNBBTC", depth=BinanceSocketManager.WEBSOCKET_DEPTH_5)

    # then start receiving messages
    async with pbd as pbdcm:
        while True:
            res = await pbdcm.recv()
            print(res)

    await client.close_connection()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
