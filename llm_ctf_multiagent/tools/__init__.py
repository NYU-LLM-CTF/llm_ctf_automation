from .tool import ToolCall, ToolResult
from .run_command import RunCommandTool
from .misc import SubmitFlagTool, GiveupTool, DelegateTool

TOOLSETS = {
    "default": {RunCommandTool, SubmitFlagTool, GiveupTool, DelegateTool},
    "planner": {RunCommandTool, SubmitFlagTool, GiveupTool, DelegateTool},
}
