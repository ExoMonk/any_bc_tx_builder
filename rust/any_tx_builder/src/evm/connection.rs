use web3::Web3;
use web3::transports::Http;
use std::env;

pub async fn setup_web3_connection() -> web3::Result<Web3<Http>> {
    let provider_url = env::var("EVM_PROVIDER_URL")
        .expect("EVM_PROVIDER_URL must be set");
    let transport = web3::transports::Http::new(&provider_url)?;
    Ok(web3::Web3::new(transport))
}
