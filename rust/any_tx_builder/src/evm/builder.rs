use web3::types::{Address, U256, TransactionParameters, Bytes};
use web3::Web3;
use web3::transports::Http;
use std::error::Error;
use serde_json::Value;
use reqwest;
use std::fs;
use std::path::Path;

pub struct EVMTransactionBuilder {
    w3: Web3<Http>,
}

// Constants (you might want to move these to a separate config file)
const POLYGON_STAKING_CONTRACT: &str = "0x4AE8f648B1Ec892B6cc68C89cc088583964d08bE";
const POLYGON_TOKEN_CONTRACT: &str = "0x44499312f493F62f2DFd3C6435Ca3603EbFCeeBa";

pub struct PolygonStakingTransactionBuilder {
    evm_builder: EVMTransactionBuilder,
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
        data: Bytes,
    ) -> Result<TransactionParameters, Box<dyn Error>> {
        let nonce = self.w3.eth().transaction_count(from, None).await?;
        let gas_price = self.estimate_gas_price().await?;
        let gas = self.estimate_gas(TransactionParameters {
            nonce: Some(nonce),
            to: Some(to),
            value,
            gas_price: Some(gas_price.0),
            max_fee_per_gas: Some(gas_price.1),
            max_priority_fee_per_gas: Some(gas_price.2),
            gas: U256::from(21000), // Default gas limit, will be updated
            data,
            ..Default::default()
        }).await?;

        Ok(TransactionParameters {
            nonce: Some(nonce),
            to: Some(to),
            value,
            gas,
            gas_price: Some(gas_price.0),
            max_fee_per_gas: Some(gas_price.1),
            max_priority_fee_per_gas: Some(gas_price.2),
            data,
            ..Default::default()
        })
    }

    async fn estimate_gas_price(&self) -> Result<(U256, U256, U256), Box<dyn Error>> {
        let latest_block = self.w3.eth().block(web3::types::BlockNumber::Latest).await?.unwrap();
        let base_fee = latest_block.base_fee_per_gas.unwrap();
        let max_priority_fee = self.w3.eth().max_priority_fee_per_gas().await?;
        let max_fee_per_gas = base_fee + max_priority_fee;

        Ok((base_fee, max_fee_per_gas, max_priority_fee))
    }

    async fn estimate_gas(&self, transaction: TransactionParameters) -> Result<U256, Box<dyn Error>> {
        let estimated_gas = self.w3.eth().estimate_gas(transaction.clone(), None).await?;
        Ok(estimated_gas * U256::from(110) / U256::from(100)) // Add 10% buffer
    }

    pub async fn get_contract_abi(&self, contract_address: &str) -> Result<Value, Box<dyn Error>> {
        let local_file_path = format!("./abi/{}.json", contract_address);
        if Path::new(&local_file_path).exists() {
            let abi_string = fs::read_to_string(local_file_path)?;
            return Ok(serde_json::from_str(&abi_string)?);
        }

        let etherscan_api_key = std::env::var("ETHERSCAN_API_KEY")?;
        let api_url = if std::env::var("ENV")? == "dev" {
            format!("https://api-sepolia.etherscan.io/api?module=contract&action=getabi&address={}&apikey={}", contract_address, etherscan_api_key)
        } else {
            format!("https://api.etherscan.io/api?module=contract&action=getabi&address={}&apikey={}", contract_address, etherscan_api_key)
        };

        let response = reqwest::get(&api_url).await?.json::<Value>().await?;
        
        if response["status"] == "1" {
            let abi: Value = serde_json::from_str(&response["result"].as_str().unwrap())?;
            
            // Save ABI to local file for future use
            fs::create_dir_all("./abi")?;
            fs::write(&local_file_path, serde_json::to_string_pretty(&abi)?)?;

            Ok(abi)
        } else {
            Err(format!("API Error: {}", response["message"]).into())
        }
    }

    pub fn sign_transaction(&self, transaction: TransactionParameters, private_key: &str) -> Result<SignedTransaction, Box<dyn Error>> {
        let private_key = private_key.parse()?;
        let signed = self.w3.accounts().sign_transaction(transaction, &private_key).await?;
        Ok(signed)
    }
    
    pub async fn broadcast_transaction(&self, signed_transaction: SignedTransaction) -> Result<web3::types::H256, Box<dyn Error>> {
        let transaction_hash = self.w3.eth().send_raw_transaction(signed_transaction.raw_transaction).await?;
        println!(" ✅ Transaction sent: {:?}", transaction_hash);
        Ok(transaction_hash)
    }

    pub async fn is_transaction_broadcasted(&self, tx_hash: web3::types::H256) -> Result<bool, Box<dyn Error>> {
        match self.w3.eth().transaction_receipt(tx_hash).await? {
            Some(receipt) => Ok(receipt.status == Some(web3::types::U64::from(1))),
            None => Ok(false),
        }
    }

    pub async fn build_allowance_transaction(
        &self,
        from_address: Address,
        token_address: Address,
        spender: Address,
        amount: U256,
    ) -> Result<TransactionParameters, Box<dyn Error>> {
        let token_abi = self.get_contract_abi(&token_address.to_string()).await?;
        let contract = web3::contract::Contract::new(self.w3.eth(), token_address, token_abi);
        
        let data = contract.abi().function("approve")?.encode_input(&[
            web3::contract::tokens::Token::Address(spender),
            web3::contract::tokens::Token::Uint(amount),
        ])?;

        self.build_transaction(from_address, token_address, U256::zero(), data.into()).await
    }

    pub async fn build_contract_transaction(
        &self,
        from_address: Address,
        contract_address: Address,
        function_name: &str,
        function_args: Vec<web3::contract::tokens::Token>,
        value: U256,
    ) -> Result<TransactionParameters, Box<dyn Error>> {
        let contract_abi = self.get_contract_abi(&contract_address.to_string()).await?;
        let contract = web3::contract::Contract::new(self.w3.eth(), contract_address, contract_abi);
        
        let data = contract.abi().function(function_name)?.encode_input(&function_args)?;

        self.build_transaction(from_address, contract_address, value, data.into()).await
    }
}

