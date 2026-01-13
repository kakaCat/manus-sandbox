"""
A2A代理基类

提供代理的基础功能：
- 消息处理
- 任务执行
- 状态管理
- 心跳检测
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
import asyncio
import logging

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from protocols.a2a_protocol import A2AMessage, A2ATask, TaskStatus


class BaseAgent(ABC):
    """
    A2A代理基类
    
    Attributes:
        agent_id: 代理唯一标识
        agent_name: 代理名称
        capabilities: 代理能力列表
        status: 代理状态
        message_queue: 消息队列
        task_queue: 任务队列
        logger: 日志记录器
    """
    
    def __init__(self, agent_id: str, agent_name: str):
        """
        初始化代理
        
        Args:
            agent_id: 代理唯一标识
            agent_name: 代理名称
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.capabilities: List[str] = []
        self.status = "offline"
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.logger = logging.getLogger(f"Agent[{agent_id}]")
        
        # 任务存储
        self.tasks: Dict[str, A2ATask] = {}
        
        # 消息处理映射
        self._message_handlers: Dict[str, Callable] = {}
        
        # 注册默认处理器
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """注册默认消息处理器"""
        self._message_handlers["task_request"] = self._handle_task_request
        self._message_handlers["task_result"] = self._handle_task_result
        self._message_handlers["task_cancel"] = self._handle_task_cancel
        self._message_handlers["heartbeat"] = self._handle_heartbeat
        self._message_handlers["status_update"] = self._handle_status_update
    
    @property
    def agent_info(self) -> Dict[str, Any]:
        """获取代理信息"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "capabilities": self.capabilities,
            "status": self.status,
            "version": "1.0.0"
        }
    
    def add_capability(self, capability: str):
        """添加代理能力"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.logger.info(f"Added capability: {capability}")
    
    def remove_capability(self, capability: str):
        """移除代理能力"""
        if capability in self.capabilities:
            self.capabilities.remove(capability)
    
    async def start(self):
        """启动代理"""
        self.status = "running"
        self.logger.info(f"Agent {self.agent_name} started")
        
        # 启动消息处理循环
        asyncio.create_task(self._message_processing_loop())
        
        # 启动任务处理循环
        asyncio.create_task(self._task_processing_loop())
    
    async def stop(self):
        """停止代理"""
        self.status = "stopped"
        self.logger.info(f"Agent {self.agent_name} stopped")
    
    async def _message_processing_loop(self):
        """消息处理循环"""
        while self.status == "running":
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                await self._process_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
    
    async def _task_processing_loop(self):
        """任务处理循环"""
        while self.status == "running":
            try:
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                await self._execute_task(task)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing task: {e}")
    
    async def _process_message(self, message: A2AMessage):
        """
        处理接收到的消息
        
        Args:
            message: 接收到的A2A消息
        """
        self.logger.info(f"Processing message from {message.sender_agent}")
        
        # 根据消息类型分发处理
        payload = message.payload
        msg_type = payload.get("method", "") if "method" in payload else ""
        
        handler = self._message_handlers.get(msg_type)
        if handler:
            await handler(message)
        else:
            self.logger.warning(f"No handler for message type: {msg_type}")
    
    async def _handle_task_request(self, message: A2AMessage):
        """
        处理任务请求
        
        Args:
            message: 任务请求消息
        """
        task_data = message.payload.get("params", {})
        task = A2ATask.from_dict(task_data)
        
        self.tasks[task.task_id] = task
        task.assigned_agent = self.agent_id
        task.status = TaskStatus.PENDING
        
        await self.task_queue.put(task)
        
        self.logger.info(f"Accepted task: {task.task_id}")
    
    async def _handle_task_result(self, message: A2AMessage):
        """
        处理任务结果
        
        Args:
            message: 任务结果消息
        """
        task_id = message.payload.get("task_id")
        result = message.payload.get("result")
        
        if task_id in self.tasks:
            self.tasks[task_id].output_data = result
            self.tasks[task_id].status = TaskStatus.COMPLETED
            self.tasks[task_id].updated_at = datetime.now()
            
            self.logger.info(f"Task completed: {task_id}")
    
    async def _handle_task_cancel(self, message: A2AMessage):
        """
        处理任务取消
        
        Args:
            message: 任务取消消息
        """
        task_id = message.payload.get("task_id")
        
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.CANCELLED
            self.logger.info(f"Task cancelled: {task_id}")
    
    async def _handle_heartbeat(self, message: A2AMessage):
        """处理心跳消息"""
        self.logger.debug(f"Heartbeat received from {message.sender_agent}")
    
    async def _handle_status_update(self, message: A2AMessage):
        """处理状态更新消息"""
        new_status = message.payload.get("status", "unknown")
        self.logger.info(f"Status update: {new_status}")
    
    @abstractmethod
    async def execute_task(self, task: A2ATask) -> Dict[str, Any]:
        """
        执行任务（子类必须实现）
        
        Args:
            task: 要执行的任务
            
        Returns:
            任务执行结果
        """
        pass
    
    async def _execute_task(self, task: A2ATask):
        """
        执行任务（内部方法）
        
        Args:
            task: 要执行的任务
        """
        try:
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.now()
            
            # 调用子类实现
            result = await self.execute_task(task)
            
            task.output_data = result
            task.status = TaskStatus.COMPLETED
            task.updated_at = datetime.now()
            
            self.logger.info(f"Task {task.task_id} executed successfully")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.output_data = {"error": str(e)}
            task.updated_at = datetime.now()
            
            self.logger.error(f"Task {task.task_id} failed: {e}")
    
    def register_message_handler(self, method: str, handler: Callable):
        """
        注册消息处理器
        
        Args:
            method: 消息方法名
            handler: 处理函数
        """
        self._message_handlers[method] = handler
        self.logger.info(f"Registered handler for method: {method}")
