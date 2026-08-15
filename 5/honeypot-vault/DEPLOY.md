# Standing up the target (browser, no install)

1. Open https://remix.ethereum.org
2. New file -> paste `HoneypotVault.sol` -> Solidity compiler tab -> Compile.
3. "Deploy & Run Transactions" tab -> Environment = **Remix VM**.
4. In the deploy box:
   - set **Value = 9** with unit **Ether**  (this seeds the vault)
   - constructor `_encFlag` =
     `0xe67f4da79a8fd7b3de2e13c6641278bd570b384f7256607f8ef1d8ac2c338de9`
   - click **Deploy**.
5. The vault appears under "Deployed Contracts". `vaultBalance` should read 10^19
   wei (10 ETH) once you've added your own deposit.

Now it's on you: interact with the contract until the vault is empty, then call
`claim()` and read the emitted `FlagRevealed` log.

(Foundry users: `forge install foundry-rs/forge-std`, then work from
`Challenge.starter.t.sol`.)
