"""
具体代理实现示例

包含以下示例代理：
1. ResearchAgent - 研究代理，负责信息收集和分析
2. CodingAgent - 编码代理，负责代码编写和审查
3. WriterAgent - 写作代理，负责文档撰写
"""

from typing import Any, Dict, List
import asyncio
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from .base_agent import BaseAgent
from protocols.a2a_protocol import A2AMessage, A2ATask, TaskStatus


class ResearchAgent(BaseAgent):
    """
    研究代理
    
    负责信息收集、数据分析、趋势研究等任务
    """
    
    def __init__(self, agent_id: str = "research_agent"):
        """
        初始化研究代理
        
        Args:
            agent_id: 代理ID
        """
        super().__init__(agent_id, "ResearchAgent")
        
        # 添加研究相关能力
        self.add_capability("web_search")
        self.add_capability("data_analysis")
        self.add_capability("report_generation")
        self.add_capability("trend_analysis")
    
    async def execute_task(self, task: A2ATask) -> Dict[str, Any]:
        """
        执行研究任务
        
        Args:
            task: 研究任务
            
        Returns:
            研究结果
        """
        task_type = task.task_type
        input_data = task.input_data
        
        if task_type == "web_search":
            return await self._web_search(input_data)
        elif task_type == "data_analysis":
            return await self._data_analysis(input_data)
        elif task_type == "report_generation":
            return await self._generate_report(input_data)
        elif task_type == "trend_analysis":
            return await self._trend_analysis(input_data)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _web_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        网络搜索
        
        Args:
            params: 搜索参数
            
        Returns:
            搜索结果
        """
        query = params.get("query", "")
        max_results = params.get("max_results", 5)
        
        # 模拟搜索结果
        await asyncio.sleep(0.5)  # 模拟搜索延迟
        
        results = []
        for i in range(max_results):
            results.append({
                "title": f"Search Result {i+1} for '{query}'",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"This is a sample search result for the query: {query}",
                "relevance_score": 0.9 - (i * 0.1)
            })
        
        return {
            "query": query,
            "total_results": max_results * 10,
            "results": results,
            "search_engine": "mock_search"
        }
    
    async def _data_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        数据分析
        
        Args:
            params: 分析参数
            
        Returns:
            分析结果
        """
        data = params.get("data", [])
        analysis_type = params.get("analysis_type", "basic")
        
        await asyncio.sleep(0.3)  # 模拟分析延迟
        
        if analysis_type == "basic":
            return {
                "analysis_type": "basic",
                "count": len(data),
                "sum": sum(data) if data else 0,
                "average": sum(data) / len(data) if data else 0,
                "min": min(data) if data else None,
                "max": max(data) if data else None
            }
        elif analysis_type == "statistical":
            import statistics
            return {
                "analysis_type": "statistical",
                "count": len(data),
                "mean": statistics.mean(data) if data else 0,
                "median": statistics.median(data) if data else 0,
                "stdev": statistics.stdev(data) if data else 0,
                "variance": statistics.variance(data) if data else 0
            }
        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}
    
    async def _generate_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成报告
        
        Args:
            params: 报告参数
            
        Returns:
            报告内容
        """
        title = params.get("title", "Research Report")
        sections = params.get("sections", [])
        data = params.get("data", {})
        
        await asyncio.sleep(0.4)  # 模拟报告生成
        
        report_content = f"# {title}\n\n"
        
        for section in sections:
            report_content += f"## {section['title']}\n\n{section['content']}\n\n"
        
        report_content += "\n## Summary\n\n"
        report_content += f"Total sections: {len(sections)}\n"
        report_content += f"Data points analyzed: {len(data)}\n"
        
        return {
            "title": title,
            "sections": len(sections),
            "content": report_content,
            "generated_at": "2024-01-01T00:00:00"
        }
    
    async def _trend_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        趋势分析
        
        Args:
            params: 分析参数
            
        Returns:
            趋势分析结果
        """
        data_points = params.get("data_points", [])
        time_range = params.get("time_range", "7d")
        
        await asyncio.sleep(0.3)  # 模拟分析
        
        # 模拟趋势分析结果
        if len(data_points) >= 2:
            first = data_points[0]
            last = data_points[-1]
            change = ((last - first) / first) * 100 if first != 0 else 0
            
            trend = "up" if change > 0 else "down" if change < 0 else "stable"
        else:
            trend = "unknown"
            change = 0
        
        return {
            "trend": trend,
            "change_percent": round(change, 2),
            "data_points_analyzed": len(data_points),
            "time_range": time_range,
            "forecast": f"Expected to continue {trend} in next period"
        }


