// Library for interacting with smart contracts on the blockchain (etherscan.io)
// https://docs.ethers.org/
const { ethers } = require("ethers");

// Import function to send notification to Slack
const send = require("./func_notif_slack");

// Import fs module to read file
const fs = require("fs");

// Access to the contract's ABI through the @uniswap/v3-periphery package
// https://docs.uniswap.org/sdk/v3/guides/swaps/quoting
const quoterABI =
  require("@uniswap/v3-periphery/artifacts/contracts/lens/Quoter.sol/Quoter.json").abi; // Get abi object
// console.log(quoterABI);

const fPath = "../uniswapV2/profit_surf_rate_uniswap.json";

function readFile(fPath) {
  const fs = require("fs");

  // Create error handler
  try {
    // Import a JSON file for profitable surface rate transactions.
    const data = fs.readFileSync(fPath, "utf8");
    console.log("\nSuccessfully read file.");
    return data;
  } catch {
    console.log("\nError file not found !!!");
  } finally {
    console.log("END\n\n");
  }
}
/*


*/
// Function to get the price from factory address
async function getPrice(
  factoryAddress,
  baseAddress,
  quoteAddress,
  amountIn,
  direction
) {
  const url = "https://mainnet.infura.io/v3/ab2b7216dfdf40d3812451d0403d1157";
  const provider = new ethers.providers.JsonRpcProvider(url);
  const listTokenAddress = [baseAddress, quoteAddress];

  // ABI for the factory/pool address
  // NOTE: The V2 pair contract does not have a `fee()` function.
  const poolABI = [
    "function token0() view returns (address)",
    "function token1() view returns (address)",
  ];

  // The fee for a standard Uniswap V3 pool to check against.
  // Common values are 500 (0.05%), 3000 (0.3%), 10000 (1%).
  // We will assume 3000 as a default for V2-like pairs.
  const tokenFee = 3000;

  // Create a contract for the pool address
  let token0ID = "";
  let token1ID = "";
  try {
    const poolContract = new ethers.Contract(
      factoryAddress,
      poolABI,
      provider
    );
    token0ID = (await poolContract.token0()).toLowerCase();
    token1ID = (await poolContract.token1()).toLowerCase();
  } catch (e) {
    console.log("Error fetching from pool contract:", e.message);
    return 0;
  }

  // Verify if the token IDs from the factory match the provided addresses, regardless of order.
  const tokenAddresses = [baseAddress.toLowerCase(), quoteAddress.toLowerCase()];
  if (
    tokenAddresses.includes(token0ID) &&
    tokenAddresses.includes(token1ID)
  ) {
    console.log("VALID ADDRESS PAIR", baseAddress, quoteAddress);

    // ABI for coin token
    const abiToken = [
      "function decimals() view returns (uint8)",
      "function name() view returns (string)",
      "function symbol() view returns (string)",
    ];

    // Create a contract for the token address
    async function getTokenContract(tokenAddress) {
      const tokenContract = new ethers.Contract(
        tokenAddress,
        abiToken,
        provider
      );
      const decimals = await tokenContract.decimals();
      const name = await tokenContract.name();
      const symbol = await tokenContract.symbol();
      return {
        address: tokenAddress,
        name: name,
        symbol: symbol,
        decimals: decimals,
      };
    }

    // Get token details
    let listTokenDetails = [];
    for (let token of listTokenAddress) {
      listTokenDetails.push(await getTokenContract(token));
    }

    // Identify the direction of the transaction
    let inputA = "";
    let inputDecimalsA = 0;
    let inputB = "";
    let inputDecimalsB = 0;

    if (direction == "base_to_quote") {
      inputA = listTokenDetails[0].address;
      inputDecimalsA = listTokenDetails[0].decimals;
      inputB = listTokenDetails[1].address;
      inputDecimalsB = listTokenDetails[1].decimals;
      console.log(
        `Forward: ${listTokenDetails[0].symbol} to ${listTokenDetails[1].symbol}`
      );
    } else if (direction == "quote_to_base") {
      inputA = listTokenDetails[1].address;
      inputDecimalsA = listTokenDetails[1].decimals;
      inputB = listTokenDetails[0].address;
      inputDecimalsB = listTokenDetails[0].decimals;
      console.log(
        `Reverse: ${listTokenDetails[1].symbol} to ${listTokenDetails[0].symbol}`
      );
    } else {
      console.log("Error: direction not defined");
      return 0; // Exit if direction is invalid
    }

    // Reformatting the amountIn to the correct decimal
    if (typeof amountIn != "string") {
      amountIn = amountIn.toString();
    }

    // Truncate the input amount to the token's decimal precision to avoid underflow errors.
    const parts = amountIn.split('.');
    if (parts.length > 1 && parts[1].length > inputDecimalsA) {
        amountIn = `${parts[0]}.${parts[1].substring(0, inputDecimalsA)}`;
    }

    const amountInParse = ethers.utils.parseUnits(amountIn, inputDecimalsA);

    // Get the price from the Uniswap V3 contract
    const uniswapQuoterAddress = "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6";
    const quoterContract = new ethers.Contract(
      uniswapQuoterAddress,
      quoterABI,
      provider
    );

    let quotedAmountOut = "0";
    try {
      // Use callStatic to simulate the call and catch reverts
      quotedAmountOut = await quoterContract.callStatic.quoteExactInputSingle(
        inputA,
        inputB,
        tokenFee,
        amountInParse,
        0
      );
    } catch (err) {
      console.log("\nError during quoteExactInputSingle call. This pool might not exist or have enough liquidity.");
      console.log("Parameters used:");
      console.log(`  - tokenIn: ${inputA}`);
      console.log(`  - tokenOut: ${inputB}`);
      console.log(`  - fee: ${tokenFee}`);
      console.log(`  - amountIn: ${amountInParse.toString()}`);
      // console.error(err); // Uncomment for full error trace
      return 0;
    }

    // Format the quoted amount
    const outputQuotedAmount = ethers.utils.formatUnits(
      quotedAmountOut,
      inputDecimalsB
    );
    console.log("Quoted Amount Out: ", outputQuotedAmount);

    return Number(outputQuotedAmount);
  } else {
    console.log("INVALID ADDRESS PAIR\n");
    console.log(`Provided: ${baseAddress}, ${quoteAddress}`);
    console.log(`From Factory: ${token0ID}, ${token1ID}`);
    return 0;
  }
}
/*


*/
// Main control function for other functions that relate to depth rate calculation
async function getDepth(loopLimit = 1) {
  // Get current date and time
  const startTime = new Date();

  // Store profitable listTrades into an array
  let listTrades = [];

  file = readFile(fPath);
  // Converting a JSON object in text format to a Javascript object that can be used inside a program
  profitSurfRate = JSON.parse(file);
  // limitList = profitSurfRate.slice(0, loopLimit); // Only get one element for testing purposes

  let i = 0;
  // Loop through each element in the array using forOf which is for iteable objects
  for (let info of profitSurfRate) {
    const startingAmount = info.starting_amount;
    console.log("Starting Amount: ", startingAmount);

    const direction = info.direction;
    const poolContract1 = info.pool_contract_1;
    const poolContract2 = info.pool_contract_2;
    const poolContract3 = info.pool_contract_3;
    const poolDirectionT1 = info.pool_direction_trade_1;
    const poolDirectionT2 = info.pool_direction_trade_2;
    const poolDirectionT3 = info.pool_direction_trade_3;
    const tradeDesc1 = info.trade_desc_1;
    const tradeDesc2 = info.trade_desc_2;
    const tradeDesc3 = info.trade_desc_3;

    // Check if this factory address have the same token pair, check on the Contract tab > Read Contract > token0 (baseId) and token1 (quoteId)
    const aTokenAddress = info.a_address;
    const bTokenAddress = info.b_address;
    const cTokenAddress = info.c_address;

    const aBaseId = info.a_base_id;
    const aQuoteId = info.a_quote_id;
    const bBaseId = info.b_base_id;
    const bQuoteId = info.b_quote_id;
    const cBaseId = info.c_base_id;
    const cQuoteId = info.c_quote_id;
    const combine = info.combine;

    i++;
    console.log(`\n\n${i}.Combine: ${combine}`);

    // Get price for Trade 1
    console.log("\nCalculating Trade 1");
    const acquiredCoinDetailT1 = await getPrice(
      aTokenAddress,
      aBaseId,
      aQuoteId,
      startingAmount,
      poolDirectionT1
    );

    // Get price for Trade 2
    console.log("\nCalculating Trade 2");
    const acquiredCoinDetailT2 = await getPrice(
      bTokenAddress,
      bBaseId,
      bQuoteId,
      acquiredCoinDetailT1,
      poolDirectionT2
    );

    // Get price for Trade 3
    console.log("\nCalculating Trade 3");
    const acquiredCoinDetailT3 = await getPrice(
      cTokenAddress,
      cBaseId,
      cQuoteId,
      acquiredCoinDetailT2,
      poolDirectionT3
    );

    if (acquiredCoinDetailT3) {
      // Calculate the profit
      const profit = acquiredCoinDetailT3 - startingAmount;
      const profit_percentage = profit / startingAmount;

      // Take profit if the profit is more than 1%
      if (profit_percentage > 0.01) {
        console.log("Profitable Trade");
        const foundAt = new Date();
        listTrades.push({
          startingAmount: startingAmount,
          profit: profit,
          profit_percentage: profit_percentage,
          foundAt: foundAt,
          direction: direction,
          poolContract1: poolContract1,
          poolDirectionT1: poolDirectionT1,
          acquiredCoinDetailT1: acquiredCoinDetailT1,
          poolContract2: poolContract2,
          poolDirectionT2: poolDirectionT2,
          acquiredCoinDetailT2: acquiredCoinDetailT2,
          poolContract3: poolContract3,
          poolDirectionT3: poolDirectionT3,
          acquiredCoinDetailT3: acquiredCoinDetailT3,
          tradeDesc1: tradeDesc1,
          tradeDesc2: tradeDesc2,
          tradeDesc3: tradeDesc3,
          combine: combine,

          // Check if this factory address have the same token pair, check on the Contract tab > Read Contract > token0 (baseId) and token1 (quoteId)
          // aTokenAddress: aTokenAddress,
          // bTokenAddress: bTokenAddress,
          // cTokenAddress: cTokenAddress,

          // Token details
          // aBaseId: aBaseId,
          // aQuoteId: aQuoteId,
          // bBaseId: bBaseId,
          // bQuoteId: bQuoteId,
          // cBaseId: cBaseId,
          // cQuoteId: cQuoteId,
        });

        // Send notification to Slack
        send.sendNotif(
          "Uniswap V2",
          `\n
      startingAmount: ${listTrades[listTrades.length - 1].startingAmount}
      foundAt: ${listTrades[listTrades.length - 1].foundAt}
      direction: ${listTrades[listTrades.length - 1].direction}
      poolContract1: ${listTrades[listTrades.length - 1].poolContract1}
      poolDirectionT1: ${listTrades[listTrades.length - 1].poolDirectionT1}
      acquiredCoinDetailT1: ${
        listTrades[listTrades.length - 1].acquiredCoinDetailT1
      }
      poolContract2: ${listTrades[listTrades.length - 1].poolContract2}
      poolDirectionT2: ${listTrades[listTrades.length - 1].poolDirectionT2}
      acquiredCoinDetailT2: ${
        listTrades[listTrades.length - 1].acquiredCoinDetailT2
      }
      poolContract3: ${listTrades[listTrades.length - 1].poolContract3}
      poolDirectionT3: ${listTrades[listTrades.length - 1].poolDirectionT3}
      acquiredCoinDetailT3: ${
        listTrades[listTrades.length - 1].acquiredCoinDetailT3
      }
      tradeDesc1: ${listTrades[listTrades.length - 1].tradeDesc1}
      tradeDesc2: ${listTrades[listTrades.length - 1].tradeDesc2}
      tradeDesc3: ${listTrades[listTrades.length - 1].tradeDesc3}
      combine: ${listTrades[listTrades.length - 1].combine}
      `
        );

        // Store the list of profitable trade to a JSON file
        fs.writeFile(
          "profitableTrades.json",
          JSON.stringify(listTrades), // Use JSON.stringify() method to convert the object into a JSON string
          (err) => {
            if (err) console.log("Error: ", err);
          }
        );

        console.log("Saved !!!");
      } else {
        console.log("Not Profitable", profit, profit_percentage);
      }
    } else {
      console.log("Trading Execution Failed !!!");
    }

    const endTime = new Date();
    const dataLog = `\n\nStart Time: ${startTime}\nEnd Time: ${endTime}\nDifference: ${
      (endTime - startTime) / 3600000
    } hours`;
    fs.appendFile("log_getDepth.txt", dataLog, (err) => {
      if (err) {
        console.log(err);
      } else {
        console.log("File written successfully\n");
      }
    });
  }
}

