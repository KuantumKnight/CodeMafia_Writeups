# The Honeypot Vault

A vault contract lets people deposit and withdraw ETH. Something about the way it
pays out is... generous. The flag is never stored in plaintext — the contract's
`claim()` function will only reveal it once the vault holds exactly **0 wei**.

Empty the pot, then claim your prize.

Files:
- `HoneypotVault.sol` — the target contract
- `IVault.sol` — its interface
- `Challenge.starter.t.sol` — a Foundry setup file (optional, for forge users)
- `DEPLOY.md` — how to stand the contract up in your browser (no install)

Flag format: `CTF{...}`
