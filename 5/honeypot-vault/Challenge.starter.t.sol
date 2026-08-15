// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/HoneypotVault.sol";

/*
 *  PLAYER STARTER FILE
 *  Setup deploys a HoneypotVault seeded to 10 ether total.
 *  Your job: drain it to zero, then read the flag from claim().
 *  Run:  forge test -vvv --match-path test/Challenge.starter.t.sol
 *  Do NOT change the seeding amounts.
 */
contract ChallengeStarter is Test {
    HoneypotVault vault;
    bytes32 constant ENC_FLAG = 0xe67f4da79a8fd7b3de2e13c6641278bd570b384f7256607f8ef1d8ac2c338de9;

    function setUp() public {
        vault = new HoneypotVault(ENC_FLAG);
        vm.deal(address(vault), 9 ether);   // + your 1 ether deposit == 10 ether pot
    }

    function test_solve() public {
        // TODO: build & run your attacker, then: emit log_string(vault.claim());
        assertTrue(false, "implement your attack");
    }
}
