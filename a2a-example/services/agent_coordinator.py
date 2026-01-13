"""
A2A代理协调器

负责协调多个代理之间的协作：
- 任务分解和分发
- 结果聚合
- 依赖管理
- 流程编排
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
import asyncio
import json

from protocols.a2a_protocol import A2AMessage, A2ATask, TaskStatus, A2AProtocol
from services.agent_communicator import AgentCommunicator


class TaskStatusTracker:
    """
    任务状态跟踪器
    
    Attributes:
        task_id: 任务ID
        status: 当前状态
        assigned_agent: 分配的代理
        created_at: 创建时间
        updated_at: 更新时间
        result: 任务结果
        subtasks: 子任务列表
    """
    
    def __init__(self, task: A2ATask):
        self.task_id = task.task_id
        self.task_type = task.task_type
        self.status = task.status
        self.assigned_agent = task.assigned_agent
        self.created_at = task.created_at
        self.updated_at = task.updated_at
        self.result = None
        self.subtasks: List['TaskStatusTracker'] = []
        self.error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status.value if hasattr(self.status, 'value') else self.status,
            "assigned_agent": self.assigned_agent,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "result": self.result,
            "subtasks": [st.to_dict() for st in self.subtasks],
            "error": self.error
        }


class AgentCoordinator:
    """
    A2A代理协调器
    
    负责协调多个代理完成复杂任务：
    - 任务分解
    - 任务分发
    - 结果聚合
    - 流程控制
    
    Example:
        coordinator = AgentCoordinator("coordinator_agent")
        
        # 注册代理
        coordinator.register_agent("researcher", research_agent)
        coordinator.register_agent("coder", coding_agent)
        coordinator.register_agent("writer", writer_agent)
        
        # 执行协作任务
        result = await coordinator.execute_workflow(
            "multi_agent_task",
            {
                "steps": [
                    {"agent": "researcher", "task_type": "web_search", "params": {...}},
                    {"agent": "coder", "task_type": "code_generation", "params": {...}},
                    {"agent": "writer", "task_type": "technical_writing", "params": {...}}
                ]
            }
        )
    """
    
    def __init__(self, coordinator_id: str = "coordinator"):
        """
        初始化协调器
        
        Args:
            coordinator_id: 协调器ID
        """
        self.coordinator_id = coordinator_id
        self.agents: Dict[str, Any] = {}
        self.agent_communicators: Dict[str, AgentCommunicator] = {}
        self.task_status: Dict[str, TaskStatusTracker] = {}
        self.workflow_results: Dict[str, Any] = {}
        
        # 协作配置
        self.config = {
            "timeout": 300,  # 任务超时时间（秒）
            "retry_count": 3,  # 重试次数
            "parallel_execution": True  # 是否并行执行
        }
    
    def register_agent(self, agent_name: str, agent_instance: Any):
        """
        注册代理
        
        Args:
            agent_name: 代理名称（标识符）
            agent_instance: 代理实例
        """
        self.agents[agent_name] = agent_instance
        self.agent_communicators[agent_name] = AgentCommunicator(agent_instance.agent_id)
        
        print(f"Registered agent: {agent_name} ({agent_instance.agent_id})")
    
    def get_registered_agents(self) -> List[Dict[str, Any]]:
        """获取已注册的代理列表"""
        return [
            {
                "name": name,
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "capabilities": agent.capabilities,
                "status": agent.status
            }
            for name, agent in self.agents.items()
        ]
    
    async def execute_workflow(
        self,
        workflow_id: str,
        workflow_config: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        执行工作流
        
        Args:
            workflow_id: 工作流ID
            workflow_config: 工作流配置
            progress_callback: 进度回调函数
            
        Returns:
            工作流执行结果
        """
        print(f"\n{'='*60}")
        print(f"Starting workflow: {workflow_id}")
        print(f"{'='*60}")
        
        start_time = datetime.now()
        steps = workflow_config.get("steps", [])
        results = []
        
        # 初始化任务状态跟踪
        for i, step in enumerate(steps):
            step_id = f"{workflow_id}_step_{i}"
            task = A2ATask(
                task_id=step_id,
                task_type=step.get("task_type", ""),
                input_data=step.get("params", {}),
                priority=step.get("priority", 5),
                dependencies=step.get("dependencies", [])
            )
            self.task_status[step_id] = TaskStatusTracker(task)
        
        # 执行工作流步骤
        for i, step in enumerate(steps):
            step_id = f"{workflow_id}_step_{i}"
            agent_name = step.get("agent")
            task_type = step.get("task_type", "")
            params = step.get("params", {})
            
            if agent_name not in self.agents:
                error_msg = f"Agent not found: {agent_name}"
                print(f"Error: {error_msg}")
                results.append({
                    "step": i,
                    "agent": agent_name,
                    "status": "failed",
                    "error": error_msg
                })
                continue
            
            print(f"\n[Step {i+1}/{len(steps)}] {agent_name}: {task_type}")
            
            # 检查依赖
            dependencies = step.get("dependencies", [])
            if dependencies:
                await self._wait_for_dependencies(dependencies)
            
            # 执行步骤
            step_result = await self._execute_step(
                agent_name=agent_name,
                task_type=task_type,
                params=params,
                step_id=step_id
            )
            
            results.append({
                "step": i,
                "agent": agent_name,
                "task_type": task_type,
                "status": step_result["status"],
                "result": step_result.get("data"),
                "duration": step_result.get("duration", 0)
            })
            
            # 更新进度
            if progress_callback:
                progress_callback(i + 1, len(steps), step_result)
            
            # 传递结果到下一步（如果配置了结果传递）
            if step_result["status"] == "completed" and "output_key" in step:
                output_key = step["output_key"]
                for next_step in steps[i+1:]:
                    if "params" in next_step and output_key in step_result.get("data", {}):
                        next_step["params"][output_key] = step_result["data"][output_key]
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 汇总结果
        summary = {
            "workflow_id": workflow_id,
            "status": "completed" if all(r["status"] == "completed" for r in results) else "partial",
            "total_steps": len(steps),
            "completed_steps": sum(1 for r in results if r["status"] == "completed"),
            "failed_steps": sum(1 for r in results if r["status"] == "failed"),
            "duration_seconds": duration,
            "results": results,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
        self.workflow_results[workflow_id] = summary
        
        print(f"\n{'='*60}")
        print(f"Workflow completed: {workflow_id}")
        print(f"Duration: {duration:.2f}s")
        print(f"Steps: {summary['completed_steps']}/{summary['total_steps']}")
        print(f"{'='*60}\n")
        
        return summary
    
    async def _execute_step(
        self,
        agent_name: str,
        task_type: str,
        params: Dict[str, Any],
        step_id: str
    ) -> Dict[str, Any]:
        """
        执行单个步骤
        
        Args:
            agent_name: 代理名称
            task_type: 任务类型
            params: 任务参数
            step_id: 步骤ID
            
        Returns:
            执行结果
        """
        import time
        start_time = time.time()
        
        agent = self.agents[agent_name]
        communicator = self.agent_communicators[agent_name]
        
        # 创建任务
        task = A2ATask(
            task_id=step_id,
            task_type=task_type,
            input_data=params,
            assigned_agent=agent.agent_id
        )
        
        # 更新状态
        self.task_status[step_id].status = TaskStatus.IN_PROGRESS
        self.task_status[step_id].assigned_agent = agent.agent_id
        
        try:
            # 获取代理能力
            if task_type in agent.capabilities:
                # 本地执行（如果是同一个进程中的代理）
                result = await agent.execute_task(task)
                status = "completed"
            else:
                # 远程执行（通过通信器）
                result = await self._send_task_to_agent(
                    communicator=communicator,
                    agent_name=agent_name,
                    task=task
                )
                status = "completed"
            
            duration = time.time() - start_time
            
            # 更新状态
            self.task_status[step_id].status = TaskStatus.COMPLETED
            self.task_status[step_id].result = result
            self.task_status[step_id].updated_at = datetime.now()
            
            print(f"  ✓ {task_type} completed in {duration:.2f}s")
            
            return {
                "status": status,
                "data": result,
                "duration": duration
            }
            
        except Exception as e:
            duration = time.time() - start_time
            
            # 更新状态
            self.task_status[step_id].status = TaskStatus.FAILED
            self.task_status[step_id].error = str(e)
            self.task_status[step_id].updated_at = datetime.now()
            
            print(f"  ✗ {task_type} failed: {e}")
            
            return {
                "status": "failed",
                "error": str(e),
                "duration": duration
            }
    
    async def _send_task_to_agent(
        self,
        communicator: AgentCommunicator,
        agent_name: str,
        task: A2ATask
    ) -> Dict[str, Any]:
        """
        发送任务到代理
        
        Args:
            communicator: 通信器
            agent_name: 代理名称
            task: 任务对象
            
        Returns:
            任务执行结果
        """
        # 创建完成future
        result_future = asyncio.Future()
        
        # 发送任务
        msg_id = await communicator.send_task(
            receiver_agent=agent_name,
            task=task,
            callback=lambda result: result_future.set_result(result)
        )
        
        # 等待结果
        try:
            result = await asyncio.wait_for(
                result_future,
                timeout=self.config["timeout"]
            )
            return result
        except asyncio.TimeoutError:
            raise Exception(f"Task timeout after {self.config['timeout']}s")
    
    async def _wait_for_dependencies(self, dependency_ids: List[str]):
        """
        等待依赖任务完成
        
        Args:
            dependency_ids: 依赖的任务ID列表
        """
        for dep_id in dependency_ids:
            if dep_id in self.task_status:
                tracker = self.task_status[dep_id]
                while tracker.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    await asyncio.sleep(0.1)
                
                if tracker.status == TaskStatus.FAILED:
                    raise Exception(f"Dependency {dep_id} failed")
    
    async def execute_parallel_tasks(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        并行执行多个任务
        
        Args:
            tasks: 任务配置列表
            
        Returns:
            执行结果列表
        """
        if not self.config["parallel_execution"]:
            # 顺序执行
            results = []
            for task in tasks:
                result = await self._execute_step(
                    task["agent"],
                    task["task_type"],
                    task.get("params", {}),
                    task.get("step_id", f"task_{len(results)}")
                )
                results.append(result)
            return results
        
        # 初始化并行任务状态
        for index, task in enumerate(tasks):
            step_id = task.get("step_id", f"parallel_task_{index}")
            new_task = A2ATask(
                task_id=step_id,
                task_type=task.get("task_type", ""),
                input_data=task.get("params", {}),
                priority=task.get("priority", 5),
                dependencies=task.get("dependencies", [])
            )
            self.task_status[step_id] = TaskStatusTracker(new_task)
        
        # 并行执行
        async def execute_and_collect(task: Dict[str, Any], index: int) -> Dict[str, Any]:
            step_id = task.get("step_id", f"parallel_task_{index}")
            return await self._execute_step(
                task["agent"],
                task["task_type"],
                task.get("params", {}),
                step_id
            )
        
        tasks_with_index = [(task, i) for i, task in enumerate(tasks)]
        results = await asyncio.gather(
            *[execute_and_collect(task, i) for task, i in tasks_with_index]
        )
        
        return results
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        获取工作流状态
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            工作流状态
        """
        if workflow_id in self.workflow_results:
            return self.workflow_results[workflow_id]
        
        # 检查进行中的任务
        if workflow_id in self.task_status:
            tracker = self.task_status[workflow_id]
            return {
                "workflow_id": workflow_id,
                "status": tracker.status.value,
                "task": tracker.to_dict()
            }
        
        return None
    
    def get_all_task_status(self) -> List[Dict[str, Any]]:
        """获取所有任务状态"""
        return [tracker.to_dict() for tracker in self.task_status.values()]
