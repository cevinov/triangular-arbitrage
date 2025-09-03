// Modul for sending notification to Slack
// https://slack.dev/node-slack-sdk/webhook
// Version: @slack/webhook@7.0.2

function sendNotif(exchange, messages) {
  const { IncomingWebhook } = require("@slack/webhook");
  const url =
    "https://hooks.slack.com/services/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";

  const webhook = new IncomingWebhook(url);
  const data = `ARBITRAGE OPPORTUNITY FOUND for ${exchange}\n ${messages}`;

  // Send the notification
  (async () => {
    await webhook.send({
      text: data,
    });
  })();
}

// Export the function
exports.sendNotif = sendNotif;

// data = {
//   startingAmount: 10,
//   acquiredCoinDetailT1: 23780.233916,
//   acquiredCoinDetailT2: 0.22766509916667577,
//   acquiredCoinDetailT3: 14.94437747,
//   profit: 4.944377469999999,
//   profit_percentage: 0.4944377469999999,
//   foundAt: "2024-01-22T13:05:34.321Z",
//   combine: ["USDCWETH", "WETHGALA", "GALAUSDC"],
//   direction: "reverse",
//   poolContract1: "USDC_WETH",
//   poolDirectionT1: "quote_to_base",
//   poolContract2: "GALA_USDC",
//   poolDirectionT2: "quote_to_base",
//   poolContract3: "WETH_GALA",
//   poolDirectionT3: "quote_to_base",
//   swap1: "WETH",
//   swap2: "USDC",
//   swap3: "GALA",
//   aTokenAddress: "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
//   bTokenAddress: "0x465e56cd21ad47d4d4790f17de5e0458f20c3719",
//   cTokenAddress: "0xd73ea444eef6faf5423b49be3448e94ed214f1ec",
//   aBaseId: "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
//   aQuoteId: "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
//   bBaseId: "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
//   bQuoteId: "0xd1d2eb1b1e90b638588728b4130137d262c87cae",
//   cBaseId: "0x15d4c048f83bd7e37d49ea4c83a07267ec4203da",
//   cQuoteId: "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
// };

// sendNotif("Uniswap", data);