// res = [
//   {
//     starting_amount: 66426016.23625115,
//     direction: "forward",
//     swap_1: "ELON",
//     swap_2: "USDT",
//     swap_3: "USDC",
//     swap_1_rate: 1.7705251525918558e-7,
//     swap_2_rate: 0.9988551426993928,
//     swap_3_rate: 6484671.100363343,
//     acquired_coin_t1: 11.760893253275766,
//     acquired_coin_t2: 11.747428708773091,
//     acquired_coin_t3: 76178211.45135953,
//     pool_contract_1: "ELON_USDT",
//     pool_contract_2: "USDC_USDT",
//     pool_contract_3: "ELON_USDC",
//     pool_direction_trade_1: "base_to_quote",
//     pool_direction_trade_2: "quote_to_base",
//     pool_direction_trade_3: "quote_to_base",
//     a_address: "0x543842cbfef3b3f5614b2153c28936967218a0e6",
//     b_address: "0xa7b3bcc6c88da2856867d29f11c67c3a85634882",
//     c_address: "0x3416cf6c708da44db2624d63ea0aaef7113527c6",
//     a_base_id: "0x761d38e5ddf6ccf6cf7c55759d5210750b5d60f3",
//     a_quote_id: "0xdac17f958d2ee523a2206206994597c13d831ec7",
//     b_base_id: "0x761d38e5ddf6ccf6cf7c55759d5210750b5d60f3",
//     b_quote_id: "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
//     c_base_id: "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
//     c_quote_id: "0xdac17f958d2ee523a2206206994597c13d831ec7",
//     trade_desc_1:
//       "1. Start with ELON of 66426016.23625115. Swap at rate 1.7705251525918558e-07 for USDT acquiring 11.760893253275766.",
//     trade_desc_2:
//       "2. Swap 11.760893253275766 of USDT at rate 0.9988551426993928 for USDC acquiring 11.747428708773091.",
//     trade_desc_3:
//       "3. Swap 11.747428708773091 of USDC at rate 6484671.100363343 for ELON acquiring 76178211.45135953.",
//     profit_surface: 9752195.215108372,
//     profit_percentage: 0.14681288699330783,
//     combine: ["ELONUSDT", "ELONUSDC", "USDCUSDT"],
//   },
// ];

