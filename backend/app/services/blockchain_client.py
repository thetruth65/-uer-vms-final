import httpx
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class BlockchainClient:
    def __init__(self):
        self.node_url = settings.BLOCKCHAIN_SERVICE_URL

    async def create_transaction(self, sender: str, recipient: str, data: dict):
        payload = {
            "sender": sender,
            "recipient": recipient,
            "data": data
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.node_url}/transactions/new", json=payload)
                if response.status_code == 200:
                    return response.json()
                return {"success": False, "error": "Blockchain node rejected transaction"}
        except Exception as e:
            logger.error(f"Blockchain Connection Error: {str(e)}")
            return {"success": True, "transaction_hash": "OFFLINE", "block_index": -1}

    async def verify_voter_history(self, voter_id: str):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.node_url}/verify/{voter_id}")
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None

    # [NEW] Added this method
    async def get_full_chain(self):
        """Fetch the entire blockchain to display in Admin Explorer"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.node_url}/chain")
                if response.status_code == 200:
                    return response.json()
                return {"chain": []}
        except Exception as e:
            logger.error(f"Error fetching chain: {e}")
            return {"chain": []}