class CodingAgent(BaseAgent):
    """
    编码代理
    
    负责代码编写、审查、调试和优化
    """
    
    def __init__(self, agent_id: str = "coding_agent"):
        """
        初始化编码代理
        
        Args:
            agent_id: 代理ID
        """
        super().__init__(agent_id, "CodingAgent")
        
        # 添加编码相关能力
        self.add_capability("code_generation")
        self.add_capability("code_review")
        self.add_capability("debugging")
        self.add_capability("refactoring")
        self.add_capability("documentation")
    
    async def execute_task(self, task: A2ATask) -> Dict[str, Any]:
        """
        执行编码任务
        
        Args:
            task: 编码任务
            
        Returns:
            编码结果
        """
        task_type = task.task_type
        input_data = task.input_data
        
        if task_type == "code_generation":
            return await self._generate_code(input_data)
        elif task_type == "code_review":
            return await self._review_code(input_data)
        elif task_type == "debugging":
            return await self._debug_code(input_data)
        elif task_type == "refactoring":
            return await self._refactor_code(input_data)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _generate_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成代码
        
        Args:
            params: 生成参数
            
        Returns:
            生成的代码
        """
        language = params.get("language", "python")
        requirements = params.get("requirements", "")
        style = params.get("style", "standard")
        
        await asyncio.sleep(0.5)  # 模拟代码生成
        
        # 生成示例代码
        code_templates = {
            "python": f'''"""
{requirements}
"""

def main():
    """Main function"""
    print("Hello, World!")
    
    # TODO: Implement requirements
    # {requirements}
    
    return True

if __name__ == "__main__":
    main()
''',
            "javascript": f'''/**
 * {requirements}
 */

function main() {{
    console.log("Hello, World!");
    
    // TODO: Implement requirements
    // {requirements}
    
    return true;
}}

module.exports = {{ main }};
''',
            "java": f'''/**
 * {requirements}
 */

public class Main {{
    public static void main(String[] args) {{
        System.out.println("Hello, World!");
        
        // TODO: Implement requirements
        // {requirements}
    }}
    
    public static boolean main() {{
        return true;
    }}
}}
'''
        }
        
        code = code_templates.get(language, f"# Language not supported: {language}")
        
        return {
            "language": language,
            "code": code,
            "style": style,
            "lines_of_code": len(code.split('\n')),
            "generated_with": "CodeAgent v1.0"
        }
    
    async def _review_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        审查代码
        
        Args:
            params: 审查参数
            
        Returns:
            审查结果
        """
        code = params.get("code", "")
        language = params.get("language", "python")
        
        await asyncio.sleep(0.4)  # 模拟代码审查
        
        issues = []
        suggestions = []
        
        # 模拟代码审查结果
        if "TODO" in code:
            issues.append({
                "type": "warning",
                "line": code.split("TODO")[0].count('\n') + 1,
                "message": "TODO comments found",
                "severity": "low"
            })
            suggestions.append("Complete TODO items before final submission")
        
        if "print(" in code and language == "python":
            issues.append({
                "type": "code_smell",
                "line": [i for i, line in enumerate(code.split('\n')) if "print(" in line][0] + 1,
                "message": "Debug print statements found",
                "severity": "medium"
            })
            suggestions.append("Remove debug print statements")
        
        # 计算代码质量分数
        base_score = 100
        base_score -= len(issues) * 10
        quality_score = max(0, base_score)
        
        return {
            "quality_score": quality_score,
            "issues_found": len(issues),
            "issues": issues,
            "suggestions": suggestions,
            "lines_analyzed": len(code.split('\n')),
            "language": language
        }
    
    async def _debug_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        调试代码
        
        Args:
            params: 调试参数
            
        Returns:
            调试结果
        """
        code = params.get("code", "")
        error = params.get("error", "")
        
        await asyncio.sleep(0.4)  # 模拟调试
        
        # 模拟调试结果
        bugs = []
        fixes = []
        
        if "undefined" in error.lower():
            bugs.append({
                "type": "ReferenceError",
                "description": "Variable is not defined",
                "suggested_fix": "Check variable name and scope"
            })
        
        if "syntax" in error.lower():
            bugs.append({
                "type": "SyntaxError",
                "description": "Invalid syntax",
                "suggested_fix": "Review code syntax"
            })
        
        return {
            "bugs_found": len(bugs),
            "bugs": bugs,
            "fixes": fixes,
            "error_analyzed": error,
            "debug_status": "completed" if len(bugs) == 0 else "needs_fixes"
        }
    
    async def _refactor_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        重构代码
        
        Args:
            params: 重构参数
            
        Returns:
            重构后的代码
        """
        code = params.get("code", "")
        refactoring_type = params.get("type", "readability")
        
        await asyncio.sleep(0.4)  # 模拟重构
        
        # 模拟重构结果
        refactored_code = code
        
        improvements = []
        
        if refactoring_type == "readability":
            # 添加空行改善可读性
            lines = code.split('\n')
            new_lines = []
            for i, line in enumerate(lines):
                new_lines.append(line)
                if i < len(lines) - 1 and line.strip() and lines[i+1].strip():
                    if not (line.strip().endswith(':') or lines[i+1].strip().startswith('#')):
                        new_lines.append('')
            refactored_code = '\n'.join(new_lines)
            improvements.append("Added spacing for readability")
        
        return {
            "refactoring_type": refactoring_type,
            "original_lines": len(code.split('\n')),
            "refactored_lines": len(refactored_code.split('\n')),
            "improvements": improvements,
            "refactored_code": refactored_code
        }