// getDepth(res);

const timeoutMs = 300000; // Delay 5 minutes
// Set interval to run the function every 1 minute
// setInterval(() => {
//   getDepth();
// }, timeoutMs);

getDepth();

/*
Output:

data = {
  starting_amount: 10.006003602161297,
  direction: "forward",
  swap_1: "USDC",
  swap_2: "WETH",
  swap_3: "UST",
  swap_1_rate: 0.00044469956980515164,
  swap_2_rate: 51098.60364869714,
  swap_3_rate: 9.973038590823956,
  acquired_coin_t1: 0.004449665497349926,
  acquired_coin_t2: 227.37169361836672,
  acquired_coin_t3: 2267.5866749169722,
  pool_contract_1: "USDC_WETH",
  pool_contract_2: "UST_WETH",
  pool_contract_3: "USDC_UST",
  pool_direction_trade_1: "base_to_quote",
  pool_direction_trade_2: "quote_to_base",
  pool_direction_trade_3: "quote_to_base",
  a_address: "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
  b_address: "0x9d96880952b4c80a55099b9c258250f2cc5813ec",
  c_address: "0x7a5ae802895d5f90b6edbafc870fd348fba2a3d2",
  a_base_id: "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  a_quote_id: "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
  b_base_id: "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  b_quote_id: "0xa693b19d2931d498c5b318df961919bb4aee87a5",
  c_base_id: "0xa693b19d2931d498c5b318df961919bb4aee87a5",
  c_quote_id: "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
  trade_desc_1:
    "1. Start with USDC of 10.006003602161297. Swap at rate 0.00044469956980515164 for WETH acquiring 0.004449665497349926.",
  trade_desc_2:
    "2. Swap 0.004449665497349926 of WETH at rate 51098.60364869714 for UST acquiring 227.37169361836672.",
  trade_desc_3:
    "3. Swap 227.37169361836672 of UST at rate 9.973038590823956 for USDC acquiring 2267.5866749169722.",
  profit_surface: 2257.580671314811,
  profit_percentage: 22562.26122912022,
  combine: ["USDCWETH", "USDCUST", "USTWETH"],
};

send.sendNotif("Uniswap", data);
*/
