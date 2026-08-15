// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title HoneypotVault
 * @notice A vault that pays out on request. Deposit, withdraw, done.
 *         The flag is not stored in the clear anywhere. `claim()` only reveals
 *         it once the vault has been emptied to the last wei, and the key it
 *         uses is a value that only exists after the vault is drained.
 * @dev    Read the source. There is a well-known mistake in withdraw().
 *         Works fully offline in Remix VM or `forge test`.
 */
contract HoneypotVault {
    mapping(address => uint256) public balances;

    // Full-width evolving key. Advances once per completed withdrawal.
    uint256 public chaos =
        0x9e3779b97f4a7c15f39cc0605cedc8341082276bf3a27251f86c6a11d0c18e95;

    // flagBytes XOR bytes32(chaos_after_full_drain). Fully masked - no plaintext.
    bytes32 private immutable encFlag;

    // Emitting the flag as an event makes it render cleanly in every tool
    // (Remix transaction logs, `forge test -vvv`, etc).
    event FlagRevealed(string flag);

    constructor(bytes32 _encFlag) payable {
        encFlag = _encFlag;
    }

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() external {
        uint256 bal = balances[msg.sender];
        require(bal > 0, "no balance");

        // ---- interaction BEFORE effects: this is the bug ----
        (bool ok, ) = msg.sender.call{value: bal}("");
        require(ok, "transfer failed");

        balances[msg.sender] = 0;          // effect happens too late

        unchecked {                        // deliberate wrap-around, mod 2**256
            chaos = chaos * 1000003 + 7;
        }
    }

    /// @notice Reveals the flag, but only when the vault is bone dry.
    ///         Emits FlagRevealed(flag) AND returns it.
    function claim() external returns (string memory) {
        require(address(this).balance == 0, "vault not empty yet");
        bytes32 flagBytes = encFlag ^ bytes32(chaos);
        string memory flag = string(_trim(flagBytes));
        emit FlagRevealed(flag);
        return flag;
    }

    function vaultBalance() external view returns (uint256) {
        return address(this).balance;
    }

    function _trim(bytes32 data) private pure returns (bytes memory) {
        uint256 len = 0;
        for (uint256 i = 0; i < 32; i++) {
            if (data[i] != 0) len = i + 1;
        }
        bytes memory out = new bytes(len);
        for (uint256 i = 0; i < len; i++) {
            out[i] = data[i];
        }
        return out;
    }
}
