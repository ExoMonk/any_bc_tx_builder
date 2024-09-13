use super::builder::EVMTransactionBuilder;
use web3::types::{Address, U256, TransactionParameters, Bytes};
use web3::Web3;
use web3::transports::Http;
use std::error::Error;
use serde_json::Value;
use reqwest;

pub struct Swapper {
    tx_builder: EVMTransactionBuilder,
    account: web3::types::Account,
    client: reqwest::Client,
}

impl Swapper {
    pub fn new(tx_builder: EVMTransactionBuilder, private_key: &str) -> Result<Self, Box<dyn Error>> {
        let account = tx_builder.w3.accounts().private_key_to_account(private_key)?;
        let client = reqwest::Client::new();
        Ok(Self { tx_builder, account })
    }

    pub async fn sign_and_send_transaction(&self, transaction: TransactionParameters) -> Result<web3::types::H256, Box<dyn Error>> {
        let signed_txn = self.tx_builder.sign_transaction(transaction, &self.account.private_key)?;
        let tx_hash = self.tx_builder.broadcast_transaction(signed_txn).await?;
        println!(" ✅ Transaction sent: {:?}", tx_hash);
        Ok(tx_hash)
    }

    pub async fn swap(
        &self,
        token_in: Address,
        token_out: Address,
        amount_in: U256,
        min_amount_out: U256,
        recipient: Option<Address>,
        aggregator: &str,
        slippage: f64,
    ) -> Result<web3::types::H256, Box<dyn Error>> {
        // 1. Get a quote from the aggregator
        let quote = self.get_quote(token_in, token_out, amount_in, aggregator).await?;
        
        // 2. Approve token spending if necessary
        if token_in != Address::zero() {
            let sent_allowance_tx = self.approve_token(self.account.address, token_in, amount_in, quote.router).await?;
            self.tx_builder.w3.eth().transaction_receipt(sent_allowance_tx).await?;
        }

        // 3. Build the swap transaction
        let swap_data = quote.data;
        let mut swap_tx = self.tx_builder.build_contract_transaction(
            self.account.address,
            quote.router,
            "swap", // This might vary depending on the aggregator
            vec![],
            if token_in == Address::zero() { amount_in } else { U256::zero() },
        ).await?;
        
        // Modify the transaction data with the swap_data from the quote
        swap_tx.data = swap_data;

        self.sign_and_send_transaction(swap_tx).await
    }

    async fn approve_token(&self, from_address: Address, token: Address, amount: U256, spender: Address) -> Result<web3::types::H256, Box<dyn Error>> {
        let allowance_tx = self.tx_builder.build_allowance_transaction(
            from_address,
            token,
            spender,
            amount,
        ).await?;
        self.sign_and_send_transaction(allowance_tx).await
    }

    async fn get_quote(&self, token_in: Address, token_out: Address, amount_in: U256, aggregator: &str) -> Result<Quote, Box<dyn Error>> {
        match aggregator.to_lowercase().as_str() {
            "1inch" => self.get_1inch_quote(token_in, token_out, amount_in).await,
            "uniswap" => self.get_uniswap_quote(token_in, token_out, amount_in).await,
            _ => Err("Unsupported aggregator".into()),
        }
    }

    async fn get_1inch_quote(&self, token_in: Address, token_out: Address, amount_in: U256) -> Result<Quote, Box<dyn Error>> {
        let api_url = "https://api.1inch.io/v5.0/1/swap"; // Assuming Ethereum mainnet
        let params = [
            ("fromTokenAddress", token_in.to_string()),
            ("toTokenAddress", token_out.to_string()),
            ("amount", amount_in.to_string()),
            ("fromAddress", self.account.address.to_string()),
            ("slippage", "1".to_string()), // 1% slippage, adjust as needed
        ];

        let response: Value = self.client.get(api_url)
            .query(&params)
            .send()
            .await?
            .json()
            .await?;

        let router = Address::from_str(&response["tx"]["to"].as_str().ok_or("Invalid router address")?)?;
        let data = Bytes::from_str(&response["tx"]["data"].as_str().ok_or("Invalid transaction data")?)?;

        Ok(Quote { router, data })
    }

    async fn get_uniswap_quote(&self, token_in: Address, token_out: Address, amount_in: U256) -> Result<Quote, Box<dyn Error>> {
        let api_url = "https://api.uniswap.org/v1/quote"; // Uniswap API endpoint
        let params = [
            ("tokenIn", token_in.to_string()),
            ("tokenOut", token_out.to_string()),
            ("amount", amount_in.to_string()),
            ("recipient", self.account.address.to_string()),
        ];

        let response: Value = self.client.get(api_url)
            .query(&params)
            .send()
            .await?
            .json()
            .await?;

        let router = Address::from_str(&response["methodParameters"]["to"].as_str().ok_or("Invalid router address")?)?;
        let data = Bytes::from_str(&response["methodParameters"]["calldata"].as_str().ok_or("Invalid transaction data")?)?;

        Ok(Quote { router, data })
    }
}

struct Quote {
    router: Address,
    data: Bytes,
}