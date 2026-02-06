"""
FEATURE-023-C: Trace Viewer & DAG Visualization

TraceLogParser for parsing trace log files into visualization-ready graph structures.

Handles the log format:
    [TRACE-START] trace_id | API | timestamp
    [INFO] → start_function: name | input_json
    [INFO] ← return_function: name | output_json | duration
    [ERROR] ← exception: name | error | duration
    [TRACE-END] trace_id | total_duration | status
"""
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class TraceLogParser:
    """
    Parse trace log files into graph structure for visualization.
    
    Usage:
        parser = TraceLogParser()
        result = parser.parse(Path("trace.log"))
        # result = {"trace_id": "...", "nodes": [...], "edges": [...]}
    """
    
    # Regex patterns for parsing log lines
    TRACE_START_PATTERN = re.compile(
        r'\[TRACE-START\]\s*([^\|]+)\s*\|\s*([^\|]+)\s*\|\s*(.+)'
    )
    TRACE_END_PATTERN = re.compile(
        r'\[TRACE-END\]\s*([^\|]+)\s*\|\s*(\d+)ms\s*\|\s*(\w+)'
    )
    FUNCTION_START_PATTERN = re.compile(
        r'\[(INFO|DEBUG)\]\s*→\s*start_function:\s*([^\|]+)\s*\|\s*(.+)'
    )
    FUNCTION_RETURN_PATTERN = re.compile(
        r'\[(INFO|DEBUG)\]\s*←\s*return_function:\s*([^\|]+)\s*\|\s*([^\|]+)\s*\|\s*(\d+)ms'
    )
    EXCEPTION_PATTERN = re.compile(
        r'\[(ERROR|INFO|DEBUG)\]\s*←\s*exception:\s*([^\|]+)\s*\|\s*([^|]+):\s*([^\|]+)\s*\|\s*(\d+)ms'
    )
    STACK_LINE_PATTERN = re.compile(
        r'\s+at\s+(\w+)\s+\(([^:]+):?(\d+)?\)'
    )
    
    def parse(self, filepath: Path) -> Dict[str, Any]:
        """
        Parse trace log file into visualization-ready structure.
        
        Args:
            filepath: Path to the trace log file
            
        Returns:
            Dictionary with trace data:
            {
                "trace_id": str,
                "api": str,
                "timestamp": str,
                "total_time_ms": int,
                "status": str ("success" or "error"),
                "nodes": [
                    {
                        "id": str,
                        "label": str,
                        "timing": str,
                        "status": str,
                        "level": str,
                        "input": str,
                        "output": str,
                        "error": dict or None
                    }
                ],
                "edges": [
                    {"source": str, "target": str}
                ]
            }
        """
        result = {
            "trace_id": "",
            "api": "",
            "timestamp": "",
            "total_time_ms": 0,
            "status": "success",
            "nodes": [],
            "edges": []
        }
        
        if not filepath.exists():
            return result
        
        content = filepath.read_text()
        if not content.strip():
            return result
        
        lines = content.splitlines()
        nodes = []
        edges = []
        call_stack = []  # Stack of node indices for tracking parent-child
        node_counter = 0
        current_error_node = None
        stack_lines = []
        
        for raw_line in lines:
            # Keep original line for stack trace matching
            line = raw_line.strip()
            
            # Check for stack trace lines (indented with 'at')
            stack_match = self.STACK_LINE_PATTERN.match(raw_line)
            if stack_match and current_error_node is not None:
                func, file_path, line_num = stack_match.groups()
                stack_lines.append({
                    "func": func,
                    "file": file_path,
                    "line": int(line_num) if line_num else None
                })
                continue
            
            # If we were collecting stack and hit non-stack line, finalize
            if stack_lines and current_error_node is not None:
                nodes[current_error_node]["error"]["stack"] = stack_lines
                stack_lines = []
                current_error_node = None
            
            # TRACE-START
            start_match = self.TRACE_START_PATTERN.match(line)
            if start_match:
                trace_id, api, timestamp = start_match.groups()
                result["trace_id"] = trace_id.strip()
                result["api"] = api.strip()
                result["timestamp"] = timestamp.strip()
                
                # Create root API node
                nodes.append({
                    "id": f"node-{node_counter}",
                    "label": api.strip(),
                    "timing": "",
                    "status": "success",
                    "level": "API",
                    "input": "{}",
                    "output": "{}",
                    "error": None
                })
                call_stack.append(node_counter)
                node_counter += 1
                continue
            
            # TRACE-END
            end_match = self.TRACE_END_PATTERN.match(line)
            if end_match:
                _, total_ms, status = end_match.groups()
                result["total_time_ms"] = int(total_ms)
                result["status"] = status.lower()
                
                # Update root node timing
                if nodes:
                    nodes[0]["timing"] = f"{total_ms}ms"
                    if status.upper() == "ERROR":
                        nodes[0]["status"] = "error"
                continue
            
            # Function start
            func_start_match = self.FUNCTION_START_PATTERN.match(line)
            if func_start_match:
                level, func_name, input_json = func_start_match.groups()
                func_name = func_name.strip()
                
                # Create function node
                new_node = {
                    "id": f"node-{node_counter}",
                    "label": func_name,
                    "timing": "",
                    "status": "success",
                    "level": level,
                    "input": input_json.strip(),
                    "output": "{}",
                    "error": None
                }
                nodes.append(new_node)
                
                # Create edge from parent
                if call_stack:
                    parent_id = call_stack[-1]
                    edges.append({
                        "source": f"node-{parent_id}",
                        "target": f"node-{node_counter}"
                    })
                
                call_stack.append(node_counter)
                node_counter += 1
                continue
            
            # Function return
            func_return_match = self.FUNCTION_RETURN_PATTERN.match(line)
            if func_return_match:
                level, func_name, output_json, duration = func_return_match.groups()
                func_name = func_name.strip()
                
                # Pop from stack and update node
                if call_stack:
                    current_id = call_stack.pop()
                    if current_id < len(nodes):
                        nodes[current_id]["output"] = output_json.strip()
                        nodes[current_id]["timing"] = f"{duration}ms"
                continue
            
            # Exception
            exception_match = self.EXCEPTION_PATTERN.match(line)
            if exception_match:
                level, func_name, error_type, error_msg, duration = exception_match.groups()
                func_name = func_name.strip()
                
                # Pop from stack and update node with error
                if call_stack:
                    current_id = call_stack.pop()
                    if current_id < len(nodes):
                        nodes[current_id]["status"] = "error"
                        nodes[current_id]["timing"] = f"{duration}ms"
                        nodes[current_id]["error"] = {
                            "type": error_type.strip(),
                            "message": error_msg.strip(),
                            "stack": []
                        }
                        current_error_node = current_id
                continue
        
        # Finalize any remaining stack lines
        if stack_lines and current_error_node is not None:
            nodes[current_error_node]["error"]["stack"] = stack_lines
        
        result["nodes"] = nodes
        result["edges"] = edges
        
        return result
