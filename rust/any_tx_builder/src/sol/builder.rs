use solana_sdk::{
    instruction::Instruction,
    message::Message,
    pubkey::Pubkey,
    signature::Keypair,
    transaction::Transaction,
};

pub struct SolanaTransactionBuilder {
    instructions: Vec<Instruction>,
    signers: Vec<Keypair>,
    recent_blockhash: Option<String>,
    fee_payer: Option<Pubkey>,
}

impl SolanaTransactionBuilder {
    pub fn new() -> Self {
        Self {
            instructions: Vec::new(),
            signers: Vec::new(),
            recent_blockhash: None,
            fee_payer: None,
        }
    }

    pub fn add_instruction(&mut self, instruction: Instruction) -> &mut Self {
        self.instructions.push(instruction);
        self
    }

    pub fn add_signer(&mut self, signer: Keypair) -> &mut Self {
        self.signers.push(signer);
        self
    }

    pub fn set_recent_blockhash(&mut self, recent_blockhash: String) -> &mut Self {
        self.recent_blockhash = Some(recent_blockhash);
        self
    }

    pub fn set_fee_payer(&mut self, fee_payer: Pubkey) -> &mut Self {
        self.fee_payer = Some(fee_payer);
        self
    }

    pub fn build(&self) -> Result<Transaction, &'static str> {
        if self.instructions.is_empty() {
            return Err("No instructions added to the transaction");
        }

        if self.recent_blockhash.is_none() {
            return Err("Recent blockhash not set");
        }

        let message = Message::new(&self.instructions, self.fee_payer.as_ref());
        let mut transaction = Transaction::new_unsigned(message);

        transaction.sign(&self.signers, self.recent_blockhash.as_ref().unwrap().clone());

        Ok(transaction)
    }
}