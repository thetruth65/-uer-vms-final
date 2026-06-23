import os
import asyncio
import httpx
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load main env file
load_dotenv(".env")

DATABASE_URL = os.getenv("DATABASE_URL")
BLOCKCHAIN_SERVICE_URL = os.getenv("BLOCKCHAIN_SERVICE_URL", "http://localhost:5000")

def reset_sql_database():
    print(f"🔌 Connecting to Supabase Database...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("🗑️ Wiping SQL Tables...")
        # Order matters to avoid foreign key issues (if any)
        tables = [
            "voters",
            "audit_logs",
            "blockchain_ledger",
            "voter_assets",
            "face_encodings"
        ]
        
        for table in tables:
            try:
                conn.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))
                print(f"  ✅ Cleared {table}")
            except Exception as e:
                print(f"  ⚠️ Could not clear {table} (it may not exist yet)")
        conn.commit()
    print("✅ Database Wipe Complete!")

async def reset_blockchain_node():
    print("🗑️ Wiping Blockchain Ledger...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BLOCKCHAIN_SERVICE_URL}/reset")
            if response.status_code == 200:
                print("  ✅ Blockchain Node Reset to Genesis Block!")
            else:
                print(f"  ⚠️ Blockchain Node returned {response.status_code}")
    except Exception as e:
        print(f"  ⚠️ Could not reach Blockchain Node at {BLOCKCHAIN_SERVICE_URL}: {e}")

async def main():
    print("==================================================")
    print("  Electoral System - Full Environment Reset Tool")
    print("==================================================")
    
    reset_sql_database()
    await reset_blockchain_node()
    
    # --- WIPE REDIS CACHE ---
    print("\n🗑️ Wiping Redis Cache...")
    redis_url = os.getenv("REDIS_URL", "rediss://default:gQAAAAAAAaTlAAIgcDFhOWE1ZWVjOWYwOWE0ODNiOTUwNWQyOTJiMGFlODE4NA@crucial-parakeet-107749.upstash.io:6379")
    try:
        import redis
        redis_client = redis.from_url(redis_url)
        redis_client.flushdb()
        print("  ✅ Cleared Redis Cache successfully!")
    except Exception as e:
        print(f"  ⚠️ Could not connect to Redis: {e}")

    print("\n==================================================")
    print("🚀 System is now completely fresh and ready for testing!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
