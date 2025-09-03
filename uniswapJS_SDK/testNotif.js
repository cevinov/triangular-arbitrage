const { sendNotif } = require("./func_notif_slack");

// Open JSON file
const fs = require("fs");
const data = fs.readFileSync("./profitableTrades.json");
const trades = JSON.parse(data);
console.log(trades[trades.length - 1]);

sendNotif(
  "Uniswap V2",
  `\nstartingAmount: ${trades[trades.length - 1].startingAmount}
foundAt: ${trades[trades.length - 1].foundAt}
direction: ${trades[trades.length - 1].direction}
poolContract1: ${trades[trades.length - 1].poolContract1}
poolDirectionT1: ${trades[trades.length - 1].poolDirectionT1}
acquiredCoinDetailT1: ${trades[trades.length - 1].acquiredCoinDetailT1}
poolContract2: ${trades[trades.length - 1].poolContract2}
poolDirectionT2: ${trades[trades.length - 1].poolDirectionT2}
acquiredCoinDetailT2: ${trades[trades.length - 1].acquiredCoinDetailT2}
poolContract3: ${trades[trades.length - 1].poolContract3}
poolDirectionT3: ${trades[trades.length - 1].poolDirectionT3}
acquiredCoinDetailT3: ${trades[trades.length - 1].acquiredCoinDetailT3}
tradeDesc1: ${trades[trades.length - 1].tradeDesc1}
tradeDesc2: ${trades[trades.length - 1].tradeDesc2}
tradeDesc3: ${trades[trades.length - 1].tradeDesc3}
combine: ${trades[trades.length - 1].combine}
`
);
