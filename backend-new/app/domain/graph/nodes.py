from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate


def create_planner_node(llm, sandbox):
    async def planner(state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state["messages"]
        current_step = state.get("current_step", 0)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a planning agent. Break down the user's task into a clear step-by-step plan. "
                      "Return the plan as a numbered list, one step per line."),
            ("human", "{input}")
        ])

        last_message = messages[-1].content if messages else ""

        response = await llm.ainvoke(prompt.format_messages(input=last_message))

        plan = [line.strip() for line in response.content.strip().split('\n') if line.strip()]

        return {
            "plan": plan,
            "current_step": current_step
        }

    return planner


def create_executor_node(llm, sandbox, tools):
    async def executor(state: Dict[str, Any]) -> Dict[str, Any]:
        from langchain.agents import create_tool_calling_agent, AgentExecutor

        # 创建工具调用代理的提示
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a task execution agent. Use the available tools to complete the user's task.\n\n"
                       "Available tools: " + ", ".join([tool.name for tool in tools]) + "\n\n"
                       "Think step by step and use the appropriate tool. Be concise in your responses."),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        # 创建工具调用代理
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,  # 减少日志输出
            handle_parsing_errors=True,
            max_iterations=5,  # 减少迭代次数
            max_execution_time=30.0  # 30秒超时
        )

        # 获取用户输入
        messages = state["messages"]
        user_message = messages[-1].content if messages else ""

        try:
            # 执行代理
            result = await agent_executor.ainvoke({
                "input": user_message,
                "chat_history": messages[:-1] if len(messages) > 1 else []
            })

            output = result.get("output", "Task completed successfully")

            return {
                "results": [result],
                "messages": messages + [AIMessage(content=output)],
                "current_step": state.get("current_step", 0) + 1
            }

        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            return {
                "results": [{"error": error_msg}],
                "messages": messages + [AIMessage(content=error_msg)],
                "current_step": state.get("current_step", 0) + 1
            }

    return executor


def create_reflector_node(llm, sandbox):
    async def reflector(state: Dict[str, Any]) -> Dict[str, Any]:
        current_step = state.get("current_step", 0)
        results = state.get("results", [])

        # 检查最大迭代次数
        if current_step >= 10:
            return {
                "is_complete": True,
                "final_message": "Maximum iterations reached. Task may be incomplete.",
                "current_step": current_step
            }

        # 获取最后的结果
        last_result = results[-1] if results else {}
        messages = state.get("messages", [])
        last_message = messages[-1].content if messages else ""

        # 构建反思提示
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a task completion evaluator. Analyze if the user's task has been successfully completed.\n\n"
                       "Consider:\n"
                       "- Has the core objective been achieved?\n"
                       "- Are there any remaining steps?\n"
                       "- Is the result satisfactory?\n\n"
                       "Respond with only: 'COMPLETE' if done, or 'CONTINUE: [brief reason]' if more work needed."),
            ("human", "Task: {task}\n\nLast Result: {result}\n\nIs this task complete?")
        ])

        try:
            response = await llm.ainvoke(
                prompt.format_messages(
                    task=last_message,
                    result=str(last_result)
                )
            )

            response_text = response.content.strip()
            is_complete = response_text.upper().startswith("COMPLETE")

            return {
                "is_complete": is_complete,
                "final_message": response_text if is_complete else f"Continuing: {response_text}",
                "current_step": current_step
            }

        except Exception as e:
            # LLM调用失败时，默认继续执行
            return {
                "is_complete": False,
                "final_message": f"Evaluation failed: {str(e)}. Continuing execution.",
                "current_step": current_step
            }

    return reflector
