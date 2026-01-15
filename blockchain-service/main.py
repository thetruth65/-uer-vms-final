from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from blockchain import Blockchain
from uuid import uuid4

app = FastAPI()
blockchain = Blockchain()
node_identifier = str(uuid4()).replace('-', '')

class Transaction(BaseModel):
    sender: str
    recipient: str
    data: dict

@app.get("/chain")
def full_chain():
    return {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
        "is_valid": blockchain.check_integrity()
    }

@app.post("/transactions/new")
def new_transaction(tx: Transaction):
    index = blockchain.new_transaction(tx.sender, tx.recipient, tx.data)
    # In a real system, you wait for mining. For this VMS, we auto-mine for speed.
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    
    return {"message": "Transaction added and Block Mined", "block_index": block['index'], "transaction_hash": blockchain.hash(block)}

@app.get("/verify/{voter_id}")
def verify_voter_on_chain(voter_id: str):
    """Scan chain to find latest state of a voter"""
    history = []
    for block in blockchain.chain:
        for tx in block['transactions']:
            if tx['data'].get('voter_id') == voter_id:
                history.append(tx)
    if not history:
        raise HTTPException(status_code=404, detail="Voter not found on chain")
    return {"history": history, "latest": history[-1]}