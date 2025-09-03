// https://docs.ethers.org
// npm install ethers

/*
The key difference is that it is easier for us to work with big numbers in ethers.js than in web3.js.
*/

const { ethers } = require("ethers");
console.log("\n\nEthers version: ", ethers.version);

// Infura Endpoint (ETHEREUM MAINNET)
url = "https://mainnet.infura.io/v3/5ab76f78c3f34a36b1c7e23bede5d927";
const provider = new ethers.providers.JsonRpcProvider(url);

async function funcEthers(url) {
  // https://docs.ethers.org/v6/api/providers/#Provider
  await provider.getBlockNumber().then(function (result) {
    console.log("\n\nBlock Number: ", result);
  });

  await provider.getNetwork().then(function (result) {
    console.log("Network: ", result.name);
  });
}

funcEthers(url);
/*
Output:
Ethers version:  6.9.2


Block Number:  18992742
Network:  mainnet
*/

// Working with ABI and Contract
const ethAddress = "0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72";

// https://docs.ethers.org/v6/getting-started/#starting-contracts
// For list of functions, go to etherscan.io, click on contract tab, click on Read Contract. Make sure the data type of the return value

const abi = [
  "function decimals() view returns (uint)",
  "function symbol() view returns (string)",
  "function balanceOf(address addr) view returns (uint)",
  "function totalSupply() view returns (uint)",
];

// Create a contract
const ethContract = new ethers.Contract(ethAddress, abi, provider);

// Arrow function convert hex to decimal
const hexToDecimal = (hex) => parseInt(hex, 16);

async function getDetails(ethAddress) {
  const tokenSymbol = await ethContract.symbol();
  const tokenDecimals = await ethContract.decimals();
  const tokenBalance = await ethContract.balanceOf(ethAddress);
  const tokenSupply = await ethContract.totalSupply();

  console.log("\n\nSymbol:", tokenSymbol);
  console.log("Decimals:", hexToDecimal(tokenDecimals._hex));
  console.log("Total Supply:", hexToDecimal(tokenSupply._hex));
  console.log("Balance:", hexToDecimal(tokenBalance._hex));
}

getDetails(ethAddress);
/*
Output:

Symbol: ENS
Decimals: 18n
Total Supply: 100000000000000000000000000n
Balance: 140824540770981319168


With toString:

Symbol: ENS
Decimals: 18
Total Supply: 100000000000000000000000000
Balance: 140824540770981319168
*/
