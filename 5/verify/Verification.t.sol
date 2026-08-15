// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../honeypot-vault/HoneypotVault.sol";
import "./Exploit.sol";

interface Vm {
    function deal(address who, uint256 newBalance) external;
}

contract VerificationTest {
    Vm private constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));
    bytes32 private constant ENC_FLAG = 0xe67f4da79a8fd7b3de2e13c6641278bd570b384f7256607f8ef1d8ac2c338de9;

    function testDrainAndClaim() public {
        HoneypotVault vault = new HoneypotVault(ENC_FLAG);
        vm.deal(address(vault), 9 ether);
        vm.deal(address(this), 1 ether);

        VaultDrainer drainer = new VaultDrainer(address(vault));
        string memory flag = drainer.attackAndClaim{value: 1 ether}();

        require(vault.vaultBalance() == 0, "vault not empty");
        require(
            keccak256(bytes(flag)) == keccak256(bytes("CTF{h0n3yp0t_dr41n3d_r33ntry}")),
            "wrong flag"
        );
    }
}
