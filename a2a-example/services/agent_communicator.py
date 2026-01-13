"""
A2A通信服务

提供代理间的通信功能：
- 消息路由
- 任务分发
- 代理发现
- 连接管理
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
import asyncio
import json

from protocols.a2a_protocol import A2AMessage, A2ATask, A2AProtocol, TaskStatus


class AgentCommunicator:
    """
    代理通信器
    
    负责代理间的消息传递和任务分发
    
    Attributes:
        local_agent: 本地代理实例
        message_handlers: 消息处理器映射
        task_handlers: 任务处理器映射
        connected_agents: 已连接的代理列表
        message_history: 消息历史
    """
    
    def __init__(self, local_agent_id: str):
        """
        初始化通信器
        
        Args:
            local_agent_id: 本地代理ID
        """
        self.local_agent_id = local_agent_id
        self.message_handlers: Dict[str, Callable] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.connected_agents: Dict[str, Dict] = {}
        self.message_history: List[Dict] = []
        
        # 消息队列
        self._incoming_messages: asyncio.Queue = asyncio.Queue()
        self._outgoing_messages: asyncio.Queue = asyncio.Queue()
        
        # 任务回调
        self._task_callbacks: Dict[str, Callable] = {}
        
        # 启动消息处理循环
        asyncio.create_task(self._process_outgoing_messages())
    
    async def connect_to_agent(
        self,
        agent_id: str,
        agent_info: Dict[str, Any],
        connection_type: str = "direct"
    ):
        """
        连接到其他代理
        
        Args:
            agent_id: 目标代理ID
            agent_info: 目标代理信息
            connection_type: 连接类型
        """
        self.connected_agents[agent_id] = {
            "info": agent_info,
            "connection_type": connection_type,
            "connected_at": datetime.now().isoformat(),
            "status": "connected"
        }
        print(f"Connected to agent: {agent_id}")
    
    async def disconnect_from_agent(self, agent_id: str):
        """
        断开与代理的连接
        
        Args:
            agent_id: 目标代理ID
        """
        if agent_id in self.connected_agents:
            del self.connected_agents[agent_id]
            print(f"Disconnected from agent: {agent_id}")
    
    def get_connected_agents(self) -> List[Dict[str, Any]]:
        """获取已连接的代理列表"""
        return list(self.connected_agents.values())
    
    def register_message_handler(self, method: str, handler: Callable):
        """
        注册消息处理器
        
        Args:
            method: 消息方法名
            handler: 处理函数
        """
        self.message_handlers[method] = handler
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """
        注册任务处理器
        
        Args:
            task_type: 任务类型
            handler: 处理函数
        """
        self.task_handlers[task_type] = handler
    
    async def send_message(
        self,
        receiver_agent: str,
        method: str,
        params: Dict[str, Any],
        task_id: Optional[str] = None,
        callback: Optional[Callable] = None
    ) -> str:
        """
        发送消息到其他代理
        
        Args:
            receiver_agent: 接收方代理ID
            method: 消息方法
            params: 消息参数
            task_id: 关联的任务ID
            callback: 响应回调函数
            
        Returns:
            消息ID
        """
        message = A2AProtocol.create_request(
            sender_agent=self.local_agent_id,
            receiver_agent=receiver_agent,
            method=method,
            params=params,
            task_id=task_id
        )
        
        msg_id = message.msg_id
        
        # 注册回调
        if callback:
            self._task_callbacks[msg_id] = callback
        
        # 添加到消息队列
        await self._outgoing_messages.put(message)
        
        # 记录消息历史
        self.message_history.append({
            "msg_id": msg_id,
            "direction": "outgoing",
            "method": method,
            "receiver": receiver_agent,
            "timestamp": datetime.now().isoformat()
        })
        
        return msg_id
    
    async def broadcast_message(
        self,
        method: str,
        params: Dict[str, Any],
        exclude_agents: Optional[List[str]] = None
    ) -> List[str]:
        """
        广播消息到所有已连接的代理
        
        Args:
            method: 消息方法
            params: 消息参数
            exclude_agents: 排除的代理列表
            
        Returns:
            发送的消息ID列表
        """
        exclude = exclude_agents or []
        message_ids = []
        
        for agent_id in self.connected_agents.keys():
            if agent_id not in exclude:
                msg_id = await self.send_message(
                    receiver_agent=agent_id,
                    method=method,
                    params=params
                )
                message_ids.append(msg_id)
        
        return message_ids
    
    async def send_task(
        self,
        receiver_agent: str,
        task: A2ATask,
        callback: Optional[Callable] = None
    ) -> str:
        """
        发送任务到其他代理
        
        Args:
            receiver_agent: 接收方代理ID
            task: 任务对象
            callback: 结果回调函数
            
        Returns:
            消息ID
        """
        return await self.send_message(
            receiver_agent=receiver_agent,
            method="task_request",
            params=task.to_dict(),
            task_id=task.task_id,
            callback=callback
        )
    
    async def request_task_execution(
        self,
        agent_id: str,
        task_type: str,
        input_data: Dict[str, Any],
        priority: int = 5,
        dependencies: Optional[List[str]] = None
    ) -> A2ATask:
        """
        请求其他代理执行任务
        
        Args:
            agent_id: 目标代理ID
            task_type: 任务类型
            input_data: 输入数据
            priority: 优先级
            dependencies: 依赖任务ID列表
            
        Returns:
            创建的任务对象
        """
        task = A2ATask(
            task_type=task_type,
            input_data=input_data,
            priority=priority,
            dependencies=dependencies or []
        )
        
        await self.send_task(agent_id, task)
        
        return task
    
    async def _process_outgoing_messages(self):
        """处理发送消息队列"""
        while True:
            try:
                message = await self._outgoing_messages.get()
                
                # 模拟消息发送
                receiver = message.receiver_agent
                
                if receiver in self.connected_agents:
                    # 消息发送到已连接的代理
                    print(f"[{self.local_agent_id}] → [{receiver}] {message.payload.get('method')}")
                    
                    # 模拟接收方响应（实际环境中需要通过网络发送）
                    await self._simulate_response(message)
                else:
                    print(f"Agent {receiver} not connected")
                    
            except Exception as e:
                print(f"Error processing outgoing message: {e}")
    
    async def _simulate_response(self, message: A2AMessage):
        """
        模拟消息响应（用于测试）
        
        Args:
            message: 原始消息
        """
        try:
            method = message.payload.get("method")
            
            # 根据方法名生成模拟响应
            if method == "task_request":
                # 模拟任务执行结果
                task_data = message.payload.get("params", {})
                task = A2ATask.from_dict(task_data)
                
                result = {
                    "status": "completed",
                    "task_id": task.task_id,
                    "output_data": {
                        "message": f"Task {task.task_type} executed by {message.receiver_agent}",
                        "result": f"Mock result for {task.task_type}"
                    }
                }
                
            elif method == "web_search":
                result = {
                    "status": "completed",
                    "results": [
                        {"title": "Mock Result 1", "url": "https://example.com/1"},
                        {"title": "Mock Result 2", "url": "https://example.com/2"}
                    ]
                }
            
            elif method == "code_generation":
                result = {
                    "status": "completed",
                    "code": "# Generated code\nprint('Hello World')",
                    "language": "python"
                }
            
            else:
                result = {
                    "status": "completed",
                    "message": f"Method {method} executed successfully"
                }
            
            # 创建响应消息
            response = A2AProtocol.create_response(
                sender_agent=message.receiver_agent,
                receiver_agent=message.sender_agent,
                request_id=message.msg_id,
                result=result,
                task_id=message.payload.get("task_id")
            )
            
            # 处理响应
            await self._handle_response(response)
            
        except Exception as e:
            # 发送错误响应
            error_response = A2AProtocol.create_error(
                sender_agent=message.receiver_agent,
                receiver_agent=message.sender_agent,
                request_id=message.msg_id,
                error_code=-32603,
                error_message=str(e)
            )
            await self._handle_response(error_response)
    
    async def _handle_response(self, response: A2AMessage):
        """
        处理接收到的响应
        
        Args:
            response: 响应消息
        """
        request_id = response.payload.get("request_id")
        
        # 检查是否有回调
        if request_id in self._task_callbacks:
            callback = self._task_callbacks.pop(request_id)
            if response.message_type.value == "error":
                await callback(response.payload.get("error"))
            else:
                await callback(response.payload.get("result"))
        
        # 记录消息历史
        self.message_history.append({
            "msg_id": response.msg_id,
            "direction": "incoming",
            "method": "response",
            "sender": response.sender_agent,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_message_history(self, direction: Optional[str] = None) -> List[Dict]:
        """
        获取消息历史
        
        Args:
            direction: 过滤方向（incoming/outgoing）
            
        Returns:
            消息历史列表
        """
        if direction:
            return [msg for msg in self.message_history if msg["direction"] == direction]
        return self.message_history
    
    def clear_message_history(self):
        """清空消息历史"""
        self.message_history.clear()
