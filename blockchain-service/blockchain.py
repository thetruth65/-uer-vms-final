import hashlib
import json
from time import time
from typing import List, Dict, Any

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        # Genesis Block
        self.new_block(previous_hash="1", proof=100)

    def new_block(self, proof: int, previous_hash: str = None) -> Dict[str, Any]:
        """Create a new block in the blockchain"""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.pending_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.pending_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, data: Dict) -> int:
        """Adds a new transaction to the list of transactions"""
        self.pending_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'data': data, # Voter Data Hash, ID, Event Type
            'timestamp': time()
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        """SHA-256 Hashing of a Block"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof: int) -> int:
        """Simple PoW Algorithm"""
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """Validates the proof: Does hash(last_proof, proof) contain 4 leading zeroes?"""
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def check_integrity(self) -> bool:
        """Check if the chain is valid"""
        for i in range(1, len(self.chain)):
            previous_block = self.chain[i-1]
            current_block = self.chain[i]
            
            # Check 1: Hash Link
            if current_block['previous_hash'] != self.hash(previous_block):
                return False
            
            # Check 2: PoW
            if not self.valid_proof(previous_block['proof'], current_block['proof']):
                return False
        return True