// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IVault {
    function deposit() external payable;
    function withdraw() external;
    function claim() external returns (string memory);
    function balances(address) external view returns (uint256);
    function chaos() external view returns (uint256);
    function vaultBalance() external view returns (uint256);
}
