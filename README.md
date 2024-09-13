# Automatically build transactions on diverse Blockchains

Build transactions on diverse Blockchains with Python & Rust
Manipulate MEV with Python & Rust
Key Features:

1. Multi-chain support: EVM-compatible chains and Tendermint-based chains
2. Modular design: Separate builders for different blockchain types
3. Extensibility: Easy to add support for new chains or transaction types
4. DeFi operations: Token swapping with multiple aggregator support
5. Staking operations: Particularly detailed for Polygon staking

Areas for Potential Expansion:

1. Implement more Tendermint-based chain operations in Rust
2. Expand Injective Protocol support beyond send transactions
3. Add support for more DeFi operations across different chains
4. Implement error handling and recovery mechanisms
5. Add more comprehensive testing and documentation

Requirements:

- Python 3.10+
- Rust 1.81+

## 1. EVM Blockchain Tx Handler & MEV Handler

- Polygon
- Ethereum
- EVM-like Blockchains

**Python implementation (`evm/builder.py` and `evm/swapper.py`)**
**Rust implementation (`evm/swapper.rs`)**

- `setup_web3_connection` function:
  - Establishes a Web3 connection to an EVM-compatible blockchain

- `EVMTransactionBuilder` class:
Handles gas estimation, contract ABI fetching, and transaction building
Supports allowance, contract interactions, and transaction signing/broadcasting

- `PolygonStakingTransactionBuilder` class (extends `EVMTransactionBuilder`):
  - Specialized for Polygon staking operations
  - Supports staking, unstaking, restaking, and reward withdrawal

- `Swapper` class:
  - Implements token swapping functionality
  - Supports multiple aggregators (e.g., 1inch, Uniswap)
  - Handles token approvals and swap execution

## 2. Tendermint Tx Handler

- Cosmos
- Celestia
- ...

**Python implementation (`tendermint/builder.py`):**

- Abstract `TendermintTxBuilder` class:
  - Defines interface for Tendermint-based blockchain transactions

- `CosmosTxBuilder` class (implements `TendermintTxBuilder`):
  - Supports send, delegate, undelegate, and redelegate transactions

- `InjectiveTxBuilder` class (implements `TendermintTxBuilder`):
  - Specialized for Injective Protocol transactions
  - Currently implements send transaction

## 3. Solana Tx Handler

- Solana

**Python implementation (`solana/builder.py`):**

- Abstract `SolanaTxBuilder` class:
  - Defines interface for Solana transactions

- `SolanaTxBuilder` class (implements `SolanaTxBuilder`):
  - Supports send transaction