impl PolygonStakingTransactionBuilder {
    pub fn new(w3: Web3<Http>) -> Self {
        Self {
            evm_builder: EVMTransactionBuilder::new(w3),
        }
    }

    pub async fn build_POL_allowance_transaction(
        &self,
        from_address: Address,
        amount: U256,
    ) -> Result<TransactionParameters, Box<dyn Error>> {
        let token_address = Address::from_str(POLYGON_TOKEN_CONTRACT)?;
        let staking_address = Address::from_str(POLYGON_STAKING_CONTRACT)?;

        self.evm_builder.build_allowance_transaction(
            from_address,
            token_address,
            staking_address,
            amount,
        ).await
    }

    pub async fn build_staking_transaction(
        &self,
        from_address: Address,
        amount: U256,
        validator_address: Address,
    ) -> Result<TransactionParameters, Box<dyn Error>> {
        let function_name = "buyVoucherPOL";
        let function_args = vec![
            web3::contract::tokens::Token::Uint(amount),
            web3::contract::tokens::Token::Uint(U256::zero()),
        ];

        self.evm_builder.build_contract_transaction(
            from_address,
            validator_address,
            function_name,
            function_args,
            U256::zero(),
        ).await
    }

    pub async fn build_unstaking_transaction(
        &self,
        from_address: Address,
        validator_address: Address,
        amount: U256,
    ) -> Result<TransactionParameters, Box<dyn Error>> {
        let function_name = "sellVoucher_newPOL";
        let function_args = vec![
            web3::contract::tokens::Token::Uint(amount),
            web3::contract::tokens::Token::Uint(amount),
        ];

        self.evm_builder.build_contract_transaction(
            from_address,
            validator_address,
            function_name,
            function_args,
            U256::zero(),
        ).await
    }

    pub async fn build_restaking_transaction(
        &self,
        from_address: Address,
        validator_address: Address,
    ) -> Result<TransactionParameters, Box<dyn Error>> {
        let function_name = "restake";
        let function_args = vec![];

        self.evm_builder.build_contract_transaction(
            from_address,
            validator_address,
            function_name,
            function_args,
            U256::zero(),
        ).await
    }

    pub async fn build_withdraw_rewards_transaction(
        &self,
        from_address: Address,
        validator_address: Address,
    ) -> Result<TransactionParameters, Box<dyn Error>> {
        let function_name = "withdrawRewardsPOL";
        let function_args = vec![];

        self.evm_builder.build_contract_transaction(
            from_address,
            validator_address,
            function_name,
            function_args,
            U256::zero(),
        ).await
    }

    // Delegate other methods to the inner EVMTransactionBuilder
    pub async fn sign_transaction(&self, transaction: TransactionParameters, private_key: &str) -> Result<web3::types::SignedTransaction, Box<dyn Error>> {
        self.evm_builder.sign_transaction(transaction, private_key)
    }

    pub async fn broadcast_transaction(&self, signed_transaction: web3::types::SignedTransaction) -> Result<web3::types::H256, Box<dyn Error>> {
        self.evm_builder.broadcast_transaction(signed_transaction).await
    }

    pub async fn is_transaction_broadcasted(&self, tx_hash: web3::types::H256) -> Result<bool, Box<dyn Error>> {
        self.evm_builder.is_transaction_broadcasted(tx_hash).await
    }
}
