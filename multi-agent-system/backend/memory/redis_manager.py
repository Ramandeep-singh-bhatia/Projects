"""
Redis Manager for agent state and shared memory.
Handles short-term memory, message passing, and workflow state.
"""

import json
import asyncio
from typing import Any, Dict, List, Optional, Set
from datetime import timedelta
import redis.asyncio as redis
from loguru import logger

from backend.config import settings


class RedisManager:
    """Manages Redis connections and operations for agent memory and state."""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self._subscriptions: Set[str] = set()

    async def connect(self):
        """Establish connection to Redis."""
        try:
            self.redis_client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Close Redis connection."""
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")

    # ==================== Key-Value Operations ====================

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set a key-value pair in Redis.

        Args:
            key: The key to set
            value: The value (will be JSON serialized)
            ttl: Time-to-live in seconds (optional)

        Returns:
            bool: True if successful
        """
        try:
            serialized_value = json.dumps(value)
            if ttl:
                await self.redis_client.setex(key, ttl, serialized_value)
            else:
                await self.redis_client.set(key, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from Redis.

        Args:
            key: The key to retrieve

        Returns:
            The deserialized value or None if not found
        """
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """Delete a key from Redis."""
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking key existence {key}: {e}")
            return False

    # ==================== Workflow State Management ====================

    async def save_workflow_state(
        self,
        workflow_id: str,
        state: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Save workflow state to Redis.

        Args:
            workflow_id: Unique workflow identifier
            state: Workflow state dictionary
            ttl: Time-to-live in seconds (default: 24 hours)

        Returns:
            bool: True if successful
        """
        key = f"workflow:{workflow_id}:state"
        ttl = ttl or (settings.memory_ttl_hours * 3600)
        return await self.set(key, state, ttl)

    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve workflow state from Redis."""
        key = f"workflow:{workflow_id}:state"
        return await self.get(key)

    async def update_workflow_state(
        self,
        workflow_id: str,
        updates: Dict[str, Any],
    ) -> bool:
        """
        Update specific fields in workflow state.

        Args:
            workflow_id: Unique workflow identifier
            updates: Dictionary of fields to update

        Returns:
            bool: True if successful
        """
        current_state = await self.get_workflow_state(workflow_id)
        if current_state is None:
            current_state = {}

        current_state.update(updates)
        return await self.save_workflow_state(workflow_id, current_state)

    # ==================== Agent Memory Operations ====================

    async def save_agent_memory(
        self,
        agent_id: str,
        memory_type: str,
        memory_data: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Save agent memory to Redis.

        Args:
            agent_id: Unique agent identifier
            memory_type: Type of memory (short_term, episodic, etc.)
            memory_data: Memory data to store
            ttl: Time-to-live in seconds

        Returns:
            bool: True if successful
        """
        key = f"agent:{agent_id}:memory:{memory_type}"
        ttl = ttl or (settings.memory_ttl_hours * 3600)
        return await self.set(key, memory_data, ttl)

    async def get_agent_memory(
        self,
        agent_id: str,
        memory_type: str,
    ) -> Optional[Any]:
        """Retrieve agent memory from Redis."""
        key = f"agent:{agent_id}:memory:{memory_type}"
        return await self.get(key)

    async def append_to_agent_memory(
        self,
        agent_id: str,
        memory_type: str,
        item: Any,
    ) -> bool:
        """
        Append an item to agent's memory list.

        Args:
            agent_id: Unique agent identifier
            memory_type: Type of memory
            item: Item to append

        Returns:
            bool: True if successful
        """
        memory = await self.get_agent_memory(agent_id, memory_type)
        if memory is None:
            memory = []

        if isinstance(memory, list):
            memory.append(item)
            return await self.save_agent_memory(agent_id, memory_type, memory)
        else:
            logger.error(f"Memory type {memory_type} is not a list")
            return False

    # ==================== Pub/Sub Messaging ====================

    async def publish(self, channel: str, message: Dict[str, Any]) -> int:
        """
        Publish a message to a channel.

        Args:
            channel: Channel name
            message: Message dictionary

        Returns:
            int: Number of subscribers that received the message
        """
        try:
            serialized_message = json.dumps(message)
            return await self.redis_client.publish(channel, serialized_message)
        except Exception as e:
            logger.error(f"Error publishing to channel {channel}: {e}")
            return 0

    async def subscribe(self, channel: str):
        """
        Subscribe to a channel.

        Args:
            channel: Channel name to subscribe to
        """
        try:
            if not self.pubsub:
                self.pubsub = self.redis_client.pubsub()

            await self.pubsub.subscribe(channel)
            self._subscriptions.add(channel)
            logger.info(f"Subscribed to channel: {channel}")
        except Exception as e:
            logger.error(f"Error subscribing to channel {channel}: {e}")

    async def unsubscribe(self, channel: str):
        """Unsubscribe from a channel."""
        try:
            if self.pubsub and channel in self._subscriptions:
                await self.pubsub.unsubscribe(channel)
                self._subscriptions.remove(channel)
                logger.info(f"Unsubscribed from channel: {channel}")
        except Exception as e:
            logger.error(f"Error unsubscribing from channel {channel}: {e}")

    async def listen(self):
        """
        Listen for messages on subscribed channels.

        Yields:
            Dict[str, Any]: Received messages
        """
        if not self.pubsub:
            logger.error("PubSub not initialized. Call subscribe() first.")
            return

        async for message in self.pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    yield data
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding message: {e}")

    # ==================== List Operations ====================

    async def push_to_list(self, key: str, value: Any, position: str = "right") -> bool:
        """
        Push a value to a Redis list.

        Args:
            key: List key
            value: Value to push
            position: 'left' or 'right' (default: 'right')

        Returns:
            bool: True if successful
        """
        try:
            serialized_value = json.dumps(value)
            if position == "left":
                await self.redis_client.lpush(key, serialized_value)
            else:
                await self.redis_client.rpush(key, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Error pushing to list {key}: {e}")
            return False

    async def pop_from_list(
        self,
        key: str,
        position: str = "left",
    ) -> Optional[Any]:
        """
        Pop a value from a Redis list.

        Args:
            key: List key
            position: 'left' or 'right' (default: 'left')

        Returns:
            The popped value or None
        """
        try:
            if position == "left":
                value = await self.redis_client.lpop(key)
            else:
                value = await self.redis_client.rpop(key)

            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error popping from list {key}: {e}")
            return None

    async def get_list(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """
        Get all items from a Redis list.

        Args:
            key: List key
            start: Start index (default: 0)
            end: End index (default: -1 for all)

        Returns:
            List of items
        """
        try:
            values = await self.redis_client.lrange(key, start, end)
            return [json.loads(v) for v in values]
        except Exception as e:
            logger.error(f"Error getting list {key}: {e}")
            return []

    # ==================== Hash Operations ====================

    async def hset(self, key: str, field: str, value: Any) -> bool:
        """Set a field in a Redis hash."""
        try:
            serialized_value = json.dumps(value)
            await self.redis_client.hset(key, field, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Error setting hash field {key}:{field}: {e}")
            return False

    async def hget(self, key: str, field: str) -> Optional[Any]:
        """Get a field from a Redis hash."""
        try:
            value = await self.redis_client.hget(key, field)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting hash field {key}:{field}: {e}")
            return None

    async def hgetall(self, key: str) -> Dict[str, Any]:
        """Get all fields from a Redis hash."""
        try:
            hash_data = await self.redis_client.hgetall(key)
            return {k: json.loads(v) for k, v in hash_data.items()}
        except Exception as e:
            logger.error(f"Error getting hash {key}: {e}")
            return {}

    # ==================== Utility Methods ====================

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter."""
        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing key {key}: {e}")
            return 0

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for a key."""
        try:
            return await self.redis_client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Error setting expiration for key {key}: {e}")
            return False

    async def get_keys_by_pattern(self, pattern: str) -> List[str]:
        """Get all keys matching a pattern."""
        try:
            return await self.redis_client.keys(pattern)
        except Exception as e:
            logger.error(f"Error getting keys by pattern {pattern}: {e}")
            return []


# Global Redis manager instance
redis_manager = RedisManager()
