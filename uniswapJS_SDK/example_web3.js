/* 
Documentation web3 JS: 
https://docs.web3js.org/libdocs/Web3Eth
https://web3js.readthedocs.io/en/
*/

const Web3 = require("web3");

//private RPC endpoint
const web3 = new Web3(
  "https://mainnet.infura.io/v3/5ab76f78c3f34a36b1c7e23bede5d927"
);

//or public RPC endpoint
//const web3 = new Web3('https://eth.llamarpc.com');

web3.eth.getBlockNumber().then(function (result) {
  console.log("blockNumber :", result);
});
// 18982920n

console.log(`Version: ${Web3.version}`);
// console.log("\n\nList Connection: ", web3);

/*
Output:

Version: 4.3.0
Contract Input 1: { internalType: 'uint256', name: 'freeSupply', type: 'uint256' }
blockNumber : 18992746n
*/

// Create new object for contract
const ethAddress = "0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72"; // This is an address for the Ethereum Name Service; get this from etherscan.io

// This ABI (Application Binary Interface) from address above in the contract tab
const abi = require("./example_abi.json");
const testContract = new web3.eth.Contract(abi, ethAddress);
console.log("Contract Input 1:", abi[0].inputs[0]);

// Read contract to get token symbol
// To get function name, go to etherscan.io, click on contract tab, click on Read Contract
// Example: https://etherscan.io/address/0xc18360217d8f7ab5e7c516566761ea12ce7f9d72#readContract
async function getTokenDetails() {
  await testContract.methods
    .symbol()
    .call()
    .then(function (result) {
      console.log("\n\nToken Name:", result);
    });

  await testContract.methods
    .totalSupply()
    .call()
    .then(function (result) {
      console.log("Total Supply:", result);
    });

  await testContract.methods
    .decimals()
    .call()
    .then(function (result) {
      console.log("Decimals:", result);
    });
}
getTokenDetails();
/*
Output:

Token Name: ENS
Total Supply: 100000000000000000000000000n
Decimals: 18n
*/
