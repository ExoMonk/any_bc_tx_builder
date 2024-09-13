use dotenv::dotenv;
use std::env;

mod evm {
    pub mod connection;
    pub mod builder;
    pub mod swapper;
}

use crate::evm::builder::EVMTransactionBuilder, PolygonStakingTransactionBuilder;
use crate::evm::swapper::Swapper;
use web3::Web3;
use web3::transports::Http;
use web3::types::{Address, U256};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Load environment variables
    dotenv().ok();

    let w3 = setup_web3_connection().await?;

    let evm_builder = EVMTransactionBuilder::new(web3.clone());
    let swapper = Swapper::new(evm_builder, "your_private_key_here")?;

    let token_in = Address::from_str("0x6B175474E89094C44Da98b954EedeAC495271d0F")?; // DAI
    let token_out = Address::from_str("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")?; // USDC
    let amount_in = U256::from(1000000000000000000u64); // 1 DAI

    // Swap using 1inch
    let tx_hash = swapper.swap(token_in, token_out, amount_in, U256::zero(), None, "1inch", 0.005).await?;
    println!("1inch swap transaction hash: {:?}", tx_hash);

    // Swap using Uniswap
    let tx_hash = swapper.swap(token_in, token_out, amount_in, U256::zero(), None, "uniswap", 0.005).await?;
    println!("Uniswap swap transaction hash: {:?}", tx_hash);

    Ok(())
}