class WriterAgent(BaseAgent):
    """
    写作代理
    
    负责文档撰写、内容创作和编辑
    """
    
    def __init__(self, agent_id: str = "writer_agent"):
        """
        初始化写作代理
        
        Args:
            agent_id: 代理ID
        """
        super().__init__(agent_id, "WriterAgent")
        
        # 添加写作相关能力
        self.add_capability("technical_writing")
        self.add_capability("creative_writing")
        self.add_capability("editing")
        self.add_capability("translation")
        self.add_capability("summarization")
    
    async def execute_task(self, task: A2ATask) -> Dict[str, Any]:
        """
        执行写作任务
        
        Args:
            task: 写作任务
            
        Returns:
            写作结果
        """
        task_type = task.task_type
        input_data = task.input_data
        
        if task_type == "technical_writing":
            return await self._technical_write(input_data)
        elif task_type == "creative_writing":
            return await self._creative_write(input_data)
        elif task_type == "editing":
            return await self._edit_content(input_data)
        elif task_type == "summarization":
            return await self._summarize(input_data)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _technical_write(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        技术写作
        
        Args:
            params: 写作参数
            
        Returns:
            生成的文档
        """
        topic = params.get("topic", "")
        audience = params.get("audience", "developers")
        format_type = params.get("format", "markdown")
        
        await asyncio.sleep(0.5)  # 模拟写作
        
        content = f"# {topic}\n\n"
        content += f"## Overview\n\nThis document provides a comprehensive guide on {topic} for {audience}.\n\n"
        content += "## Introduction\n\n"
        content += f"{topic} is an important concept in modern software development.\n\n"
        content += "## Key Concepts\n\n"
        content += "### Concept 1\n\nDescription of concept 1.\n\n"
        content += "### Concept 2\n\nDescription of concept 2.\n\n"
        content += "## Implementation\n\n"
        content += "```python\n# Example code\ndef example():\n    pass\n```\n\n"
        content += "## Best Practices\n\n1. Always follow coding standards\n2. Write comprehensive tests\n3. Document your code\n\n"
        content += "## Conclusion\n\nThis guide covers the essential aspects of {topic}.\n"
        
        return {
            "topic": topic,
            "audience": audience,
            "format": format_type,
            "content": content,
            "word_count": len(content.split()),
            "reading_time": f"{len(content.split()) // 200} minutes"
        }
    
    async def _creative_write(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        创意写作
        
        Args:
            params: 写作参数
            
        Returns:
            创作内容
        """
        prompt = params.get("prompt", "")
        genre = params.get("genre", "story")
        length = params.get("length", "short")
        
        await asyncio.sleep(0.5)  # 模拟创作
        
        content = f"## {genre.title()} Story\n\n"
        content += f"Prompt: {prompt}\n\n"
        
        if genre == "story":
            content += "Once upon a time, in a world far beyond our imagination, there lived a young hero who would change the course of history.\n\n"
            content += "The journey began on a quiet morning, when the first light of dawn touched the ancient towers...\n\n"
        elif genre == "poem":
            content += "In digital realms where code does flow,\nWhere silicon rivers softly glow,\nA new intelligence takes form,\nBeyond the limits of the norm.\n\n"
        else:
            content += f"Creative content based on: {prompt}\n"
        
        return {
            "genre": genre,
            "length": length,
            "prompt": prompt,
            "content": content,
            "word_count": len(content.split())
        }
    
    async def _edit_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        编辑内容
        
        Args:
            params: 编辑参数
            
        Returns:
            编辑结果
        """
        content = params.get("content", "")
        edit_type = params.get("type", "proofread")
        
        await asyncio.sleep(0.3)  # 模拟编辑
        
        # 模拟编辑结果
        changes = []
        edited_content = content
        
        # 模拟一些编辑操作
        if edit_type == "proofread":
            changes.append({
                "type": "grammar",
                "original": "teh",
                "replacement": "the",
                "reason": "Spelling correction"
            })
        elif edit_type == "style":
            changes.append({
                "type": "style",
                "original": "very good",
                "replacement": "excellent",
                "reason": "Improved vocabulary"
            })
        
        return {
            "edit_type": edit_type,
            "changes_made": len(changes),
            "changes": changes,
            "edited_content": edited_content,
            "original_length": len(content),
            "edited_length": len(edited_content)
        }
    
    async def _summarize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        摘要内容
        
        Args:
            params: 摘要参数
            
        Returns:
            摘要结果
        """
        content = params.get("content", "")
        length = params.get("length", "short")
        
        await asyncio.sleep(0.3)  # 模拟摘要
        
        # 模拟摘要
        words = content.split()
        
        if length == "short":
            summary_words = words[:50]
        elif length == "medium":
            summary_words = words[:100]
        else:
            summary_words = words[:200]
        
        summary = ' '.join(summary_words)
        if len(words) > len(summary_words):
            summary += "..."
        
        return {
            "original_length": len(words),
            "summary_length": len(summary_words),
            "compression_ratio": f"{len(summary_words)/len(words)*100:.1f}%" if words else "100%",
            "summary": summary,
            "length": length
        }
