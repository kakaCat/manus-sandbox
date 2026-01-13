#!/usr/bin/env python3
"""
A2A协议示例程序

演示如何使用A2A协议实现代理间的通信和协作

运行方式:
    python examples/a2a_example.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.agent_implementations import ResearchAgent, CodingAgent, WriterAgent
from agents.base_agent import BaseAgent
from services.agent_communicator import AgentCommunicator
from services.agent_coordinator import AgentCoordinator
from protocols.a2a_protocol import A2AMessage, A2ATask, TaskStatus, A2AProtocol


async def demo_basic_messaging():
    """演示基本消息传递"""
    print("\n" + "="*60)
    print("Demo 1: Basic Message Passing")
    print("="*60)
    
    # 创建两个代理
    agent_a = ResearchAgent("agent_a")
    agent_b = CodingAgent("agent_b")
    
    # 创建通信器
    comm_a = AgentCommunicator(agent_a.agent_id)
    comm_b = AgentCommunicator(agent_b.agent_id)
    
    # 建立连接
    await comm_a.connect_to_agent(agent_b.agent_id, agent_b.agent_info)
    await comm_b.connect_to_agent(agent_a.agent_id, agent_a.agent_info)
    
    # 发送消息
    msg_id = await comm_a.send_message(
        receiver_agent=agent_b.agent_id,
        method="code_review",
        params={"code": "def hello(): print('world')"}
    )
    
    print(f"Message sent: {msg_id}")
    
    # 发送任务
    task = A2ATask(
        task_type="code_generation",
        input_data={
            "language": "python",
            "requirements": "Create a function to calculate fibonacci"
        }
    )
    
    task_msg_id = await comm_a.send_task(agent_b.agent_id, task)
    print(f"Task sent: {task_msg_id}")
    
    # 等待消息处理
    await asyncio.sleep(1)
    
    # 查看消息历史
    history = comm_a.get_message_history()
    print(f"Message history count: {len(history)}")
    
    print("\n✓ Basic messaging demo completed\n")


async def demo_single_agent_task():
    """演示单个代理执行任务"""
    print("\n" + "="*60)
    print("Demo 2: Single Agent Task Execution")
    print("="*60)
    
    # 创建代理
    research_agent = ResearchAgent("researcher")
    
    # 启动代理
    await research_agent.start()
    
    # 创建并执行任务
    task = A2ATask(
        task_type="web_search",
        input_data={
            "query": "A2A protocol agent-to-agent communication",
            "max_results": 3
        }
    )
    
    print(f"Executing task: {task.task_type}")
    print(f"Input: {task.input_data}")
    
    # 执行任务
    result = await research_agent.execute_task(task)
    
    print(f"\nResult:")
    print(f"  Query: {result['query']}")
    print(f"  Total results: {result['total_results']}")
    print(f"  Search engine: {result['search_engine']}")
    
    # 创建分析任务
    analysis_task = A2ATask(
        task_type="data_analysis",
        input_data={
            "data": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            "analysis_type": "statistical"
        }
    )
    
    print(f"\nExecuting analysis task: {analysis_task.task_type}")
    analysis_result = await research_agent.execute_task(analysis_task)
    
    print(f"\nAnalysis Result:")
    print(f"  Mean: {analysis_result['mean']}")
    print(f"  Median: {analysis_result['median']}")
    print(f"  Std Dev: {analysis_result['stdev']:.2f}")
    
    # 停止代理
    await research_agent.stop()
    
    print("\n✓ Single agent task demo completed\n")


async def demo_multi_agent_collaboration():
    """演示多代理协作"""
    print("\n" + "="*60)
    print("Demo 3: Multi-Agent Collaboration")
    print("="*60)
    
    # 创建多个代理
    research_agent = ResearchAgent("researcher")
    coding_agent = CodingAgent("coder")
    writer_agent = WriterAgent("writer")
    
    # 启动所有代理
    await research_agent.start()
    await coding_agent.start()
    await writer_agent.start()
    
    # 创建协调器
    coordinator = AgentCoordinator("main_coordinator")
    
    # 注册代理
    coordinator.register_agent("researcher", research_agent)
    coordinator.register_agent("coder", coding_agent)
    coordinator.register_agent("writer", writer_agent)
    
    print("\nRegistered agents:")
    for agent in coordinator.get_registered_agents():
        print(f"  - {agent['name']}: {agent['agent_name']} ({agent['capabilities']})")
    
    # 执行工作流
    workflow_config = {
        "steps": [
            {
                "agent": "researcher",
                "task_type": "web_search",
                "params": {
                    "query": "best practices for REST API design",
                    "max_results": 5
                }
            },
            {
                "agent": "coder",
                "task_type": "code_generation",
                "params": {
                    "language": "python",
                    "requirements": "Create a REST API for user management"
                },
                "output_key": "generated_code"
            },
            {
                "agent": "writer",
                "task_type": "technical_writing",
                "params": {
                    "topic": "REST API Design Guidelines",
                    "audience": "developers"
                }
            }
        ]
    }
    
    # 定义进度回调
    def progress_callback(current: int, total: int, result: dict):
        status = "✓" if result["status"] == "completed" else "✗"
        print(f"  [{status}] Step {current}/{total}: {result.get('data', {}).get('language', 'N/A') if isinstance(result.get('data'), dict) else 'N/A'}")
    
    # 执行工作流
    result = await coordinator.execute_workflow(
        workflow_id="api_development_workflow",
        workflow_config=workflow_config,
        progress_callback=progress_callback
    )
    
    print(f"\nWorkflow Summary:")
    print(f"  Status: {result['status']}")
    print(f"  Duration: {result['duration_seconds']:.2f}s")
    print(f"  Completed: {result['completed_steps']}/{result['total_steps']}")
    
    # 停止所有代理
    await research_agent.stop()
    await coding_agent.stop()
    await writer_agent.stop()
    
    print("\n✓ Multi-agent collaboration demo completed\n")


async def demo_parallel_tasks():
    """演示并行任务执行"""
    print("\n" + "="*60)
    print("Demo 4: Parallel Task Execution")
    print("="*60)
    
    # 创建代理
    research_agent = ResearchAgent("parallel_researcher")
    coding_agent = CodingAgent("parallel_coder")
    
    # 启动代理
    await research_agent.start()
    await coding_agent.start()
    
    # 创建协调器
    coordinator = AgentCoordinator("parallel_coordinator")
    coordinator.register_agent("researcher", research_agent)
    coordinator.register_agent("coder", coding_agent)
    
    # 配置并行执行
    coordinator.config["parallel_execution"] = True
    
    # 并行任务
    tasks = [
        {
            "agent": "researcher",
            "task_type": "data_analysis",
            "params": {
                "data": [1, 2, 3, 4, 5],
                "analysis_type": "basic"
            },
            "step_id": "analysis_1"
        },
        {
            "agent": "researcher",
            "task_type": "data_analysis",
            "params": {
                "data": [10, 20, 30, 40, 50],
                "analysis_type": "statistical"
            },
            "step_id": "analysis_2"
        },
        {
            "agent": "coder",
            "task_type": "code_generation",
            "params": {
                "language": "python",
                "requirements": "Create a utility function"
            },
            "step_id": "code_gen_1"
        },
        {
            "agent": "coder",
            "task_type": "code_review",
            "params": {
                "code": "# Sample code\nprint('test')",
                "language": "python"
            },
            "step_id": "code_review_1"
        }
    ]
    
    print("\nExecuting 4 tasks in parallel...")
    
    # 并行执行
    start_time = asyncio.get_event_loop().time()
    results = await coordinator.execute_parallel_tasks(tasks)
    duration = asyncio.get_event_loop().time() - start_time
    
    print(f"\nParallel execution completed in {duration:.2f}s")
    print(f"Tasks completed: {len(results)}")
    
    for i, result in enumerate(results):
        status = "✓" if result["status"] == "completed" else "✗"
        print(f"  [{status}] Task {i+1}: {result.get('data', {}).get('analysis_type', result.get('data', {}).get('language', 'N/A')) if isinstance(result.get('data'), dict) else 'completed'}")
    
    # 停止代理
    await research_agent.stop()
    await coding_agent.stop()
    
    print("\n✓ Parallel tasks demo completed\n")


async def demo_complex_workflow():
    """演示复杂工作流"""
    print("\n" + "="*60)
    print("Demo 5: Complex Research & Development Workflow")
    print("="*60)
    
    # 创建所有代理
    research_agent = ResearchAgent("senior_researcher")
    coding_agent = "senior_coder"
    coding_agent_instance = CodingAgent(coding_agent)
    writer_agent = "tech_writer"
    writer_agent_instance = WriterAgent(writer_agent)
    
    # 启动代理
    await research_agent.start()
    await coding_agent_instance.start()
    await writer_agent_instance.start()
    
    # 创建协调器
    coordinator = AgentCoordinator("workflow_lead")
    coordinator.register_agent("researcher", research_agent)
    coordinator.register_agent("coder", coding_agent_instance)
    coordinator.register_agent("writer", writer_agent_instance)
    
    # 复杂工作流：市场调研 → 产品开发 → 文档撰写
    complex_workflow = {
        "steps": [
            {
                "agent": "researcher",
                "task_type": "trend_analysis",
                "params": {
                    "data_points": [100, 120, 140, 160, 180, 200, 220, 240],
                    "time_range": "30d"
                },
                "priority": 10
            },
            {
                "agent": "researcher",
                "task_type": "web_search",
                "params": {
                    "query": "latest trends in AI-powered development tools",
                    "max_results": 5
                }
            },
            {
                "agent": "researcher",
                "task_type": "data_analysis",
                "params": {
                    "data": [25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
                    "analysis_type": "statistical"
                },
                "dependencies": []  # 可以并行
            },
            {
                "agent": "coder",
                "task_type": "code_generation",
                "params": {
                    "language": "python",
                    "requirements": "Create an AI-powered code analysis tool with REST API"
                },
                "priority": 8
            },
            {
                "agent": "writer",
                "task_type": "technical_writing",
                "params": {
                    "topic": "AI Code Analysis Tool - Technical Documentation",
                    "audience": "developers"
                },
                "dependencies": ["code_gen_1_step_3"]  # 依赖于编码步骤
            },
            {
                "agent": "writer",
                "task_type": "summarization",
                "params": {
                    "content": "This is a comprehensive technical documentation for an AI-powered code analysis tool. The tool uses machine learning algorithms to analyze code quality, detect potential bugs, and suggest improvements. It supports multiple programming languages and can be integrated into existing CI/CD pipelines.",
                    "length": "short"
                }
            }
        ]
    }
    
    print("\nStarting complex workflow with 6 steps...")
    
    # 执行工作流
    result = await coordinator.execute_workflow(
        workflow_id="complex_rd_workflow",
        workflow_config=complex_workflow,
        progress_callback=lambda current, total, res: print(
            f"  Progress: {current}/{total} - Status: {res['status']}"
        )
    )
    
    print(f"\n{'='*60}")
    print("Workflow Results:")
    print(f"{'='*60}")
    print(f"Status: {result['status']}")
    print(f"Duration: {result['duration_seconds']:.2f}s")
    print(f"\nStep Results:")
    
    for step_result in result["results"]:
        status_icon = "✓" if step_result["status"] == "completed" else "✗"
        print(f"  [{status_icon}] {step_result['agent']}: {step_result['task_type']}")
        if step_result.get("duration"):
            print(f"      Duration: {step_result['duration']:.2f}s")
    
    # 停止所有代理
    await research_agent.stop()
    await coding_agent_instance.stop()
    await writer_agent_instance.stop()
    
    print("\n✓ Complex workflow demo completed\n")


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("A2A Protocol Demonstration")
    print("Agent-to-Agent Communication Framework")
    print("="*60)
    
    # 运行所有演示
    await demo_basic_messaging()
    await demo_single_agent_task()
    await demo_multi_agent_collaboration()
    await demo_parallel_tasks()
    await demo_complex_workflow()
    
    print("="*60)
    print("All demonstrations completed!")
    print("="*60)
    print("\nA2A Protocol Features Demonstrated:")
    print("  ✓ Message passing between agents")
    print("  ✓ Task creation and execution")
    print("  ✓ Multi-agent collaboration")
    print("  ✓ Parallel task execution")
    print("  ✓ Complex workflow orchestration")
    print("  ✓ Task dependency management")
    print("  ✓ Progress tracking and callbacks")
    print()


if __name__ == "__main__":
    asyncio.run(main())
