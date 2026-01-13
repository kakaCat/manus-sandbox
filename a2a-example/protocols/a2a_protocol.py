"""
A2A (Agent-to-Agent) 协议核心实现

基于JSON-RPC 2.0规范的代理间通信协议
支持任务分发、结果收集、流式消息传递
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class MessageType(str, Enum):
    """消息类型枚举"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ErrorCode(int, Enum):
    """错误代码枚举"""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


@dataclass
class A2AMessage:
    """
    A2A协议消息基类
    
    Attributes:
        msg_id: 消息唯一标识
        message_type: 消息类型
        sender_agent: 发送方代理ID
        receiver_agent: 接收方代理ID
        timestamp: 时间戳
        payload: 消息负载
        metadata: 元数据
    """
    message_type: MessageType
    sender_agent: str
    receiver_agent: str
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """将消息转换为字典"""
        return {
            "msg_id": self.msg_id,
            "message_type": self.message_type.value,
            "sender_agent": self.sender_agent,
            "receiver_agent": self.receiver_agent,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """从字典创建消息"""
        return cls(
            msg_id=data.get("msg_id", str(uuid.uuid4())),
            message_type=MessageType(data.get("message_type", "request")),
            sender_agent=data["sender_agent"],
            receiver_agent=data["receiver_agent"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            payload=data.get("payload", {}),
            metadata=data.get("metadata", {})
        )


@dataclass
class A2ATask:
    """
    A2A任务
    
    Attributes:
        task_id: 任务唯一标识
        task_type: 任务类型
        status: 任务状态
        priority: 任务优先级(1-10)
        input_data: 输入数据
        output_data: 输出数据
        created_at: 创建时间
        updated_at: 更新时间
        assigned_agent: 分配的代理
        dependencies: 依赖的任务ID列表
        metadata: 任务元数据
    """
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    assigned_agent: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status.value,
            "priority": self.priority,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "assigned_agent": self.assigned_agent,
            "dependencies": self.dependencies,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2ATask':
        """从字典创建任务"""
        return cls(
            task_id=data.get("task_id", str(uuid.uuid4())),
            task_type=data.get("task_type", ""),
            status=TaskStatus(data.get("status", "pending")),
            priority=data.get("priority", 5),
            input_data=data.get("input_data", {}),
            output_data=data.get("output_data", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            assigned_agent=data.get("assigned_agent"),
            dependencies=data.get("dependencies", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class A2AEvent:
    """
    A2A事件
    
    Attributes:
        event_type: 事件类型
        source_agent: 事件源代理
        target_agent: 事件目标代理
        task_id: 关联的任务ID
        event_data: 事件数据
        timestamp: 事件时间戳
    """
    event_type: str
    source_agent: str
    target_agent: Optional[str] = None
    task_id: Optional[str] = None
    event_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_type": self.event_type,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "task_id": self.task_id,
            "event_data": self.event_data,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AEvent':
        """从字典创建事件"""
        return cls(
            event_type=data["event_type"],
            source_agent=data["source_agent"],
            target_agent=data.get("target_agent"),
            task_id=data.get("task_id"),
            event_data=data.get("event_data", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now()
        )


class A2AProtocol:
    """
    A2A协议处理器
    
    负责消息的序列化、反序列化和协议验证
    """
    
    @staticmethod
    def create_request(
        sender_agent: str,
        receiver_agent: str,
        method: str,
        params: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> A2AMessage:
        """创建请求消息"""
        return A2AMessage(
            message_type=MessageType.REQUEST,
            sender_agent=sender_agent,
            receiver_agent=receiver_agent,
            payload={
                "method": method,
                "params": params,
                "task_id": task_id
            }
        )

    @staticmethod
    def create_response(
        sender_agent: str,
        receiver_agent: str,
        request_id: str,
        result: Any,
        task_id: Optional[str] = None
    ) -> A2AMessage:
        """创建响应消息"""
        return A2AMessage(
            message_type=MessageType.RESPONSE,
            sender_agent=sender_agent,
            receiver_agent=receiver_agent,
            payload={
                "request_id": request_id,
                "result": result,
                "task_id": task_id
            }
        )

    @staticmethod
    def create_error(
        sender_agent: str,
        receiver_agent: str,
        request_id: str,
        error_code: ErrorCode,
        error_message: str,
        error_data: Optional[Dict] = None
    ) -> A2AMessage:
        """创建错误消息"""
        return A2AMessage(
            message_type=MessageType.ERROR,
            sender_agent=sender_agent,
            receiver_agent=receiver_agent,
            payload={
                "request_id": request_id,
                "error": {
                    "code": error_code.value,
                    "message": error_message,
                    "data": error_data
                }
            }
        )

    @staticmethod
    def create_notification(
        sender_agent: str,
        receiver_agent: str,
        event_type: str,
        event_data: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> A2AMessage:
        """创建通知消息"""
        return A2AMessage(
            message_type=MessageType.NOTIFICATION,
            sender_agent=sender_agent,
            receiver_agent=receiver_agent,
            payload={
                "event_type": event_type,
                "task_id": task_id,
                "data": event_data
            }
        )

    @staticmethod
    def serialize_message(message: A2AMessage) -> str:
        """序列化消息为JSON字符串"""
        import json
        return json.dumps(message.to_dict(), indent=2)

    @staticmethod
    def deserialize_message(json_str: str) -> A2AMessage:
        """从JSON字符串反序列化消息"""
        import json
        data = json.loads(json_str)
        return A2AMessage.from_dict(data)
