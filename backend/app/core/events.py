import redis
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisPubSubManager:
    def __init__(self):
        self.redis_client = None

    def connect(self):
        try:
            # We will use a standard redis connection URL from config, default to localhost
            redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("✅ Connected to Redis successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.redis_client = None

    def publish_event(self, channel: str, event_data: dict):
        if not self.redis_client:
            logger.warning("Redis client not connected. Falling back to sync mode or dropping event.")
            return False
            
        try:
            message = json.dumps(event_data)
            self.redis_client.publish(channel, message)
            logger.info(f"📤 Published event to {channel}: {event_data.get('type', 'UNKNOWN')}")
            return True
        except Exception as e:
            logger.error(f"❌ Error publishing to {channel}: {e}")
            return False

pubsub_manager = RedisPubSubManager()
