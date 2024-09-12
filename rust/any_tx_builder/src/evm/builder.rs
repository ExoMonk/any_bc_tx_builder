use web3::types::{Address, U256, TransactionParameters};
use web3::Web3;
use web3::transports::Http;

pub struct EVMTransactionBuilder {
    w3: Web3<Http>,
}

impl EVMTransactionBuilder {
    pub fn new(w3: Web3<Http>) -> Self {
        Self { w3 }
    }

    pub async fn build_transaction(
        &self,
        from: Address,
        to: Address,
        value: U256,
        gas: U256,
        gas_price: U256,
    ) -> web3::Result<TransactionParameters> {
        let nonce = self.w3.eth().transaction_count(from, None).await?;

        Ok(TransactionParameters {
            nonce: Some(nonce),
            to: Some(to),
            value,
            gas,
            gas_price: Some(gas_price),
            ..Default::default()
        })
    }
}