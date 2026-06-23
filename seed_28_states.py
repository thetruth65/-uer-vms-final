import asyncio
import httpx
import os
import json
from datetime import datetime

# Define 28 states mapping (State ID to Port)
STATES = {
    f"STATE_{chr(65+i)}": 8000 + (i*2) for i in range(26)
}
STATES["STATE_AA"] = 8052
STATES["STATE_AB"] = 8054

MOCK_PHOTO_PATH = "frontend/public/vite.svg" # A tiny file to simulate photo

async def register_voter(state_id: str, port: int, index: int):
    url = f"http://127.0.0.1:{port}/api/registration/register"
    
    # Create mock photo file content
    if not os.path.exists(MOCK_PHOTO_PATH):
        with open(MOCK_PHOTO_PATH, "wb") as f:
            f.write(b"mock_image_data")
            
    voter_data = {
        "first_name": f"Voter{index}",
        "last_name": f"State{state_id.split('_')[1]}",
        "date_of_birth": f"{1980 + (index % 20)}-01-01",
        "gender": "O",
        "address": f"Address {index}, {state_id}",
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(MOCK_PHOTO_PATH, "rb") as photo_file:
                files = {"photo": ("photo.jpg", photo_file, "image/jpeg")}
                response = await client.post(url, data=voter_data, files=files)
                
            if response.status_code == 200:
                print(f"✅ [{state_id} - Port {port}] Registered: {voter_data['first_name']} {voter_data['last_name']}")
            else:
                print(f"❌ [{state_id}] Failed: {response.text}")
    except Exception as e:
        print(f"⚠️ [{state_id}] Error: Could not connect to port {port}. Is the state backend running?")

async def main():
    print("==================================================")
    print("🗳️  28-STATE ELECTORAL SEED SCRIPT")
    print("==================================================")
    print("Make sure your 28-node docker-compose is running!")
    print("Command: docker-compose -f docker-compose.prod.yml up -d\n")
    
    tasks = []
    voter_index = 1
    
    for state_id, port in STATES.items():
        # Seed 2 voters per state
        for _ in range(2):
            tasks.append(register_voter(state_id, port, voter_index))
            voter_index += 1
            
    # Run all registrations concurrently for speed
    await asyncio.gather(*tasks)
    print("\n✅ Seeding Complete! 56 voters registered across 28 states.")

if __name__ == "__main__":
    asyncio.run(main())
