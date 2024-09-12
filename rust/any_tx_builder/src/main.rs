use dotenv::dotenv;
use std::env;
use web3::types::{Address, U256};
use web3::Web3;

mod evm {
    pub mod connection;
    pub mod builder;
}

use evm::connection::setup_web3_connection;
use evm::builder::EVMTransactionBuilder;

#[tokio::main]
async fn main() -> web3::Result<()> {
    // Load environment variables
    dotenv().ok();

    // Setup Web3 connection
    let w3 = setup_web3_connection().await?;
    let builder = EVMTransactionBuilder::new(w3.clone());
    
    let from_address: Address = env::var("FROM_ADDRESS")
        .expect("FROM_ADDRESS must be set")
        .parse()
        .expect("Invalid FROM_ADDRESS");
    let to_address: Address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e".parse().expect("Invalid to_address");
    let value = web3::types::U256::exp10(17); // 0.1 ether
    let gas = U256::from(21000);
    let gas_price = w3.eth().gas_price().await?;

    // Build the transaction
    let transaction = builder.build_transaction(from_address, to_address, value, gas, gas_price).await?;
    println!("Transaction built:");
    println!("{:?}", transaction);

    Ok(())
}