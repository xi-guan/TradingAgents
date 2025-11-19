"""WebSocket 连接管理器"""

import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 用户 ID -> WebSocket 连接集合
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """建立连接"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected: user_id={user_id}, total={len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """断开连接"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

            logger.info(f"WebSocket disconnected: user_id={user_id}")

    async def send_personal_message(
        self,
        message: dict,
        user_id: str,
        websocket: WebSocket
    ):
        """发送个人消息"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            self.disconnect(websocket, user_id)

    async def broadcast_to_user(self, user_id: str, message: dict):
        """向特定用户的所有连接广播消息"""
        if user_id not in self.active_connections:
            return

        dead_connections = set()

        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                dead_connections.add(connection)
            except Exception as e:
                logger.error(f"Failed to broadcast to user {user_id}: {e}")
                dead_connections.add(connection)

        # 清理死连接
        self.active_connections[user_id] -= dead_connections

        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def broadcast_to_all(self, message: dict):
        """广播消息给所有连接"""
        for user_id in list(self.active_connections.keys()):
            await self.broadcast_to_user(user_id, message)

    def get_user_connection_count(self, user_id: str) -> int:
        """获取用户连接数"""
        return len(self.active_connections.get(user_id, set()))

    def get_total_connections(self) -> int:
        """获取总连接数"""
        return sum(len(connections) for connections in self.active_connections.values())


# 全局 WebSocket 管理器实例
websocket_manager = WebSocketManager()
